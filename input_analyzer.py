from typing import Dict, List, Any
import logging
from transformers import pipeline
from config import Settings

logger = logging.getLogger(__name__)

class InputAnalyzer:
    def __init__(self, config: Settings):
        self.nlp = pipeline("text-classification", model=config.nlp_model)
        self.ner = pipeline("ner", model=config.ner_model)

    async def analyze(self, user_input: str) -> Dict[str, Any]:
        keywords = self._extract_keywords(user_input)
        intent = await self._determine_intent(user_input)
        entities = await self._extract_entities(user_input)
        sentiment = await self._analyze_sentiment(user_input)
        preferred_type = self._determine_preferred_type(user_input)

        analysis = {
            "original_input": user_input,
            "keywords": keywords,
            "intent": intent,
            "entities": entities,
            "sentiment": sentiment,
            "preferred_type": preferred_type
        }

        logger.info(f"Input analysis: {analysis}")
        return analysis

    def _extract_keywords(self, text: str) -> List[str]:
        # Implement keyword extraction logic
        # This is a placeholder implementation
        return [word for word in text.split() if len(word) > 3]

    async def _determine_intent(self, text: str) -> str:
        result = await self.nlp(text)
        return result[0]['label']

    async def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        entities = await self.ner(text)
        return [{"text": entity["word"], "label": entity["entity"]} for entity in entities]

    async def _analyze_sentiment(self, text: str) -> str:
        result = await self.nlp(text, task="sentiment-analysis")
        return result[0]['label']

    def _determine_preferred_type(self, text: str) -> str:
        type_indicators = {
            "api": ["api", "rest", "endpoint"],
            "bot": ["bot", "chatbot"],
            "local_ai": ["local", "offline"],
            "custom_ai": ["custom", "specific"]
        }

        for ai_type, indicators in type_indicators.items():
            if any(indicator in text.lower() for indicator in indicators):
                return ai_type

        return "any"