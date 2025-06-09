import streamlit as st
import base64
import os
import crew

# Custom sidebar width - making it wider to accommodate PDF previews
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 600px;
        max-width: 600px;
    }
    </style>
    """,++
    unsafe_allow_html=True
)

# Initialize session state
if "uploaded_pdfs" not in st.session_state:
    st.session_state.uploaded_pdfs = []

if "should_clear_uploader" not in st.session_state:
    st.session_state.should_clear_uploader = False

# Helpers
def get_temp_dir_path():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    temp_dir_path = os.path.join(desktop_path, "5/knowledge")
    if not os.path.exists(temp_dir_path):
        os.makedirs(temp_dir_path)
    return temp_dir_path

def save_uploaded_file(uploadedfile):
    temp_dir_path = get_temp_dir_path()
    file_path = os.path.join(temp_dir_path, uploadedfile.name)
    with open(file_path, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return file_path

def display_pdf(file_bytes: bytes, file_name: str):
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
    pdf_display = f"""
    <iframe 
        src="data:application/pdf;base64,{base64_pdf}" 
        width="100%" 
        height="400px" 
        type="application/pdf"
    ></iframe>
    """
    st.markdown(f"### Preview of {file_name}")
    st.markdown(pdf_display, unsafe_allow_html=True)

def remove_pdf(idx):
    if 0 <= idx < len(st.session_state.uploaded_pdfs):
        file_to_remove = st.session_state.uploaded_pdfs[idx]["file_name"]
        
        # Delete from local folder
        temp_dir_path = get_temp_dir_path()
        file_path = os.path.join(temp_dir_path, file_to_remove)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                st.success(f"File {file_to_remove} deleted successfully")
            else:
                st.warning(f"File {file_to_remove} not found in {temp_dir_path}")
        except Exception as e:
            st.error(f"Error deleting file: {str(e)}")
        
        # Remove from session state
        st.session_state.uploaded_pdfs.pop(idx)
        st.rerun()

def handle_upload():
    if st.session_state.pdf_uploader is not None:
        datafile = st.session_state.pdf_uploader
        
        # Prevent duplicate upload
        if not any(pdf["file_name"] == datafile.name for pdf in st.session_state.uploaded_pdfs):
            # Save the file to disk
            file_path = save_uploaded_file(datafile)
            
            # Store file info in session state
            st.session_state.uploaded_pdfs.append({
                "file_name": datafile.name,
                "file_path": file_path,
                "file_content": datafile.getvalue(),
                "show_preview": False
            })
            
            st.session_state.should_clear_uploader = True

def toggle_preview(idx):
    if 0 <= idx < len(st.session_state.uploaded_pdfs):
        st.session_state.uploaded_pdfs[idx]["show_preview"] = not st.session_state.uploaded_pdfs[idx].get("show_preview", False)
        st.rerun()

# Sidebar: Upload and manage files
with st.sidebar:
    st.header("Add Your PDF Documents")
    
    # Use on_change callback to handle the file upload
    datafile = st.file_uploader("Upload PDF", type=['pdf'], key="pdf_uploader", on_change=handle_upload)
    
    # Handle the clear uploader flag
    if st.session_state.should_clear_uploader:
        st.session_state.should_clear_uploader = False
    
    if st.session_state.uploaded_pdfs:
        st.subheader("Uploaded Documents")
        for idx, pdf in enumerate(st.session_state.uploaded_pdfs):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"{idx + 1}. {pdf['file_name']}")
            with col2:
                preview_label = "Hide" if pdf.get("show_preview", False) else "Preview"
                if st.button(preview_label, key=f"preview_{idx}"):
                    toggle_preview(idx)
            with col3:
                if st.button("Remove", key=f"remove_{idx}"):
                    remove_pdf(idx)
            
            # Show the preview in the sidebar (moved from main panel)
            if pdf.get("show_preview", False):
                display_pdf(pdf["file_content"], pdf["file_name"])
            
    if st.button("Run Crew"):
        crew.run_script()


