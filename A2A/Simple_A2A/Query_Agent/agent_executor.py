from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    TaskStatus,
    TaskState
)
from a2a.utils import new_text_artifact
from query_agent.agent import QueryAgent

class queryAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent=QueryAgent()

    async def execute(self, context:RequestContext, event_queue:EventQueue):

        user_query= context.get_user_input()

        llm_output=await self.agent.resolveUserQuery(user_query)

        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                context_id=context.context_id,
                task_id=context.task_id,
                artifact=new_text_artifact(
                    "Query_agent_answer",
                    llm_output
                )

            )
        )

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                context_id=context.context_id,
                task_id=context.context_id,
                status=TaskStatus(state=TaskState.completed),
                final=True
            )
        )

    async def cancel(self, context, event_queue):
        raise Exception('Error Processing Request')
        