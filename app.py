from flask import Flask, render_template, request, render_template_string
from PyPDF2 import PdfReader
from docx import Document
import re
import html

app = Flask(__name__)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# LOGIN PAGE
# =========================================================

@app.route("/login")
def login():
    return render_template("login.html")


# =========================================================
# UPLOAD PAGE
# =========================================================

@app.route("/upload")
def upload():
    return render_template("upload.html")


# =========================================================
# TEXT EXTRACTION
# =========================================================

def extract_resume_text(file, filename):

    text = ""

    if filename.endswith(".pdf"):

        reader = PdfReader(file)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    elif filename.endswith(".docx"):

        document = Document(file)

        for paragraph in document.paragraphs:

            if paragraph.text.strip():
                text += paragraph.text + "\n"

    return text


# =========================================================
# SKILL CHECK FUNCTION
# =========================================================

def skill_exists(skill, text):

    skill = skill.lower()
    text = text.lower()

    # Power BI variations
    if skill == "power bi":

        return (
            "power bi" in text
            or "powerbi" in text
        )

    # C++ special case
    if skill == "c++":

        return "c++" in text

    # Node.js special case
    if skill == "node.js":

        return (
            "node.js" in text
            or "node js" in text
        )

    pattern = (
        r"(?<!\w)"
        + re.escape(skill)
        + r"(?!\w)"
    )

    return bool(
        re.search(pattern, text)
    )


# =========================================================
# SKILLS DATABASE
# =========================================================

SKILLS = [

    "python",
    "java",
    "c++",
    "c",
    "sql",
    "mysql",
    "excel",
    "power bi",
    "machine learning",
    "data analysis",
    "data analytics",
    "html",
    "css",
    "javascript",
    "flask",
    "django",
    "git",
    "github",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "tableau",
    "mongodb",
    "php",
    "react",
    "node.js",
    "communication",
    "problem solving"

]


# =========================================================
# IMPORTANT ATS SKILLS
# =========================================================

IMPORTANT_SKILLS = [

    "python",
    "sql",
    "excel",
    "power bi",
    "data analysis",
    "machine learning",
    "html",
    "css",
    "javascript",
    "git",
    "pandas",
    "numpy"

]


# =========================================================
# JOB ROLES
# =========================================================

ROLES = {

    "Data Analyst": [

        "python",
        "sql",
        "excel",
        "power bi",
        "data analysis"

    ],

    "Python Developer": [

        "python",
        "flask",
        "django",
        "sql",
        "git"

    ],

    "Web Developer": [

        "html",
        "css",
        "javascript",
        "flask"

    ],

    "Machine Learning Engineer": [

        "python",
        "machine learning",
        "sql",
        "pandas",
        "numpy"

    ]

}


# =========================================================
# RESUME ANALYSIS
# =========================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    # -----------------------------------------------------
    # GET RESUME
    # -----------------------------------------------------

    file = request.files.get("resume")

    # Get Job Description
    job_description = request.form.get(
        "job_description",
        ""
    )


    # -----------------------------------------------------
    # CHECK RESUME
    # -----------------------------------------------------

    if not file or file.filename == "":

        return """
        <h2>No resume selected.</h2>
        <p>Please go back and upload a PDF or DOCX resume.</p>
        """


    # -----------------------------------------------------
    # CHECK JOB DESCRIPTION
    # -----------------------------------------------------

    if not job_description.strip():

        return """
        <h2>No Job Description provided.</h2>
        <p>Please go back and enter a Job Description.</p>
        """


    # -----------------------------------------------------
    # CHECK FILE TYPE
    # -----------------------------------------------------

    filename = file.filename.lower()

    if not (
        filename.endswith(".pdf")
        or filename.endswith(".docx")
    ):

        return """
        <h2>Invalid File</h2>

        <p>
            Please upload a PDF or DOCX resume.
        </p>
        """


    # -----------------------------------------------------
    # READ RESUME
    # -----------------------------------------------------

    try:

        text = extract_resume_text(
            file,
            filename
        )

    except Exception as e:

        return f"""
        <h2>Error reading resume</h2>

        <p>
            {html.escape(str(e))}
        </p>
        """


    # -----------------------------------------------------
    # CHECK EXTRACTED TEXT
    # -----------------------------------------------------

    if not text.strip():

        return """
        <h2>Could not extract text from resume.</h2>

        <p>
            Please upload a text-based PDF or DOCX resume.
        </p>
        """


    # =====================================================
    # CLEAN TEXT
    # =====================================================

    text_clean = re.sub(
        r"\s+",
        " ",
        text.lower()
    )

    job_clean = re.sub(
        r"\s+",
        " ",
        job_description.lower()
    )


    # =====================================================
    # FIND RESUME SKILLS
    # =====================================================

    found_skills = []

    for skill in SKILLS:

        if skill_exists(
            skill,
            text_clean
        ):

            found_skills.append(skill)


    # =====================================================
    # MISSING ATS SKILLS
    # =====================================================

    missing_skills = []

    for skill in IMPORTANT_SKILLS:

        if not skill_exists(
            skill,
            text_clean
        ):

            missing_skills.append(skill)


    # =====================================================
    # RESUME SECTIONS
    # =====================================================

    section_keywords = {

        "Education": [
            "education",
            "educational qualification",
            "academic"
        ],

        "Experience": [
            "experience",
            "work experience",
            "employment"
        ],

        "Skills": [
            "skills",
            "technical skills",
            "technical knowledge"
        ],

        "Projects": [
            "projects",
            "project"
        ],

        "Contact": [
            "contact",
            "email",
            "phone",
            "mobile"
        ]

    }


    sections_found = []

    for section, keywords in section_keywords.items():

        for keyword in keywords:

            if keyword in text_clean:

                sections_found.append(section)

                break


    # =====================================================
    # ATS SCORE
    # =====================================================

    skill_score = (
        len(found_skills)
        / len(IMPORTANT_SKILLS)
    ) * 50


    section_score = (
        len(sections_found)
        / len(section_keywords)
    ) * 30


    word_count = len(
        text.split()
    )


    content_score = 0

    if word_count >= 100:
        content_score += 10

    if word_count >= 200:
        content_score += 10


    ats_score = int(
        skill_score
        + section_score
        + content_score
    )


    if ats_score > 100:
        ats_score = 100


    # =====================================================
    # JOB DESCRIPTION SKILLS
    # =====================================================

    job_skills = []

    for skill in SKILLS:

        if skill_exists(
            skill,
            job_clean
        ):

            job_skills.append(skill)


    # =====================================================
    # MATCHED JOB SKILLS
    # =====================================================

    matched_job_skills = []

    for skill in job_skills:

        if skill_exists(
            skill,
            text_clean
        ):

            matched_job_skills.append(skill)


    # =====================================================
    # MISSING JOB SKILLS
    # =====================================================

    missing_job_skills = []

    for skill in job_skills:

        if not skill_exists(
            skill,
            text_clean
        ):

            missing_job_skills.append(skill)


    # =====================================================
    # JOB MATCH PERCENTAGE
    # =====================================================

    if len(job_skills) > 0:

        job_match = int(
            (
                len(matched_job_skills)
                / len(job_skills)
            ) * 100
        )

    else:

        # If no predefined skill is found
        # in the job description
        job_match = 0


    if job_match > 100:
        job_match = 100


    # =====================================================
    # JOB ROLE MATCHING
    # =====================================================

    role_scores = {}

    for role, role_skills in ROLES.items():

        matched = 0

        for skill in role_skills:

            if skill_exists(
                skill,
                text_clean
            ):

                matched += 1


        score = int(
            (
                matched
                / len(role_skills)
            ) * 100
        )

        role_scores[role] = score


    # =====================================================
    # RECOMMENDED ROLE
    # =====================================================

    recommended_role = max(
        role_scores,
        key=role_scores.get
    )

    recommended_score = role_scores[
        recommended_role
    ]


    # =====================================================
    # IMPROVEMENT SUGGESTION
    # =====================================================

    if job_match >= 80:

        suggestion = (
            "Excellent job match! Your resume contains "
            "most of the important skills required "
            "for this job."
        )

    elif job_match >= 60:

        suggestion = (
            "Good job match. Add the missing job skills "
            "and improve your project or experience "
            "details to increase your chances."
        )

    elif job_match >= 40:

        suggestion = (
            "Your resume has a moderate job match. "
            "Add more skills mentioned in the Job "
            "Description and include relevant projects."
        )

    else:

        suggestion = (
            "Your resume has a low job match. "
            "Carefully review the Job Description and "
            "add relevant skills, projects and "
            "experience where applicable."
        )


    # =====================================================
    # FOUND SKILLS HTML
    # =====================================================

    found_html = ""

    if found_skills:

        for skill in found_skills:

            found_html += f"""
            <span class="skill found-skill">
                ✓ {html.escape(skill.title())}
            </span>
            """

    else:

        found_html = """
        <p>No technical skills detected.</p>
        """


    # =====================================================
    # MISSING ATS SKILLS HTML
    # =====================================================

    missing_html = ""

    if missing_skills:

        for skill in missing_skills:

            missing_html += f"""
            <span class="skill missing-skill">
                ✕ {html.escape(skill.title())}
            </span>
            """

    else:

        missing_html = """
        <p>Great! No major ATS skills are missing.</p>
        """


    # =====================================================
    # MATCHED JOB SKILLS HTML
    # =====================================================

    matched_job_html = ""

    if matched_job_skills:

        for skill in matched_job_skills:

            matched_job_html += f"""
            <span class="skill found-skill">
                ✓ {html.escape(skill.title())}
            </span>
            """

    else:

        matched_job_html = """
        <p>No matching skills found.</p>
        """


    # =====================================================
    # MISSING JOB SKILLS HTML
    # =====================================================

    missing_job_html = ""

    if missing_job_skills:

        for skill in missing_job_skills:

            missing_job_html += f"""
            <span class="skill missing-skill">
                ✕ {html.escape(skill.title())}
            </span>
            """

    else:

        missing_job_html = """
        <p>Excellent! No job-specific skills are missing.</p>
        """


    # =====================================================
    # JOB ROLE HTML
    # =====================================================

    role_html = ""

    for role, score in role_scores.items():

        role_html += f"""

        <div class="role">

            <div class="role-name">
                {html.escape(role)}
            </div>

            <div class="role-right">

                <div class="role-progress">

                    <div
                        class="role-progress-bar"
                        style="width: {score}%;">
                    </div>

                </div>

                <span class="role-score">
                    {score}%
                </span>

            </div>

        </div>

        """


    # =====================================================
    # SAFE TEXT
    # =====================================================

    safe_text = html.escape(text)

    safe_job_description = html.escape(
        job_description
    )


    # =====================================================
    # RESULT PAGE
    # =====================================================

    return render_template_string("""

<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width,
                   initial-scale=1.0">

    <title>AI Resume Analysis</title>

    <link rel="stylesheet"
          href="{{ url_for(
              'static',
              filename='css/style.css'
          ) }}">

</head>


<body>


<header>

    <h1>AI Resume Analyzer</h1>

    <p>Resume Analysis Report</p>

</header>


<div class="container">


    <!-- ATS SCORE -->

    <div class="card">

        <h2>ATS Score</h2>

        <div class="score">

            {{ ats_score }}/100

        </div>

        <div class="progress-container">

            <div
                class="progress-bar"
                style="width: {{ ats_score }}%;">
            </div>

        </div>

        <p class="score-text">
            Overall Resume Score
        </p>

    </div>


    <!-- JOB MATCH -->

    <div class="card">

        <h2>Job Description Match</h2>

        <div class="score">

            {{ job_match }}%

        </div>

        <div class="progress-container">

            <div
                class="progress-bar"
                style="width: {{ job_match }}%;">
            </div>

        </div>

        <p class="score-text">
            Resume Match with Job Description
        </p>

    </div>


    <!-- MATCHED JOB SKILLS -->

    <div class="card">

        <h2>Matched Job Skills</h2>

        <div class="skills-container">

            {{ matched_job_html | safe }}

        </div>

    </div>


    <!-- MISSING JOB SKILLS -->

    <div class="card">

        <h2>Missing Job Skills</h2>

        <div class="skills-container">

            {{ missing_job_html | safe }}

        </div>

    </div>


    <!-- RECOMMENDED ROLE -->

    <div class="card">

        <h2>Recommended Job Role</h2>

        <div class="recommended-role">

            {{ recommended_role }}

        </div>

        <p>

            Match Score:

            <strong>
                {{ recommended_score }}%
            </strong>

        </p>


        <h3>Job Role Matching</h3>

        {{ role_html | safe }}

    </div>


    <!-- RESUME SKILLS -->

    <div class="card">

        <h2>Skills Found in Resume</h2>

        <div class="skills-container">

            {{ found_html | safe }}

        </div>

    </div>


    <!-- ATS MISSING SKILLS -->

    <div class="card">

        <h2>General Missing Skills</h2>

        <div class="skills-container">

            {{ missing_html | safe }}

        </div>

    </div>


    <!-- SUGGESTION -->

    <div class="card">

        <h2>
            Resume Improvement Suggestion
        </h2>

        <div class="suggestion">

            {{ suggestion }}

        </div>

    </div>


    <!-- JOB DESCRIPTION -->

    <div class="card">

        <h2>Job Description Used</h2>

        <div class="resume-text">

            {{ safe_job_description }}

        </div>

    </div>


    <!-- EXTRACTED RESUME TEXT -->

    <div class="card">

        <h2>Extracted Resume Text</h2>

        <div class="resume-text">

            {{ safe_text }}

        </div>

    </div>


</div>


</body>

</html>

""",

    ats_score=ats_score,

    job_match=job_match,

    matched_job_html=matched_job_html,

    missing_job_html=missing_job_html,

    recommended_role=recommended_role,

    recommended_score=recommended_score,

    role_html=role_html,

    found_html=found_html,

    missing_html=missing_html,

    suggestion=suggestion,

    safe_job_description=safe_job_description,

    safe_text=safe_text

    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)
    