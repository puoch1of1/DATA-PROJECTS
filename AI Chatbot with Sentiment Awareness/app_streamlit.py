"""Streamlit Web UI for the Sentiment-Aware Chatbot with Advanced Analytics.

Features:
- Real-time emotion and intent detection
- Conversation history with detailed metadata
- Session analytics and statistics
- Sentiment trajectory visualization
- Keyword cloud and topic tracking
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

from chatbot import SentimentAwareChatbot


st.set_page_config(
    page_title="Sentiment-Aware Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Sentiment-Aware Chatbot with Advanced Analytics")
st.caption("Emotion, Intent, and Topic Intelligence for Natural Conversations")

# Initialize session state
if "bot" not in st.session_state:
    st.session_state.bot = SentimentAwareChatbot()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for analytics and settings
with st.sidebar:
    st.header("Chatbot Settings & Analytics")

    # Theme selection
    theme = st.radio("Select response tone:", ["Supportive", "Analytical", "Casual"])

    st.divider()

    # Display session metrics
    if st.session_state.bot.history:
        st.subheader("Session Metrics")

        summary = st.session_state.bot.get_session_summary()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Messages", summary['total_messages'])
        with col2:
            st.metric("Overall Sentiment", summary['overall_sentiment'].capitalize())
        with col3:
            st.metric("Avg Emotion Score", f"{summary['average_emotion_score']:.2f}")

        st.divider()

        # Emotion distribution
        st.subheader("Emotion Distribution")
        emotion_data = summary['emotion_breakdown']
        if sum(emotion_data.values()) > 0:
            fig_emotion = px.pie(
                values=list(emotion_data.values()),
                names=list(emotion_data.keys()),
                title="Emotions Over Time",
                hole=0.4,
                color_discrete_map={
                    "very_happy": "#FFD700",
                    "happy": "#90EE90",
                    "neutral": "#87CEEB",
                    "unhappy": "#FF6B6B",
                    "very_unhappy": "#8B0000"
                }
            )
            st.plotly_chart(fig_emotion, use_container_width=True)

        st.divider()

        # Intent distribution
        st.subheader("User Intent Breakdown")
        intent_data = summary['intent_breakdown']
        if sum(intent_data.values()) > 0:
            fig_intent = px.bar(
                x=list(intent_data.keys()),
                y=list(intent_data.values()),
                title="Types of Requests",
                color=list(intent_data.keys()),
                labels={"x": "Intent", "y": "Count"}
            )
            st.plotly_chart(fig_intent, use_container_width=True)

        st.divider()

        # Top keywords
        st.subheader("Key Topics Discussed")
        top_keywords = summary['top_keywords']
        if top_keywords:
            keywords_df = pd.DataFrame(top_keywords, columns=["Keyword", "Frequency"])
            fig_keywords = px.bar(
                keywords_df,
                x="Keyword",
                y="Frequency",
                title="Most Discussed Topics",
                color="Frequency",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_keywords, use_container_width=True)

# Main chat interface
st.subheader("Chat Interface")

# Display conversation history
for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("How are you feeling today?")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get bot response
    emotion, intent, response, score = st.session_state.bot.reply(prompt)

    # Format bot response with metadata
    bot_metadata = f"""
**Detected Emotion:** {emotion.replace('_', ' ').title()} (confidence: {score})

**Intent:** {intent.replace('_', ' ').title()}

**Response:**
{response}
"""

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_metadata,
        "emotion": emotion,
        "intent": intent,
        "score": score
    })

    # Re-run to display new messages
    st.rerun()

# Detailed conversation history and analytics
st.divider()

with st.expander("Detailed Conversation History", expanded=False):
    if not st.session_state.bot.history:
        st.write("No chat history yet. Start a conversation!")
    else:
        # Create detailed history table
        history_data = []
        for idx, turn in enumerate(st.session_state.bot.history, start=1):
            history_data.append({
                "Turn": idx,
                "User Message": turn.user_text[:50] + "..." if len(turn.user_text) > 50 else turn.user_text,
                "Emotion": turn.emotion,
                "Score": round(turn.emotion_score, 2),
                "Intent": turn.intent,
                "Keywords": ", ".join(turn.keywords[:3]) if turn.keywords else "None",
            })

        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True)

        # Sentiment trajectory
        st.subheader("Sentiment Trajectory")
        sentiment_scores = [turn.emotion_score for turn in st.session_state.bot.history]
        fig_trajectory = go.Figure()
        fig_trajectory.add_trace(go.Scatter(
            y=sentiment_scores,
            mode='lines+markers',
            name='Emotion Score',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8),
            fill='tozeroy'
        ))
        fig_trajectory.update_xaxes(title_text="Message Number")
        fig_trajectory.update_yaxes(title_text="Sentiment Score")
        fig_trajectory.update_layout(
            title="Emotional Trajectory Over Conversation",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_trajectory, use_container_width=True)

with st.expander("Export Session Data", expanded=False):
    if st.session_state.bot.history:
        # Export options
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate Conversation Summary"):
                summary = st.session_state.bot.get_session_summary()
                summary_text = f"""
Conversation Session Summary
=============================

Total Messages: {summary['total_messages']}
Overall Sentiment: {summary['overall_sentiment']}
Average Emotion Score: {summary['average_emotion_score']}

Emotion Breakdown:
{chr(10).join([f"  - {e.replace('_', ' ').title()}: {c}" for e, c in summary['emotion_breakdown'].items()])}

Intent Breakdown:
{chr(10).join([f"  - {i.replace('_', ' ').title()}: {c}" for i, c in summary['intent_breakdown'].items()])}

Top Keywords:
{', '.join([k[0] for k in summary['top_keywords']])}

Dominant Emotion: {summary['dominant_emotion']}
Dominant Intent: {summary['dominant_intent']}
"""
                st.text_area("Session Summary", value=summary_text, height=300)

        with col2:
            if st.button("Clear Conversation"):
                st.session_state.messages = []
                st.session_state.bot = SentimentAwareChatbot()
                st.success("Conversation cleared!")
                st.rerun()

