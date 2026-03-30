"""Streamlit UI for the sentiment-aware chatbot."""

from __future__ import annotations

import streamlit as st

from chatbot import SentimentAwareChatbot


st.set_page_config(page_title="Sentiment-Aware Chatbot", page_icon="💬", layout="centered")

st.title("Sentiment-Aware Chatbot")
st.caption("Emotion labels: happy, neutral, unhappy")

if "bot" not in st.session_state:
    st.session_state.bot = SentimentAwareChatbot()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

prompt = st.chat_input("How are you feeling today?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    emotion, response = st.session_state.bot.reply(prompt)
    bot_text = f"**Detected emotion:** {emotion}\n\n{response}"

    st.session_state.messages.append({"role": "assistant", "content": bot_text})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st.markdown(bot_text)

with st.expander("Session memory preview"):
    if not st.session_state.bot.history:
        st.write("No chat history yet.")
    else:
        for idx, turn in enumerate(st.session_state.bot.history[-8:], start=1):
            st.write(f"{idx}. User: {turn.user_text}")
            st.write(f"   Emotion: {turn.emotion}")
            st.write(f"   Bot: {turn.bot_response}")
