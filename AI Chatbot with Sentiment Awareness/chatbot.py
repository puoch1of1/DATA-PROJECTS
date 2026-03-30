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
from typing import List

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


@dataclass(frozen=True)
class SentimentThresholds:
    """Thresholds for converting VADER compound score into emotion labels."""

    happy: float = 0.25
    unhappy: float = -0.25


@dataclass
class ChatTurn:
    """Single user-bot exchange kept in session memory."""

    user_text: str
    emotion: str
    bot_response: str


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


def build_response_with_memory(
    emotion: str,
    user_text: str,
    history: List[ChatTurn],
) -> str:
    """Adapt the response using both current emotion and recent chat memory."""
    base_response = build_response(emotion, user_text)

    if not history:
        return f"{base_response} This is our first message in this session."

    last_turn = history[-1]

    if emotion == "happy" and last_turn.emotion == "unhappy":
        return (
            f"{base_response} I also notice you sound better than before, "
            "which is great progress."
        )

    if emotion == "unhappy" and last_turn.emotion == "happy":
        return (
            f"{base_response} You sounded more positive earlier, so we can use "
            "what was working then as a starting point."
        )

    if emotion == last_turn.emotion:
        return f"{base_response} I can see this feeling is continuing from your last message."

    return f"{base_response} Compared with your last message, your tone has shifted a bit."


class SentimentAwareChatbot:
    """Chatbot that tracks per-session memory in process."""

    def __init__(self) -> None:
        self.analyzer = SentimentIntensityAnalyzer()
        self.thresholds = SentimentThresholds()
        self.history: List[ChatTurn] = []

    def reply(self, user_text: str) -> tuple[str, str]:
        """Return detected emotion and bot response, then store the turn."""
        emotion = detect_emotion(user_text, self.analyzer, self.thresholds)
        response = build_response_with_memory(emotion, user_text, self.history)
        self.history.append(ChatTurn(user_text=user_text, emotion=emotion, bot_response=response))
        return emotion, response


def run_chatbot() -> None:
    """Run the interactive CLI loop."""
    bot = SentimentAwareChatbot()

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

        emotion, response = bot.reply(user_text)

        print(f"Bot ({emotion}): {response}")


if __name__ == "__main__":
    run_chatbot()
