from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication
from a2a.types import (
    AgentCapabilities,
    AgentSkill,
    AgentCard
)
from agent_executor import queryAgentExecutor

import uvicorn


if __name__=="__main__":

    agent_skill=AgentSkill(
        id="Normal_query_agent",
        name="Normal_query_agent",
        description="This is a normal query Agent",
        tags=['normal','simple'],
        examples=['hi','how are you?']
    )


    agent_card=AgentCard(
        name="Normal_query_agent",
        description="This is a normal query Agent",
        url="http://localhost:8005",
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=['text'],
        default_output_modes=['text'],
        skills=[agent_skill]
    )


    request_handler=DefaultRequestHandler(
        agent_executor=queryAgentExecutor(),
        task_store=InMemoryTaskStore()
    )

    app=A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card
    )

    uvicorn.run(app.build(),host='0.0.0.0',port=8005)