import streamlit as st
import pandas as pd
from db import SessionLocal
from models import Email
from responder import send_reply, generate_draft
from nlp import process_new_emails
from imap_fetcher import fetch_and_store
from config import PROCESS_BATCH
from setup_kb import create_sample_kb_data

st.set_page_config(page_title="SupportBot Dashboard", layout="wide")

# Initialize knowledge base on startup
@st.cache_resource
def initialize_kb():
    """Initialize knowledge base with sample data if empty"""
    try:
        create_sample_kb_data(auto_mode=True)
    except Exception as e:
        st.warning(f"Knowledge base initialization failed: {e}")

initialize_kb()

st.title("📬 SupportBot Dashboard")

# --- Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Fetch New Emails"):
        try:
            fetch_and_store(limit=PROCESS_BATCH)
            process_new_emails()
            # generate_drafts()
            st.success("New emails fetched and processed!")
        except Exception as e:
            st.error(f"Error fetching emails: {str(e)}")

with col2:
    if st.button("📊 Refresh Data"):
        st.rerun()

# --- Fetch emails ---
session = SessionLocal()
all_emails = session.query(Email).order_by(Email.priority.desc(), Email.id.desc()).all()

# Separate pending and replied emails
pending_emails = [e for e in all_emails if e.status != 'replied']
replied_emails = [e for e in all_emails if e.status == 'replied']

if not all_emails:
    st.info("No emails in the system yet.")
else:
    # --- PENDING EMAILS QUEUE ---
    if pending_emails:
        pending_df = pd.DataFrame([{
            "ID": e.id,
            "From": e.sender,
            "Subject": e.subject,
            "Sentiment": e.sentiment,
            "Priority": e.priority,
            "Date Received": e.date_received,
            "Status": e.status
        } for e in pending_emails])

        st.subheader("📋 Pending Email Queue")
        st.dataframe(pending_df, use_container_width=True)

        # --- Select email ---
        selected_id = st.selectbox("Select an email to review:", pending_df["ID"].tolist())
        email = session.query(Email).get(selected_id)
    else:
        st.info("No pending emails in the queue.")
        email = None

    if email:
        st.subheader("📧 Email Details")
        st.write(f"**From:** {email.sender}")
        st.write(f"**Subject:** {email.subject}")
        st.write(f"**Body:** {email.body}")
        st.write(f"**Sentiment:** {email.sentiment}")
        st.write(f"**Priority:** {email.priority}")
        st.write(f"**Support Type:** {email.support}")

        # --- Draft Generation ---
        col_draft, col_send = st.columns(2)
        
        with col_draft:
            if st.button("✍️ Generate Draft"):
                with st.spinner("Generating draft..."):
                    generate_draft(email)
                    session.commit()  # Save draft to database
                    st.success("Draft generated!")
                    st.rerun()  # Refresh to show new draft
        
        # --- Show Draft (if exists) ---
        if email.draft_reply:
            st.subheader("✍️ Draft Reply")
            draft = st.text_area(
                "Edit the draft reply before sending:", 
                value=email.draft_reply, 
                height=200,
                key=f"draft_{email.id}"
            )
            
            with col_send:
                if st.button("📧 Send Reply"):
                    if draft.strip():
                        with st.spinner("Sending reply..."):
                            success = send_reply(email, draft)
                            if success:
                                session.commit()
                                st.success("Reply sent and email marked as replied!")
                                st.rerun()
                            else:
                                st.error("Failed to send reply. Please try again.")
                    else:
                        st.error("Please enter a reply message.")
        else:
            st.info("Click 'Generate Draft' to create an AI-powered reply.")

    # --- REPLIED EMAILS SECTION ---
    if replied_emails:
        st.subheader("✅ Replied Emails")
        replied_df = pd.DataFrame([{
            "ID": e.id,
            "From": e.sender,
            "Subject": e.subject,
            "Priority": e.priority,
            "Date Received": e.date_received.strftime("%Y-%m-%d %H:%M") if e.date_received else "N/A",
            "Date Sent": e.date_sent.strftime("%Y-%m-%d %H:%M") if e.date_sent else "N/A"
        } for e in replied_emails])
        
        st.dataframe(replied_df, use_container_width=True)
        
        # Show replied email details in expander
        with st.expander("View Replied Email Details"):
            replied_id = st.selectbox("Select a replied email to view:", replied_df["ID"].tolist(), key="replied_select")
            replied_email = session.query(Email).get(replied_id)
            
            if replied_email:
                st.write(f"**From:** {replied_email.sender}")
                st.write(f"**Subject:** {replied_email.subject}")
                st.write(f"**Body:** {replied_email.body}")
                if replied_email.draft_reply:
                    st.write(f"**Reply Sent:** {replied_email.draft_reply}")
    else:
        st.info("No replied emails yet.")

# --- Analytics ---
st.subheader("📊 Analytics Dashboard")

if all_emails:
    # Create analytics data
    status_counts = {}
    priority_counts = {}
    sentiment_counts = {}
    
    for email in all_emails:
        # Status distribution
        status = email.status or 'unknown'
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Priority distribution
        priority = email.priority or 'Not urgent'
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Sentiment distribution
        sentiment = email.sentiment or 'Neutral'
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
    
    # Create three columns for charts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Email Status")
        if status_counts:
            status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
            st.plotly_chart({
                'data': [{
                    'x': status_df['Status'].tolist(),
                    'y': status_df['Count'].tolist(),
                    'type': 'bar',
                    'marker': {'color': '#1f77b4'}
                }],
                'layout': {
                    'height': 300,
                    'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40},
                    'xaxis': {'fixedrange': True},
                    'yaxis': {'fixedrange': True, 'dtick': 1},
                    'showlegend': False
                }
            }, use_container_width=True, config={'displayModeBar': False})
        
        # Show metrics below chart
        total = len(all_emails)
        pending = len(pending_emails)
        replied = len(replied_emails)
        st.metric("Total Emails", total)
        st.metric("Pending", pending)
        st.metric("Replied", replied)
    
    with col2:
        st.subheader("⚡ Priority Levels")
        if priority_counts:
            priority_df = pd.DataFrame(list(priority_counts.items()), columns=['Priority', 'Count'])
            st.plotly_chart({
                'data': [{
                    'x': priority_df['Priority'].tolist(),
                    'y': priority_df['Count'].tolist(),
                    'type': 'bar',
                    'marker': {'color': '#ff7f0e'}
                }],
                'layout': {
                    'height': 300,
                    'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40},
                    'xaxis': {'fixedrange': True},
                    'yaxis': {'fixedrange': True, 'dtick': 1},
                    'showlegend': False
                }
            }, use_container_width=True, config={'displayModeBar': False})
            
            # Show priority breakdown
            for priority, count in priority_counts.items():
                st.metric(priority, count)
    
    with col3:
        st.subheader("😊 Sentiment Analysis")
        if sentiment_counts:
            sentiment_df = pd.DataFrame(list(sentiment_counts.items()), columns=['Sentiment', 'Count'])
            st.plotly_chart({
                'data': [{
                    'x': sentiment_df['Sentiment'].tolist(),
                    'y': sentiment_df['Count'].tolist(),
                    'type': 'bar',
                    'marker': {'color': '#2ca02c'}
                }],
                'layout': {
                    'height': 300,
                    'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40},
                    'xaxis': {'fixedrange': True},
                    'yaxis': {'fixedrange': True, 'dtick': 1},
                    'showlegend': False
                }
            }, use_container_width=True, config={'displayModeBar': False})
            
            # Show sentiment breakdown
            for sentiment, count in sentiment_counts.items():
                st.metric(sentiment, count)
    
else:
    st.info("No emails available for analytics. Fetch some emails first!")

session.close()
