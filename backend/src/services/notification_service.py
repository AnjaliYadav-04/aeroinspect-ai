import json
from typing import List
from config import settings
import redis

class NotificationService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def publish_inspection_update(self, inspection_id: str, message: dict):
        self.redis_client.publish(f"inspection:{inspection_id}", json.dumps(message))

    async def publish_detection_alert(self, detection: dict):
        if detection.get("severity") in ["critical", "high"]:
            self.redis_client.publish("alerts:critical", json.dumps(detection))

    async def get_recent_alerts(self, limit: int = 50) -> List[dict]:
        alerts = self.redis_client.lrange("alerts:recent", 0, limit - 1)
        return [json.loads(a) for a in alerts]

notification_service = NotificationService()
