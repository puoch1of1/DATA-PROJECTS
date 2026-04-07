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


def build_response(emotion: str, intent: str, user_text: str) -> str:
    """Create a response adapted to emotion and intent."""
    # Response templates by emotion and intent
    responses = {
        "very_happy": {
            "emotional_support": [
                "That's wonderful! Your enthusiasm is truly infectious. Keep riding this positive wave!",
                "I love your energy! This kind of positivity is powerful. What's driving all this joy?",
            ],
            "help_seeking": [
                "Great mindset! With your positive outlook, you'll definitely find a solution. Let's tackle it!",
                "Your optimism is your superpower right now. What specifically can we work on together?",
            ],
            "information": [
                "Awesome! I'm excited to share this with you. Here's what you need to know.",
                "Perfect timing for some good information! What aspect interests you most?",
            ],
            "small_talk": [
                "Your mood is contagious! It sounds like things are going really well for you.",
                "This is fantastic energy! What's been the highlight of your day?",
            ],
        },
        "happy": {
            "emotional_support": [
                "That sounds positive. I'm glad to hear it. Want to share what's going especially well?",
                "It's great that you're feeling good. What's contributing to this positive mood?",
            ],
            "help_seeking": [
                "With this positive energy, you're in a great place to tackle challenges. How can I help?",
                "This is a good mindset for problem-solving. What's the issue you'd like to address?",
            ],
            "information": [
                "Glad you're interested! I have some useful information to share on that.",
                "Perfect, let me share some details that might help you.",
            ],
            "small_talk": [
                "That's great to hear! Sounds like you're in a good place right now.",
                "Your positive tone is refreshing. Tell me more about what's on your mind.",
            ],
        },
        "neutral": {
            "emotional_support": [
                "Thanks for sharing. Tell me a bit more and I can try to help further.",
                "I appreciate you opening up. What else is on your mind?",
            ],
            "help_seeking": [
                "I'm here to help. Can you walk me through what you need?",
                "Let's work through this together. What's the main challenge?",
            ],
            "information": [
                "I can provide some insights on that. What would be most helpful?",
                "That's an interesting topic. What specific aspects interest you?",
            ],
            "small_talk": [
                "Interesting. Tell me more about that.",
                "I see. What brought that to mind?",
            ],
        },
        "unhappy": {
            "emotional_support": [
                "I hear that this is challenging. It's okay to feel this way. Want to talk about it?",
                "I sense you're going through something difficult. I'm here to listen.",
            ],
            "help_seeking": [
                "I understand this feels tough. Let's break it down into smaller, manageable steps.",
                "Don't worry, we can work through this together. Where should we start?",
            ],
            "information": [
                "I can help shed some light on this. Understanding more might ease some of the frustration.",
                "Let me share some perspective that might help clarify things.",
            ],
            "small_talk": [
                "It sounds like you're having a rough time. Want to talk about it?",
                "I pick up on some frustration. What's bothering you?",
            ],
        },
        "very_unhappy": {
            "emotional_support": [
                "I can sense you're really struggling right now. You're not alone, and it's okay to feel this way.",
                "This sounds incredibly difficult. I'm genuinely here to support you through this.",
            ],
            "help_seeking": [
                "I understand you're in a tough spot. Let's take this one small step at a time, together.",
                "This feels overwhelming, but breaking it into pieces makes it manageable. Let's start there.",
            ],
            "information": [
                "Getting clarity on this might help ease some of the distress. Let me explain.",
                "Understanding what's happening is the first step toward improvement.",
            ],
            "small_talk": [
                "Something seems really wrong. I'm here to listen if you want to share.",
                "You sound like you're carrying a heavy load. Let me know if I can help.",
            ],
        },
    }

    # Get the appropriate response template
    template_list = responses.get(emotion, {}).get(intent, [])
    if not template_list:
        # Fallback response
        return "I'm here to help. Tell me more about what you're experiencing."

    # Alternate responses for variety (could use counter in real app)
    return template_list[0] if len(template_list) > 0 else template_list[-1]


def build_response_with_memory(
    emotion: str,
    intent: str,
    user_text: str,
    history: List[ChatTurn],
) -> str:
    """Adapt response using emotion, intent, and recent chat memory."""
    base_response = build_response(emotion, intent, user_text)

    if not history:
        return f"{base_response}"

    last_turn = history[-1]

    # Track emotional trajectory
    if emotion in ["happy", "very_happy"] and last_turn.emotion in ["unhappy", "very_unhappy"]:
        return (
            f"{base_response} I also notice you sound better than before, "
            "which is wonderful progress."
        )

    if emotion in ["unhappy", "very_unhappy"] and last_turn.emotion in ["happy", "very_happy"]:
        return (
            f"{base_response} You sounded more positive earlier, so let's remember "
            "what was working then."
        )

    if emotion == last_turn.emotion:
        return f"{base_response} I can see this feeling is continuing from before."

    # If intent repeated
    if intent == last_turn.intent and history:
        return f"{base_response} It seems this is still on your mind."

    return f"{base_response} I'm noticing a shift in what you're bringing up."


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
