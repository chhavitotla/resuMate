# 🧠 ResuMate — Your AI-Powered Resume Sidekick

Welcome to **ResuMate**, the fun, friendly, and brutally honest resume analyzer built just for students and freshers.

Drop your resume. We’ll respectfully drag it.  
_(Out of love. And career growth. Obviously.)_

---

### 🚀 What It Does

- 📌 **Extracts keywords** from your resume
- 💼 **Compares** it against any job description
- 📊 **Calculates ATS score** (Applicant Tracking System readiness)
- 🔍 Shows **missing keywords**
- 🔗 **Validates links** like LinkedIn, GitHub, portfolios
- 🤖 Gives **AI-powered resume feedback**
- 💬 Includes a **career chatbot** trained on student queries

---

### 🛠️ Tech Stack

- `Python`, `Streamlit`
- `LangChain` + `Ollama` + `LLaMA3`
- `spaCy` for NLP keyword matching
- `PyPDF2`, `scikit-learn`

---

### 📦 Run Locally

```bash
git clone https://github.com/chhavitotla/resuMate.git
cd resuMate

# Install dependencies
pip install -r requirements.txt

# Download NLP model
python -m spacy download en_core_web_sm

# Run the app
streamlit run app.py
