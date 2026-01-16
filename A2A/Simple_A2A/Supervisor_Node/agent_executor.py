from a2a.server.agent_execution import AgentExecutor , RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    TaskStatus,
    TaskState
) 
from agent.agent import SupervisorAgent


class SupervisorAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent=SupervisorAgent()

    async def execute(self,context:RequestContext,event_queue:EventQueue):
        
        user_query=context.get_user_input()


