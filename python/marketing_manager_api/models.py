from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class CampaignUserRequest(BaseModel):
    name: str
    budget: int
    roi: float
    date_start: datetime
    date_end: datetime


class CampaignStatus(str, Enum):
    scheduled = "SCHEDULED"
    running = "RUNNING"
    stopped = "STOPPED"


class CampaignUserResponse(BaseModel):
    campaign_id: UUID
    timestamp: datetime
    campaign_status: CampaignStatus


class EventCampaignRequested(BaseModel):
    uuid: UUID
    timestamp: datetime
    campaign_id: UUID
    user_definition: CampaignUserRequest


class EventCampaignStopped(BaseModel):
    uuid: UUID
    timestamp: datetime
    campaign_id: UUID
