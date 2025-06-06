import os
import yaml
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Use the updated Ollama import
try:
    from langchain_ollama import Ollama
except ImportError:
    # Fallback to the old import if the new one isn't available
    from langchain_community.llms import Ollama

load_dotenv()

# Langsmith Tracking (if you need it)
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "medical-consultation")

# 1. Load LLM
llm = Ollama(model="llama3.2:latest")

# 2. Read the YAML file and build ChatPromptTemplate
def load_prompt_from_yaml(yaml_file_path: str) -> ChatPromptTemplate:
    """Load prompt template from YAML file."""
    try:
        with open(yaml_file_path, "r") as f:
            yaml_dict = yaml.safe_load(f)
        
        # Convert YAML messages into the format ChatPromptTemplate expects
        messages = []
        for msg in yaml_dict["messages"]:
            messages.append((msg["role"], msg["content"]))
        
        return ChatPromptTemplate.from_messages(messages)
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file {yaml_file_path} not found")
    except Exception as e:
        raise Exception(f"Error loading template: {e}")

# Load main prompt template
prompt = load_prompt_from_yaml("template.yaml")

# 3. Create the chain with an output parser
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# 4. Define the main function to generate consultation reports
def generate_consultation_report(
    sample_name: str = "",
    description: str = "",
    date_of_visit: str = "",
    age: str = "",
    gender: str = "",
    reason_for_consultation: str = "",
    hpi: str = "",
    past_medical_history: str = "",
    past_surgical_history: str = "",
    home_medications: str = "",
    current_medications: str = "",
    allergies: str = "",
    review_of_systems: str = "",
    family_history: str = "",
    social_history: str = "",
    physical_exam: str = "",
    lab_results: str = "",
    imaging_findings: str = "",
    assessment_and_plan: str = ""
) -> str:
    """
    Calls the LLM with all required fields. Returns the fully formatted report.
    """
    inputs = {
        "sample_name": sample_name,
        "description": description,
        "date_of_visit": date_of_visit,
        "age": age,
        "gender": gender,
        "reason_for_consultation": reason_for_consultation,
        "hpi": hpi,
        "past_medical_history": past_medical_history,
        "past_surgical_history": past_surgical_history,
        "home_medications": home_medications,
        "current_medications": current_medications,
        "allergies": allergies,
        "review_of_systems": review_of_systems,
        "family_history": family_history,
        "social_history": social_history,
        "physical_exam": physical_exam,
        "lab_results": lab_results,
        "imaging_findings": imaging_findings,
        "assessment_and_plan": assessment_and_plan,
    }

    try:
        report = chain.invoke(inputs)
        return report
    except Exception as e:
        return f"Error generating report: {e}"

# --- ICD/CPT Code Extraction Chain ---
def initialize_icd_chain():
    """Initialize the ICD/CPT extraction chain."""
    try:
        icd_prompt = load_prompt_from_yaml("icd_cpt_template.yaml")
        return icd_prompt | llm | output_parser
    except Exception as e:
        print(f"Warning: Could not load ICD/CPT template: {e}")
        return None

# Initialize ICD chain
icd_chain = initialize_icd_chain()

def extract_icd_cpt_codes(full_report_text: str) -> str:
    """
    Extracts ICD-10 and CPT codes from the full consultation report text.
    """
    if not icd_chain:
        return "ICD/CPT extraction not available - template file missing"
    
    try:
        return icd_chain.invoke({"full_report_text": full_report_text})
    except Exception as e:
        return f"Error extracting medical codes: {e}"

# Alternative function that matches the original app's expectation
def generate_consultation_report_from_dict(patient_data: dict) -> str:
    """
    Alternative function that accepts a dictionary of patient data.
    """
    patient_info = patient_data.get("patient_info", {})
    medical_history = patient_data.get("medical_history", {})
    clinical_findings = patient_data.get("clinical_findings", {})
    
    return generate_consultation_report(
        sample_name=patient_info.get("sample_name", ""),
        description=patient_info.get("description", ""),
        date_of_visit=str(patient_info.get("date_of_visit", "")),
        age=patient_info.get("age", ""),
        gender=patient_info.get("gender", ""),
        reason_for_consultation=medical_history.get("reason_for_consultation", ""),
        hpi=medical_history.get("hpi", ""),
        past_medical_history=medical_history.get("past_medical_history", ""),
        past_surgical_history=medical_history.get("past_surgical_history", ""),
        home_medications=medical_history.get("home_medications", ""),
        current_medications=medical_history.get("current_medications", ""),
        allergies=medical_history.get("allergies", ""),
        review_of_systems=medical_history.get("review_of_systems", ""),
        family_history=medical_history.get("family_history", ""),
        social_history=medical_history.get("social_history", ""),
        physical_exam=clinical_findings.get("physical_exam", ""),
        lab_results=clinical_findings.get("lab_results", ""),
        imaging_findings=clinical_findings.get("imaging_findings", ""),
        assessment_and_plan=clinical_findings.get("assessment_and_plan", "")
    )

# Test function to verify everything works
def test_model_connection():
    """Test if the model is working properly."""
    try:
        test_response = llm.invoke("Hello, please respond with 'Model is working'")
        return f"✅ Model test successful: {test_response}"
    except Exception as e:
        return f"❌ Model test failed: {e}"

if __name__ == "__main__":
    # Test the model connection
    print(test_model_connection())
