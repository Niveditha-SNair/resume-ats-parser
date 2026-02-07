ATS Resume Parser & Ranking System

This project is a Flask-based web application that parses resumes, extracts candidate details using NLP, ranks candidates against a given job description, and exports the results to Excel or CSV format.

Features

Upload multiple resumes (PDF / DOCX)

Extracts name, email, phone, skills, and links

Skill normalization (ML → Machine Learning, AI → Artificial Intelligence, etc.)

Job Description matching using TF-IDF & cosine similarity

ATS-style scoring and ranking

Stores parsed resume data in SQLite database

Export ranked candidates to Excel and CSV

Clean and responsive web UI

Tech Stack
Backend

Python

Flask

SQLAlchemy

NLP & ML

spaCy

TF-IDF

scikit-learn

Parsing & Data

pdfplumber

docx2txt

pandas

Database

SQLite

Frontend

HTML

CSS

Project Structure
resume_ats_app/
│
├── app.py
├── resumes.db
├── templates/
│   └── index.html
├── uploads/
├── outputs/
├── .gitignore
└── README.md

How to Run the Project

Create virtual environment

python -m venv venv


Activate virtual environment

venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


Run the application

python app.py


Open browser and visit

http://127.0.0.1:5000

Output

Excel file with ranked resumes

ATS Score

Job Description Match Percentage

Extracted candidate skills and contact details

Resume data stored in SQLite database

Use Cases

Resume screening automation

Applicant Tracking Systems (ATS)

Recruitment analytics

Academic / final-year projects

Privacy

All uploaded resumes are processed locally and are not shared externally.


Domain: Python | NLP | Web Development | Automation