# 🎯 Job Skill Gap Analyzer

A Streamlit-based intelligent web application that analyzes **job descriptions vs resumes** to identify skill gaps, calculate match scores, and provide personalized learning resources to help users improve job readiness.

---

## 🚀 Live Features

- 📄 Upload resume (PDF / TXT) or paste text manually
- 🧠 Automatic skill extraction using rule-based NLP matching
- 🎯 Compare Job Description vs Resume skills
- 📊 Visual match score using interactive gauge chart (Plotly)
- 🚨 Identify missing skills (skill gap analysis)
- 📘 Personalized learning resources (YouTube, Coursera, Google)
- 🧪 Mini-project suggestions for each missing skill
- 🔍 Alternative job role recommendations based on profile match
- ➕ Add custom job roles dynamically

---

## 🛠️ Tech Stack

- Python 🐍  
- Streamlit 🎈  
- Pandas 📊  
- Plotly 📈  
- PyPDF 📄  
- Regex (for skill extraction NLP logic)

---

## 📂 Project Structure
ATS/
│── app.py
│── requirements.txt
│── README.md


---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Akil81485/ATS.git
cd ATS
###2. Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate   # Windows

###3. Install dependencies
pip install -r requirements.txt

4. Run the application
streamlit run app.py
📦 requirements.txt
streamlit
pandas
plotly
pypdf
