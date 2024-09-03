import uuid
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from cachetools import TTLCache
import logging
from config import Settings

logger = logging.getLogger(__name__)

class AIManager:
    def __init__(self, config: Settings):
        self.client = AsyncIOMotorClient(config.mongodb_url)
        self.db = self.client[config.database_name]
        self.ai_collection = self.db[config.ai_collection_name]
        self.cache = TTLCache(maxsize=config.cache_max_size, ttl=config.cache_ttl)

    async def add_ai(self, ai_data: Dict[str, Any]) -> Dict[str, str]:
        ai_id = str(uuid.uuid4())
        ai_data['_id'] = ai_id
        await self.ai_collection.insert_one(ai_data)
        self.cache[ai_id] = ai_data
        logger.info(f"AI added successfully: {ai_id}")
        return {"id": ai_id, "message": "AI added successfully"}

    async def update_ai(self, ai_id: str, ai_data: Dict[str, Any]) -> Dict[str, str]:
        result = await self.ai_collection.update_one({"_id": ai_id}, {"$set": ai_data})
        if result.modified_count == 0:
            logger.warning(f"AI not found for update: {ai_id}")
            return {"error": "AI not found"}
        self.cache[ai_id] = {**self.cache.get(ai_id, {}), **ai_data}
        logger.info(f"AI updated successfully: {ai_id}")
        return {"message": "AI updated successfully"}

    async def remove_ai(self, ai_id: str) -> Dict[str, str]:
        result = await self.ai_collection.delete_one({"_id": ai_id})
        if result.deleted_count == 0:
            logger.warning(f"AI not found for removal: {ai_id}")
            return {"error": "AI not found"}
        self.cache.pop(ai_id, None)
        logger.info(f"AI removed successfully: {ai_id}")
        return {"message": "AI removed successfully"}

    async def list_ais(self) -> List[Dict[str, Any]]:
        return await self.ai_collection.find().to_list(None)

    async def select_ai(self, analyzed_input: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        all_ais = await self.list_ais()
        best_match = max(all_ais, key=lambda ai: self._calculate_match_score(ai, analyzed_input), default=None)
        if best_match:
            logger.info(f"Selected AI: {best_match['_id']}")
        else:
            logger.warning("No suitable AI found")
        return best_match

    def _calculate_match_score(self, ai: Dict[str, Any], analyzed_input: Dict[str, Any]) -> float:
        score = 0
        ai_description = ai.get('description', '').lower()
        input_keywords = analyzed_input.get('keywords', [])
        input_intent = analyzed_input.get('intent', '').lower()

        for keyword in input_keywords:
            if keyword.lower() in ai_description:
                score += 1 / (ai_description.count(keyword.lower()) + 1)

        if input_intent in ai_description:
            score += 2

        if ai.get('type') == analyzed_input.get('preferred_type'):
            score += 1

        performance_score = ai.get('performance_score', 0)
        score += performance_score * 0.1

        return score