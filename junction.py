import importlib
import aiohttp
from typing import Dict, Any
import asyncio
import logging
from config import Settings

logger = logging.getLogger(__name__)


class Junction:
    def __init__(self, config: Settings):
        self.connected_services = {}
        self.session = aiohttp.ClientSession()
        self.config = config

    async def process(self, selected_ai: Dict[str, Any], analyzed_input: Dict[str, Any]) -> Any:
        ai_type = selected_ai.get('type')
        ai_id = selected_ai.get('_id')

        if ai_id not in self.connected_services:
            await self._connect_service(selected_ai)

        processor = getattr(self, f"_process_{ai_type}", None)
        if not processor:
            raise ValueError(f"Unsupported AI type: {ai_type}")

        try:
            result = await processor(selected_ai, analyzed_input)
            logger.info(f"Processed input with AI {ai_id}")
            return result
        except Exception as e:
            logger.exception(f"Error processing with AI {ai_id}")
            raise

    async def _connect_service(self, ai_config: Dict[str, Any]):
        ai_id = ai_config['_id']
        ai_type = ai_config['type']

        if ai_type == 'api':
            self.connected_services[ai_id] = ai_config['endpoint']
        elif ai_type in ['bot', 'local_ai', 'custom_ai']:
            module_name = f"ai_modules.{ai_id}"
            try:
                module = importlib.import_module(module_name)
                self.connected_services[ai_id] = await module.AIService.create(self.config)
            except ImportError:
                logger.exception(f"Failed to import AI module: {module_name}")
                raise ValueError(f"Failed to import AI module: {module_name}")

        logger.info(f"Connected to service: {ai_id}")

    async def _process_api(self, ai_config: Dict[str, Any], analyzed_input: Dict[str, Any]) -> Any:
        endpoint = self.connected_services[ai_config['_id']]
        api_key = ai_config['api_key']
        headers = {'Authorization': f'Bearer {api_key}'}

        async with self.session.post(endpoint, json=analyzed_input, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def _process_bot(self, ai_config: Dict[str, Any], analyzed_input: Dict[str, Any]) -> Any:
        bot_service = self.connected_services[ai_config['_id']]
        return await bot_service.process_input(analyzed_input)

    async def _process_local_ai(self, ai_config: Dict[str, Any], analyzed_input: Dict[str, Any]) -> Any:
        local_ai_service = self.connected_services[ai_config['_id']]
        return await local_ai_service.generate_response(analyzed_input)

    async def _process_custom_ai(self, ai_config: Dict[str, Any], analyzed_input: Dict[str, Any]) -> Any:
        custom_ai_service = self.connected_services[ai_config['_id']]
        return await custom_ai_service.execute(analyzed_input)

    async def close(self):
        await self.session.close()