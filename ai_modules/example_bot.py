from ai_modules.base_ai import BaseAI
from typing import Dict, Any
import random

class ExampleBot(BaseAI):
    @classmethod
    async def create(cls, config):
        return cls()

    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simple example processing
        return {"processed": input_data["original_input"].upper()}

    async def generate_response(self, input_data: Dict[str, Any]) -> str:
        responses = [
            "I understand you're saying something about {}.",
            "Interesting point about {}.",
            "Tell me more about {}.",
        ]
        topic = input_data["keywords"][0] if input_data["keywords"] else "that"
        return random.choice(responses).format(topic)

    async def execute(self, input_data: Dict[str, Any]) -> Any:
        processed = await self.process_input(input_data)
        response = await self.generate_response(input_data)
        return {"processed": processed, "response": response}