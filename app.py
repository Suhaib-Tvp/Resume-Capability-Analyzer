import os
import re
import json
import streamlit as st
from typing import Dict, Any, List
from openai import OpenAI

# --------------------------
# 🧩 Streamlit App Settings
# --------------------------
st.set_page_config(
    page_title="AI Resume Capability Analyzer",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Generative AI Resume–Job Capability Analyzer")
st.markdown(
    "Analyze how well a resume matches a job description using both rule-based logic and GPT-powered understanding."
)

# --------------------------
# 🔑 Initialize OpenAI Client
# --------------------------
# The API key is securely loaded from Streamlit Secrets (no need to hardcode it!)
api_key = st.secrets.get("OPENAI_API_KEY", None)
if not api_key:
    st.error("❌ Missing OpenAI API key. Please add it in Streamlit → Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# --------------------------
# 🧠 Resume Analyzer Class
# --------------------------
class ResumeAnalyzer:
    """Hybrid (Rule-based + Generative AI) Resume–Job Analyzer."""

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract basic rule-based skills from text."""
        text = text.lower()
        categories = {
            "core_technical": ["python", "java", "c++", "sql", "r", "javascript"],
            "frameworks": ["tensorflow", "pytorch", "django", "flask", "react", "node"],
            "cloud_devops": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins"],
            "databases": ["mysql", "postgresql", "mongodb", "oracle"],
            "tools_methodologies": ["git", "jira", "agile", "scrum", "ci/cd"],
            "soft_skills": ["communication", "leadership", "teamwork", "problem solving"],
        }

        detected = {cat: [kw for kw in keywords if kw in text] for cat, keywords in categories.items()}
        return detected

    def gpt_extract_skills(self, text: str) -> Dict[str, Any]:
        """Use GPT model to extract and categorize skills from text."""
        if not text:
            return {}

        prompt = f"""
        Extract the key technical and soft skills from this resume text.
        Categorize them into these groups:
        - Core Technical
        - Frameworks
        - Cloud & DevOps
        - Databases
        - Tools & Methodologies
        - Soft Skills

        Return a valid JSON object with this structure:
        {{
          "core_technical": ["skill1", "skill2"],
          "frameworks": ["skill1", "skill2"],
          "cloud_devops": ["skill1", "skill2"],
          "databases": ["skill1", "skill2"],
          "tools_methodologies": ["skill1", "skill2"],
          "soft_skills": ["skill1", "skill2"]
        }}

        Resume text:
        {text[:3000]}
        """

        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return response.output_parsed
        except Exception as e:
            st.error(f"⚠️ GPT error while extracting skills: {e}")
            return {}

    def detect_experience_level(self, text: str) -> str:
        """Basic rule-based detection of experience level."""
        if re.search(r"\b([5-9]|[1-9][0-9])\+?\s*(years|yrs)\b", text):
            return "senior"
        elif re.search(r"\b([2-4])\s*(years|yrs)\b", text):
            return "mid"
        elif re.search(r"\b(0-1|fresher|junior|entry)\b", text):
            return "junior"
        else:
            return "unknown"

    def gpt_detect_experience(self, text: str) -> str:
        """Use GPT to infer experience level (junior/mid/senior)."""
        if not text:
            return "unknown"

        prompt = f"""
        Based on this resume text, infer the candidate's experience level as one of:
        ["junior", "mid", "senior"]. Return only one word.

        Resume text:
        {text[:2000]}
        """

        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
                temperature=0.2
            )
            result = response.output_text.strip().lower()
            return result if result in ["junior", "mid", "senior"] else "unknown"
        except Exception:
            return "unknown"

    def score_capability(self, resume_skills: Dict[str, Any], job_skills: Dict[str, List[str]]) -> Dict[str, float]:
        """Compute percentage match between resume and job skills."""
        scores = {}
        for cat in job_skills:
            job_set = set(job_skills[cat])
            res_set = set(resume_skills.get(cat, []))
            if not job_set:
                continue
            match = len(job_set & res_set) / len(job_set)
            scores[cat] = round(match * 100, 2)
        return scores

    def generate_ai_explanation(self, analysis: Dict) -> str:
        """Use GPT to generate a motivational explanation."""
        prompt = f"""
        You are an AI career coach. Based on this candidate analysis, write a short,
        motivational summary (4–6 sentences) that explains their strengths, weaknesses,
        and next steps in a professional tone.

        Here is the data:
        {json.dumps(analysis, indent=2)}

        Format as Markdown text.
        """

        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
                temperature=0.7
            )
            return response.output_text.strip()
        except Exception as e:
            return f"⚠️ GPT explanation unavailable ({e})"

# --------------------------
# ⚙️ Streamlit Interface
# --------------------------
st.sidebar.header("⚙️ Configuration")
use_gpt = st.sidebar.checkbox("🤖 Use Generative AI (GPT)", value=True)

st.sidebar.markdown("---")
job_description = st.sidebar.text_area("💼 Paste Job Description:", height=200)
resume_text = st.sidebar.text_area("📄 Paste Resume Text:", height=300)
analyze_button = st.sidebar.button("🚀 Analyze Resume")

# --------------------------
# 🚀 Run Analysis
# --------------------------
if analyze_button:
    analyzer = ResumeAnalyzer()

    if not resume_text or not job_description:
        st.warning("Please paste both a job description and a resume text.")
        st.stop()

    job_skills = analyzer.extract_skills(job_description)

    if use_gpt:
        with st.spinner("🧠 Extracting skills and experience using GPT..."):
            resume_skills = analyzer.gpt_extract_skills(resume_text)
            experience_level = analyzer.gpt_detect_experience(resume_text)
    else:
        with st.spinner("🔍 Using rule-based extraction..."):
            resume_skills = analyzer.extract_skills(resume_text)
            experience_level = analyzer.detect_experience_level(resume_text)

    scores = analyzer.score_capability(resume_skills, job_skills)

    analysis = {
        "experience_level": experience_level,
        "capability_scores": scores,
        "resume_skills": resume_skills,
        "job_skills": job_skills
    }

    with st.spinner("🧩 Generating AI-based explanation..."):
        explanation = analyzer.generate_ai_explanation(analysis)

    # --------------------------
    # 📊 Display Results
    # --------------------------
    st.subheader("🔍 Capability Analysis")
    st.write(f"**Experience Level:** `{experience_level.title()}`")

    st.write("### Capability Match Scores")
    for cat, score in scores.items():
        st.progress(score / 100)
        st.write(f"**{cat.replace('_', ' ').title()}**: {score}%")

    st.markdown("### 🧠 AI-Generated Summary")
    st.markdown(explanation)

    st.markdown("### 🧾 Extracted Skills")
    st.json(resume_skills)

    st.markdown("### 📊 Job vs Resume Skill Comparison")
    comparison = {
        cat: {"Job": job_skills.get(cat, []), "Resume": resume_skills.get(cat, [])}
        for cat in job_skills
    }
    st.json(comparison)

# --------------------------
# 🪄 Footer
# --------------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + GPT-4o-mini | © 2025 AI Resume Capability Analyzer")
