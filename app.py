from groq import Groq import os
from flask import Flask, render_template, request
import smtplib
import sqlite3
from email.message import EmailMessage

app = Flask(__name__)


# DATABASE FUNCTION
def init_db():

    conn = sqlite3.connect('jobs.db')

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company TEXT,

            role TEXT,

            recruiter TEXT,

            skills TEXT
        )
    ''')

    conn.commit()

    conn.close()


init_db()


# GROQ AI CLIENT
client = Groq(
   api_key=os.getenv("GROQ_API_KEY")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/send', methods=['POST'])
def send():

    try:

        # FORM DATA
        company = request.form['company']

        role = request.form['role']

        skills = request.form['skills']

        recruiter = request.form['recruiter']

        resume = request.files['resume']


        # EMAIL SUBJECT
        subject = f"Application for {role}"


        # AI PROMPT
        prompt = f"""
Write a professional and realistic job application email.

Candidate Name: Parth Mali

Candidate Email: parthmali400@gmail.com

Candidate Contact Number: +919665543585

Applying Role: {role}

Company: {company}

Candidate Skills:
{skills}

Rules:
- Match skills according to role
- Highlight relevant technical skills
- Keep it short and professional
- Mention attached resume
- No placeholders
- Add contact details at the end
- End with candidate name
"""


        # AI EMAIL GENERATION
        chat_completion = client.chat.completions.create(

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            model="llama-3.3-70b-versatile"
        )


        # AI GENERATED EMAIL
        body = chat_completion.choices[0].message.content


        # YOUR EMAIL
        sender_email = "parthmali400@gmail.com"


        # GMAIL APP PASSWORD
       password = os.getenv("EMAIL_PASSWORD")


        # EMAIL MESSAGE
        msg = EmailMessage()

        msg['Subject'] = subject

        msg['From'] = sender_email

        msg['To'] = recruiter


        # AI GENERATED BODY
        msg.set_content(body)


        # READ RESUME
        file_data = resume.read()


        # ATTACH RESUME
        msg.add_attachment(
            file_data,
            maintype='application',
            subtype='octet-stream',
            filename=resume.filename
        )


        # SMTP SERVER
        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.ehlo()

        server.starttls()

        server.ehlo()


        # LOGIN
        server.login(sender_email, password)


        # SEND EMAIL
        server.send_message(msg)

        server.quit()


        # SAVE TO DATABASE
        conn = sqlite3.connect('jobs.db')

        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO applications (company, role, recruiter, skills) VALUES (?, ?, ?, ?)",
            (company, role, recruiter, skills)
        )

        conn.commit()

        conn.close()


        return "AI Email with Resume Sent Successfully"


    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(debug=True)