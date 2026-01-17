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
import httpx

class SupervisorAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent=SupervisorAgent()

    async def execute(self,context:RequestContext,event_queue:EventQueue):
        
        user_query=context.get_user_input()

        decision=await self.agent.decide(user_query)

        QUERY_BOT_URL="http://localhost:8005"

        if decision=="query":
            async with httpx.AsyncClient(timeout=None) as httpxclient:
                response=await httpxclient.post(QUERY_BOT_URL,json={"input":user_query})

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
                    response.text,
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