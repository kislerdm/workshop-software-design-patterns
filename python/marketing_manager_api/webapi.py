"""This module illustrates the Factory pattern."""
import logging
from datetime import datetime
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException

from .errors import (
    ExceptionDatabaseAdapter,
    ExceptionSourcingPlatformAdapter,
)
from .pubsub import ExceptionPubSubAdapter
from .models import (
    CampaignStatus,
    CampaignUserRequest,
    CampaignUserResponse,
    EventCampaignRequested,
    EventCampaignStopped,
)

_log = logging.Logger(__name__)

app = FastAPI()


@app.post("/campaign/start")
async def start(req: CampaignUserRequest) -> CampaignUserResponse | HTTPException:
    """Starts the campaign"""
    campaign_id = uuid4()
    now = datetime.utcnow()

    req_campaign_requested = EventCampaignRequested(
        uuid=uuid4(),
        timestamp=now,
        campaign_id=campaign_id,
        user_definition=req,
    )

    with dbClient() as sess:
        sess.write_campaign_requested(req_campaign_requested)

        try:
            pubsubClient.publish_campaign_status_update("com.maas.api.Campaign", req_campaign_requested)
        except Exception as ex:
            _log.error("pubsub error: %s" % ex)
            return HTTPException(status_code=500, detail="server error")

    return CampaignUserResponse(campaign_id=campaign_id, timestamp=now, campaign_status=CampaignStatus.scheduled)


@app.put("/campaign/{campaign_id}/stop")
async def stop(campaign_id: UUID) -> CampaignUserResponse | HTTPException:
    """Stops the campaign."""
    now = datetime.utcnow()
    new_status = CampaignStatus.stopped

    with dbClient() as sess:
        try:
            platform_campaign_id = sess.read_platform_campaing_id(campaign_id)

            sourcingPlatformClient.stop(platform_campaign_id)

            sess.update_campaign_status(campaign_id, now, new_status)

            pubsubClient.publish_campaign_status_update(
                "com.maas.api.Campaign", EventCampaignStopped(uuid=uuid4(), timestamp=now, campaign_id=campaign_id)
            )
        except ExceptionDatabaseAdapter as ex:
            _log.error("database client error: %s" % ex)
            return HTTPException(status_code=500, detail="server error")
        except ExceptionSourcingPlatformAdapter as ex:
            _log.error("sourcing platform client error: %s" % ex)
            return HTTPException(status_code=500, detail="server error")
        except ExceptionPubSubAdapter as ex:
            _log.error("pubsub client error: %s" % ex)
            return HTTPException(status_code=500, detail="server error")

    return CampaignUserResponse(campaign_id=campaign_id, timestamp=now, campaign_status=new_status)
