import os, re
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, request, send_file
import pdfplumber, docx2txt, spacy, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "resumes.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    skills = db.Column(db.Text)
    skill_count = db.Column(db.Integer)
    jd_match = db.Column(db.Float)
    ats_score = db.Column(db.Float)
    links = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
with app.app_context():
    db.create_all()

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

nlp = spacy.load("en_core_web_sm")

# ---------- Skill Normalization ----------
SKILL_SYNONYMS = {
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "js": "JavaScript",
    "aws": "Amazon Web Services",
    "nlp": "Natural Language Processing"
}

BASE_SKILLS = [
    "Python", "Java", "Machine Learning", "Artificial Intelligence",
    "Cybersecurity", "JavaScript", "SQL", "AWS", "Linux"
]

# ---------- Regex ----------
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"\+?\d[\d\s-]{8,}")
LINK_RE = re.compile(r"https?://\S+")

# ---------- Helpers ----------
def extract_text(path):
    if path.endswith(".pdf"):
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text += t
        return text
    return docx2txt.process(path)

def normalize_skills(text):
    found = set()
    lower = text.lower()
    for skill in BASE_SKILLS:
        if skill.lower() in lower:
            found.add(skill)
    for k, v in SKILL_SYNONYMS.items():
        if k in lower:
            found.add(v)
    return list(found)

def jd_similarity(resume, jd):
    tfidf = TfidfVectorizer()
    vec = tfidf.fit_transform([resume, jd])
    return cosine_similarity(vec[0], vec[1])[0][0] * 100

def ats_score(skill_count, jd_score, has_links):
    return round(
        (skill_count * 5) +
        (jd_score * 0.5) +
        (10 if has_links else 0), 2
    )

def extract_info(text, jd):
    doc = nlp(text)
    name = next((e.text for e in doc.ents if e.label_ == "PERSON"), "")
    skills = normalize_skills(text)
    email = EMAIL_RE.findall(text)
    phone = PHONE_RE.findall(text)
    links = LINK_RE.findall(text)

    jd_score = jd_similarity(text, jd)
    score = ats_score(len(skills), jd_score, bool(links))

    return {
        "Name": name,
        "Email": email[0] if email else "",
        "Phone": phone[0] if phone else "",
        "Skills": ", ".join(skills),
        "Skill Count": len(skills),
        "JD Match %": round(jd_score, 2),
        "ATS Score": score,
        "Links": ", ".join(links)
    }

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        jd = request.form["jd"]
        files = request.files.getlist("resumes")
        data = []

        for file in files:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)
            text = extract_text(path)
            info = extract_info(text, jd)

            resume = Resume(
                filename=file.filename,
                name=info["Name"],
                email=info["Email"],
                phone=info["Phone"],
                skills=info["Skills"],
                skill_count=info["Skill Count"],
                jd_match=info["JD Match %"],
                ats_score=info["ATS Score"],
                links=info["Links"]
            )
            db.session.add(resume)
            data.append(info)
        db.session.commit()

    

        df = pd.DataFrame(data).sort_values("ATS Score", ascending=False)

        excel_path = os.path.join(OUTPUT_FOLDER, "ranked_resumes.xlsx")
        csv_path = os.path.join(OUTPUT_FOLDER, "ranked_resumes.csv")

        df.to_excel(excel_path, index=False)
        df.to_csv(csv_path, index=False)

        return send_file(excel_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

