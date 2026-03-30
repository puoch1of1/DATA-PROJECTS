# AI Chatbot with Sentiment Awareness

A simple command-line chatbot that uses NLP sentiment analysis to detect whether
a user message is:

- happy
- neutral
- unhappy

The chatbot then adjusts its response tone based on detected emotion.

This version also includes:

- in-session memory so the bot can reference earlier messages
- a Streamlit web chat interface

## Tech

- Python 3.9+
- VADER sentiment analyzer (`vaderSentiment`)
- Streamlit (`streamlit`)

## Setup

1. Open a terminal in this folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python chatbot.py
```

Type `exit` or `quit` to end the chat.

## Run Web UI

```bash
streamlit run app_streamlit.py
```

The web app keeps conversation history in the same browser session using
`st.session_state`, and the chatbot logic keeps a memory list of prior turns.

## Example

```text
You: I finally got my project working and I am excited.
Bot (happy): That sounds positive. I am glad to hear it. Want to share what is going especially well?

You: I am not sure what to do next.
Bot (neutral): Thanks for sharing. Tell me a bit more and I can try to help further.

You: Everything keeps failing and I feel frustrated.
Bot (unhappy): I hear that this feels tough. If you want, we can break the problem into smaller steps.
```
