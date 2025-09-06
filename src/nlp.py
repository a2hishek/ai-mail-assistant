import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from db import SessionLocal
from sqlalchemy import or_
from models import Email
#import nltk

#nltk.download('vader_lexicon')

# Initialize VADER
sia = SentimentIntensityAnalyzer()

# Regex patterns
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_RE = re.compile(r"\+?\d[\d\-\(\) ]{7,}\d")

# Urgency keywords
URGENCY_KEYWORDS = ["urgent", "immediately", "asap", "critical", "cannot access", "down", "issue"]

def analyze_sentiment(text: str) -> str:
    scores = sia.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def detect_urgency(text: str) -> str:
    text_lower = text.lower()
    if any(kw in text_lower for kw in URGENCY_KEYWORDS):
        return "Urgent"
    return "Not urgent"

def extract_contacts(text: str):
    emails = EMAIL_RE.findall(text)
    phones = PHONE_RE.findall(text)
    return emails, phones

def process_new_emails():
    session = SessionLocal()
    emails = session.query(Email).filter(or_(Email.sentiment == None, Email.sentiment == "Neutral")).all()
    print(f"🔎 Processing {len(emails)} new emails...")

    for em in emails:
        full_text = f"{em.subject} {em.body}"

        # Sentiment
        em.sentiment = analyze_sentiment(full_text)

        # Urgency
        em.priority = detect_urgency(full_text)

        # Extract contacts
        found_emails, found_phones = extract_contacts(full_text)
        if found_emails:
            em.body += f"\n\n[Extracted emails: {', '.join(found_emails)}]"
        if found_phones:
            em.body += f"\n\n[Extracted phones: {', '.join(found_phones)}]"
        
        em.status = "analyzed"

    session.commit()
    session.close()
    print("✅ NLP processing complete.")
