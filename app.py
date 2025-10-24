# app.py
import streamlit as st
import re
import io
import os
import json
import time
from PyPDF2 import PdfReader
import docx2txt
from typing import List, Dict, Any
import google.generativeai as genai
from fpdf import FPDF
import base64

# Configure the page
st.set_page_config(
    page_title="GenAI Resume Capability Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini API
def init_gemini():
    """Initialize Gemini AI with API key"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            return True
        else:
            st.sidebar.warning("🔑 Gemini API key not found. Using enhanced rule-based analysis.")
            return False
    except Exception as e:
        st.sidebar.error(f"❌ Gemini initialization failed: {str(e)}")
        return False

# Check if Gemini is available
GEMINI_AVAILABLE = init_gemini()

def call_gemini(prompt: str, model: str = "gemini-pro") -> str:
    """Call Gemini AI API"""
    if not GEMINI_AVAILABLE:
        return "Gemini AI not available. Using enhanced rule-based analysis."
    
    try:
        model = genai.GenerativeModel(model)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI service error: {str(e)}. Using rule-based analysis."

# Sample job descriptions
SAMPLE_JOBS = [
    {
        "title": "Senior Python Developer",
        "description": """
        We are looking for a Senior Python Developer with 5+ years of experience.
        Required Skills:
        - Python programming
        - Django or Flask framework experience
        - REST API development
        - Database design with SQL
        - Cloud platforms (AWS/Azure)
        - Docker and containerization
        - CI/CD pipelines
        - Agile development methodology
        
        Preferred Qualifications:
        - Machine learning experience
        - Microservices architecture
        - Kubernetes experience
        - Test-driven development
        """
    },
    {
        "title": "Data Scientist",
        "description": """
        Data Scientist Position
        Requirements:
        - Python programming for data analysis
        - SQL and database skills
        - Machine learning algorithms
        - Data visualization with Tableau or Power BI
        - Statistical analysis
        - Data cleaning and preprocessing
        
        Nice to Have:
        - R programming language
        - Big data tools (Spark, Hadoop)
        - Deep learning experience
        - Cloud computing experience
        """
    }
    # Add more sample jobs as needed...
]

# File processing functions
def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF file using PyPDF2"""
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX file using docx2txt"""
    try:
        file_content = uploaded_file.read()
        text = docx2txt.process(io.BytesIO(file_content))
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return ""

def extract_text_from_txt(uploaded_file):
    """Extract text from TXT file"""
    try:
        file_content = uploaded_file.read()
        if isinstance(file_content, bytes):
            text = file_content.decode('utf-8')
        else:
            text = str(file_content)
        return text
    except Exception as e:
        st.error(f"Error reading TXT file: {str(e)}")
        return ""

def process_uploaded_resume(uploaded_file):
    """Process uploaded resume based on file type"""
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.type
    
    if file_type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    elif file_type == "text/plain":
        return extract_text_from_txt(uploaded_file)
    else:
        st.error(f"Unsupported file type: {file_type}")
        return ""

# Enhanced Resume Analyzer with Gen AI Capabilities
class ResumeAnalyzer:
    def __init__(self):
        # Skills with weights (Gen AI: Intelligent prioritization)
        self.skill_keywords = {
            'core_technical': {
                'weight': 1.5,
                'skills': ['python', 'java', 'javascript', 'sql', 'machine learning', 'data analysis', 'c++', 'r']
            },
            'frameworks': {
                'weight': 1.3,
                'skills': ['django', 'flask', 'react', 'angular', 'vue', 'spring', 'tensorflow', 'pytorch', 'node.js', 'express']
            },
            'cloud_devops': {
                'weight': 1.4,
                'skills': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'terraform']
            },
            'databases': {
                'weight': 1.2,
                'skills': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'dynamodb']
            },
            'tools_methodologies': {
                'weight': 1.1,
                'skills': ['git', 'agile', 'scrum', 'jira', 'linux', 'rest api', 'microservices', 'devops']
            },
            'soft_skills': {
                'weight': 0.9,
                'skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'project management', 'collaboration']
            }
        }
        
        # Experience level indicators (Gen AI: Pattern recognition)
        self.experience_indicators = {
            'senior': ['senior', 'lead', 'principal', 'architect', '5+ years', '7+ years', '10+ years', 'manager'],
            'mid': ['mid-level', '3+ years', '4+ years', 'experienced', 'professional', 'specialist'],
            'junior': ['junior', 'entry', 'graduate', '0-2 years', '1+ years', 'associate', 'intern']
        }
    
    def extract_skills(self, text: str) -> Dict[str, Any]:
        """Extract and categorize skills"""
        if not text:
            return {}
            
        text_lower = text.lower()
        found_skills = {}
        
        for category, data in self.skill_keywords.items():
            skills = data['skills']
            found = [skill for skill in skills if skill in text_lower]
            if found:
                found_skills[category] = {
                    'skills': found,
                    'weight': data['weight']
                }
        
        return found_skills
    
    def detect_experience_level(self, text: str) -> str:
        """Detect experience level from text"""
        if not text:
            return "unknown"
            
        text_lower = text.lower()
        
        for level, indicators in self.experience_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    return level
        return "unknown"
    
    def calculate_capability_score(self, resume_skills: Dict, job_skills: Dict, 
                                 resume_exp: str, job_title: str) -> Dict[str, Any]:
        """Calculate comprehensive scores"""
        
        # Calculate weighted skill match
        total_possible_score = 0
        actual_score = 0
        
        for category, job_data in job_skills.items():
            job_skill_list = job_data['skills']
            weight = job_data['weight']
            
            total_possible_score += len(job_skill_list) * weight
            
            resume_category_skills = resume_skills.get(category, {'skills': []})
            resume_skill_list = resume_category_skills['skills']
            
            for skill in job_skill_list:
                if skill in resume_skill_list:
                    actual_score += weight
        
        skill_match_percentage = (actual_score / total_possible_score * 100) if total_possible_score > 0 else 0
        
        # Calculate experience compatibility
        job_level = self.detect_job_level(job_title)
        exp_compatibility = self.calculate_experience_compatibility(resume_exp, job_level)
        
        # Overall capability score
        overall_capability = (skill_match_percentage * 0.7) + (exp_compatibility * 0.3)
        
        return {
            'overall_capability': round(overall_capability, 1),
            'skill_match': round(skill_match_percentage, 1),
            'experience_compatibility': round(exp_compatibility, 1),
            'skill_breakdown': {
                'total_possible': total_possible_score,
                'actual_achieved': actual_score
            }
        }
    
    def detect_job_level(self, job_title: str) -> str:
        """Detect job level from title"""
        if not job_title:
            return "mid"
            
        job_lower = job_title.lower()
        
        if any(word in job_lower for word in ['senior', 'lead', 'principal', 'architect', 'staff', 'manager']):
            return 'senior'
        elif any(word in job_lower for word in ['junior', 'entry', 'associate', 'graduate', 'intern']):
            return 'junior'
        else:
            return 'mid'
    
    def calculate_experience_compatibility(self, resume_exp: str, job_level: str) -> float:
        """Experience compatibility matrix"""
        compatibility_matrix = {
            'senior': {'senior': 100, 'mid': 70, 'junior': 40, 'unknown': 50},
            'mid': {'senior': 60, 'mid': 100, 'junior': 80, 'unknown': 70},
            'junior': {'senior': 30, 'mid': 60, 'junior': 100, 'unknown': 80},
            'unknown': {'senior': 40, 'mid': 60, 'junior': 80, 'unknown': 50}
        }
        
        return compatibility_matrix.get(job_level, {}).get(resume_exp, 50)
    
    def analyze_resume_job_match(self, resume_text: str, job_description: str, job_title: str) -> Dict[str, Any]:
        """Main analysis function"""
        if not resume_text or not job_description:
            return self.get_empty_analysis()
            
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        resume_experience = self.detect_experience_level(resume_text)
        
        # Calculate capability scores
        capability_scores = self.calculate_capability_score(resume_skills, job_skills, resume_experience, job_title)
        
        # Find matching and missing skills
        matching_skills = {}
        missing_skills = {}
        
        for category, job_data in job_skills.items():
            job_skill_list = job_data['skills']
            resume_category_skills = resume_skills.get(category, {'skills': []})
            resume_skill_list = resume_category_skills['skills']
            
            matching = [skill for skill in job_skill_list if skill in resume_skill_list]
            missing = [skill for skill in job_skill_list if skill not in resume_skill_list]
            
            if matching:
                matching_skills[category] = matching
            if missing:
                missing_skills[category] = missing
        
        return {
            **capability_scores,
            "resume_experience_level": resume_experience,
            "job_level": self.detect_job_level(job_title),
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "resume_skills": resume_skills,
            "job_skills": job_skills
        }
    
    def get_empty_analysis(self):
        """Return empty analysis structure"""
        return {
            'overall_capability': 0,
            'skill_match': 0,
            'experience_compatibility': 0,
            'resume_experience_level': 'unknown',
            'job_level': 'unknown',
            'matching_skills': {},
            'missing_skills': {},
            'resume_skills': {},
            'job_skills': {},
            'skill_breakdown': {'total_possible': 0, 'actual_achieved': 0}
        }
    
    def generate_ai_explanation(self, analysis: Dict) -> str:
        """Create natural language explanations using Gemini"""
        if GEMINI_AVAILABLE:
            prompt = f"""
            As a career coach, provide a brief but insightful analysis of this job match:
            
            Overall Capability: {analysis['overall_capability']}%
            Skill Match: {analysis['skill_match']}%
            Experience Compatibility: {analysis['experience_compatibility']}%
            Candidate Level: {analysis['resume_experience_level']}
            Job Level: {analysis['job_level']}
            
            Provide a 2-3 sentence professional assessment focusing on strengths and fit.
            """
            return call_gemini(prompt)
        else:
            # Fallback to rule-based explanation
            score = analysis['overall_capability']
            if score >= 85:
                return "🧠 **AI Insight**: Excellent match! Strong technical alignment and ideal experience fit."
            elif score >= 70:
                return "📊 **AI Assessment**: Strong candidate with good technical alignment."
            elif score >= 50:
                return "💡 **AI Analysis**: Moderate fit with room for skill development."
            else:
                return "🎯 **AI Recommendation**: Foundational match - consider skill development."
    
    def generate_cover_letter(self, resume_text: str, job_description: str, job_title: str, analysis: Dict) -> str:
        """Generate cover letter using Gemini AI"""
        if not GEMINI_AVAILABLE:
            return "Gemini AI not available for cover letter generation."
        
        prompt = f"""
        Generate a professional cover letter for this job application:
        
        JOB TITLE: {job_title}
        JOB DESCRIPTION: {job_description[:1000]}
        RESUME EXCERPT: {resume_text[:1500]}
        MATCH ANALYSIS: Overall capability: {analysis['overall_capability']}%
        
        Requirements:
        - Professional tone
        - 250-400 words
        - Highlight relevant skills and experience
        - Address potential gaps positively
        - Include opening and closing sections
        - Focus on value proposition
        
        Generate only the cover letter content without any additional explanations.
        """
        
        return call_gemini(prompt)
    
    def get_personalized_recommendation(self, analysis: Dict) -> str:
        """Create tailored advice using Gemini"""
        if GEMINI_AVAILABLE:
            prompt = f"""
            Based on this job match analysis, provide specific career advice:
            
            Capability Score: {analysis['overall_capability']}%
            Skill Match: {analysis['skill_match']}%
            Experience Fit: {analysis['experience_compatibility']}%
            
            Provide 2-3 specific, actionable recommendations for this candidate.
            """
            return call_gemini(prompt)
        else:
            # Fallback recommendations
            overall = analysis['overall_capability']
            if overall >= 80:
                return "**Next Steps**: You're a strong candidate! Focus on interview preparation."
            elif overall >= 60:
                return "**Next Steps**: You're competitive! Develop 1-2 key missing skills."
            else:
                return "**Next Steps**: Build foundation in missing technical areas."

# PDF Report Generator
class PDFReport:
    def __init__(self):
        self.pdf = FPDF()
    
    def generate_report(self, analysis: Dict, resume_file_name: str, job_title: str, cover_letter: str = "") -> str:
        """Generate PDF report"""
        self.pdf.add_page()
        
        # Title
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'AI Resume Analysis Report', 0, 1, 'C')
        self.pdf.ln(10)
        
        # Basic info
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f'Resume: {resume_file_name}', 0, 1)
        self.pdf.cell(0, 10, f'Target Position: {job_title}', 0, 1)
        self.pdf.cell(0, 10, f'Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
        self.pdf.ln(10)
        
        # Scores
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, 'Assessment Scores', 0, 1)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f'Overall Capability: {analysis["overall_capability"]}%', 0, 1)
        self.pdf.cell(0, 10, f'Skill Match: {analysis["skill_match"]}%', 0, 1)
        self.pdf.cell(0, 10, f'Experience Compatibility: {analysis["experience_compatibility"]}%', 0, 1)
        self.pdf.ln(10)
        
        # Cover letter
        if cover_letter and cover_letter != "Gemini AI not available for cover letter generation.":
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 14)
            self.pdf.cell(0, 10, 'AI-Generated Cover Letter', 0, 1)
            self.pdf.set_font('Arial', '', 11)
            self.pdf.multi_cell(0, 8, cover_letter)
        
        # Save PDF
        filename = f"resume_analysis_{int(time.time())}.pdf"
        self.pdf.output(filename)
        return filename

# Initialize analyzer and PDF generator
analyzer = ResumeAnalyzer()
pdf_generator = PDFReport()

# Main Streamlit App
def main():
    # Header
    st.title("🧠 GenAI Resume Capability Analyzer")
    st.markdown("### *Intelligent Career Assessment Using Generative AI*")
    
    # Gemini status
    if GEMINI_AVAILABLE:
        st.sidebar.success("✅ Gemini AI Connected")
    else:
        st.sidebar.warning("🔑 Add GEMINI_API_KEY to enable AI features")
    
    st.markdown("---")
    
    # Sidebar for input
    st.sidebar.header("📤 Upload Your Resume")
    
    # File uploader
    uploaded_file = st.sidebar.file_uploader(
        "Choose your resume file",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    resume_text = ""
    
    if uploaded_file is not None:
        # Process the uploaded file
        with st.spinner("🔍 Processing your resume..."):
            resume_text = process_uploaded_resume(uploaded_file)
        
        if resume_text:
            st.sidebar.success("✅ Resume processed successfully!")
    
    # Job description input
    st.sidebar.header("💼 Job Description")
    
    job_option = st.sidebar.radio("Choose Job Input:", ["Use Sample Job", "Paste Custom Description"])
    
    job_description = ""
    selected_job = ""
    
    if job_option == "Use Sample Job":
        selected_job = st.sidebar.selectbox("Select Sample Job:", [j["title"] for j in SAMPLE_JOBS])
        job_description = next(j["description"] for j in SAMPLE_JOBS if j["title"] == selected_job)
        job_title = selected_job
    else:
        job_description = st.sidebar.text_area("Paste Job Description:", height=150)
        job_title = st.sidebar.text_input("Job Title:", placeholder="e.g., Senior Python Developer")
    
    # Main content area
    if uploaded_file is None:
        # Welcome section
        st.info("👋 Welcome to the GenAI Resume Analyzer!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 How It Works:
            1. **Upload Your Resume** - AI processes and analyzes your content
            2. **Provide Job Details** - Use samples or paste a specific role
            3. **Get AI Assessment** - Receive comprehensive capability analysis
            4. **Download Report** - Get PDF with insights and cover letter
            """)
            
        with col2:
            st.markdown("""
            ### 🧠 AI Features:
            - **Skill Matching** - Technical competencies alignment
            - **Experience Analysis** - Career level compatibility  
            - **AI Insights** - Gemini-powered recommendations
            - **Cover Letter Generation** - Personalized job applications
            - **PDF Reports** - Professional analysis export
            """)
        
    elif resume_text and job_description and (job_title or selected_job):
        # Display analysis interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Your Resume Analysis")
            st.info(f"Uploaded: {uploaded_file.name}")
            
        with col2:
            st.subheader("💼 Target Position")
            display_job_title = selected_job if job_option == "Use Sample Job" else job_title
            st.info(f"Position: {display_job_title}")
        
        # Analyze button
        st.markdown("---")
        if st.button("🧠 **Generate AI Capability Analysis**", use_container_width=True, type="primary"):
            with st.spinner("🔄 AI is analyzing your capabilities..."):
                # Perform comprehensive analysis
                job_title_for_analysis = selected_job if job_option == "Use Sample Job" else job_title
                analysis = analyzer.analyze_resume_job_match(resume_text, job_description, job_title_for_analysis)
                ai_explanation = analyzer.generate_ai_explanation(analysis)
                recommendation = analyzer.get_personalized_recommendation(analysis)
                
                # Generate cover letter
                cover_letter = ""
                if GEMINI_AVAILABLE:
                    with st.spinner("📝 Generating cover letter..."):
                        cover_letter = analyzer.generate_cover_letter(resume_text, job_description, job_title_for_analysis, analysis)
                
                # Display results
                st.subheader("📊 AI Capability Assessment Results")
                
                # Scores
                col3, col4, col5 = st.columns(3)
                with col3:
                    st.metric("Overall Capability", f"{analysis['overall_capability']}%")
                with col4:
                    st.metric("Skills Match", f"{analysis['skill_match']}%")
                with col5:
                    st.metric("Experience Fit", f"{analysis['experience_compatibility']}%")
                
                # AI Explanation
                st.info(ai_explanation)
                
                # Skills analysis
                col6, col7 = st.columns(2)
                with col6:
                    st.subheader("✅ Matching Skills")
                    if analysis['matching_skills']:
                        for category, skills in analysis['matching_skills'].items():
                            with st.expander(f"{category.replace('_', ' ').title()} ({len(skills)} skills)"):
                                for skill in skills:
                                    st.success(f"• {skill}")
                    else:
                        st.warning("No matching skills detected")
                
                with col7:
                    st.subheader("📚 Skills to Develop")
                    if analysis['missing_skills']:
                        for category, skills in analysis['missing_skills'].items():
                            with st.expander(f"{category.replace('_', ' ').title()} ({len(skills)} to learn)"):
                                for skill in skills:
                                    st.error(f"• {skill}")
                    else:
                        st.success("Great! No critical skills missing")
                
                # Recommendations
                st.subheader("🎯 AI Recommendations")
                st.write(recommendation)
                
                # Cover Letter
                if cover_letter and cover_letter != "Gemini AI not available for cover letter generation.":
                    st.subheader("✍️ AI-Generated Cover Letter")
                    st.text_area("Cover Letter Preview", cover_letter, height=300)
                
                # PDF Report Download
                st.subheader("📄 Download Report")
                if st.button("📥 Generate PDF Report", type="secondary"):
                    with st.spinner("Generating PDF report..."):
                        pdf_filename = pdf_generator.generate_report(
                            analysis, uploaded_file.name, job_title_for_analysis, cover_letter
                        )
                        
                        with open(pdf_filename, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                        
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_data,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
    
    elif uploaded_file and not resume_text:
        st.error("❌ Could not extract text from the uploaded file.")
        st.info("Try uploading a DOCX or text-based PDF for best results.")

if __name__ == "__main__":
    main()
