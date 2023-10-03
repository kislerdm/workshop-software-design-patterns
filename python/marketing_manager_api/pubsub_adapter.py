import json

from .models import EventCampaignRequested, EventCampaignStopped
from .pubsub import PubSubClient


class Adaptee:
    def publish_campaign_status_update(self, topic: str, data: EventCampaignRequested | EventCampaignStopped) -> None:
        pass


class PubSubClientAdapter(PubSubClient, Adaptee):
    def publish_campaign_status_update(self, topic: str, data: EventCampaignRequested | EventCampaignStopped) -> None:
        """Publishes campaign status update to a specific topic.

        Args:
            topic: Topic to publish.
            data: Event record.
        """
        self.publish(topic, json.dumps(data).encode("utf-8"))
