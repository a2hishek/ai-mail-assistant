import imaplib, email, re
import time
import random
from email.header import decode_header
from datetime import datetime
from config import IMAP_HOST, IMAP_USER, IMAP_PASS, IMAP_FOLDER, PROCESS_BATCH
from db import engine
from sqlalchemy import text

SUPPORT_TERMS = re.compile(r"\b(support|query|request|help)\b", re.I)

def _decode(val):
    if isinstance(val, bytes):
        try:
            return val.decode()
        except:
            return val.decode("latin-1", errors="ignore")
    return val

def _decode_header(h):
    if not h: return ""
    parts = decode_header(h)
    s = ""
    for txt, enc in parts:
        if isinstance(txt, bytes):
            s += txt.decode(enc or "utf-8", errors="ignore")
        else:
            s += txt
    return s

def fetch_and_store(limit=50):
    print("Connecting to IMAP...", IMAP_HOST)
    m = imaplib.IMAP4_SSL(IMAP_HOST)
    m.login(IMAP_USER, IMAP_PASS)
    m.select(IMAP_FOLDER)
    typ, data = m.search(None, "UNSEEN")
    ids = data[0].split()
    if not ids:
        print("No unseen emails.")
        m.logout()
        return
    ids = ids[-limit:]
    print(f"Found {len(ids)} unseen messages (processing up to {limit})")

    with engine.begin() as conn:
        for i in ids:
            typ, msg_data = m.fetch(i, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            #msg_id = msg.get("Message-ID") or str(i)
            sender = email.utils.parseaddr(msg.get("From",""))[1]
            subject = _decode_header(msg.get("Subject", ""))
            date_str = msg.get("Date")
            try:
                received_at = datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(date_str)))
            except Exception:
                received_at = datetime.utcnow()

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    disp = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in disp:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += _decode(payload)
            else:
                if msg.get_content_type() == "text/plain":
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = _decode(payload)

            is_support = 'Yes' if SUPPORT_TERMS.search(subject or "") else 'No'
            status = 'pending'
            # Generate short unique ID: HKU + timestamp last 4 digits + random 2 digits
            timestamp = str(int(time.time()))[-4:]
            random_num = f"{random.randint(10, 99)}"
            id = f"HKU{timestamp}{random_num}"

            conn.execute(text("""
                INSERT OR IGNORE INTO emails (id, sender, subject, body, date_received, support, status)
                VALUES (:id, :sender, :subject, :body, :received_at, :is_support, :status)
            """), dict(id=id, sender=sender, subject=subject, body=body, received_at=received_at, is_support=is_support, status=status))
            print("Stored:", subject[:80], "from", sender)
    m.logout()
    print("Done.")



if __name__ == "__main__":
    fetch_and_store(limit=PROCESS_BATCH)