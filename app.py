import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import urllib.parse
from pypdf import PdfReader
# Page Configuration
st.set_page_config(
    page_title="Job Skill Gap Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS for Premium Look and Feel
st.markdown("""
<style>
    /* Main layout improvements */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #1f4068, #162447);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: 0.5px;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Cards and Containers */
    .step-card {
        background-color: #ffffff;
        padding: 1.8rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #eef2f5;
        margin-bottom: 1.5rem;
    }
    
    .dark-card-title {
        color: #1f4068;
        font-weight: 600;
        font-size: 1.25rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #eef2f5;
        padding-bottom: 0.5rem;
    }
    
    /* Badges */
    .skill-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        text-align: center;
    }
    
    .badge-blue {
        background-color: #e3f2fd;
        color: #0d47a1;
        border: 1px solid #bbdefb;
    }
    
    .badge-green {
        background-color: #e8f5e9;
        color: #1b5e20;
        border: 1px solid #c8e6c9;
    }
    
    .badge-red {
        background-color: #ffebee;
        color: #c62828;
        border: 1px solid #ffcdd2;
    }
    
    /* Highlight containers */
    .highlight-container {
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
    }
    
    .highlight-match {
        background-color: #f1f8e9;
        border-left: 5px solid #4caf50;
    }
    
    .highlight-gap {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    
    /* Resource cards */
    .resource-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    
    .resource-link {
        display: inline-block;
        background-color: #1f4068;
        color: white !important;
        padding: 0.3rem 0.7rem;
        border-radius: 5px;
        text-decoration: none;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .resource-link:hover {
        background-color: #162447;
    }
</style>
""", unsafe_allow_html=True)
# Master Skill Pool (Used for extracting skills from JD and Resume text)
MASTER_SKILL_POOL = [
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "R", "SQL", "HTML", "CSS", "Bash", "Shell", "PowerShell",
    # Frameworks & Libraries
    "React", "Angular", "Vue", "Next.js", "Django", "Flask", "FastAPI", "Spring Boot", "Express", "Node.js", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Tailwind CSS", "Bootstrap", "jQuery",
    # Cloud & DevOps
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "CI/CD", "Jenkins", "GitHub Actions", "Terraform", "Ansible", "Linux", "Unix", "Git", "GitHub", "GitLab",
    # Database
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle", "Cassandra", "DynamoDB",
    # Concepts & Methodologies
    "Data Structures", "Algorithms", "OOP", "System Design", "REST APIs", "GraphQL", "Agile", "Scrum", "TDD", "Testing", "Microservices", "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Statistics", "Data Visualization", "Tableau", "PowerBI",
    # Design & Product
    "Figma", "UI/UX", "Wireframing", "Prototyping", "User Research", "Adobe XD", "Sketch", "Usability Testing", "Information Architecture", "Visual Design", "Interaction Design",
    # Additional Skills
    "Excel", "Data Analytics", "Technical Writing", "Project Management", "Cybersecurity", "Networking", "Cryptography"
]
# Preset Jobs & Skills Mapping
DEFAULT_JOBS = {
    "Software Engineer": {
        "skills": ["Python", "Java", "C++", "Git", "SQL", "Data Structures", "Algorithms", "OOP", "Testing", "System Design", "REST APIs", "Agile"],
        "description": "Develops, tests, and maintains complex software applications, backend services, and systems architectures. Focuses on code quality, scalability, and algorithms."
    },
    "Data Scientist": {
        "skills": ["Python", "SQL", "Machine Learning", "Deep Learning", "Statistics", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Data Visualization", "Tableau"],
        "description": "Analyzes complex data systems to extract insights, build predictive models, and guide corporate decision-making. Prepares pipelines and trains ML classifiers."
    },
    "Frontend Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Git", "Responsive Design", "TypeScript", "UI/UX", "Tailwind CSS", "Bootstrap", "Figma"],
        "description": "Designs, builds, and maintains user-facing components of web applications. Collaborates with designers to ensure layouts are responsive and accessible."
    },
    "DevOps Engineer": {
        "skills": ["Docker", "Kubernetes", "AWS", "Git", "CI/CD", "Linux", "Terraform", "Bash", "Python", "Jenkins", "Cloud Computing"],
        "description": "Bridges the gap between software development and systems operations. Automates build/deploy pipelines, manages cloud infrastructure, and monitors reliability."
    },
    "UX Designer": {
        "skills": ["Figma", "UI/UX", "Wireframing", "Prototyping", "User Research", "Adobe XD", "Sketch", "Usability Testing", "Information Architecture", "Visual Design"],
        "description": "Focuses on optimizing user-centered software experiences, ensuring intuitive navigability, building interactive mockups, and conducting usability feedback loops."
    }
}
# Skill Specific Resources & Starter Projects
SKILL_RESOURCES = {
    "Python": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=python+programming+tutorial", "Coursera": "https://www.coursera.org/search?query=python"},
        "project": "Build a CLI-based contact book application that saves, reads, and searches contacts via a local JSON file."
    },
    "SQL": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=sql+for+beginners", "Udemy": "https://www.udemy.com/courses/search/?q=sql"},
        "project": "Create a database schema for an e-commerce store and write queries to extract monthly sales metrics and top 5 buyers."
    },
    "Git": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=git+and+github+tutorial"},
        "project": "Create a GitHub repository, commit files, create and merge branches locally and solve a manual merge conflict."
    },
    "Data Structures": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=data+structures+and+algorithms"},
        "project": "Implement custom classes for Linked Lists, Stacks, Queues, and a Binary Search Tree in Python from scratch."
    },
    "Algorithms": {
        "links": {"Coursera": "https://www.coursera.org/search?query=algorithms"},
        "project": "Create an interactive visualizer dashboard displaying how Bubble Sort, Quick Sort, and Merge Sort function step-by-step."
    },
    "Machine Learning": {
        "links": {"Coursera": "https://www.coursera.org/specializations/machine-learning-introduction"},
        "project": "Train a regression or classification model on a housing or customer churn dataset using Scikit-Learn; evaluate accuracy metrics."
    },
    "Docker": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=docker+tutorial"},
        "project": "Dockerize a basic Flask or Express web application using a custom Dockerfile; bind ports and run it inside a local container."
    },
    "Figma": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=figma+ui+design+tutorial"},
        "project": "Design a 5-screen interactive responsive prototype for a mobile banking application detailing payment transfers."
    },
    "React": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=reactjs+tutorial"},
        "project": "Build a dynamic weather forecasting app with React that queries details from a public OpenWeather API."
    },
    "AWS": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=aws+tutorial"},
        "project": "Host a static webpage on AWS S3, set up CloudFront for caching, and point it to a custom domain using Route 53."
    },
    "Kubernetes": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=kubernetes+tutorial"},
        "project": "Launch a Minikube cluster and deploy a web application alongside a MySQL database deployment communicating securely."
    },
    "CI/CD": {
        "links": {"YouTube": "https://www.youtube.com/results?search_query=ci+cd+pipeline+tutorial"},
        "project": "Implement GitHub Actions workflows that automatically build code, lint syntax, and run unit tests on every pull request."
    },
    "UI/UX": {
        "links": {"Coursera": "https://www.coursera.org/specializations/ui-ux-design"},
        "project": "Conduct user surveys, map out a user journey vector, and generate low-fidelity wireframes for a food delivery service."
    }
}
# --- HELPER FUNCTIONS ---
def get_recommendation(skill):
    """Fetch or dynamically construct links and projects for a skill."""
    if skill in SKILL_RESOURCES:
        return SKILL_RESOURCES[skill]
    
    query = urllib.parse.quote(skill)
    return {
        "links": {
            "YouTube": f"https://www.youtube.com/results?search_query={query}+tutorial",
            "Coursera": f"https://www.coursera.org/search?query={query}",
            "Google": f"https://www.google.com/search?q=how+to+learn+{query}"
        },
        "project": f"Create a practical mini-project utilizing {skill} to master its core features and workflows."
    }
def extract_skills_from_text(text):
    """Scans text for occurrences of skills in the MASTER_SKILL_POOL."""
    if not text:
        return set()
    
    extracted = set()
    text_lower = text.lower()
    
    # Custom aliases or special character handlers
    special_skills = {
        "C++": ["c++", "cpp"],
        "C#": ["c#", "c-sharp"],
        ".NET": [".net", "dotnet"],
        "Node.js": ["node.js", "nodejs", "node"],
        "React": ["react", "react.js", "reactjs"],
        "Vue": ["vue", "vue.js", "vuejs"],
        "Angular": ["angular", "angular.js", "angularjs"],
        "Next.js": ["next.js", "nextjs"],
        "CI/CD": ["ci/cd", "ci-cd", "continuous integration"],
        "UI/UX": ["ui/ux", "ui-ux", "user interface", "user experience"],
        "Tailwind CSS": ["tailwind css", "tailwind"],
        "Data Analytics": ["data analytics", "data analysis"],
        "PowerShell": ["powershell", "ps1"]
    }
    
    # First match special cases
    for skill, aliases in special_skills.items():
        for alias in aliases:
            escaped_alias = re.escape(alias)
            # Match boundary on left and right, handling symbols appropriately
            pattern = rf"(?:^|[\s,.;():])({escaped_alias})(?:$|[\s,.;():])"
            if re.search(pattern, text_lower):
                extracted.add(skill)
                break
                
    # Match standard skills
    for skill in MASTER_SKILL_POOL:
        if skill in extracted:
            continue
        
        skill_lower = skill.lower()
        escaped_skill = re.escape(skill_lower)
        
        # Guard short words from partial matches (like 'Go' in 'Google' or 'Django')
        if skill_lower in ["go", "r", "c"]:
            pattern = rf"(?:^|[\s,.;():])({escaped_skill})(?:$|[\s,.;():])"
        else:
            pattern = rf"\b{escaped_skill}\b"
            
        if re.search(pattern, text_lower):
            extracted.add(skill)
            
    return extracted
def extract_text_from_pdf(pdf_file):
    """Extract text content from uploaded PDF file."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return ""
# Initialize Session State for Custom Jobs
if "jobs_db" not in st.session_state:
    st.session_state.jobs_db = DEFAULT_JOBS.copy()
# --- APP LAYOUT ---
# Top Banner Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🎯 Job Skill Gap Analyzer</div>
    <div class="header-subtitle">Analyze job specifications, scan your resume, and discover the path to bridge your skill gaps.</div>
</div>
""", unsafe_allow_html=True)
# Main container grid
col_left, col_right = st.columns([1, 1])
with col_left:
    # -------------------------------------------------------------
    # STEP 1: Provide Job Description (JD)
    # -------------------------------------------------------------
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="dark-card-title">Step 1: Select or Provide Job Description</div>', unsafe_allow_html=True)
    
    # Dropdown including predefined and custom saved roles
    available_jobs = list(st.session_state.jobs_db.keys())
    selection_options = available_jobs + ["➕ Add Custom Job Role"]
    
    job_choice = st.selectbox(
        "Choose Target Job Role",
        options=selection_options,
        index=0
    )
    
    current_required_skills = set()
    current_jd_text = ""
    
    if job_choice == "➕ Add Custom Job Role":
        st.markdown("---")
        st.subheader("Create a New Job Description")
        new_title = st.text_input("New Job Title", placeholder="e.g., AI Research Scientist")
        new_jd = st.text_area("Paste Job Description (JD)", height=150, placeholder="We are looking for an engineer proficient in PyTorch, Python, NLP, and Deep Learning...")
        
        if st.button("💾 Save Job Role", use_container_width=True):
            if not new_title.strip():
                st.warning("Please enter a valid job title.")
            elif not new_jd.strip():
                st.warning("Please paste a job description.")
            else:
                # Extract skills automatically from text
                extracted_skills = list(extract_skills_from_text(new_jd))
                
                # Check if it has any extracted skills, if none warn
                if not extracted_skills:
                    st.info("💡 Note: We couldn't automatically detect master skills in your JD text. We will use it anyway.")
                
                # Save to session database
                st.session_state.jobs_db[new_title] = {
                    "skills": extracted_skills,
                    "description": new_jd
                }
                st.success(f"Job '{new_title}' successfully saved to list! Selecting it now...")
                st.rerun()
    else:
        # Load preset job specs
        job_info = st.session_state.jobs_db[job_choice]
        current_required_skills = set(job_info["skills"])
        current_jd_text = job_info["description"]
        
        # Display description
        st.info(f"**Description:** {current_jd_text}")
        
        # Allow editing or manual override of skills
        st.markdown("**Required Skills Detected:**")
        if current_required_skills:
            badges_html = "".join([f'<span class="skill-badge badge-blue">{skill}</span>' for skill in sorted(current_required_skills)])
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.markdown("*No predefined skills found for this custom role. Paste a detailed JD below to parse.*")
            
        # Re-parse action
        with st.expander("Update / Parse Skills from JD Text"):
            updated_jd = st.text_area("Job Description Text", value=current_jd_text, height=120)
            if st.button("Re-Extract Skills", key="re_extract"):
                parsed = extract_skills_from_text(updated_jd)
                st.session_state.jobs_db[job_choice]["skills"] = list(parsed)
                st.session_state.jobs_db[job_choice]["description"] = updated_jd
                st.success("Required skills updated!")
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)
    # -------------------------------------------------------------
    # STEP 2: Attach Resume
    # -------------------------------------------------------------
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="dark-card-title">Step 2: Attach Resume & Extract Skills</div>', unsafe_allow_html=True)
    
    resume_input_method = st.radio(
        "Choose Resume Input Method:",
        options=["Upload File (PDF / TXT)", "Paste Resume Text"]
    )
    
    resume_text = ""
    
    if resume_input_method == "Upload File (PDF / TXT)":
        uploaded_file = st.file_uploader("Upload your Resume", type=["pdf", "txt"])
        if uploaded_file is not None:
            file_type = uploaded_file.name.split(".")[-1].lower()
            if file_type == "pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = str(uploaded_file.read(), "utf-8", errors="ignore")
    else:
        resume_text = st.text_area(
            "Paste your resume text here:",
            height=200,
            placeholder="John Doe\nSoftware Developer...\nSkills: Python, Git, SQL, Docker, HTML, CSS..."
        )
        
    student_skills = set()
    if resume_text:
        student_skills = extract_skills_from_text(resume_text)
        
        st.markdown("**Your Extracted Skills:**")
        if student_skills:
            badges_html = "".join([f'<span class="skill-badge badge-blue">{skill}</span>' for skill in sorted(student_skills)])
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.warning("No skills detected yet. Please ensure your resume text lists some technical skills from our repository.")
    else:
        st.info("Awaiting resume attachment...")
        
    st.markdown('</div>', unsafe_allow_html=True)
with col_right:
    # -------------------------------------------------------------
    # STEP 3: Analyze & Highlight Skill Gaps
    # -------------------------------------------------------------
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="dark-card-title">Step 3: Skill Gap Analysis & Score</div>', unsafe_allow_html=True)
    
    if job_choice != "➕ Add Custom Job Role" and (resume_text or student_skills):
        # Calculate stats using set operations
        matching_skills = current_required_skills & student_skills
        missing_skills = current_required_skills - student_skills
        
        # Calculate Score
        total_req = len(current_required_skills)
        if total_req > 0:
            match_score = round((len(matching_skills) / total_req) * 100)
        else:
            match_score = 0
            
        # Draw gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = match_score,
            title = {'text': "__", 'font': {'size': 20, 'color': '#1f4068'}},
            number = {'suffix': "%", 'font': {'size': 40, 'color': '#1f4068'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#1f4068"},
                'bar': {'color': "#1f4068"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#eef2f5",
                'steps': [
                    {'range': [0, 40], 'color': '#ffebee'},
                    {'range': [40, 75], 'color': '#fff9c4'},
                    {'range': [75, 100], 'color': '#e8f5e9'}
                ],
            }
        ))
        fig.update_layout(height=220, margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
        # Displays Matching and Missing side-by-side or stacked
        col_match, col_gap = st.columns(2)
        
        with col_match:
            st.markdown('<div class="highlight-container highlight-match">', unsafe_allow_html=True)
            st.markdown("##### ✅ Matching Skills")
            if matching_skills:
                matching_badges = "".join([f'<span class="skill-badge badge-green">{s}</span>' for s in sorted(matching_skills)])
                st.markdown(matching_badges, unsafe_allow_html=True)
            else:
                st.markdown("<small style='color:gray;'>No overlapping skills found.</small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_gap:
            # Highlight missing skills in a separate container as requested
            st.markdown('<div class="highlight-container highlight-gap">', unsafe_allow_html=True)
            st.markdown("##### 🚨 Missing Skills (Gaps)")
            if missing_skills:
                missing_badges = "".join([f'<span class="skill-badge badge-red">{s}</span>' for s in sorted(missing_skills)])
                st.markdown(missing_badges, unsafe_allow_html=True)
            else:
                st.markdown("<small style='color:green; font-weight:bold;'>Perfect Fit! 100% Match.</small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Recommendation details
        if missing_skills:
            st.markdown("#### 📘 Custom Learning & Resource Paths")
            st.write("Click options below to study the missing concepts:")
            
            for m_skill in sorted(missing_skills):
                rec = get_recommendation(m_skill)
                with st.expander(f"Recommended for: **{m_skill}**"):
                    st.write(f"**🎓 Mini-Project Goal:** {rec['project']}")
                    
                    # Render links
                    links_html = ""
                    for platform, url in rec["links"].items():
                        links_html += f'<a class="resource-link" href="{url}" target="_blank">🔗 Study on {platform}</a>'
                    st.markdown(links_html, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.success("Great job! Your resume fully covers all the skills specified in this job description.")
            
        # Variation: Job Matchmaker (Alternative jobs)
        st.markdown("---")
        st.markdown("##### 🔍 Job Matchmaker (Alternative Suggestions)")
        st.write("Here is how your resume matches other job roles in our database:")
        
        matches = []
        for other_title, other_info in st.session_state.jobs_db.items():
            if other_title == job_choice:
                continue
            other_skills = set(other_info["skills"])
            if len(other_skills) > 0:
                other_matching = other_skills & student_skills
                other_score = round((len(other_matching) / len(other_skills)) * 100)
                matches.append({"Job Title": other_title, "Match Score": f"{other_score}%", "Matching Skills": len(other_matching)})
        
        if matches:
            matches_df = pd.DataFrame(matches).sort_values("Matching Skills", ascending=False)
            st.dataframe(matches_df, hide_index=True, use_container_width=True)
        else:
            st.write("Add more jobs or skills to see comparisons.")
            
    else:
        st.info("Select a Job (Step 1) and upload/paste your Resume (Step 2) to display the gap analysis and scores.")
        
    st.markdown('</div>', unsafe_allow_html=True)
# Application Information Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/student-male--v1.png", width=70)
    st.title("About the Analyzer")
    st.markdown("""
    This analyzer applies **List, Set, and Dictionary** operations to help students target career roles:
    
    - **Dictionaries**: Manage job configurations and resource URLs.
    - **Sets**: Compute overlapping skill matches (`&`) and missing requirements (`-`).
    - **Lists**: Store master skill keywords and catalog custom items.
    
    ---
    
    ### Instructions:
    1. Select a job title or choose **Add Custom Job Role** to store your own JD.
    2. Upload your Resume (`.pdf`, `.txt`) or paste raw resume text.
    3. View missing skills separately, research them using provided links, and check alternative job alignments.
    """)
    st.markdown("---")
    if st.button("🔄 Reset Presets"):
        st.session_state.jobs_db = DEFAULT_JOBS.copy()
        st.toast("Predefined Job Descriptions Reset!")
        st.rerun()

