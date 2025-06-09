# AI-Powered Sales Assistant

An intelligent agentic solution designed to streamline and automate the creation of tailored sales proposals. This tool uses a multi-agent system, powered by CrewAI and local LLMs, to analyze customer requirement documents, gather necessary information, and generate customized proposals.

---

## 🚀 Features

* **Interactive Web Interface**: A user-friendly interface built with Streamlit for easy management of customer documents.
* **Dynamic Document Handling**: Upload, preview, and remove customer PDF documents directly from the UI.
* **Automated Requirements Analysis**: An AI agent systematically analyzes provided documents to find answers to crucial sales questions.
* **Interactive Q&A for Missing Information**: If the documents don't provide all the necessary details, the system interactively prompts the user for the missing information.
* **Tailored Proposal Generation**: A dedicated AI agent drafts a comprehensive sales proposal, blending information from the customer's documents with your company's profile.
* **Advanced Agentic Workflow**: Leverages an advanced framework to manage a team of specialized AI agents for a sophisticated, multi-step process.
* **Local & Private**: Utilizes Ollama to run large language models on your local machine, ensuring all data remains private and secure.

---

## ⚙️ How It Works

The AI Sales Assistant operates through a multi-stage agentic workflow.

### **Stage 1: Information Gathering**

1.  **Document Upload**: The process begins when you upload one or more customer requirement documents through the interactive web interface.
2.  **Requirements Identification**: An "Analyst" agent initiates the process. It uses a predefined checklist of questions to create a structured list of all information required for a proposal.
3.  **Automated Analysis**: A "Document Analyzer" agent then scans the uploaded documents to find answers to these questions, populating the requirements list with any information it discovers.

### **Stage 2: Proposal Generation**

This stage's workflow adapts based on the outcome of the first.

**Scenario A: All Information is Found**

If the "Document Analyzer" agent finds answers to all the required questions within the provided documents, the system proceeds directly to the final step.

**Scenario B: Information Gaps are Detected**

1.  **Interactive Q&A**: If the system detects that some requirements have not been met, it will enter an interactive Q&A mode. You will be prompted in the command line (where the application was launched) to provide the missing answers.
2.  **Data Consolidation**: Your answers are seamlessly integrated with the information previously extracted from the documents.

**Final Step: Proposal Generation**

1.  **Drafting the Proposal**: A "Proposal Generator" agent takes over. It synthesizes all the gathered information—both from the documents and your interactive input—along with a pre-configured company profile to draft a professional, tailored sales proposal.
2.  **Final Output**: The final, customized proposal is then saved as a text file in the project's root directory.

---

## 🛠️ Setup and Installation

### **Prerequisites**

* Python 3.8+
* [Ollama](https://ollama.com/) installed and running.

### **Installation Steps**

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/ai-sales-assistant.git](https://github.com/your-username/ai-sales-assistant.git)
    cd ai-sales-assistant
    ```

2.  **Install Dependencies**
    ```bash
    pip install streamlit crewai "crewai[tools]" langchain-community pydantic
    ```

3.  **Set Up Ollama Models**

    You need to have the language model for generation and the embedding model for analysis. Pull them using the following commands:
    ```bash
    ollama pull llama3
    ollama pull mxbai-embed-large
    ```
    *Ensure the Ollama application is running before you start the assistant.*

---

## ▶️ Usage

1.  **Define a Checklist**: Before running, define the standard list of questions you want the assistant to use. This is done in a designated text file within the project.
2.  **Prepare the Upload Location**: Ensure the designated folder for document uploads exists. The application is configured to use a specific path which can be adjusted in the application's source code.
3.  **Launch the Application**: Start the interactive web interface by running the main Streamlit application script from your terminal.
4.  **Upload Documents**: Open your web browser to the local application URL and use the sidebar to upload the customer's PDF documents.
5.  **Run the Crew**: Click the "Run Crew" button in the sidebar to initiate the analysis and proposal generation process.
6.  **Answer Questions (If Prompted)**: If the agents couldn't find all the answers in the PDFs, switch to your terminal. You will be prompted to enter the answers for the remaining questions.
7.  **Retrieve Your Proposal**: A text file containing the final, tailored proposal will be generated in the project's root directory once the process is complete.

---
