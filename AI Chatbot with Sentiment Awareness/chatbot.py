"""Simple CLI chatbot with sentiment awareness.

The bot classifies each user message into one of three emotions:
- happy
- neutral
- unhappy

Sentiment analysis is powered by VADER, a lightweight NLP model that works well
for short conversational text.
"""

from __future__ import annotations

from dataclasses import dataclass

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


@dataclass(frozen=True)
class SentimentThresholds:
    """Thresholds for converting VADER compound score into emotion labels."""

    happy: float = 0.25
    unhappy: float = -0.25


def detect_emotion(
    text: str,
    analyzer: SentimentIntensityAnalyzer,
    thresholds: SentimentThresholds,
) -> str:
    """Return happy, neutral, or unhappy based on VADER compound score."""
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= thresholds.happy:
        return "happy"
    if compound <= thresholds.unhappy:
        return "unhappy"
    return "neutral"


def build_response(emotion: str, user_text: str) -> str:
    """Create a response adapted to the detected user emotion."""
    if emotion == "happy":
        return (
            "That sounds positive. I am glad to hear it. "
            "Want to share what is going especially well?"
        )

    if emotion == "unhappy":
        return (
            "I hear that this feels tough. "
            "If you want, we can break the problem into smaller steps."
        )

    return (
        "Thanks for sharing. "
        "Tell me a bit more and I can try to help further."
    )


def run_chatbot() -> None:
    """Run the interactive CLI loop."""
    analyzer = SentimentIntensityAnalyzer()
    thresholds = SentimentThresholds()

    print("Sentiment-Aware Chatbot")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        user_text = input("You: ").strip()

        if not user_text:
            print("Bot: I did not catch that. Please type a message.")
            continue

        if user_text.lower() in {"exit", "quit"}:
            print("Bot: Thanks for chatting. Take care.")
            break

        emotion = detect_emotion(user_text, analyzer, thresholds)
        response = build_response(emotion, user_text)

        print(f"Bot ({emotion}): {response}")


if __name__ == "__main__":
    run_chatbot()
