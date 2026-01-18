from a2a.server.agent_execution import AgentExecutor , RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    TaskStatus,
    TaskState
) 
from a2a.utils import new_text_artifact
from agent.agent import SupervisorAgent
from client_class import Agent_Client_Class

class SupervisorAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent=SupervisorAgent()
        self.client=Agent_Client_Class()

    async def execute(self,context:RequestContext,event_queue:EventQueue):
        
        user_query=context.get_user_input()

        decision=await self.agent.decide(user_query)

        QUERY_BOT_URL="http://localhost:8005"

        if decision=="query":
            response=await self.client.create_connection(QUERY_BOT_URL,user_query)

        else:
            response={
                "text":"math"
            }
            return response
        
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                context_id=context.context_id,
                task_id=context.task_id,
                artifact=new_text_artifact(
                    "final_answer",
                    str(response)
                ),
            )
        )

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                context_id=context.context_id,
                task_id=context.task_id,
                status=TaskStatus(state=TaskState.completed),
                final=True,
            )
        )
    
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')