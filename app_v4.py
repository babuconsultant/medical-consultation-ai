# 🏥 Medical Consultation Report Generator
# AI-Powered Medical Documentation with Advanced Speech Recognition

import streamlit as st
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import json
import io
from model import generate_consultation_report, extract_icd_cpt_codes
from audio_processor import EnhancedAudioProcessor, create_audio_processor, get_supported_audio_formats, MODEL_RECOMMENDATIONS

# Pydantic Models (keeping existing models)
class PatientInfo(BaseModel):
    sample_name: str = Field(default="", description="Patient sample name")
    description: str = Field(default="", description="Brief description")
    date_of_visit: date = Field(default_factory=date.today, description="Date of consultation")
    age: Optional[str] = Field(default="", description="Patient age")
    gender: str = Field(default="Male", description="Patient gender")

    @validator('age')
    def validate_age(cls, v):
        if v and not v.isdigit():
            raise ValueError('Age must be a number')
        return v

class MedicalHistory(BaseModel):
    reason_for_consultation: str = Field(default="", description="Reason for consultation")
    hpi: str = Field(default="", description="History of Present Illness")
    past_medical_history: str = Field(default="", description="Past Medical History")
    past_surgical_history: str = Field(default="", description="Past Surgical History")
    home_medications: str = Field(default="", description="Home Medications")
    current_medications: str = Field(default="", description="Current Medications")
    allergies: str = Field(default="No known allergies", description="Allergies")
    review_of_systems: str = Field(default="", description="Review of Systems")
    family_history: str = Field(default="", description="Family History")
    social_history: str = Field(default="", description="Social History")

class ClinicalFindings(BaseModel):
    physical_exam: str = Field(default="", description="Physical Exam Findings")
    lab_results: str = Field(default="", description="Laboratory Results")
    imaging_findings: str = Field(default="", description="Imaging/Other Diagnostics")
    assessment_and_plan: str = Field(default="", description="Assessment and Plan")

class MedicalCodes(BaseModel):
    icd_codes: List[str] = Field(default_factory=list, description="ICD-10 codes")
    cpt_codes: List[str] = Field(default_factory=list, description="CPT codes")
    description: str = Field(default="", description="Code descriptions")

# Enhanced Auto-fill function
def auto_fill_fields(transcribed_text: str) -> dict:
    """
    Auto-fill medical fields based on transcribed text using advanced keyword matching.
    """
    fields = {}
    text_lower = transcribed_text.lower()

    # Common medical complaints and their mapping
    complaint_mapping = {
        'chest pain': 'Patient presents with complaint of chest pain',
        'headache': 'Patient presents with complaint of headache',
        'abdominal pain': 'Patient presents with complaint of abdominal pain',
        'shortness of breath': 'Patient presents with complaint of shortness of breath',
        'nausea': 'Patient presents with complaint of nausea',
        'vomiting': 'Patient presents with complaint of vomiting',
        'fever': 'Patient presents with complaint of fever',
        'cough': 'Patient presents with complaint of cough'
    }

    # Check for complaints
    for complaint, description in complaint_mapping.items():
        if complaint in text_lower:
            fields["reason_for_consultation"] = description
            break

    # Medication extraction
    medication_keywords = ['taking', 'prescribed', 'medication', 'pills', 'tablets', 'drug']
    if any(keyword in text_lower for keyword in medication_keywords):
        sentences = transcribed_text.split('.')
        med_sentences = [s.strip() for s in sentences if any(keyword in s.lower() for keyword in medication_keywords)]
        if med_sentences:
            fields["current_medications"] = '. '.join(med_sentences)

    # Allergy extraction
    allergy_keywords = ['allergic', 'allergy', 'allergies', 'reaction']
    if any(keyword in text_lower for keyword in allergy_keywords):
        sentences = transcribed_text.split('.')
        allergy_sentences = [s.strip() for s in sentences if any(keyword in s.lower() for keyword in allergy_keywords)]
        if allergy_sentences:
            fields["allergies"] = '. '.join(allergy_sentences)

    # History extraction
    history_keywords = ['history', 'previous', 'past', 'before', 'earlier']
    if any(keyword in text_lower for keyword in history_keywords):
        sentences = transcribed_text.split('.')
        history_sentences = [s.strip() for s in sentences if any(keyword in s.lower() for keyword in history_keywords)]
        if history_sentences:
            fields["past_medical_history"] = '. '.join(history_sentences)

    # Default HPI assignment if no specific category found
    if not any(fields.get(key) for key in ["reason_for_consultation", "current_medications", "allergies", "past_medical_history"]):
        fields["hpi"] = transcribed_text

    return fields

# Streamlit UI Configuration
st.set_page_config(
    page_title="Medical Consultation Report Generator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
        border-radius: 10px;
        border: 1px solid #1f77b4;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background-color: #ecf0f1;
        border-left: 4px solid #3498db;
    }
    .audio-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 2rem;
    }
    .transcription-box {
        background-color: #fff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ced4da;
        min-height: 100px;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="main-header">
    🏥 AI-Powered Medical Documentation with Advanced Speech Recognition
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'patient_info' not in st.session_state:
    st.session_state.patient_info = PatientInfo()
if 'medical_history' not in st.session_state:
    st.session_state.medical_history = MedicalHistory()
if 'clinical_findings' not in st.session_state:
    st.session_state.clinical_findings = ClinicalFindings()
if 'medical_codes' not in st.session_state:
    st.session_state.medical_codes = MedicalCodes()

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🎙️ Audio Processing Settings")
    
    # Model selection (kept for compatibility)
    model_options = list(MODEL_RECOMMENDATIONS.keys())
    selected_model = st.selectbox(
        "Select Processing Mode:",
        model_options,
        index=0,
        help="Choose the speech recognition processing mode"
    )
    
    # Display model info
    if selected_model in MODEL_RECOMMENDATIONS:
        model_info = MODEL_RECOMMENDATIONS[selected_model]
        st.info(f"**{model_info['description']}**\n\n{model_info['use_case']}")
    
    # Audio processor initialization
    audio_processor = create_audio_processor(selected_model)
    
    # System info
    with st.expander("🔧 System Information"):
        system_info = audio_processor.get_model_info()
        st.json(system_info)

# Main Content Area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-header">🎤 Audio Input Methods</div>', unsafe_allow_html=True)
    
    # Audio input tabs
    audio_tab1, audio_tab2, audio_tab3 = st.tabs(["📁 Upload Audio", "🎙️ Record Audio", "🔴 Live Recording"])
    
    with audio_tab1:
        st.markdown("### Upload Audio File")
        uploaded_audio = st.file_uploader(
            "Choose an audio file",
            type=['wav', 'mp3', 'm4a', 'flac', 'ogg', 'mp4', 'avi', 'mov'],
            help="Upload an audio file containing medical consultation"
        )
        
        if uploaded_audio is not None:
            st.markdown(f"""
            <div class="audio-section">
                <h4>📄 File Information</h4>
                <p><strong>Filename:</strong> {uploaded_audio.name}</p>
                <p><strong>Size:</strong> {uploaded_audio.size:,} bytes ({uploaded_audio.size/1024/1024:.2f} MB)</p>
                <p><strong>Type:</strong> {uploaded_audio.type}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Audio player
            st.audio(uploaded_audio, format='audio/wav')
            
            if st.button("🎯 Transcribe Uploaded Audio", key="transcribe_upload"):
                with st.spinner("Processing uploaded audio..."):
                    result = audio_processor.transcribe_uploaded_file(uploaded_audio)
                    
                    if result['text'] and 'error' not in result:
                        st.session_state.transcription_result = result
                        st.success("✅ Audio transcribed successfully!")
                        
                        # Auto-fill fields
                        auto_filled = auto_fill_fields(result['text'])
                        for field, value in auto_filled.items():
                            if hasattr(st.session_state.medical_history, field):
                                setattr(st.session_state.medical_history, field, value)
                        
                        if auto_filled:
                            st.info(f"🤖 Auto-filled {len(auto_filled)} field(s) based on transcription")
                    else:
                        st.error(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
    
    with audio_tab2:
        st.markdown("### Record Audio (Fixed Duration)")
        
        # Recording duration
        duration = st.slider("Recording Duration (seconds)", 5, 60, 30)
        
        if st.button("🎤 Start Recording", key="record_fixed"):
            with st.spinner(f"Recording for {duration} seconds..."):
                result = audio_processor.record_and_transcribe(duration=duration)
                
                if result['text'] and 'error' not in result:
                    st.session_state.transcription_result = result
                    st.success("✅ Recording transcribed successfully!")
                    
                    # Auto-fill fields
                    auto_filled = auto_fill_fields(result['text'])
                    for field, value in auto_filled.items():
                        if hasattr(st.session_state.medical_history, field):
                            setattr(st.session_state.medical_history, field, value)
                    
                    if auto_filled:
                        st.info(f"🤖 Auto-filled {len(auto_filled)} field(s) based on transcription")
                else:
                    st.error(f"❌ Recording failed: {result.get('error', 'Unknown error')}")
    
    with audio_tab3:
        st.markdown("### Live Recording (Start/Stop)")
        st.info("🎙️ Click 'Start Recording' to begin, then 'Stop Recording' when finished.")
        
        # Live recording functionality - need to implement this
        col_start, col_stop = st.columns(2)
        
        with col_start:
            if st.button("🔴 Start Recording", key="start_live"):
                st.session_state.recording_active = True
                st.info("Recording started... Click 'Stop Recording' when finished.")
        
        with col_stop:
            if st.button("⏹️ Stop Recording", key="stop_live"):
                if hasattr(st.session_state, 'recording_active') and st.session_state.recording_active:
                    st.session_state.recording_active = False
                    st.success("Recording stopped and processing...")
                    # Note: Live recording functionality would need to be implemented in audio_processor.py
                    st.info("Live recording feature would be implemented here")

with col2:
    st.markdown('<div class="section-header">📝 Transcription Results</div>', unsafe_allow_html=True)
    
    if 'transcription_result' in st.session_state:
        result = st.session_state.transcription_result
        
        # Transcription display
        st.markdown("### 📄 Transcribed Text")
        st.markdown(f"""
        <div class="transcription-box">
            {result['text']}
        </div>
        """, unsafe_allow_html=True)
        
        # Transcription metadata
        with st.expander("📊 Transcription Details"):
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.metric("Confidence", f"{result['confidence']:.2f}")
                st.metric("Duration", f"{result['duration']:.2f}s")
            with col_meta2:
                st.metric("Language", result['language'])
                st.metric("System", result['model_used'])
        
        # Edit transcription
        st.markdown("### ✏️ Edit Transcription")
        edited_text = st.text_area(
            "Edit the transcribed text if needed:",
            value=result['text'],
            height=150,
            key="edit_transcription"
        )
        
        if st.button("🔄 Update Auto-fill with Edited Text"):
            auto_filled = auto_fill_fields(edited_text)
            for field, value in auto_filled.items():
                if hasattr(st.session_state.medical_history, field):
                    setattr(st.session_state.medical_history, field, value)
            
            st.success(f"✅ Updated {len(auto_filled)} field(s) with edited transcription")
    else:
        st.info("🎙️ Upload an audio file or record audio to see transcription results here.")

# Medical Form Section
st.markdown('<div class="section-header">📋 Medical Consultation Form</div>', unsafe_allow_html=True)

# Patient Information
with st.expander("👤 Patient Information", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.patient_info.sample_name = st.text_input(
            "Patient Name", 
            value=st.session_state.patient_info.sample_name
        )
        st.session_state.patient_info.age = st.text_input(
            "Age", 
            value=st.session_state.patient_info.age
        )
    with col2:
        st.session_state.patient_info.gender = st.selectbox(
            "Gender", 
            ["Male", "Female", "Other"], 
            index=["Male", "Female", "Other"].index(st.session_state.patient_info.gender)
        )
        st.session_state.patient_info.date_of_visit = st.date_input(
            "Date of Visit", 
            value=st.session_state.patient_info.date_of_visit
        )
    
    st.session_state.patient_info.description = st.text_area(
        "Brief Description", 
        value=st.session_state.patient_info.description,
        height=100
    )

# Medical History
with st.expander("📚 Medical History", expanded=True):
    st.session_state.medical_history.reason_for_consultation = st.text_area(
        "Reason for Consultation",
        value=st.session_state.medical_history.reason_for_consultation,
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.medical_history.hpi = st.text_area(
            "History of Present Illness (HPI)",
            value=st.session_state.medical_history.hpi,
            height=150
        )
        st.session_state.medical_history.past_medical_history = st.text_area(
            "Past Medical History",
            value=st.session_state.medical_history.past_medical_history,
            height=100
        )
        st.session_state.medical_history.current_medications = st.text_area(
            "Current Medications",
            value=st.session_state.medical_history.current_medications,
            height=100
        )
        st.session_state.medical_history.family_history = st.text_area(
            "Family History",
            value=st.session_state.medical_history.family_history,
            height=100
        )
    
    with col2:
        st.session_state.medical_history.past_surgical_history = st.text_area(
            "Past Surgical History",
            value=st.session_state.medical_history.past_surgical_history,
            height=100
        )
        st.session_state.medical_history.allergies = st.text_area(
            "Allergies",
            value=st.session_state.medical_history.allergies,
            height=100
        )
        st.session_state.medical_history.review_of_systems = st.text_area(
            "Review of Systems",
            value=st.session_state.medical_history.review_of_systems,
            height=100
        )
        st.session_state.medical_history.social_history = st.text_area(
            "Social History",
            value=st.session_state.medical_history.social_history,
            height=100
        )

# Clinical Findings
with st.expander("🔬 Clinical Findings", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.clinical_findings.physical_exam = st.text_area(
            "Physical Exam Findings",
            value=st.session_state.clinical_findings.physical_exam,
            height=150
        )
        st.session_state.clinical_findings.lab_results = st.text_area(
            "Laboratory Results",
            value=st.session_state.clinical_findings.lab_results,
            height=150
        )
    
    with col2:
        st.session_state.clinical_findings.imaging_findings = st.text_area(
            "Imaging/Other Diagnostics",
            value=st.session_state.clinical_findings.imaging_findings,
            height=150
        )
        st.session_state.clinical_findings.assessment_and_plan = st.text_area(
            "Assessment and Plan",
            value=st.session_state.clinical_findings.assessment_and_plan,
            height=150
        )

# Generate Report Section
st.markdown('<div class="section-header">📄 Generate Medical Report</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🏥 Generate Complete Medical Report", type="primary", use_container_width=True):
        # Prepare data for report generation
        patient_data = {
            "patient_info": st.session_state.patient_info.dict(),
            "medical_history": st.session_state.medical_history.dict(),
            "clinical_findings": st.session_state.clinical_findings.dict()
        }
        
        with st.spinner("🤖 Generating comprehensive medical report..."):
            try:
                # Generate the report using corrected function call
                report = generate_consultation_report(
                    sample_name=patient_data["patient_info"]["sample_name"],
                    description=patient_data["patient_info"]["description"],
                    date_of_visit=str(patient_data["patient_info"]["date_of_visit"]),
                    age=patient_data["patient_info"]["age"],
                    gender=patient_data["patient_info"]["gender"],
                    reason_for_consultation=patient_data["medical_history"]["reason_for_consultation"],
                    hpi=patient_data["medical_history"]["hpi"],
                    past_medical_history=patient_data["medical_history"]["past_medical_history"],
                    past_surgical_history=patient_data["medical_history"]["past_surgical_history"],
                    home_medications=patient_data["medical_history"]["home_medications"],
                    current_medications=patient_data["medical_history"]["current_medications"],
                    allergies=patient_data["medical_history"]["allergies"],
                    review_of_systems=patient_data["medical_history"]["review_of_systems"],
                    family_history=patient_data["medical_history"]["family_history"],
                    social_history=patient_data["medical_history"]["social_history"],
                    physical_exam=patient_data["clinical_findings"]["physical_exam"],
                    lab_results=patient_data["clinical_findings"]["lab_results"],
                    imaging_findings=patient_data["clinical_findings"]["imaging_findings"],
                    assessment_and_plan=patient_data["clinical_findings"]["assessment_and_plan"]
                )
                
                # Extract medical codes
                codes_result = extract_icd_cpt_codes(report)
                
                # Display the generated report
                st.markdown("### 📋 Generated Medical Report")
                st.markdown("---")
                st.markdown(report)
                
                # Display medical codes
                st.markdown("### 🏷️ Medical Codes")
                st.markdown(codes_result)
                
                # Download options
                st.markdown("### 💾 Download Options")
                
                # Prepare download data
                full_report_data = {
                    "patient_info": patient_data["patient_info"],
                    "medical_history": patient_data["medical_history"],
                    "clinical_findings": patient_data["clinical_findings"],
                    "generated_report": report,
                    "medical_codes": codes_result,
                    "generation_timestamp": datetime.now().isoformat()
                }
                
                # JSON download
                json_str = json.dumps(full_report_data, indent=2, default=str)
                st.download_button(
                    label="📄 Download as JSON",
                    data=json_str,
                    file_name=f"medical_report_{st.session_state.patient_info.sample_name}_{date.today()}.json",
                    mime="application/json"
                )
                
                # Text download
                text_report = f"""
MEDICAL CONSULTATION REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{report}

MEDICAL CODES:
{codes_result}
                """
                
                st.download_button(
                    label="📝 Download as Text",
                    data=text_report,
                    file_name=f"medical_report_{st.session_state.patient_info.sample_name}_{date.today()}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    🏥 Medical Consultation Report Generator v4.0<br>
    AI-Powered Medical Documentation with Advanced Speech Recognition<br>
    <small>⚠️ This tool is for documentation assistance only. Always verify medical information.</small>
</div>
""", unsafe_allow_html=True)