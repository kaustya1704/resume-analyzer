from flask import Flask, render_template, request
import PyPDF2
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Extract text from PDF
def extract_text(file_path):
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text()
    except:
        return "error"
    return text.lower()


# Analyze resume
def analyze_resume(text, jd_text):

    skills = [
        "python","java","sql","html","css","javascript",
        "react","node","mongodb","c++","machine learning",
        "data science","excel","power bi","aws",
        "django","flask","git","github","linux"
    ]

    found = [s for s in skills if s in text]
    missing = [s for s in skills if s not in text]

    # 🔥 BASE SCORE
    score = int((len(found) / len(skills)) * 100)

    # 🔥 DYNAMIC IMPROVEMENTS
    if len(text) < 300:
        score -= 15
    elif len(text) > 1000:
        score += 10

    if "project" in text:
        score += 5
    if "internship" in text:
        score += 5
    if "experience" in text:
        score += 5

    if "python" not in text:
        score -= 5
    if "sql" not in text:
        score -= 5

    # Important skills bonus
    important = ["python", "sql", "machine learning"]
    for skill in important:
        if skill in text:
            score += 3

    # Final limit
    score = max(0, min(score, 100))


    # 🔥 ATS MATCH
    if jd_text:
        jd_words = set(jd_text.lower().split())
        resume_words = set(text.split())
        match_score = int(len(jd_words & resume_words) / len(jd_words) * 100)
    else:
        match_score = 0


    # 🔥 CATEGORY
    if "machine learning" in text or "data science" in text:
        category = "Data Science"
    elif "react" in text or "javascript" in text:
        category = "Web Development"
    elif "java" in text:
        category = "Software Development"
    elif "python" in text:
        category = "Backend Development"
    else:
        category = "General"


    # 🔥 JOB SUGGESTIONS
    jobs = []

    if "machine learning" in text:
        jobs.extend(["Data Scientist", "ML Engineer"])

    if "react" in text:
        jobs.append("Frontend Developer")

    if "node" in text:
        jobs.append("Backend Developer")

    if "java" in text:
        jobs.append("Java Developer")

    if "python" in text:
        jobs.append("Python Developer")

    if not jobs:
        jobs.append("Software Developer")


    # 🔥 TIPS
    tips = []

    if "project" not in text:
        tips.append("Add a Projects section")

    if "internship" not in text:
        tips.append("Mention internships")

    if "python" not in text:
        tips.append("Add Python skills")

    if "sql" not in text:
        tips.append("Include SQL skills")

    if "react" not in text:
        tips.append("Learn React for frontend roles")


    return found, missing, score, jobs, tips, category, match_score


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["resume"]
        jd = request.form.get("jd")

        if file.filename == "":
            return "No file selected"

        filename = file.filename.replace(" ", "_")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        text = extract_text(filepath)

        if text == "" or text == "error":
            return "Could not read PDF"

        found, missing, score, jobs, tips, category, match_score = analyze_resume(text, jd)

        return render_template("index.html",
                               found=found,
                               missing=missing,
                               score=score,
                               jobs=jobs,
                               tips=tips,
                               category=category,
                               match_score=match_score,
                               filename=filename)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)