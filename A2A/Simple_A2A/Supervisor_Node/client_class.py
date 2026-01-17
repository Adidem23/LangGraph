import asyncio
import httpx
from a2a.client import (
    A2ACardResolver,
    ClientConfig,
    ClientFactory,
    create_text_message_object
)

from a2a.types import TransportProtocol
from a2a.utils.message import get_message_text


class Agent_Client:

    async def create_connection(url:str,user_input:str):

        async with httpx.AsyncClient() as httpx_client:
            
            resolver=A2ACardResolver(
                httpx_client=httpx_client,
                base_url=url
            )

            try:
           
                agent_card = await resolver.get_agent_card()

                config = ClientConfig(
                    httpx_client=httpx_client,
                    supported_transports=[
                        TransportProtocol.jsonrpc,
                        TransportProtocol.http_json,
                    ],
                    streaming=agent_card.capabilities.streaming,
                )

                client = ClientFactory(config).create(agent_card)

                try:
                    request = create_text_message_object(content=user_input)

                    async for response in client.send_message(request):
                        task, _ = response
                        return get_message_text(task.artifacts[-1])

                except Exception as e:
                    print(f'An error occurred: {e}')


            except Exception as e:
                print(f'Error initializing client: {e}')

    

            
