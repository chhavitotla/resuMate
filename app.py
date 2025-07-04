import os
import re
import time
import spacy
import PyPDF2
import streamlit as st
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@400;600;700&display=swap');

    html, body, .stApp {
        background-color: #f5ebff;
        color: #2c2c2c;
        font-family: 'IBM Plex Serif', serif;
    }

    section[data-testid="stSidebar"] {
        background-color: #decaff;
        color: #2c2c2c;
        padding: 1rem;
        border-right: 2px solid #cbaeff;
    }

    section[data-testid="stSidebar"] * {
        color: #2c2c2c !important;
        font-family: 'IBM Plex Serif', serif !important;
    }

    h1, h2, h3, h4 {
        color: #6e00c7;
        font-family: 'IBM Plex Serif', serif !important;
    }

    .stButton > button {
        background-color: #a64dff;
        color: #fff;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        transition: 0.3s ease;
        font-family: 'IBM Plex Serif', serif !important;
    }

    .stButton > button:hover {
        background-color: #9124ff;
        color: #fff;
        transform: scale(1.02);
    }

    .stRadio > div {
        background-color: #f5e6ff;
        border-radius: 10px;
        padding: 1rem;
        font-family: 'IBM Plex Serif', serif !important;
    }

    a {
        color: #7f00ff;
        text-decoration: none;
        font-family: 'IBM Plex Serif', serif !important;
    }

    a:hover {
        text-decoration: underline;
    }

    section[data-testid="stFileUploader"] > div {
        background-color: #eadbfa !important;
        border: 2px dashed #c6aefc !important;
        border-radius: 12px;
        padding: 1rem;
    }

    textarea {
        background-color: #2c2c2c !important;
        color: #f5ebff !important;
        font-weight: 500;
        border: 1.5px solid #cbaeff;
        border-radius: 8px;
        font-family: 'IBM Plex Serif', serif !important;
    }

    textarea::placeholder {
        color: #d2bfff !important;
        opacity: 1;
    }

    label, .css-1cpxqw2 {
        color: #6e00c7 !important;
        font-weight: 600;
        font-family: 'IBM Plex Serif', serif !important;
    }

    .metric-label, .metric-value {
        color: #2c2c2c !important;
        font-family: 'IBM Plex Serif', serif !important;
    }

    .stMarkdown {
        font-family: 'IBM Plex Serif', serif !important;
    }

    .stAlert {
        border-left: 5px solid #9124ff;
        background-color: #f7e7ff;
        color: #2c2c2c;
        font-family: 'IBM Plex Serif', serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Paths
BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts"
QUESTIONS_FILE = PROMPTS_DIR / "questions.txt"
FEEDBACK_FILE = PROMPTS_DIR / "feedback.txt"

# Load chatbot prompt
with open(QUESTIONS_FILE, "r") as f:
    chatbot_prompt = f.read()

# Load feedback prompt
with open(FEEDBACK_FILE, "r") as f:
    feedback_template = f.read()

# LLM
llm = ChatOllama(model="llama3", temperature=0)

# Sidebar navigation with playful student-friendly vibe
st.sidebar.title("🎓 ResuMate")
st.sidebar.markdown("_Let’s prep you for your dream job!_")

page = st.sidebar.radio("🛍️ Navigate your journey:", ["🏠 Home", "🗞 Resume Analyzer", "🧠 Chatbot"])

# --- HOME PAGE ---
if page == "🏠 Home":
    st.markdown("""
    <h1 style='font-family: "IBM Plex Serif", serif;'>👋 Welcome to ResuMate</h1>
    <h3>Drop your resume. We’ll respectfully drag it.<br>
    <small>(Out of love. And career growth. Obviously.)</small></h3>
    <p>Once you hit upload, we’ll deep dive into your ✨LinkedIn-core✨ masterpiece and call out the good, the bad, and the “why is this still in Comic Sans?”</p>
    <h4>What you’ll get:</h4>
    <ul>
        <li>📌 Real talk feedback — no sugar, just spice</li>
        <li>🤖 Robot-proof tips (ATS ain’t slick)</li>
        <li>💅 Glow-up ideas that scream <em>“hire meeee”</em></li>
    </ul>
    <p>Let’s make your resume the <strong>main character</strong>.<br>
    <strong>Ready when you are. 💻💖</strong></p>
    """, unsafe_allow_html=True)

# --- RESUME ANALYZER PAGE ---
elif page == "🗞 Resume Analyzer":
    st.title("Resume Analyzer")

    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Paste the Job Description")

    if st.button("Submit"):
        if not uploaded_file or not job_description.strip():
            st.warning("Please upload a resume and enter a job description.")
            st.stop()

        try:
            resume_text = ""
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                resume_text += page.extract_text()

            resume_doc = nlp(resume_text)
            resume_keywords = [token.text.lower() for token in resume_doc if token.is_alpha and not token.is_stop]
            resume_keywords = list(set(resume_keywords))

            jd_doc = nlp(job_description)
            jd_keywords = [token.text.lower() for token in jd_doc if token.is_alpha and not token.is_stop]
            jd_keywords = list(set(jd_keywords))

            matched = list(set(resume_keywords).intersection(set(jd_keywords)))
            missing = list(set(jd_keywords) - set(resume_keywords))
            total_keywords = len(jd_keywords)
            matched_count = len(matched)
            ats_score = round((matched_count / total_keywords) * 100) if total_keywords else 0

            urls = re.findall(r"https?://\S+", resume_text)

            st.session_state.resume_keywords = resume_keywords
            st.session_state.jd_keywords = jd_keywords
            st.session_state.matched = matched
            st.session_state.missing = missing
            st.session_state.ats_score = ats_score
            st.session_state.urls = urls
            st.session_state.resume_text = resume_text
            st.session_state.submitted = True

            time.sleep(0.1)
            st.experimental_rerun()

        except Exception as e:
            st.error(f"Something went wrong during analysis: {e}")

    if st.session_state.get("submitted"):
        st.markdown("#### ✅ Resume keywords extracted:")
        st.write(", ".join(st.session_state.resume_keywords))

        st.markdown("### ✅ Your resume analysis is complete!")
        st.markdown("Would you like to take a look at its whereabouts?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 View ATS Score"):
                ats = st.session_state.ats_score
                st.success(f"✨ Slay level: {ats}%. {'Almost boss level. 🚀' if ats >= 80 else 'You’re hireable with a hint of chaos. Let’s fix that.'}")

        with col2:
            if st.button("🔍 View Missing Keywords"):
                st.markdown("### Missing Keywords from Resume:")
                st.write(", ".join(st.session_state.missing))

        if st.button("🔗 Check Resume Links"):
            st.markdown("### 🔗 URL Validation Results:")
            for url in st.session_state.urls:
                st.write(f"[{url}]({url})")

        if st.button("📝 Get AI Feedback"):
            filled_prompt = feedback_template.format(
                resume_keywords=", ".join(st.session_state.resume_keywords),
                jd_keywords=", ".join(st.session_state.jd_keywords),
                matched_keywords=", ".join(st.session_state.matched),
                missing_keywords=", ".join(st.session_state.missing),
                ats_score=st.session_state.ats_score
            )
            feedback = llm.invoke(filled_prompt)
            st.markdown("### AI Feedback:")
            st.success(feedback.content)

# --- CHATBOT PAGE ---
elif page == "🧠 Chatbot":
    st.title("Career Chatbot")

    with open(QUESTIONS_FILE, "r") as f:
        all_questions = [q.strip() for q in f.readlines() if q.strip()]

    selected_question = st.selectbox("Choose a question to ask", all_questions)

    if st.button("Ask"):
        full_prompt = f"{chatbot_prompt}\n\nQuestion: {selected_question}"
        response = llm.invoke(full_prompt)
        st.markdown("### Response:")
        st.success(response.content)
