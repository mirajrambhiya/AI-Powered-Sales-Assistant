import os
import json
from crewai import Agent,Task,LLM,Crew
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource



def run_script():
    class AnalystOutput(BaseModel):
        questions: List[Dict[str, str]] = Field(default_factory=list)

    llm = LLM(model = "ollama/llama3",
            base_url="http://localhost:11434")

    text_source = TextFileKnowledgeSource(
    file_paths=["things_to_cover.txt"]
    )

    def find_pdf_files(folder_path):
        pdf_files = []

        # Iterate through all files in the folder
        for filename in os.listdir(folder_path):
            # Check if the file is a PDF (case insensitive)
            if filename.lower().endswith('.pdf'):
                pdf_files.append(filename)

        return pdf_files

    pdf_files = find_pdf_files("knowledge")

    analyst_agent = Agent(
    role = "Sales Proposal Requirements Analyst",
    goal = "You analyze certain documents to gather all questions to create a tailored sales proposal for the customer. You must return a properly formatted Python dictionary with questions and answers.",
    backstory = "As a seasoned sales proposal specialist with extensive experience in enterprise solutions, you have mastered the art of requirements analysis. "
                "Your keen eye for detail and systematic approach ensures no critical information is missed in the proposal process. "
                "You excel at identifying gaps in customer information and coordinating with other team members to gather missing details. "
                "Your ability to maintain a comprehensive checklist of requirements while adapting to each customer's unique needs has made you an invaluable asset "
                "in creating successful, tailored sales proposals. You understand that thorough requirements gathering is the foundation of any successful proposal.",
    knowledge_sources = [text_source],
    llm = llm
    )

    #Tasks

    analyst_task = Task(
        description = """
            Take context of questions only from documents in text_source.
            Create a json object containing all questions along with their answers as "".
            Do not answer any questions randomly.
        """,
        expected_output = """
            A Python dictionary with the structure {"questions": [{"question": "Q1", "answer": ""}, {"question": "Q2", "answer": ""}]}
        """,

        agent = analyst_agent,
        output_json = AnalystOutput,
        output_file = "analyst_output.json"
    )

    # Initialize pdf_source as None
    pdf_source = None
    
    if pdf_files != []:
        pdf_source = PDFKnowledgeSource(
            file_paths= pdf_files,
            chunk_size=200,
            chunk_overlap=50
        )

        customer_doc_analyzer = Agent(
            role = "Customer Document Analyzer",
            goal = "Analyze the customer documents provided and extract important and necessary details from the document",
            backstory = "As a highly skilled document analyst with years of experience in business intelligence, you excel at extracting critical information from complex documents. "
                        "Your meticulous attention to detail and systematic approach ensures that no important information is overlooked. "
                        "You have developed a keen eye for identifying key business requirements, technical specifications, and strategic priorities within various document types. "
                        "Your background in both technical documentation and business analysis allows you to understand the context and significance of information across different business domains. "
                        "You take pride in your ability to organize and structure information in a way that supports effective decision-making and proposal development.",
            llm = llm,
            knowledge_sources = [pdf_source]
        )

        customer_doc_analysis = Task(
            description = """
                Using the json received from the analyst task, search for answers in the pdf_source using retrieval from documents in pdf_source.
                Considering each question from json object, retrieve the relevant answers from the pdf_source for each question.
                Add these relevant answers for the questions to the a new json object created.
                For any answers not found in the pdf_source documents, keep the answers key as "" in the new json object created.
            """,
            expected_output = """
                A json object containing the questions and their corresponding answers found from the documents in the pdf_source.
                For any answer not found in the documents in pdf_source, the json object contains the respective question along with the answer as "".
                Output is a python dictionary with the structure {"questions": [{"question": "Q1", "answer": "A1"}, {"question": "Q2", "answer": ""}]}
            """,
            agent = customer_doc_analyzer,
            output_json = AnalystOutput,
            output_file = "analyst_output.json",
            context = [analyst_task]
        )

        crew_1 = Crew(
        agents = [analyst_agent, customer_doc_analyzer],
        tasks = [analyst_task, customer_doc_analysis],
        verbose = True,
        embedder={
        "provider": "ollama",
        "config": {
            "model": "mxbai-embed-large"
            }
        }
        )
        crew_output_1 = crew_1.kickoff()

    else:
        crew_1 = Crew(
        agents = [analyst_agent],
        tasks = [analyst_task],
        verbose = True,
        embedder={
        "provider": "ollama",
        "config": {
            "model": "mxbai-embed-large"
            }
        }
        )
        crew_output_1 = crew_1.kickoff()

    def check_unanswered_questions(output_file="analyst_output.json"):
        if not os.path.exists(output_file):
            return False
        
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            unanswered_questions = [q for q in data["questions"] if not q.get("answer")]
            
            if unanswered_questions:
                return True
            else:
                return False
                
        except json.JSONDecodeError:
            print(f"Error: {output_file} contains invalid JSON")
            return False
        except Exception as e:
            print(f"Error checking unanswered questions: {str(e)}")
            return False
    
    # Call the function after analyst task completes
    has_unanswered = check_unanswered_questions()

    company_source = StringKnowledgeSource(
            content="""
                    **Company Profile: Synapse Analytics Solutions**

                    **1. Company Description:**

                    Synapse Analytics Solutions is a B2B technology firm specializing in developing and implementing AI-powered predictive analytics software for mid-to-large sized manufacturing companies in India. Based in Pune, Maharashtra, Synapse provides a cloud-based platform designed to integrate with existing manufacturing execution systems (MES) and enterprise resource planning (ERP) software. Their core focus is helping manufacturers improve operational efficiency, reduce downtime, and enhance product quality through data-driven insights. They position themselves as partners in digital transformation for the manufacturing sector.

                    **2. Mission Statement:**

                    To empower manufacturers with predictive insights, transforming operational data into actionable intelligence for enhanced productivity, reliability, and competitive advantage.

                    **3. Vision:**

                    To be the leading provider of predictive analytics solutions for the Indian manufacturing sector, recognized for driving measurable improvements and fostering innovation in industrial operations.

                    **4. Target Audience (Client Base):**

                    - **Industry Sectors:** Automotive Manufacturing & Assembly, Heavy Machinery, Pharmaceuticals, Chemicals, Consumer Packaged Goods (CPG) Manufacturing.
                    - **Company Size:** Mid-to-large enterprises, typically with annual revenues exceeding ₹100 Crore, multiple production lines, and established data collection practices (even if not fully utilized).
                    - **Decision Makers & Influencers:** Chief Operating Officers (COOs), Plant Managers, Heads of Manufacturing, Operations Directors, Quality Assurance (QA) Managers, Maintenance Managers, IT Directors, Chief Technology Officers (CTOs).
                    - **Client Pain Points:** Unplanned equipment downtime, high maintenance costs, inconsistent product quality, production bottlenecks, difficulty in forecasting demand accurately, underutilization of collected sensor/machine data, pressure to adopt Industry 4.0 practices.

                    **5. Product/Service Offering:**

                    Synapse offers a modular SaaS platform called **"Synapse Predictive Suite"**. Key modules include:

                    - **Module 1: Predictive Maintenance (Synapse PM)**
                    - *Description:* Uses machine learning algorithms to analyze sensor data (vibration, temperature, pressure, etc.) from critical equipment to predict potential failures *before* they happen. Provides alerts, estimated time-to-failure, and root cause suggestions. Includes dashboarding for asset health monitoring.
                    - *Use Case Example:* An automotive parts manufacturer uses Synapse PM on their CNC machines. The system flags an abnormal vibration pattern on a specific spindle, predicting a bearing failure within the next 72 hours. Maintenance is scheduled proactively during a planned shift change, avoiding costly emergency downtime and potential damage to the machine.
                    - *Value Proposition:* Reduces unplanned downtime, lowers maintenance costs (shift from reactive to predictive), extends equipment lifespan, improves safety.
                    - **Module 2: Quality Control Analytics (Synapse QC)**
                    - *Description:* Analyzes production line data (sensor readings, machine settings, environmental factors, manual inspection results) to identify patterns correlated with quality defects. Helps pinpoint root causes of quality issues and predict batches likely to have deviations.
                    - *Use Case Example:* A pharmaceutical company uses Synapse QC to monitor tablet press parameters. The system identifies a subtle combination of humidity and compression force that correlates with a higher incidence of tablet capping. Operators adjust settings proactively, reducing batch rejection rates.
                    - *Value Proposition:* Improves product consistency, reduces scrap and rework rates, enhances compliance, identifies optimization opportunities in the production process.
                    - **Service Component:**
                    - **Implementation & Integration Services:** Tailored setup, integration with existing client systems (ERP, MES, SCADA), data mapping, and validation.
                    - **Training:** On-site or remote training for operators, maintenance teams, and analysts on using the platform effectively.
                    - **Ongoing Support & Consulting:** Dedicated customer success manager, technical support, and optional data science consulting services for custom model development or deeper analysis.

                    **6. Pricing Strategy:**

                    - **Subscription Model:** Primarily Annual Recurring Revenue (ARR) based on: 
                    - Number of assets/machines being monitored (for Synapse PM).
                    - Number of production lines or data points analyzed (for Synapse QC).
                    - Number of user licenses.
                    - **Tiered Structure:** Different tiers (e.g., Standard, Professional, Enterprise) offering varying levels of features, data history, API access, and support.
                    - **Implementation Fee:** One-time fee for setup, integration, and initial training, varying based on complexity.
                    - **Pricing Example:** A mid-sized plant using Synapse PM on 50 critical assets might have an annual subscription fee ranging from ₹15 Lakhs to ₹40 Lakhs depending on the tier and add-ons, plus an initial implementation fee. Pricing emphasizes Return on Investment (ROI) through documented cost savings (downtime reduction, scrap reduction).

                    **7. Sales & Distribution Channels:**

                    - **Direct Sales Force:** Experienced account executives with engineering or manufacturing backgrounds who understand client operations and can articulate ROI. Based regionally across India's industrial hubs.
                    - **Inside Sales Team:** For lead generation, qualification, setting up initial meetings and demos.
                    - **Channel Partners:** Collaboration with system integrators, industrial automation companies, and ERP consultants who serve the manufacturing sector.
                    - **Sales Process:** Consultative selling approach involving discovery calls, technical deep-dives, customized demos, proof-of-concept (PoC) projects (sometimes paid), detailed proposal outlining ROI, and contract negotiation. Long sales cycles (typically 6-18 months).

                    **8. Marketing & Communication (B2B Focus):**

                    - **Content Marketing:** Whitepapers on predictive maintenance benefits, case studies detailing client ROI, articles on Industry 4.0 adoption, webinars featuring industry experts.
                    - **Digital Marketing:** Targeted LinkedIn advertising and content promotion, Search Engine Optimization (SEO) for relevant keywords (e.g., "predictive maintenance software India", "manufacturing analytics platform"), targeted email campaigns to nurture leads.
                    - **Industry Events:** Participation (booths, speaking slots) in major manufacturing, automation, and technology trade shows and conferences in India.
                    - **Account-Based Marketing (ABM):** Highly personalized marketing and sales efforts targeted at specific high-value potential clients.
                    - **Website:** Professional website focused on solutions, client results (case studies, testimonials), resources (whitepapers, blog), and clear calls-to-action (Request a Demo, Contact Sales).

                    **9. Unique Selling Proposition (USP):**
                    Synapse Analytics Solutions offers **AI-driven predictive analytics specifically tailored for the Indian manufacturing context**, combining sophisticated technology with deep domain expertise and strong local support. Unlike generic global platforms, Synapse focuses on integrating seamlessly with systems common in India and addressing the specific operational challenges and regulatory nuances faced by Indian manufacturers, all while demonstrating clear ROI. Their blend of powerful software and hands-on implementation/support services differentiates them.
                    """,
            chunk_size=4000,    
            chunk_overlap=200     
        )

    if(has_unanswered):        

        langchain_llm = Ollama(model="gemma3")
        
        # Initialize conversation memory
        memory = ConversationBufferMemory()
        
        # Create conversation chain
        conversation = ConversationChain(
            llm=langchain_llm,
            memory=memory,
            verbose=True
        )
        
        # Load the analyst output file
        output_file = "analyst_output.json"
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        # Get unanswered questions
        unanswered_questions = [q for q in data["questions"] if not q.get("answer")]
        
        
        # Ask each unanswered question and collect answers
        for i, question in enumerate(unanswered_questions):
            print(f"Question {i+1}: {question['question']}")
            
            # Get user's answer
            user_answer = input("Your answer: ")
            
            # Update the question with the answer
            for q in data["questions"]:
                if q["question"] == question["question"]:
                    q["answer"] = user_answer
                    break
            
            print("\n")
        
        # Save the updated data back to the file
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        
        # Store the entire conversation
        conversation_history = {
            "questions": data["questions"],
            "full_conversation": memory.chat_memory.messages
        }

        # Save the conversation history
        with open("knowledge/conversation_history.json", 'w') as f:
            json.dump(conversation_history, f, indent=4)

        json_source = JSONKnowledgeSource(
            file_paths=["conversation_history.json"]
        )

        proposal_generator_agent = Agent(
            role = "Sales Proposal Generator",
            goal = "Generate a tailored sales proposal based on the customer's requirements",
            backstory = "With a background in sales and proposal writing, you excel at creating comprehensive and personalized proposals. "
                        "Your experience in crafting successful sales proposals has honed your ability to present solutions that align with customer needs. "
                        "You understand that a well-crafted proposal must address the customer's specific requirements and build confidence in the solution. "
                        "Your approach is both professional and persuasive, ensuring that the proposal not only meets but exceeds customer expectations. "
                        "You believe that a successful sales proposal is the key to closing deals and building long-term relationships with clients.",
            llm = llm,
            knowledge_sources = [json_source, company_source]
        )

        generation_task = Task(
            description = """
                Using the json_source containing questions and answers provided in the list from the analyst_task, generate a tailored sales proposal.
                Generate the sales proposal putting more emphasis on the answers in the json_source and taking into context the documents in the company_source.

            """,
            expected_output = """
                A tailored sales proposal based on the customer's requirements.
            """,
            agent = proposal_generator_agent,
            output_file = "sales_proposal.txt"
        )

        crew_2 = Crew(
            agents = [proposal_generator_agent],
            tasks = [generation_task],
            verbose = True,
            embedder={
            "provider": "ollama",
            "config": {
                "model": "mxbai-embed-large"
                }
            }
        )
        
        crew_output_2 = crew_2.kickoff()

    else:
        json_source = JSONKnowledgeSource(
            file_paths=["analyst_output.json"]
        )

        proposal_generator_agent = Agent(
            role = "Sales Proposal Generator",
            goal = "Generate a tailored sales proposal based on the customer's requirements",
            backstory = "With a background in sales and proposal writing, you excel at creating comprehensive and personalized proposals. "
                        "Your experience in crafting successful sales proposals has honed your ability to present solutions that align with customer needs. "
                        "You understand that a well-crafted proposal must address the customer's specific requirements and build confidence in the solution. "
                        "Your approach is both professional and persuasive, ensuring that the proposal not only meets but exceeds customer expectations. "
                        "You believe that a successful sales proposal is the key to closing deals and building long-term relationships with clients.",
            llm = llm,
            knowledge_sources = [json_source, company_source]
        )

        generation_task = Task(
            description = """
                Using the json_source containing questions and answers provided in the list from the analyst_task, generate a tailored sales proposal.
                Generate the sales proposal putting more emphasis on the answers in the json_source and taking into context the documents in the company_source.
            """,
            expected_output = """
                A tailored sales proposal based on the customer's requirements.
            """,
            agent = proposal_generator_agent,
            context = [analyst_task],
            output_file = "sales_proposal.txt"
        )   

        crew_2 = Crew(
            agents = [proposal_generator_agent],
            tasks = [generation_task],
            verbose = True,
            embedder={
            "provider": "ollama",
            "config": {
                "model": "mxbai-embed-large"
                }
            }
        )
        crew_output_2 = crew_2.kickoff()