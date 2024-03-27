# Standard library imports
import logging
import os
import sys

# Third-party imports
from fastapi import FastAPI, HTTPException
from vocode.streaming.models.telephony import TwilioConfig
#from pyngrok import ngrok
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.telephony.server.base import (
    TwilioInboundCallConfig,
    TelephonyServer,
)
from dotenv import load_dotenv
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig
from pydantic import BaseModel
from outbound_call_rest import make_outbound_call


# Local application/library specific imports
from speller_agent import (
    SpellerAgentFactory,
    SpellerAgentConfig,
)

# if running from python, this will load the local .env
# docker-compose will load the .env file by itself
load_dotenv()

app = FastAPI(title="voice.voxtell.ai",summary="Voxtel's favorite app.",version="0.0.1")


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config_manager = RedisConfigManager(
    logger=logger,
)

BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    raise ValueError("BASE_URL must be set in environment if not using pyngrok")

telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Thank you for calling Voxtell. This is Eva  speaking. How can I assist you today?"),
                prompt_preamble="Have a pleasant conversation about life",
                generate_responses=True,
            ),
            synthesizer_config=AzureSynthesizerConfig.from_telephone_output_device(voice_name="en-US-BlueNeural"),
            # uncomment this to use the speller agent instead
            # agent_config=SpellerAgentConfig(
            #     initial_message=BaseMessage(text="im a speller agent, say something to me and ill spell it out for you"),
            #     generate_responses=False,
            # ),
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
            ),
            logger=logger,
        )
    ],
    agent_factory=SpellerAgentFactory(),
    logger=logger,
)


class Item(BaseModel):
    phone: str
    initial_message: str
    prompt: str


@app.post("/start-call")
async def start_call(contact: Item):
    try:
        await make_outbound_call(contact)
        return {"status": "Call started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(telephony_server.get_router())
