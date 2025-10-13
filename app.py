# app.py
import streamlit as st
import re
import io
from PyPDF2 import PdfReader
import docx2txt
from typing import List, Dict, Any

# Configure the page
st.set_page_config(
    page_title="GenAI Resume Capability Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    },
    {
        "title": "Full Stack Developer",
        "description": """
        Full Stack Developer Position
        Required Skills:
        - JavaScript (React, Angular, or Vue)
        - Node.js or Python backend
        - HTML5, CSS3, responsive design
        - RESTful API development
        - Database management (SQL/NoSQL)
        - Git version control
        - Agile methodology
        """
    },
    {
        "title": "Machine Learning Engineer",
        "description": """
        Machine Learning Engineer
        Requirements:
        - Strong Python programming skills
        - Machine learning frameworks (TensorFlow, PyTorch)
        - Data preprocessing and feature engineering
        - Model deployment and MLOps
        - SQL and database skills
        - Statistical analysis
        
        Preferred:
        - Deep learning experience
        - Cloud platforms (AWS SageMaker, GCP AI)
        - Docker and Kubernetes
        - Big data technologies
        """
    },
    {
        "title": "DevOps Engineer",
        "description": """
        DevOps Engineer
        Responsibilities:
        - Build and maintain CI/CD pipelines
        - Automate infrastructure using IaC (Terraform, Ansible)
        - Manage containerization (Docker, Kubernetes)
        - Monitor system performance and uptime
        - Collaborate with developers for continuous delivery
        
        Skills:
        - Linux/Unix systems
        - AWS, Azure, or GCP
        - Scripting with Bash or Python
        - Git, Jenkins, GitLab CI
        """
    },
    {
        "title": "Cloud Architect",
        "description": """
        Cloud Architect
        Responsibilities:
        - Design and implement cloud solutions (AWS/Azure/GCP)
        - Optimize infrastructure for scalability and cost
        - Manage cloud security and compliance
        - Lead migration to cloud environments
        
        Skills:
        - Cloud architecture frameworks
        - Virtualization and networking
        - IaC tools like Terraform or CloudFormation
        - DevOps collaboration
        """
    },
    {
        "title": "Cybersecurity Engineer",
        "description": """
        Cybersecurity Engineer
        Responsibilities:
        - Secure systems and networks from cyber threats
        - Implement firewalls, IDS/IPS, and security tools
        - Perform vulnerability assessments and penetration tests
        - Incident response and mitigation
        
        Skills:
        - Knowledge of security protocols
        - SIEM tools (Splunk, QRadar)
        - Cloud and network security
        - Certifications: CEH, CISSP, or Security+
        """
    },
    {
        "title": "Data Engineer",
        "description": """
        Data Engineer
        Responsibilities:
        - Build and maintain ETL pipelines
        - Design and optimize data warehouses
        - Integrate large datasets from multiple sources
        
        Skills:
        - SQL, Python
        - Spark, Kafka, or Airflow
        - Cloud data platforms (AWS Redshift, BigQuery, Snowflake)
        - Data modeling and schema design
        """
    },
    {
        "title": "AI Engineer",
        "description": """
        AI Engineer
        Responsibilities:
        - Develop AI-based solutions using NLP or computer vision
        - Train and optimize deep learning models
        - Collaborate with data scientists for deployment
        
        Skills:
        - Python, TensorFlow, PyTorch
        - ML lifecycle management (MLflow)
        - API integration and cloud deployment
        - Understanding of statistics and data science
        """
    },
    {
        "title": "Frontend Developer",
        "description": """
        Frontend Developer
        Responsibilities:
        - Build responsive web interfaces
        - Collaborate with designers and backend developers
        - Ensure high performance and accessibility
        
        Skills:
        - React, Angular, or Vue.js
        - HTML5, CSS3, JavaScript (ES6+)
        - REST APIs integration
        - Git version control
        """
    },
    {
        "title": "Backend Developer",
        "description": """
        Backend Developer
        Responsibilities:
        - Design scalable backend systems
        - Implement APIs and microservices
        - Manage data storage and retrieval
        
        Skills:
        - Node.js, Python, Java, or Go
        - SQL/NoSQL databases
        - REST and GraphQL APIs
        - Docker, Kubernetes, and CI/CD
        """
    },
    {
        "title": "Site Reliability Engineer",
        "description": """
        Site Reliability Engineer
        Responsibilities:
        - Maintain service uptime and reliability
        - Build monitoring and alerting systems
        - Automate deployments and scaling
        
        Skills:
        - Linux administration
        - Scripting (Python, Bash)
        - Cloud infrastructure (AWS/GCP)
        - Prometheus, Grafana, or Datadog
        """
    },
    {
        "title": "IT Project Manager",
        "description": """
        IT Project Manager
        Responsibilities:
        - Lead software and infrastructure projects
        - Manage resources, timelines, and budgets
        - Communicate with stakeholders and teams
        
        Skills:
        - Agile and Scrum methodologies
        - Tools: Jira, Trello, MS Project
        - Technical background in IT or software
        - PMP or Agile certification preferred
        """
    },
    {
        "title": "Business Analyst (IT)",
        "description": """
        Business Analyst (IT)
        Responsibilities:
        - Gather and analyze business requirements
        - Collaborate with developers and stakeholders
        - Document workflows and functional specifications
        
        Skills:
        - SQL and data querying
        - Analytical and problem-solving skills
        - Agile environment experience
        - Excellent communication skills
        """
    },
    {
        "title": "Network Engineer",
        "description": """
        Network Engineer
        Responsibilities:
        - Design and implement network infrastructure
        - Troubleshoot network issues and optimize performance
        - Maintain routers, switches, and firewalls
        
        Skills:
        - TCP/IP, VPN, DNS, and VLAN configuration
        - Cisco, Juniper, or Fortinet devices
        - Network security and monitoring tools
        - CCNA or CCNP certification a plus
        """
    },
    {
        "title": "Database Administrator (DBA)",
        "description": """
        Database Administrator
        Responsibilities:
        - Maintain and secure databases
        - Optimize queries and manage backups
        - Ensure data integrity and performance
        
        Skills:
        - SQL Server, MySQL, PostgreSQL, or Oracle
        - Database tuning and indexing
        - Replication and clustering
        - Scripting for automation (Python, Bash)
        """
    },
    {
        "title": "Systems Administrator",
        "description": """
        Systems Administrator
        Responsibilities:
        - Maintain and support IT systems and servers
        - Ensure uptime and system security
        - Manage backups and disaster recovery
        
        Skills:
        - Windows/Linux server management
        - Active Directory and network configuration
        - Virtualization (VMware, Hyper-V)
        - Monitoring tools (Nagios, Zabbix)
        """
    },
    {
        "title": "Technical Support Engineer",
        "description": """
        Technical Support Engineer
        Responsibilities:
        - Provide IT support to end users
        - Troubleshoot hardware/software issues
        - Document solutions and maintain logs
        
        Skills:
        - Windows/Mac/Linux troubleshooting
        - Networking basics
        - Customer communication skills
        - Ticketing systems (ServiceNow, Jira)
        """
    },
    {
        "title": "Solutions Architect",
        "description": """
        Solutions Architect
        Responsibilities:
        - Design end-to-end technical solutions for clients
        - Collaborate with engineers and product managers
        - Ensure scalability, performance, and security
        
        Skills:
        - System design and integration
        - Cloud platforms (AWS, Azure, GCP)
        - Strong programming and architecture skills
        - Excellent communication and documentation
        """
    },
    {
        "title": "Data Analyst",
        "description": """
        Data Analyst
        Responsibilities:
        - Analyze datasets to extract insights
        - Create dashboards and reports
        - Support business decisions with data-driven insights
        
        Skills:
        - SQL, Excel, Python (pandas)
        - Visualization tools (Tableau, Power BI)
        - Statistical analysis
        - Data cleaning and transformation
        """
    }
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

# Enhanced Resume Analyzer with Improved Content Generation
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
        """Gen AI: Natural Language Understanding - Extract and categorize skills"""
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
        """Gen AI: Pattern Recognition - Detect experience level from text"""
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
        """Gen AI: Intelligent Decision Making - Calculate comprehensive scores"""
        
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
        
        # Overall capability score (Gen AI: Multi-factor analysis)
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
        """Gen AI: Context Understanding - Detect job level from title"""
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
        """Gen AI: Relationship Mapping - Experience compatibility matrix"""
        compatibility_matrix = {
            'senior': {'senior': 100, 'mid': 70, 'junior': 40, 'unknown': 50},
            'mid': {'senior': 60, 'mid': 100, 'junior': 80, 'unknown': 70},
            'junior': {'senior': 30, 'mid': 60, 'junior': 100, 'unknown': 80},
            'unknown': {'senior': 40, 'mid': 60, 'junior': 80, 'unknown': 50}
        }
        
        return compatibility_matrix.get(job_level, {}).get(resume_exp, 50)
    
    def analyze_resume_job_match(self, resume_text: str, job_description: str, job_title: str) -> Dict[str, Any]:
        """Gen AI: Comprehensive Analysis - Main analysis function"""
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
        """Enhanced Gen AI: Dynamic Content Generation with Multiple Variations"""
        score = analysis['overall_capability']
        skill_match = analysis['skill_match']
        exp_match = analysis['experience_compatibility']
        missing_count = sum(len(skills) for skills in analysis['missing_skills'].values())
        matching_count = sum(len(skills) for skills in analysis['matching_skills'].values())

        # Multiple variations for each score range
        explanations = {
            'excellent': [
                f"🧠 **AI Insight**: Outstanding alignment! Your {score}% capability demonstrates exceptional compatibility with this role. "
                f"With {skill_match}% technical proficiency and {exp_match}% experience fit, you're exceptionally well-positioned.",
                
                f"🚀 **AI Assessment**: Elite candidate detected! {score}% overall capability reflects comprehensive qualification alignment. "
                f"Your {matching_count} matching skills create a strong foundation for immediate impact.",
                
                f"💎 **AI Analysis**: Exceptional match at {score}%! The synergy between your {skill_match}% technical alignment "
                f"and {exp_match}% experience compatibility positions you as a top-tier candidate.",
                
                f"⭐ **AI Evaluation**: Premier fit with {score}% capability score. Your profile demonstrates outstanding readiness "
                f"with robust skill coverage and ideal experience progression."
            ],
            'strong': [
                f"📊 **AI Insight**: Strong candidate profile with {score}% overall capability. "
                f"Your {skill_match}% skill alignment combined with {exp_match}% experience fit creates a competitive advantage.",
                
                f"👍 **AI Assessment**: Well-qualified with {score}% match. You possess {matching_count} relevant skills "
                f"and demonstrate good experience alignment for this position.",
                
                f"💪 **AI Analysis**: Solid foundation at {score}% capability. With strategic focus on {missing_count} key areas, "
                f"you can quickly advance to elite candidate status.",
                
                f"📈 **AI Evaluation**: Promising {score}% alignment. Your technical competencies at {skill_match}% match "
                f"provide a strong platform for role-specific success."
            ],
            'moderate': [
                f"💡 **AI Insight**: Moderate fit at {score}% capability. While you have {matching_count} relevant skills, "
                f"focusing on {missing_count} missing competencies could significantly boost your readiness.",
                
                f"🔄 **AI Assessment**: Developing candidate with {score}% alignment. Your {skill_match}% technical match "
                f"and {exp_match}% experience fit indicate a solid foundation for growth.",
                
                f"🎯 **AI Analysis**: Foundational match at {score}%. You have core qualifications with room for strategic "
                f"development in specific technical domains.",
                
                f"🔍 **AI Evaluation**: {score}% capability reflects a work-in-progress profile. Targeted skill development "
                f"can transform your candidacy for this role."
            ],
            'developing': [
                f"🌱 **AI Insight**: Emerging candidate with {score}% capability. This represents an opportunity for focused "
                f"development in both technical skills ({skill_match}% current match) and experience building.",
                
                f"📚 **AI Assessment**: Development-focused profile at {score}% alignment. Consider this role as a growth "
                f"target while building your {missing_count} missing competencies.",
                
                f"🎓 **AI Analysis**: Foundational readiness at {score}%. Your current profile suggests starting with "
                f"entry-level positions to build the required {matching_count} core skills.",
                
                f"🛠️ **AI Evaluation**: Building phase with {score}% capability. This assessment highlights a clear roadmap "
                f"for developing the necessary qualifications over time."
            ]
        }

        # Select category and random variation
        if score >= 85:
            category = 'excellent'
        elif score >= 70:
            category = 'strong'
        elif score >= 50:
            category = 'moderate'
        else:
            category = 'developing'

        # Use hash for deterministic but varied selection
        variation_index = hash(f"{score}{skill_match}") % len(explanations[category])
        return explanations[category][variation_index]

    def get_capability_assessment(self, analysis: Dict) -> Dict[str, Any]:
        """Enhanced Gen AI: Multi-dimensional Assessment with Rich Variations"""
        overall = analysis['overall_capability']
        skill_match = analysis['skill_match']
        exp_compat = analysis['experience_compatibility']
        missing_skills_count = sum(len(skills) for skills in analysis['missing_skills'].values())

        # Multiple assessment variations
        assessments = {
            'excellent': [
                {
                    'level': "Elite Candidate",
                    'description': "Your profile demonstrates exceptional qualifications with comprehensive skill coverage and ideal experience alignment for this role.",
                    'color': "green",
                    'icon': "🏆"
                },
                {
                    'level': "Top-Tier Ready", 
                    'description': "You possess outstanding capabilities with strong technical proficiency and excellent experience fit for immediate impact.",
                    'color': "green",
                    'icon': "⭐"
                },
                {
                    'level': "Premium Match",
                    'description': "Exceptional alignment across all dimensions positions you as a highly desirable candidate for this position.",
                    'color': "green",
                    'icon': "💎"
                }
            ],
            'strong': [
                {
                    'level': "Highly Competitive",
                    'description': "You demonstrate strong qualifications with good technical alignment and solid experience foundation for this role.",
                    'color': "blue",
                    'icon': "🚀"
                },
                {
                    'level': "Well-Positioned",
                    'description': "Your profile shows substantial relevant capabilities with promising alignment to role requirements.",
                    'color': "blue", 
                    'icon': "👍"
                },
                {
                    'level': "Qualified Candidate",
                    'description': "You possess the core competencies needed with good overall fit and clear potential for success.",
                    'color': "blue",
                    'icon': "💪"
                }
            ],
            'moderate': [
                {
                    'level': "Developing Professional",
                    'description': "You have relevant foundational skills with clear pathways for development to reach full role compatibility.",
                    'color': "orange",
                    'icon': "📈"
                },
                {
                    'level': "Growth Candidate", 
                    'description': "Your current qualifications provide a solid base with identified areas for strategic skill enhancement.",
                    'color': "orange",
                    'icon': "🎯"
                },
                {
                    'level': "Emerging Potential",
                    'description': "You demonstrate promising capabilities with specific development opportunities to maximize your fit.",
                    'color': "orange",
                    'icon': "🔍"
                }
            ],
            'developing': [
                {
                    'level': "Foundation Builder",
                    'description': "This assessment highlights a clear development path to build the necessary qualifications for this career direction.",
                    'color': "red",
                    'icon': "🌱"
                },
                {
                    'level': "Skill Developer",
                    'description': "Your profile indicates a building phase with focused development needed in core competency areas.",
                    'color': "red",
                    'icon': "🛠️"
                },
                {
                    'level': "Career Explorer", 
                    'description': "This role represents a growth target while you develop the foundational skills and experience required.",
                    'color': "red",
                    'icon': "🎓"
                }
            ]
        }

        # Select category and random assessment
        if overall >= 85:
            category = 'excellent'
        elif overall >= 70:
            category = 'strong'
        elif overall >= 50:
            category = 'moderate'
        else:
            category = 'developing'

        assessment_index = hash(f"{overall}{exp_compat}") % len(assessments[category])
        base_assessment = assessments[category][assessment_index]

        # Enhanced strengths and weaknesses with more variety
        strengths = self._generate_strengths_analysis(analysis)
        weaknesses = self._generate_weaknesses_analysis(analysis)

        return {
            **base_assessment,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendation': self.get_personalized_recommendation(analysis)
        }

    def _generate_strengths_analysis(self, analysis: Dict) -> List[str]:
        """Generate varied strength analysis"""
        strengths = []
        skill_match = analysis['skill_match']
        exp_compat = analysis['experience_compatibility']
        matching_skills = analysis['matching_skills']
        
        strength_templates = {
            'high_skill': [
                "Exceptional technical proficiency across multiple domains",
                "Strong competency alignment with role requirements",
                "Comprehensive skill coverage in key technical areas",
                "Robust technical foundation for immediate contribution"
            ],
            'high_exp': [
                "Ideal experience level for position requirements",
                "Excellent career progression alignment",
                "Strong professional background match",
                "Relevant experience depth for role success"
            ],
            'broad_skills': [
                "Diverse skill set across multiple categories",
                "Broad technical competency coverage",
                "Versatile capabilities across different domains",
                "Comprehensive skill portfolio"
            ],
            'perfect_level': [
                "Perfect experience level synchronization",
                "Ideal career stage alignment",
                "Optimal professional level match",
                "Excellent seniority fit"
            ]
        }

        if skill_match >= 80:
            strengths.append(self._select_variation(strength_templates['high_skill'], f"skill{skill_match}"))
        if exp_compat >= 80:
            strengths.append(self._select_variation(strength_templates['high_exp'], f"exp{exp_compat}"))
        if len(matching_skills) >= 4:
            strengths.append(self._select_variation(strength_templates['broad_skills'], f"broad{len(matching_skills)}"))
        if analysis['resume_experience_level'] == analysis['job_level']:
            strengths.append(self._select_variation(strength_templates['perfect_level'], "levelmatch"))

        return strengths if strengths else ["Focus on building your core competency areas"]

    def _generate_weaknesses_analysis(self, analysis: Dict) -> List[str]:
        """Generate varied weakness analysis"""
        weaknesses = []
        skill_match = analysis['skill_match']
        exp_compat = analysis['experience_compatibility']
        missing_skills = analysis['missing_skills']
        
        weakness_templates = {
            'skill_gap': [
                "Technical skills gap requiring development",
                "Need for enhanced technical competency",
                "Skill development opportunities identified",
                "Technical proficiency enhancement needed"
            ],
            'exp_gap': [
                "Experience level misalignment",
                "Career stage development opportunity",
                "Professional experience gap",
                "Career progression adjustment needed"
            ],
            'multiple_gaps': [
                "Multiple competency areas for development",
                "Several skill enhancement opportunities",
                "Various technical domains needing attention",
                "Multiple development focus areas"
            ]
        }

        if skill_match < 60:
            weaknesses.append(self._select_variation(weakness_templates['skill_gap'], f"skillgap{skill_match}"))
        if exp_compat < 60:
            weaknesses.append(self._select_variation(weakness_templates['exp_gap'], f"expgap{exp_compat}"))
        if sum(len(skills) for skills in missing_skills.values()) > 6:
            weaknesses.append(self._select_variation(weakness_templates['multiple_gaps'], "multigap"))

        return weaknesses if weaknesses else ["Well-balanced profile with minimal development needs"]

    def _select_variation(self, variations: List[str], seed: str) -> str:
        """Select a variation based on seed for consistency"""
        index = hash(seed) % len(variations)
        return variations[index]

    def get_personalized_recommendation(self, analysis: Dict) -> str:
        """Enhanced Gen AI: Rich, Varied Recommendations"""
        overall = analysis['overall_capability']
        skill_match = analysis['skill_match']
        missing_skills = analysis['missing_skills']
        
        recommendations = {
            'excellent': [
                "**Strategic Next Steps**: Leverage your elite qualifications in negotiations and target senior-level responsibilities. "
                "Focus on demonstrating leadership potential and architectural thinking.",
                
                "**Career Advancement**: Capitalize on your strong alignment by positioning for leadership opportunities. "
                "Highlight your comprehensive skill set in strategic discussions.",
                
                "**Professional Growth**: With your exceptional readiness, focus on mentorship roles and complex project leadership. "
                "Consider specialization areas for maximum impact."
            ],
            'strong': [
                "**Development Focus**: Enhance your competitive edge by mastering 1-2 advanced skills. "
                "Position yourself for rapid advancement through demonstrated expertise.",
                
                "**Career Strategy**: Build on your solid foundation with targeted certifications or advanced projects. "
                "Showcase your growing capabilities through measurable achievements.",
                
                "**Skill Enhancement**: Refine your existing strengths while addressing minor gaps. "
                "Consider cross-functional projects to demonstrate versatility."
            ],
            'moderate': [
                "**Learning Path**: Develop a structured plan for acquiring core missing competencies. "
                "Focus on practical projects that demonstrate applied learning.",
                
                "**Career Development**: Target roles that bridge your current capabilities with future aspirations. "
                "Build a portfolio showcasing your growing expertise.",
                
                "**Skill Building**: Prioritize foundational competencies through courses and hands-on practice. "
                "Seek opportunities that allow gradual responsibility increase."
            ],
            'developing': [
                "**Foundation Strategy**: Begin with fundamental courses and entry-level positions to build core competencies. "
                "Focus on establishing a strong technical foundation.",
                
                "**Career Planning**: Develop a step-by-step progression plan from current to target capabilities. "
                "Celebrate incremental learning milestones.",
                
                "**Learning Journey**: Start with essential skills through structured learning paths. "
                "Build practical experience through personal projects and internships."
            ]
        }

        if overall >= 85:
            category = 'excellent'
        elif overall >= 70:
            category = 'strong'
        elif overall >= 50:
            category = 'moderate'
        else:
            category = 'developing'

        rec_index = hash(f"rec{overall}{skill_match}") % len(recommendations[category])
        return recommendations[category][rec_index]

    def get_improvement_suggestions(self, analysis: Dict) -> List[str]:
        """Enhanced Gen AI: Dynamic, Context-Aware Suggestions"""
        suggestions = []
        capability = analysis['overall_capability']
        missing_skills = analysis['missing_skills']
        skill_match = analysis['skill_match']

        # Capability-based suggestions with variations
        capability_suggestions = {
            'high': [
                "🎯 **Elite Preparation**: Refine your interview storytelling with specific achievement examples",
                "🚀 **Advanced Positioning**: Showcase leadership potential through complex project discussions", 
                "💎 **Strategic Impact**: Demonstrate architectural thinking in technical conversations",
                "⭐ **Expert Presence**: Develop case studies highlighting your most significant contributions"
            ],
            'medium': [
                "📈 **Competitive Enhancement**: Target 2-3 high-value skills for immediate impact improvement",
                "💪 **Strength Amplification**: Build deeper expertise in your strongest technical areas",
                "🔧 **Gap Closure**: Focus on practical application of missing competencies through projects",
                "🎯 **Strategic Development**: Align learning efforts with emerging industry trends"
            ],
            'low': [
                "🔄 **Foundation Building**: Establish core competencies through structured learning paths",
                "🌱 **Progressive Development**: Focus on incremental skill acquisition and application",
                "📚 **Fundamental Mastery**: Prioritize essential skills before advancing to complex topics",
                "🛠️ **Practical Learning**: Combine theoretical knowledge with hands-on project experience"
            ]
        }

        # Select capability level
        if capability >= 75:
            cap_level = 'high'
        elif capability >= 50:
            cap_level = 'medium'
        else:
            cap_level = 'low'

        # Add 2 capability-based suggestions
        cap_suggestions = capability_suggestions[cap_level]
        suggestions.append(self._select_variation(cap_suggestions, f"cap{capability}"))
        suggestions.append(self._select_variation(cap_suggestions, f"cap2{capability}"))

        # Skill-specific suggestions with better categorization
        skill_suggestions = {
            'core_technical': [
                "🔧 **Core Technical**: Develop proficiency in {skills} through coding practice and projects",
                "💻 **Programming Skills**: Master {skills} with hands-on coding challenges and real-world applications",
                "⚡ **Technical Foundation**: Build strong {skills} capabilities through systematic learning"
            ],
            'cloud_devops': [
                "☁️ **Cloud & DevOps**: Learn {skills} through cloud certification paths and infrastructure projects",
                "🔄 **Infrastructure Skills**: Develop {skills} expertise with containerization and automation practice",
                "⚙️ **Platform Mastery**: Acquire {skills} competencies through cloud platform experimentation"
            ],
            'frameworks': [
                "🛠️ **Framework Proficiency**: Gain {skills} experience through framework-specific projects",
                "🔨 **Tool Mastery**: Develop {skills} skills with practical implementation exercises",
                "🎯 **Technology Stack**: Build {skills} expertise through stack-focused development"
            ]
        }

        # Add skill-specific suggestions for top categories
        high_priority_categories = ['core_technical', 'cloud_devops', 'frameworks']
        for category in high_priority_categories:
            if category in missing_skills and len(missing_skills[category]) > 0:
                category_name = category.replace('_', ' ').title()
                top_skills = missing_skills[category][:2]
                skill_template = self._select_variation(skill_suggestions[category], f"skill{category}")
                suggestions.append(skill_template.format(skills=', '.join(top_skills)))

        # Experience and career suggestions
        if analysis['experience_compatibility'] < 70:
            exp_suggestions = [
                f"⏳ **Career Progression**: Seek roles that bridge {analysis['resume_experience_level'].title()} to {analysis['job_level'].title()} level responsibilities",
                f"📊 **Experience Building**: Target projects that demonstrate {analysis['job_level'].title()} level capabilities",
                f"🎯 **Professional Growth**: Pursue opportunities that develop {analysis['job_level'].title()} level competencies"
            ]
            suggestions.append(self._select_variation(exp_suggestions, "exp"))

        # Learning and development suggestions
        learning_suggestions = [
            "💼 **Portfolio Development**: Create demonstration projects for your target role",
            "📚 **Continuous Learning**: Follow industry leaders and participate in technical communities",
            "🎓 **Skill Validation**: Consider relevant certifications to validate your expertise",
            "🤝 **Professional Networking**: Engage with communities in your target technology domains"
        ]
        
        # Add 2 learning suggestions
        suggestions.append(self._select_variation(learning_suggestions, "learn1"))
        suggestions.append(self._select_variation(learning_suggestions, "learn2"))

        return suggestions[:6]  # Limit to 6 most relevant suggestions

# Initialize analyzer
analyzer = ResumeAnalyzer()

# Main Streamlit App
def main():
    # Header with Gen AI emphasis
    st.title("🧠 GenAI Resume Capability Analyzer")
    st.markdown("### *Intelligent Career Assessment Using Generative AI Principles*")
    
    # Gen AI Explanation Section
    with st.expander("🔍 How This Demonstrates Generative AI", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🤖 Intelligent Understanding**
            - Natural language processing
            - Skill pattern recognition
            - Experience level detection
            """)
            
        with col2:
            st.markdown("""
            **🎯 AI Decision Making**
            - Weighted capability scoring
            - Multi-factor analysis
            - Compatibility assessment
            """)
            
        with col3:
            st.markdown("""
            **💡 Content Generation**
            - Personalized explanations
            - Dynamic recommendations
            - Actionable insights
            """)
    
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
        # Display file details
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }
        st.sidebar.write("📁 File Details:")
        st.sidebar.json(file_details)
        
        # Process the uploaded file
        with st.spinner("🔍 AI is processing your resume..."):
            resume_text = process_uploaded_resume(uploaded_file)
        
        if resume_text:
            st.sidebar.success("✅ Resume processed successfully!")
            
            # Show AI-detected information
            detected_level = analyzer.detect_experience_level(resume_text)
            detected_skills = analyzer.extract_skills(resume_text)
            skill_categories = len(detected_skills)
            
            st.sidebar.metric("AI-Detected Experience", detected_level.title())
            st.sidebar.metric("Skill Categories Found", skill_categories)
            
    # Job description input
    st.sidebar.header("💼 Job Description")
    
    job_option = st.sidebar.radio("Choose Job Input:", ["Use Sample Job", "Paste Custom Description"])
    
    job_description = ""
    selected_job = ""
    
    if job_option == "Use Sample Job":
        selected_job = st.sidebar.selectbox("Select Sample Job:", [j["title"] for j in SAMPLE_JOBS])
        job_description = next(j["description"] for j in SAMPLE_JOBS if j["title"] == selected_job)
        job_title = selected_job
        
        with st.sidebar.expander("👀 Job Preview"):
            st.text(job_description[:300] + "..." if len(job_description) > 300 else job_description)
    else:
        job_description = st.sidebar.text_area("Paste Job Description:", height=150, 
                                             placeholder="Paste the full job description here...")
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
            4. **Review Recommendations** - Get personalized improvement suggestions
            
            ### 📊 AI-Powered Analysis:
            - **Skill Matching** - Technical competencies alignment
            - **Experience Fit** - Career level compatibility  
            - **Capability Score** - Overall readiness assessment
            - **Personalized Advice** - Actionable career guidance
            """)
            
        with col2:
            st.markdown("""
            ### 🧠 Gen AI Features:
            
            **Natural Language Understanding**
            - Resume text interpretation
            - Skill extraction and categorization
            - Experience level detection
            
            **Intelligent Decision Making**
            - Weighted scoring algorithms
            - Multi-factor capability analysis
            - Compatibility assessment
            
            **Content Generation**
            - Personalized explanations
            - Dynamic recommendations
            - Career development insights
            """)
            
            st.markdown("""
            ### 🚀 Get Started:
            **👉 Upload your resume in the sidebar to begin your AI-powered career analysis!**
            """)
        
    elif resume_text and job_description and (job_title or selected_job):
        # Display analysis interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Your Resume Analysis")
            st.info(f"Uploaded: {uploaded_file.name}")
            
            # AI-detected insights
            detected_level = analyzer.detect_experience_level(resume_text)
            skill_categories = len(analyzer.extract_skills(resume_text))
            
            col1a, col1b = st.columns(2)
            with col1a:
                st.metric("Experience Level", detected_level.title())
            with col1b:
                st.metric("Skill Categories", skill_categories)
            
            with st.expander("🔍 View Processed Resume Content"):
                st.text_area("AI-Extracted Text", resume_text, height=250, key="resume_content")
        
        with col2:
            st.subheader("💼 Target Position")
            display_job_title = selected_job if job_option == "Use Sample Job" else job_title
            st.info(f"Position: {display_job_title}")
            
            job_level = analyzer.detect_job_level(display_job_title)
            st.metric("Job Level", job_level.title())
            
            with st.expander("📝 View Job Requirements"):
                st.text_area("Job Description", job_description, height=250, key="job_content")
        
        # Analyze button
        st.markdown("---")
        if st.button("🧠 **Generate AI Capability Analysis**", use_container_width=True, type="primary"):
            with st.spinner("🔄 AI is analyzing your capabilities... This may take a few moments."):
                # Perform comprehensive analysis
                job_title_for_analysis = selected_job if job_option == "Use Sample Job" else job_title
                analysis = analyzer.analyze_resume_job_match(resume_text, job_description, job_title_for_analysis)
                assessment = analyzer.get_capability_assessment(analysis)
                ai_explanation = analyzer.generate_ai_explanation(analysis)
                suggestions = analyzer.get_improvement_suggestions(analysis)
                
                # Display comprehensive results
                st.subheader("📊 AI Capability Assessment Results")
                
                # Overall scores in columns
                col3, col4, col5 = st.columns(3)
                
                with col3:
                    st.metric(
                        "Overall Capability", 
                        f"{analysis['overall_capability']}%",
                        delta="AI Calculated",
                        help="Your total readiness score for this position"
                    )
                
                with col4:
                    st.metric(
                        "Skills Match", 
                        f"{analysis['skill_match']}%",
                        help="Technical skills alignment with job requirements"
                    )
                
                with col5:
                    st.metric(
                        "Experience Fit", 
                        f"{analysis['experience_compatibility']}%", 
                        help="Compatibility between your experience level and job requirements"
                    )
                
                # AI Explanation
                st.info(ai_explanation)
                
                # Capability level with visual
                st.subheader(f"{assessment['icon']} {assessment['level']}")
                st.write(assessment['description'])
                
                # Progress visualization
                st.subheader("📈 Detailed Breakdown")
                
                col6, col7 = st.columns(2)
                
                with col6:
                    st.write("**Technical Skills Alignment**")
                    st.progress(analysis['skill_match'] / 100)
                    st.caption(f"Weighted score: {analysis['skill_breakdown']['actual_achieved']:.1f}/{analysis['skill_breakdown']['total_possible']:.1f}")
                    
                    st.write("**Experience Compatibility**")
                    st.progress(analysis['experience_compatibility'] / 100)
                    st.caption(f"Your level: {analysis['resume_experience_level'].title()} → Job level: {analysis['job_level'].title()}")
                
                with col7:
                    # Strengths and weaknesses
                    st.write("**💪 Your Strengths**")
                    if assessment['strengths']:
                        for strength in assessment['strengths']:
                            st.success(f"• {strength}")
                    else:
                        st.info("• Focus on developing your key strengths")
                    
                    st.write("**📝 Areas for Development**")
                    if assessment['weaknesses']:
                        for weakness in assessment['weaknesses']:
                            st.error(f"• {weakness}")
                    else:
                        st.success("• Well-balanced profile!")
                
                # Skills analysis
                st.subheader("🔧 Detailed Skills Analysis")
                
                col8, col9 = st.columns(2)
                
                with col8:
                    st.write("**✅ Skills You Possess**")
                    if analysis['matching_skills']:
                        for category, skills in analysis['matching_skills'].items():
                            category_name = category.replace('_', ' ').title()
                            with st.expander(f"🎯 {category_name} ({len(skills)} skills)"):
                                for skill in skills:
                                    st.success(f"• {skill}")
                    else:
                        st.warning("No matching skills detected in the analysis")
                
                with col9:
                    st.write("**📚 Recommended Skills to Learn**")
                    if analysis['missing_skills']:
                        for category, skills in analysis['missing_skills'].items():
                            category_name = category.replace('_', ' ').title()
                            with st.expander(f"🎯 {category_name} ({len(skills)} to learn)"):
                                for skill in skills:
                                    st.error(f"• {skill}")
                    else:
                        st.success("Excellent! No critical skills missing")
                
                # Recommendations
                st.subheader("🎯 AI Recommendations & Next Steps")
                
                st.info(assessment['recommendation'])
                
                st.subheader("🚀 Your Personalized Action Plan")
                for i, suggestion in enumerate(suggestions, 1):
                    if "**" in suggestion:
                        st.markdown(f"{i}. {suggestion}")
                    else:
                        st.write(f"{i}. {suggestion}")
                
                # Gen AI Features Highlight
                st.markdown("---")
                st.subheader("🧠 Generative AI in Action")
                st.markdown("""
                **This analysis demonstrates core Gen AI principles:**
                - **🤖 Intelligent Understanding**: Your resume and job description were processed using NLP techniques
                - **🎯 AI Decision Making**: Multi-factor algorithms calculated weighted capability scores  
                - **💡 Content Generation**: All explanations and recommendations were dynamically generated
                - **🔍 Pattern Recognition**: Experience levels and skill categories were automatically detected
                """)
    
    elif uploaded_file and not resume_text:
        st.error("❌ AI could not extract text from the uploaded file.")
        st.info("""
        **Common issues and solutions:**
        - 🖼️ **Image-based PDF**: Try converting to DOCX format or using a text-based PDF
        - 🔒 **Protected file**: Ensure the file is not password protected
        - 📄 **Scanned document**: Use OCR software to extract text first
        - 💾 **Corrupted file**: Try uploading a fresh copy of your resume
        
        **Recommended**: Upload a DOCX or text-based PDF for best results.
        """)

if __name__ == "__main__":
    main()
