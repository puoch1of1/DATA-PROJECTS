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
from typing import Any, Dict, List
from collections import Counter
import random
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
        """Calculate average emotion score from the stored turn history."""
        if not self.total_turns:
            self.average_emotion_score = 0.0
            return

        emotion_scores = {
            "very_unhappy": -1.0,
            "unhappy": -0.5,
            "neutral": 0.0,
            "happy": 0.5,
            "very_happy": 1.0,
        }
        weighted_total = sum(
            emotion_scores[emotion] * count for emotion, count in self.emotion_distribution.items()
        )
        self.average_emotion_score = weighted_total / self.total_turns

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
        "help", "can you", "could you", "would you", "problem", "issue",
        "error", "fix", "resolve", "need", "assist", "support"
    ]
    emotional_keywords = [
        "feel", "sad", "happy", "frustrated", "angry", "anxious",
        "worried", "stressed", "depressed", "excited", "love", "hate"
    ]
    info_keywords = [
        "tell", "explain", "what is", "what's", "define", "information",
        "about", "how does", "does", "count", "facts", "news",
        "difference", "compare", "meaning", "details"
    ]

    info_patterns = [
        r"\bwhat(?:'s| is)\b",
        r"\bhow does\b",
        r"\bdifference between\b",
        r"\bcompare\b",
        r"\bdefine\b",
    ]

    if any(keyword in text_lower for keyword in emotional_keywords):
        return "emotional_support"
    elif any(re.search(pattern, text_lower) for pattern in info_patterns) or any(keyword in text_lower for keyword in info_keywords):
        return "information"
    elif any(keyword in text_lower for keyword in help_keywords):
        return "help_seeking"
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


def build_response(emotion: str, intent: str, user_text: str, response_tone: str = "supportive") -> str:
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

    response = random.choice(template_list)

    tone_suffixes = {
        "supportive": "",
        "analytical": " Let's approach this step by step and keep it practical.",
        "casual": " We can keep it simple and conversational.",
    }
    return f"{response}{tone_suffixes.get(response_tone, '')}"


def build_response_with_memory(
    emotion: str,
    intent: str,
    user_text: str,
    history: List[ChatTurn],
    response_tone: str = "supportive",
) -> str:
    """Adapt response using emotion, intent, and recent chat memory."""
    base_response = build_response(emotion, intent, user_text, response_tone=response_tone)

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
    """Advanced chatbot with emotion, intent, and topic tracking."""

    def __init__(self) -> None:
        self.analyzer = SentimentIntensityAnalyzer()
        self.thresholds = SentimentThresholds()
        self.history: List[ChatTurn] = []
        self.analytics = ConversationAnalytics()

    def reply(self, user_text: str, response_tone: str = "supportive") -> tuple[str, str, str, float]:
        """Return emotion, sentiment_score, intent, and bot response, then store the turn."""
        emotion, score = detect_emotion(user_text, self.analyzer, self.thresholds)
        intent = detect_intent(user_text)
        keywords = extract_keywords(user_text)
        response = build_response_with_memory(
            emotion,
            intent,
            user_text,
            self.history,
            response_tone=response_tone,
        )

        turn = ChatTurn(
            user_text=user_text,
            emotion=emotion,
            emotion_score=score,
            intent=intent,
            keywords=keywords,
            bot_response=response,
        )
        self.history.append(turn)
        self.analytics.update(turn)

        return emotion, intent, response, round(score, 2)

    def get_session_summary(self) -> Dict[str, Any]:
        """Return comprehensive session statistics."""
        dominant_emotion = max(self.analytics.emotion_distribution, key=self.analytics.emotion_distribution.get)
        dominant_intent = max(self.analytics.intent_distribution, key=self.analytics.intent_distribution.get)
        return {
            "total_messages": self.analytics.total_turns,
            "overall_sentiment": "positive" if self.analytics.average_emotion_score > 0 else "negative" if self.analytics.average_emotion_score < 0 else "neutral",
            "average_emotion_score": round(self.analytics.average_emotion_score, 2),
            "emotion_breakdown": self.analytics.emotion_distribution.copy(),
            "intent_breakdown": self.analytics.intent_distribution.copy(),
            "top_keywords": self.analytics.top_keywords(5),
            "dominant_emotion": dominant_emotion if self.analytics.total_turns else "neutral",
            "dominant_intent": dominant_intent if self.analytics.total_turns else "small_talk",
        }


def run_chatbot() -> None:
    """Run the interactive CLI loop with enhanced features."""
    bot = SentimentAwareChatbot()

    print("=" * 60)
    print("Sentiment-Aware Chatbot with Intent & Topic Tracking")
    print("=" * 60)
    print("Commands:")
    print("  Type your message to chat")
    print("  'stats' - Display session analytics")
    print("  'summary' - Get conversation summary")
    print("  'history' - Show recent conversation history")
    print("  'exit' or 'quit' - End the chat")
    print("=" * 60)

    while True:
        user_text = input("\nYou: ").strip()

        if not user_text:
            print("Bot: I did not catch that. Please type a message.")
            continue

        if user_text.lower() in {"exit", "quit"}:
            print("Bot: Thanks for chatting. Take care!")
            # Show final summary
            summary = bot.get_session_summary()
            print(f"\nSession Summary:")
            print(f"  - Total messages: {summary['total_messages']}")
            print(f"  - Overall sentiment: {summary['overall_sentiment']}")
            print(f"  - Average emotion score: {summary['average_emotion_score']}")
            break

        if user_text.lower() == "stats":
            summary = bot.get_session_summary()
            print("\nConversation Analytics:")
            print(f"  Total messages: {summary['total_messages']}")
            print(f"  Overall sentiment: {summary['overall_sentiment']}")
            print(f"  Average emotion score: {summary['average_emotion_score']}")
            print(f"  Emotion breakdown: {summary['emotion_breakdown']}")
            print(f"  Intent breakdown: {summary['intent_breakdown']}")
            if summary['top_keywords']:
                print(f"  Top keywords: {', '.join([k[0] for k in summary['top_keywords']])}")
            continue

        if user_text.lower() == "summary":
            summary = bot.get_session_summary()
            print("\nConversation Summary:")
            print(f"  Dominant emotion: {summary['dominant_emotion']}")
            print(f"  Dominant intent: {summary['dominant_intent']}")
            print(f"  Total turns: {summary['total_messages']}")
            print(f"  Sentiment trajectory: {summary['overall_sentiment']}")
            continue

        if user_text.lower() == "history":
            if not bot.history:
                print("\nBot: No chat history yet.")
            else:
                print("\nRecent conversation history:")
                for idx, turn in enumerate(bot.history[-5:], start=1):
                    print(f"\n{idx}. User: {turn.user_text}")
                    print(f"   Emotion: {turn.emotion} (score: {turn.emotion_score})")
                    print(f"   Intent: {turn.intent}")
                    if turn.keywords:
                        print(f"   Keywords: {', '.join(turn.keywords[:3])}")
                    print(f"   Bot: {turn.bot_response}")
            continue

        emotion, intent, response, score = bot.reply(user_text)
        print(f"Bot ({emotion}, score: {score}): {response}")


if __name__ == "__main__":
    run_chatbot()
