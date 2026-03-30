# AI Chatbot with Sentiment Awareness

A simple command-line chatbot that uses NLP sentiment analysis to detect whether
a user message is:

- happy
- neutral
- unhappy

The chatbot then adjusts its response tone based on detected emotion.

## Tech

- Python 3.9+
- VADER sentiment analyzer (`vaderSentiment`)

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

## Example

```text
You: I finally got my project working and I am excited.
Bot (happy): That sounds positive. I am glad to hear it. Want to share what is going especially well?

You: I am not sure what to do next.
Bot (neutral): Thanks for sharing. Tell me a bit more and I can try to help further.

You: Everything keeps failing and I feel frustrated.
Bot (unhappy): I hear that this feels tough. If you want, we can break the problem into smaller steps.
```
