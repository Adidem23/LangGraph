from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from dotenv import load_dotenv
from google.genai import types

load_dotenv()

class SupervisorAgent:
    def __init__(self):
        self.agent=Agent(
            name="Supervisor_Agent",
            model="gemini-2.0-flash",
            instruction=("You are a supervisor agent.\n"
                "Decide which agent should handle the user query.\n"
                "Respond with ONLY one word:\n"
                "- query\n"
                "- math")
        )

    async def decide(self,query:str)->str:

        session_Service=InMemorySessionService()

        await session_Service.create_session(
        app_name="Supervisor_Agent",
        user_id="user1",
        session_id="session1"
        )

        runner=Runner(
            app_name="Supervisor_Agent",
            agent=self.agent,
            session_service=session_Service,
        )

        user_message = types.Content(
        role="user",
        parts=[types.Part(text=query)]
       )

        async for event in runner.run_async(
            user_id="user1",
            session_id="session1",
            new_message=user_message
        ):
            if event.is_final_response():
               return event.content.parts[0].text

