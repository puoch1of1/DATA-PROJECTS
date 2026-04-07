"""AI Chatbot with Sentiment Awareness and Advanced NLP Features.

The bot classifies each user message into granular emotion levels:
- very_unhappy (compound <= -0.75)
- unhappy (-0.75 < compound <= -0.25)
- neutral (-0.25 < compound < 0.25)
- happy (0.25 <= compound < 0.75)
- very_happy (compound >= 0.75)

Features include:
- Intent recognition (emotional_support, help_seeking, information, small_talk)
- Keyword extraction for topic tracking
- Response variety with context-aware templates
- Conversation analytics and statistics
- Session memory with emotional trajectory tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict
from collections import Counter
import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


@dataclass(frozen=True)
class SentimentThresholds:
    """Thresholds for converting VADER compound score into emotion labels."""

    very_happy: float = 0.75
    happy: float = 0.25
    unhappy: float = -0.25
    very_unhappy: float = -0.75


@dataclass
class ChatTurn:
    """Single user-bot exchange kept in session memory."""

    user_text: str
    emotion: str
    emotion_score: float
    intent: str
    keywords: List[str]
    bot_response: str


@dataclass
class ConversationAnalytics:
    """Statistics and metrics about the conversation session."""

    total_turns: int = 0
    emotion_distribution: Dict[str, int] = field(default_factory=lambda: {
        "very_unhappy": 0, "unhappy": 0, "neutral": 0, "happy": 0, "very_happy": 0
    })
    intent_distribution: Dict[str, int] = field(default_factory=lambda: {
        "emotional_support": 0, "help_seeking": 0, "information": 0, "small_talk": 0
    })
    all_keywords: List[str] = field(default_factory=list)
    average_emotion_score: float = 0.0

    def update(self, turn: ChatTurn) -> None:
        """Update analytics with a new chat turn."""
        self.total_turns += 1
        self.emotion_distribution[turn.emotion] += 1
        self.intent_distribution[turn.intent] += 1
        self.all_keywords.extend(turn.keywords)
        self._recalculate_average()

    def _recalculate_average(self) -> None:
        """Calculate average emotion score from all turns."""
        # Score mapping for emotions
        turn_scores = []
        for emotion, count in self.emotion_distribution.items():
            if emotion == "very_unhappy":
                score = -1.0
            elif emotion == "unhappy":
                score = -0.5
            elif emotion == "neutral":
                score = 0.0
            elif emotion == "happy":
                score = 0.5
            else:  # very_happy
                score = 1.0
            turn_scores.extend([score] * count)

        if turn_scores:
            self.average_emotion_score = sum(turn_scores) / len(turn_scores)

    def top_keywords(self, n: int = 10) -> List[tuple[str, int]]:
        """Return top n keywords by frequency."""
        return Counter(self.all_keywords).most_common(n)


def detect_emotion(
    text: str,
    analyzer: SentimentIntensityAnalyzer,
    thresholds: SentimentThresholds,
) -> tuple[str, float]:
    """Return emotion label and compound score based on VADER analysis."""
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= thresholds.very_happy:
        emotion = "very_happy"
    elif compound >= thresholds.happy:
        emotion = "happy"
    elif compound <= thresholds.very_unhappy:
        emotion = "very_unhappy"
    elif compound <= thresholds.unhappy:
        emotion = "unhappy"
    else:
        emotion = "neutral"

    return emotion, compound


def detect_intent(text: str) -> str:
    """Classify user intent into categories: emotional_support, help_seeking, information, small_talk."""
    text_lower = text.lower()

    help_keywords = [
        "help", "how", "can you", "could you", "would you", "what", "where",
        "when", "why", "problem", "issue", "error", "fix", "resolve", "need"
    ]
    emotional_keywords = [
        "feel", "feel", "sad", "happy", "frustrated", "angry", "anxious",
        "worried", "stressed", "depressed", "excited", "love", "hate"
    ]
    info_keywords = [
        "tell", "explain", "what is", "define", "information", "about",
        "how does", "does", "count", "facts", "news"
    ]

    if any(keyword in text_lower for keyword in emotional_keywords):
        return "emotional_support"
    elif any(keyword in text_lower for keyword in help_keywords):
        return "help_seeking"
    elif any(keyword in text_lower for keyword in info_keywords):
        return "information"
    else:
        return "small_talk"


def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from user text."""
    # Remove common words and punctuation
    stop_words = {
        "i", "me", "my", "myself", "we", "our", "you", "your", "he", "she", "it",
        "what", "which", "who", "when", "where", "why", "how", "all", "each",
        "every", "both", "few", "more", "some", "such", "no", "nor", "not",
        "only", "own", "same", "so", "than", "too", "very", "can", "just",
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "am", "are", "was", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "should", "could", "may", "might", "must", "shall"
    }

    # Convert to lowercase and split
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()

    # Filter out stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords


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
