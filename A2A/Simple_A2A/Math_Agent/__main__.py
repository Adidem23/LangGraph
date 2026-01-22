from a2a.server.apps import A2AStarletteApplication
from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities
)
from a2a.server.request_handlers import DefaultRequestHandler
from agent_executor import MathAgentExecutor
from a2a.server.tasks import InMemoryTaskStore
import uvicorn 

if __name__=="__main__":

    agent_skill=AgentSkill(
        id="Math_agent",
        name="Math_agent",
        description="Math_agent",
        tags=['Math','Sum','Addition'],
        examples=['hi','how are you ?']
    )

    agent_card=AgentCard(
        name="Math_agent",
        description="Math_agent",
        url="http://localhost:8006",
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=['text'],
        default_output_modes=['text'],
        skills=[agent_skill]
    )

    request_handler=DefaultRequestHandler(
        agent_executor=MathAgentExecutor(),
        task_store=InMemoryTaskStore()
    )

    app=A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card
    )

    uvicorn.run(app.build(),host='0.0.0.0',port=8006)