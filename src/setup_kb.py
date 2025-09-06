"""
Knowledge Base Setup Script
Creates sample knowledge base documents for the email support system.
"""

from db import SessionLocal
from models import KBDoc
from kb_index import build_index

def create_sample_kb_data(auto_mode=False):
    """Create sample knowledge base documents"""
    session = SessionLocal()
    
    # Sample support documents
    sample_docs = [
        {
            "title": "Password Reset Instructions",
            "content": """To reset your password:
1. Go to the login page
2. Click 'Forgot Password'
3. Enter your email address
4. Check your email for reset link
5. Follow the link and create a new password
6. Your new password must be at least 8 characters long

If you don't receive the email within 5 minutes, check your spam folder."""
        },
        {
            "title": "Account Activation",
            "content": """To activate your new account:
1. Check your email for the activation link
2. Click the activation link in the email
3. Complete your profile information
4. Verify your phone number if required
5. Your account will be active immediately

If the activation link has expired, you can request a new one from the login page."""
        },
        {
            "title": "Billing and Payment Issues",
            "content": """For billing questions:
- Payment methods accepted: Credit cards, PayPal, bank transfer
- Billing cycle: Monthly or annual
- Refund policy: 30-day money-back guarantee
- Payment failures: Check card details and expiry date
- Invoice requests: Contact billing@company.com

For payment disputes, please provide transaction ID and date."""
        },
        {
            "title": "Technical Support",
            "content": """Common technical issues:
- Browser compatibility: Use Chrome, Firefox, Safari, or Edge
- Clear browser cache and cookies
- Disable browser extensions temporarily
- Check internet connection
- Try incognito/private browsing mode
- Update your browser to latest version

For mobile app issues, try restarting the app or reinstalling."""
        },
        {
            "title": "Feature Requests",
            "content": """How to submit feature requests:
1. Use the feedback form in your account settings
2. Describe the feature in detail
3. Explain how it would help you
4. Include mockups or examples if possible

We review all feature requests monthly and prioritize based on user demand and technical feasibility."""
        }
    ]
    
    # Check if documents already exist
    existing_count = session.query(KBDoc).count()
    if existing_count > 0:
        if not auto_mode:
            print(f"Knowledge base already has {existing_count} documents.")
            choice = input("Do you want to add more documents? (y/n): ")
            if choice.lower() != 'y':
                session.close()
                return
        else:
            # In auto mode, skip if KB already exists
            session.close()
            return
    
    # Add sample documents
    added_count = 0
    for doc_data in sample_docs:
        # Check if document with same title exists
        existing = session.query(KBDoc).filter(KBDoc.title == doc_data["title"]).first()
        if not existing:
            doc = KBDoc(title=doc_data["title"], content=doc_data["content"])
            session.add(doc)
            added_count += 1
            if not auto_mode:
                print(f"Added: {doc_data['title']}")
        else:
            if not auto_mode:
                print(f"Skipped (exists): {doc_data['title']}")
    
    if added_count > 0:
        session.commit()
        if not auto_mode:
            print(f"\n✅ Knowledge base setup complete! Added {added_count} documents.")
            print("Building search index...")
        build_index()
    
    session.close()

if __name__ == "__main__":
    create_sample_kb_data()
