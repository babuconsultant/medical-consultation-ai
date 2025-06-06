# 🏥 Medical Consultation Report Generator
### AI-Powered Medical Documentation with Advanced Speech Recognition

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![Pydantic](https://img.shields.io/badge/pydantic-v2.0+-green.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-brightgreen.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

*Transform medical consultations into comprehensive reports using AI-powered speech recognition and intelligent form automation.*

[🚀 Quick Start](#-quick-start) • [📖 Features](#-features) • [🎯 Demo](#-demo) • [📋 Documentation](#-documentation) • [🤝 Contributing](#-contributing)

</div>

---

## 🌟 Overview

The Medical Consultation Report Generator is a cutting-edge healthcare application that revolutionizes medical documentation by combining advanced speech recognition technology with intelligent form automation. Healthcare professionals can now convert audio consultations into structured, comprehensive medical reports with minimal manual input.

### ✨ What Makes This Special

- **🎙️ Multi-Modal Audio Processing**: Upload files, record audio, or use live recording with advanced speech recognition
- **🤖 Intelligent Auto-Fill**: Smart keyword matching automatically populates medical fields from transcribed content
- **📋 Comprehensive Medical Forms**: Complete patient information, history, and clinical findings management
- **🏥 Professional Report Generation**: AI-powered generation of formatted medical consultation reports
- **🏷️ Medical Coding Integration**: Automatic ICD-10 and CPT code extraction
- **💾 Multiple Export Formats**: Download reports as JSON or formatted text
- **🎨 Professional Healthcare UI**: Clean, responsive interface designed for medical workflows

---

## 🚀 Quick Start

### Prerequisites
Python 3.8 or higher
pip package manager
Microphone access (for recording features)

### Installation

1. **Clone the repository**

git clone https://github.com/babuconsultant/medical-consultation-ai.git
cd medical-consultation-ai

2. **Install dependencies**
pip install -r requirements.txt

3. **Run the application**
streamlit run app.py

4. **Open your browser**
Navigate to `http://localhost:8501`

---

## 📖 Features

### 🎙️ Advanced Audio Processing

| Feature | Description | Use Case |
|---------|-------------|----------|
| **File Upload** | Support for WAV, MP3, M4A, FLAC, OGG, MP4, AVI, MOV | Import existing consultation recordings |
| **Fixed Duration Recording** | 5-60 second configurable recording | Quick voice notes and brief consultations |
| **Live Recording** | Start/stop recording functionality | Real-time consultation documentation |
| **Multiple Models** | Fast, Accurate, and Medical-specialized modes | Optimized for different scenarios |

### 🤖 Intelligent Auto-Fill System

The application automatically detects and categorizes medical information:

- **Chief Complaints**: Chest pain, headache, abdominal pain, shortness of breath, etc.
- **Current Medications**: Prescription detection and dosage extraction
- **Allergies**: Known allergic reactions and sensitivities
- **Medical History**: Previous conditions and treatments
- **Smart Categorization**: Automatic field population based on context

### 📋 Comprehensive Medical Documentation

#### **Patient Information Section**
- Patient demographics and visit details
- Age, gender, and consultation date
- Brief description and case overview

#### **Medical History Section**
- **History of Present Illness (HPI)**: Detailed symptom progression
- **Past Medical History**: Previous conditions and treatments
- **Past Surgical History**: Surgical procedures and outcomes
- **Current Medications**: Active prescriptions and dosages
- **Allergies**: Known allergic reactions
- **Review of Systems**: Systematic symptom review
- **Family History**: Hereditary conditions and risk factors
- **Social History**: Lifestyle factors and social determinants

#### **Clinical Findings Section**
- **Physical Exam**: Comprehensive examination findings
- **Laboratory Results**: Lab values and interpretations
- **Imaging/Diagnostics**: Radiology and other diagnostic results
- **Assessment & Plan**: Clinical assessment and treatment plan

### 🏥 AI-Powered Report Generation

- **Professional Formatting**: Medical-grade report structure
- **Comprehensive Content**: All sections integrated into cohesive report
- **Medical Coding**: Automatic ICD-10 and CPT code extraction
- **Export Options**: JSON and text format downloads
- **Timestamp Tracking**: Generation metadata for record keeping

---

## 🎯 Demo

### Main Interface
The application features a clean, professional interface designed specifically for healthcare workflows:

- **Left Panel**: Audio input methods with real-time processing
- **Right Panel**: Transcription results with editing capabilities
- **Bottom Section**: Comprehensive medical form with expandable sections

### Audio Processing Workflow

graph TD
A[Audio Input] --> B{Processing Mode}
B -->|Fast| C[Quick Transcription]
B -->|Accurate| D[High-Precision Processing]
B -->|Medical| E[Medical-Specialized Recognition]
C --> F[Auto-Fill Engine]
D --> F
E --> F
F --> G[Medical Form Population]
G --> H[AI Report Generation]
H --> I[Medical Coding Extraction]
I --> J[Export Options]

### Sample Auto-Fill Results

When processing audio containing: *"Patient presents with chest pain and shortness of breath. Currently taking lisinopril 10mg daily. No known allergies. History of hypertension."*

The system automatically populates:
- **Reason for Consultation**: "Patient presents with complaint of chest pain"
- **Current Medications**: "Currently taking lisinopril 10mg daily"
- **Allergies**: "No known allergies"
- **Past Medical History**: "History of hypertension"

---

## 📋 Documentation

### 🔧 Technical Architecture

Core Components
├── app.py # Main Streamlit application
├── model.py # AI report generation and medical coding
├── audio_processor.py # Enhanced audio processing engine
└── requirements.txt # Project dependencies

### 🎙️ Audio Processing Modes

| Mode | Speed | Accuracy | Best For |
|------|-------|----------|----------|
| **Fast** | ⚡ High | 🎯 Good | Quick notes, brief consultations |
| **Accurate** | ⚡ Medium | 🎯 Excellent | Detailed consultations, complex cases |
| **Medical** | ⚡ Medium | 🎯 Specialized | Medical terminology, clinical language |

### 📊 Supported Audio Formats

- **Audio Files**: WAV, MP3, M4A, FLAC, OGG
- **Video Files**: MP4, AVI, MOV (audio extraction)
- **Quality**: Optimized for medical consultation audio
- **Duration**: No strict limits for uploaded files

### 🔒 Data Privacy & Security

- **Local Processing**: All audio processing happens locally
- **No Cloud Storage**: Patient data never leaves your system
- **HIPAA Considerations**: Designed with healthcare privacy in mind
- **Secure Export**: Encrypted download options available

---

## 🛠️ Installation & Setup

### System Requirements

Operating System: Windows 10+, macOS 10.14+, Linux
Python: 3.8 or higher
RAM: 4GB minimum, 8GB recommended
Storage: 2GB free space
Audio: Microphone access for recording features

### Detailed Installation

1. **Environment Setup**
Create virtual environment
python -m venv medical-ai-env
Activate environment
Windows:
medical-ai-env\Scripts\activate
macOS/Linux:
source medical-ai-env/bin/activate

2. **Install Dependencies**

Install core requirements
pip install streamlit>=1.28.0
pip install pydantic>=2.0.0
pip install python-dateutil>=2.8.0
Install audio processing dependencies
pip install -r requirements.txt

3. **Verify Installation**

Test the application
streamlit run app.py

---

## 🤝 Contributing

We welcome contributions from the healthcare and developer communities! Here's how you can help:

### 🎯 Areas for Contribution

- **🎙️ Audio Processing**: Additional speech recognition models and language support
- **🏥 Medical Features**: Enhanced medical terminology and coding systems
- **🎨 UI/UX**: Interface improvements and accessibility features
- **📊 Analytics**: Usage analytics and performance monitoring
- **🔒 Security**: Enhanced privacy and security features
- **📖 Documentation**: Tutorials, guides, and API documentation

### 🚀 Development Setup

1. **Fork the repository**
git clone https://github.com/babuconsultant/medical-consultation-ai.git
cd medical-consultation-ai
git checkout -b feature/your-feature-name

Code formatting
black app.py model.py audio_processor.py

4. **Submit pull request**
- Ensure all tests pass
- Add documentation for new features
- Follow the existing code style
- Include screenshots for UI changes

### 📋 Contribution Guidelines

- **Code Quality**: Follow PEP 8 standards and include type hints
- **Testing**: Add unit tests for new functionality
- **Documentation**: Update README and inline documentation
- **Medical Accuracy**: Ensure medical features are clinically appropriate
- **Privacy**: Maintain HIPAA compliance considerations

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

### Why Apache 2.0?

- ✅ **Free for commercial use** in healthcare settings
- ✅ **Patent protection** for AI/ML implementations
- ✅ **Enterprise-friendly** for hospital and clinic adoption
- ✅ **Modification allowed** with proper attribution
- ✅ **No licensing fees** or royalties required

---

## ⚠️ Important Medical Disclaimer

**This application is designed for documentation assistance only.**

- 🏥 **Not a diagnostic tool**: Does not provide medical diagnoses or treatment recommendations
- 👨‍⚕️ **Professional oversight required**: All generated content must be reviewed by qualified healthcare professionals
- 📋 **Documentation aid**: Intended to streamline medical record creation, not replace clinical judgment
- 🔒 **Privacy responsibility**: Users must ensure compliance with local healthcare privacy regulations
- ⚖️ **Legal compliance**: Healthcare providers remain responsible for regulatory compliance

---

## 🙏 Acknowledgments

- **Streamlit Team**: For the excellent web application framework
- **Pydantic**: For robust data validation and settings management
- **Healthcare Community**: For feedback and feature suggestions
- **Open Source Contributors**: For ongoing improvements and bug fixes

---

## 📞 Support & Community

### 🆘 Getting Help

- **📖 Documentation**: Check our comprehensive docs first
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/babuconsultant/medical-consultation-ai/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/babuconsultant/medical-consultation-ai/discussions)
- **📧 Email**: babu.consultant@outlook.com

### 🌟 Community

- **⭐ Star this repo** if you find it helpful!
- **🍴 Fork** to contribute your improvements
- **📢 Share** with healthcare professionals who might benefit
- **💡 Suggest features** through GitHub Issues

---

<div align="center">

**🏥 Made with ❤️ for healthcare professionals worldwide**

*Transforming medical documentation through AI innovation*

[![GitHub stars](https://img.shields.io/github/stars/babuconsultant/medical-consultation-ai?style=social)](https://github.com/babuconsultant/medical-consultation-ai)
[![GitHub forks](https://img.shields.io/github/forks/babuconsultant/medical-consultation-ai?style=social)](https://github.com/babuconsultant/medical-consultation-ai)
[![GitHub watchers](https://img.shields.io/github/watchers/babuconsultant/medical-consultation-ai?style=social)](https://github.com/babuconsultant/medical-consultation-ai)

</div>
