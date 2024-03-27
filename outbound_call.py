import os
from dotenv import load_dotenv

load_dotenv()

from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)

from speller_agent import SpellerAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.agent import ChatGPTAgentConfig

BASE_URL = os.environ["BASE_URL"]


async def main():
    config_manager = RedisConfigManager()

    outbound_call = OutboundCall(
        base_url=BASE_URL,
        to_phone="14077394215",
	mobile_only=False,
        from_phone="13213206916",
        config_manager=config_manager,
        #agent_config=SpellerAgentConfig(generate_responses=True),
	agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hey Debora, I have a message for you, Gabriel loves you very much."),
                prompt_preamble="Have a pleasant conversation about life",
                generate_responses=True,
            ),
    )

    input("Press enter to start call...")
    await outbound_call.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
