from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class QueryAgent:

    def __init__(self):
        self.agent=Agent(
            name="Query_agent",
            description="This is a simple Query Resolution Agent",
            model="gemini-2.5-flash",
            instruction=("""You are a Query Resolution Agent.

Your role is to handle GENERAL, NON-MATHEMATICAL user queries.

You must:
- Answer questions clearly, concisely, and accurately.
- Provide explanations, summaries, definitions, or guidance when asked.
- Ask clarifying questions ONLY if the query is ambiguous.
- Stay factual and avoid hallucinations.

You must NOT:
- Perform arithmetic, calculations, or mathematical reasoning.
- Solve equations, formulas, or numerical problems.
- Delegate tasks or mention other agents.

If the user query is mathematical or requires calculations, respond with:
"Cannot resolve. This query requires mathematical processing."

Otherwise, provide the best possible direct answer.

Always respond in plain text.
""")
        )

    async def resolveUserQuery(self,query:str)->str:

        sessionService=InMemorySessionService()

        await sessionService.create_session(
            app_name="Query_agent",
            user_id="user2",
            session_id="session2",
        )

        runner=Runner(
            app_name="Query_agent",
            agent=self.agent,
            session_service=sessionService,
        )

        user_message=types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )

        async for event in runner.run_async(
            user_id="user2",
            session_id="session2",
            new_message=user_message
        ):
            
            if event.is_final_response():
                return event.content.parts[0].text
            
