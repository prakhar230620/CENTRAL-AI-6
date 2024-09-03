from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAI(ABC):
    @abstractmethod
    async def create(cls, config):
        pass

    @abstractmethod
    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_response(self, input_data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Any:
        pass