import uuid
import random
from datetime import datetime
from models.a2a_models import A2AMessage, MessagePart, TaskResult, TaskStatus, Artifact


class MoodMirrorAgent:
    def __init__(self):
        self.name = "Mood Mirror Agent"
        self.version = "1.0.0"

    def analyze_mood(self, text: str) -> dict:
        """Analyze the emotional tone of text using keyword matching and context clues"""
        if not text.strip():
            return {"mood": "neutral", "score": 0.5}

        text_lower = text.lower()

        positive_words = [
            "happy",
            "good",
            "great",
            "awesome",
            "thanks",
            "love",
            "nice",
            "excited",
            "amazing",
            "wonderful",
            "perfect",
            "fantastic",
            "yay",
            "joy",
            "pleased",
            "delighted",
            "brilliant",
            "excellent",
            "super",
            "fantastic",
            "outstanding",
            "marvelous",
            "fabulous",
            "terrific",
        ]

        negative_words = [
            "sad",
            "bad",
            "angry",
            "hate",
            "worried",
            "stress",
            "ugh",
            "annoying",
            "terrible",
            "awful",
            "horrible",
            "dislike",
            "upset",
            "frustrated",
            "mad",
            "hate",
            "disappointed",
            "awful",
            "dreadful",
            "miserable",
            "depressed",
            "anxious",
            "scared",
            "fearful",
        ]

        excitement_clues = text.count("!") > 1
        all_caps = text.isupper()
        has_positive_emoji = any(
            emoji in text
            for emoji in ["😊", "😂", "❤️", "🎉", "✨", "🥳", "😍", "👍", "⭐"]
        )
        has_negative_emoji = any(
            emoji in text
            for emoji in ["😢", "😠", "💔", "😞", "👎", "😤", "💀", "😔", "😩"]
        )

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if excitement_clues or all_caps or has_positive_emoji:
            positive_count += 2
        if has_negative_emoji:
            negative_count += 2

        total = positive_count + negative_count

        if total == 0:
            word_count = len(text.split())
            avg_word_length = (
                sum(len(word) for word in text.split()) / word_count
                if word_count > 0
                else 0
            )

            if excitement_clues:
                mood = "excited"
                score = 0.8
            elif word_count > 15 or avg_word_length > 6:
                mood = "thoughtful"
                score = 0.5
            elif word_count <= 2:
                mood = "casual"
                score = 0.5
            else:
                mood = "neutral"
                score = 0.5
        else:
            score = positive_count / total
            if score > 0.7:
                mood = "very positive"
            elif score > 0.4:
                mood = "positive"
            elif score > 0.2:
                mood = "slightly negative"
            else:
                mood = "very negative"

        return {"mood": mood, "score": round(score, 2), "keywords_found": total > 0}

    def generate_response(self, mood: str, score: float, user_text: str) -> str:
        """Generate empathetic response based on detected mood"""

        responses = {
            "very positive": [
                f'🌟 I can feel your positive energy! "{user_text}" - that\'s wonderful!',
                f'😊 Your happiness is contagious! "{user_text}" made me smile too!',
                f'🎉 So much positivity! I love that you said: "{user_text}"',
                f'✨ Your enthusiasm in "{user_text}" is absolutely infectious!',
                f'🥳 What fantastic energy! "{user_text}" radiates positivity!',
            ],
            "positive": [
                f'🙂 That sounds nice! "{user_text}" - I\'m glad things are going well!',
                f'💫 I sense good vibes from "{user_text}" - keep it up!',
                f'✨ Your message "{user_text}" has such positive energy!',
                f'😄 I\'m smiling reading "{user_text}" - such good news!',
                f'🌞 Your optimism in "{user_text}" is really uplifting!',
            ],
            "excited": [
                f'🎊 I can feel your excitement! "{user_text}" - how thrilling!',
                f'⚡ So much energy in "{user_text}" - this is exciting!',
                f'🚀 Your excitement is palpable! "{user_text}" sounds amazing!',
                f'🌈 What an exciting message! "{user_text}" got me pumped too!',
            ],
            "neutral": [
                f'🤔 "{user_text}" - I\'m here to listen if you want to share more!',
                f'📝 You mentioned "{user_text}" - tell me how you\'re really feeling!',
                f'💭 "{user_text}" - I\'m curious to know more about your thoughts!',
                f'🎯 "{user_text}" - I\'m listening. What makes you say that?',
            ],
            "thoughtful": [
                f'🔍 "{user_text}" - that\'s intriguing! Help me understand your perspective.',
                f'🧠 "{user_text}" - that sounds like it has a story behind it!',
                f'💫 "{user_text}" - interesting point! What are your thoughts about this?',
                f'🌌 "{user_text}" - fascinating! Could you elaborate?',
            ],
            "casual": [
                f'💫 "{user_text}" - interesting! What are your thoughts about this?',
                f'🎨 "{user_text}" - creative thinking! I\'d love to explore this more with you.',
                f'🌟 "{user_text}" - I sense there\'s more to this. Want to share?',
                f'😊 "{user_text}" - simple but meaningful! Tell me more!',
            ],
            "slightly negative": [
                f'🤗 I sense some concern in "{user_text}" - I\'m here for you!',
                f'💝 "{user_text}" sounds tough - want to talk about it?',
                f'🌧️ I hear the difficulty in "{user_text}" - you\'re not alone!',
                f'🫂 "{user_text}" seems challenging - I\'m here to support you.',
            ],
            "very negative": [
                f'🫂 I can feel the pain in "{user_text}" - that must be really hard.',
                f'❤️ "{user_text}" sounds really challenging - I\'m listening.',
                f'🌈 Even in difficult moments like "{user_text}", I\'m here to support you.',
                f'💔 I hear your struggle in "{user_text}" - you\'re being so strong.',
            ],
        }

        return random.choice(responses.get(mood, responses["neutral"]))

    async def process_message(self, request_data: dict) -> TaskResult:
        """Process incoming A2A message and return telex.im compatible response"""

        user_message = request_data.get("message", {})
        message_parts = user_message.get("parts", [])

        user_text_parts = []
        for part in message_parts:
            if part.get("kind") == "text" and part.get("text"):
                clean_text = part["text"].strip()
                if clean_text and clean_text != "<p></p>":
                    user_text_parts.append(clean_text)
            elif part.get("kind") == "data":
                data_content = part.get("data")
                if isinstance(data_content, list):
                    for data_item in data_content:
                        if isinstance(data_item, dict):
                            if data_item.get("kind") == "text" and data_item.get(
                                "text"
                            ):
                                clean_text = data_item["text"].strip()
                                if clean_text and clean_text != "<p></p>":
                                    user_text_parts.append(clean_text)

        user_text = " ".join(user_text_parts).strip()

        import re

        user_text = re.sub(r"<[^>]+>", "", user_text)
        user_text = re.sub(r"\s+", " ", user_text).strip()

        if not user_text:
            user_text = "Hello!"

        mood_analysis = self.analyze_mood(user_text)
        mood_response = self.generate_response(
            mood_analysis["mood"], mood_analysis["score"], user_text
        )

        response_message = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=mood_response)],
            messageId=str(uuid.uuid4()),
            taskId=user_message.get("taskId"),
        )

        mood_artifact = Artifact(
            artifactId=str(uuid.uuid4()),
            name="mood_analysis",
            parts=[
                MessagePart(
                    kind="data",
                    data={
                        "mood": mood_analysis["mood"],
                        "score": mood_analysis["score"],
                        "keywords_found": mood_analysis["keywords_found"],
                        "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                    },
                )
            ],
        )

        task_result = TaskResult(
            id=request_data.get("id", str(uuid.uuid4())),
            contextId=user_message.get(
                "taskId", f"mood-context-{str(uuid.uuid4())[:8]}"
            ),
            status=TaskStatus(
                state="completed",
                timestamp=datetime.utcnow().isoformat() + "Z",
                message=response_message,
            ),
            artifacts=[mood_artifact],
            history=[user_message, response_message],
        )

        return task_result
