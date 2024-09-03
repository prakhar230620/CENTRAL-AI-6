import time
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class PerformanceTracker:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.client[settings.database_name]
        self.collection = self.db['performance_metrics']

    async def track_performance(self, ai_id: str, execution_time: float, success: bool):
        await self.collection.update_one(
            {'ai_id': ai_id},
            {
                '$inc': {
                    'total_executions': 1,
                    'successful_executions': 1 if success else 0
                },
                '$push': {
                    'execution_times': {
                        '$each': [execution_time],
                        '$slice': -100  # Keep only the last 100 execution times
                    }
                }
            },
            upsert=True
        )

    async def get_performance_metrics(self, ai_id: str) -> Dict[str, Any]:
        metrics = await self.collection.find_one({'ai_id': ai_id})
        if metrics:
            avg_execution_time = sum(metrics['execution_times']) / len(metrics['execution_times'])
            success_rate = metrics['successful_executions'] / metrics['total_executions']
            return {
                'average_execution_time': avg_execution_time,
                'success_rate': success_rate,
                'total_executions': metrics['total_executions']
            }
        return {}

performance_tracker = PerformanceTracker()