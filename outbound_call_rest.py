# outbound.py

import os
from dotenv import load_dotenv
from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage

load_dotenv()
BASE_URL = os.environ["BASE_URL"]

async def make_outbound_call(contact):
    config_manager = RedisConfigManager()
    outbound_call = OutboundCall(
        base_url=BASE_URL,
        to_phone=contact.phone,
        mobile_only=False,
        from_phone="13213206916",
        config_manager=config_manager,
        agent_config=ChatGPTAgentConfig(
            initial_message=BaseMessage(text=contact.initial_message),
            prompt_preamble=contact.prompt,
            generate_responses=True,
        ),
    )

    await outbound_call.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(make_outbound_call())
