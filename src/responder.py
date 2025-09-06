import os
import smtplib
import google.generativeai as genai
from db import SessionLocal
from models import Email
from kb_index import query_kb
from sqlalchemy import or_
from email.mime.text import MIMEText
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS


GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_with_gemini(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-2.0-flash")
    resp = model.generate_content(prompt)
    return resp.text.strip()

def fallback_reply(email: Email) -> str:
    return f"""Hello {email.sender},

Thank you for contacting support regarding: "{email.subject}".
We've received your request and our team will get back to you shortly.

Best regards,  
Support Team
"""

def make_prompt(email: Email) -> str:
    context_docs = query_kb(f"{email.subject} {email.body}", top_k=2)
    context_text = "\n".join(context_docs) if context_docs else "No extra context."

    return f"""You are a professional customer support assistant.
The customer sent the following email:

Subject: {email.subject}
Body: {email.body}

Customer tone: {email.sentiment}
Priority level: {email.priority}

Knowledge base context (may be useful):
{context_text}

Write a helpful, empathetic, professional reply. Use plain text formatting only - do not use markdown, bold text, asterisks, or any special formatting. Write in a natural, conversational tone without special text styling. Do not include the subject in generated response, add company details at the end as done professionally.
"""

def generate_draft(email: Email):
    # session = SessionLocal()
    # emails = session.query(Email).filter(
    #     or_(Email.draft_reply == None, Email.draft_reply == "")
    # ).all()
    print(f"✍️ Generating draft for email {email.id}.")

    
    prompt = make_prompt(email)
    if GEMINI_API_KEY:
        email.draft_reply = generate_with_gemini(prompt)
    else:
        email.draft_reply = fallback_reply(email)
    print(f"✅ Draft generated for email {email.id} ({email.subject[:40]}...)")
    email.status = "drafted"

    # session.commit()
    # session.close()
    # print("🎯 Draft generation complete.")

def send_reply(email_obj: Email, reply_text: str):
    """Send a reply to the given email using SMTP and mark it as replied."""
    try:
        # Build MIME message
        msg = MIMEText(reply_text, "plain")
        msg["Subject"] = f"Re: {email_obj.subject}"
        msg["From"] = SMTP_USER
        msg["To"] = email_obj.sender

        # Send via SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [email_obj.sender], msg.as_string())

        # Mark as replied in DB
        from datetime import datetime
        session = SessionLocal()
        db_email = session.query(Email).get(email_obj.id)
        db_email.status = "replied"
        db_email.draft_reply = reply_text  # store final sent reply
        db_email.date_sent = datetime.now()  # record when reply was sent
        session.commit()
        session.close()

        print(f"✅ Reply sent to {email_obj.sender} for email {email_obj.id}")
        return True
    except Exception as e:
        print("❌ Failed to send reply:", e)
        return False
