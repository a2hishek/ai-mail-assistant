from dotenv import load_dotenv
import os
load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")
IMAP_FOLDER = os.getenv("IMAP_FOLDER", "INBOX")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SENDER_NAME = os.getenv("SENDER_NAME", "Support Team")

DB_PATH = os.getenv("DB_PATH", "data/emails.sqlite")
FAISS_PATH = os.getenv("FAISS_PATH", "data/faiss_index")
USE_OLLAMA = os.getenv("USE_OLLAMA", "0") == "1"
MODEL_NAME = os.getenv("MODEL_NAME", "mistral")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROCESS_BATCH = int(os.getenv("PROCESS_BATCH", "50"))
