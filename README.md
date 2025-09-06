# AI Email Assistant

An intelligent email management system that automatically fetches, analyzes, and helps respond to customer support emails using AI-powered sentiment analysis and draft generation.

## Features

- **Automated Email Fetching**: Connects to IMAP servers to fetch new emails automatically
- **AI-Powered Analysis**: Analyzes email sentiment, priority, and support type classification
- **Smart Draft Generation**: Uses Google Gemini AI to generate professional reply drafts
- **Knowledge Base Integration**: Leverages FAISS vector search for context-aware responses
- **Interactive Dashboard**: Streamlit-based web interface for email management
- **Email Queue Management**: Separates pending and replied emails for better workflow
- **Analytics Dashboard**: Visual analytics for email status, priority, and sentiment distribution
- **SMTP Integration**: Send replies directly from the dashboard

## Tech Stack

- **Backend**: Python, SQLAlchemy, SQLite
- **AI/ML**: Google Generative AI (Gemini), Sentence Transformers, FAISS, NLTK
- **Frontend**: Streamlit, Plotly
- **Email**: IMAP/SMTP protocols
- **Database**: SQLite with vector indexing

## Project Structure

```
ai-email-assistant/
├── src/
│   ├── config.py           # Configuration and environment variables
│   ├── models.py           # Database models (Email table)
│   ├── db.py              # Database connection and setup
│   ├── imap_fetcher.py    # Email fetching from IMAP servers
│   ├── nlp.py             # NLP processing and sentiment analysis
│   ├── responder.py       # AI draft generation and SMTP sending
│   ├── kb_index.py        # Knowledge base vector search
│   ├── setup_kb.py        # Knowledge base initialization
│   └── dashboard_app.py   # Main Streamlit dashboard
├── data/                  # Database and index files (auto-created)
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
└── README.md             # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/a2hishek/ai-mail-assistant.git
   cd ai-email-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Email Configuration
   IMAP_HOST=imap.gmail.com
   IMAP_USER=your-email@gmail.com
   IMAP_PASS=your-app-password
   IMAP_FOLDER=INBOX
   
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASS=your-app-password
   SENDER_NAME=Your Support Team
   
   # AI Configuration
   GOOGLE_API_KEY=your-gemini-api-key
   
   # Optional Configuration
   DB_PATH=src/data/emails.sqlite
   PROCESS_BATCH=50
   ```

5. **Download NLTK data** (first run only)
   ```python
   import nltk
   nltk.download('vader_lexicon')
   nltk.download('punkt')
   ```

## Configuration

### Email Setup (Gmail)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in your `.env` file

### Google Gemini API

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GOOGLE_API_KEY`

## Usage

1. **Start the dashboard**
   ```bash
   cd src
   streamlit run dashboard_app.py
   ```

2. **Access the web interface**
   - Open your browser to `http://localhost:8501`

3. **Fetch and process emails**
   - Click "🔄 Fetch New Emails" to get new messages
   - The system will automatically analyze sentiment and priority

4. **Generate and send replies**
   - Select an email from the pending queue
   - Click "✍️ Generate Draft" for AI-powered responses
   - Edit the draft if needed
   - Click "📧 Send Reply" to send via SMTP

## Features in Detail

### Email Analysis
- **Sentiment Analysis**: Classifies emails as Positive, Negative, or Neutral
- **Priority Detection**: Identifies urgent vs non-urgent emails
- **Support Classification**: Detects support-related keywords

### AI Draft Generation
- Uses Google Gemini for natural language responses
- Context-aware using knowledge base integration
- Professional, empathetic tone
- Plain text formatting (no markdown)

### Dashboard Sections
- **Pending Email Queue**: Active emails requiring attention
- **Replied Emails**: Completed emails with audit trail
- **Analytics Dashboard**: Visual insights and metrics

### Knowledge Base
- Vector-based search using FAISS
- Sentence transformer embeddings
- Contextual information for better responses

## API Keys and Security

- Never commit API keys to version control
- Use environment variables for all sensitive data
- The `.env` file is gitignored for security
- Use app passwords for email authentication

## Troubleshooting

### Common Issues

1. **IMAP Connection Failed**
   - Verify email credentials
   - Enable "Less secure app access" or use App Passwords
   - Check IMAP server settings

2. **Gemini API Errors**
   - Verify API key is correct
   - Check API quotas and billing
   - Ensure API is enabled in Google Cloud Console

3. **Database Issues**
   - Delete `src/data/emails.sqlite` to reset database
   - Check file permissions in data directory

4. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again
   - Check Python version compatibility (3.8+)

## Development

### Adding New Features

1. **Database Changes**: Modify `models.py` and run migrations
2. **New Analysis**: Add functions to `nlp.py`
3. **UI Changes**: Update `dashboard_app.py`
4. **Email Processing**: Modify `imap_fetcher.py`

### Testing

Run the dashboard locally and test with sample emails:
```bash
cd src
python imap_fetcher.py  # Test email fetching
python nlp.py          # Test NLP processing
streamlit run dashboard_app.py  # Test full application
```





