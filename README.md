
# AI Email Assistant

An intelligent email management system that automatically fetches, analyzes, and helps respond to customer support emails using AI-powered sentiment analysis and draft generation.

## Demo Video:


 [<img width="1716" height="637" alt="image" src="https://github.com/user-attachments/assets/265bb32f-d3ea-402d-94da-5b3b514431e3" /> [Watch the Demo]](https://drive.google.com/file/d/1WBEs3qL5A-QOf4n4KpKPnl81mf6MQfks/view?usp=sharing)

## Architecture & Approach

- **.env and config.py files:** The config.py file accesses all the credentials for IMAP and SMTP client setup and for model API keys from the .env file
- **models.py and db.py:** The models.py file uses sqlalchemy lib's ORM feature to define database schemas for emails and knowledge base tables using python class syntax and lets us treat the database table as python objects. db.py file executes the schema structure defined in models.py file and creates a sqlite database for mails and knowledge base for the RAG pipeline.
- **imap_fetcher.py:** The imap_fetcher.py file fetches the unread mails from the accessed gmail account using imap server and parses the mail for extracting sender, subject, body, etc and updates the database with the parsed data.
- **nlp.py**: The nlp.py file uses sentiment analysis, regular expression and keyword matching to determine the sentiment, priority and extract email or phone number from the mails. It uses VADER to sentiment score and classify the mail as positive, negative or neutral. It uses predefined keyword matching to classify the mail as Urgent or Non-urgent, and extracts essential info and appends in the mail body using regex pattern matching. Then all the analyzed info is stored in the database. 
- **kb_index.py:** The kb_index.py file retrieves the stored docs from the knowledge base table in our database and stores the documnets and ids in separate lists, then it uses the 'all-MiniLM-L6-V2' model of sentence-transformers to create embeddings of each doc of dimension 384. Then it creates a flat index that uses euclidean distance for 384 dimensional vector space using FAISS, then we add the embeddings in our index and store the index for future use.
- **setup_kb.py:** The setup_kb file is used to store the documents in the database, it contains some sample documents that are used to generate RAG responses, after adding the documents in the database it also calls the build_index() function from kb_index.py to create the index from the addes docs.
- **responder.py:** The responder.py file performs two major functions, first it creates the AI generated response to send for the mail and second it sends the reply using SMTP server to the sender. To generate the ai response we use google gemini model, first we construct a prompt usinf the mail body, subject, sentiment and priority, we also add the context docs by querying the faiss index and finding similar docs in the knowledge base based on sentiment in the subject and body. Then we pass the prompt to the model and get a response, then from the response we construct a mail template with sender, receiver, subject and body to send via the SMTP connection and at last we update the database with the sent reply and also update the status.
- **dashboard_app.py:** The dashboard_app.py file is used to make the UI of the bot and it uses streamlit for ease of use and speed of prototyping. It integrates all the elements of the bot into a seamless UI and defines the whole flow of the application, which involves fetching emails(imap_fetcher.py), analyzing the emails(nlp.py), generating draft for reply (responder.py) and sending the response at last. It also maintains a interactive dashboard that shows the pending and replied emails separately and show useful analytics at the end with help of simple graphs. 

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





