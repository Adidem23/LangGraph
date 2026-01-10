# ============================================================
# 0️⃣ API KEY (MUST BE AT VERY TOP)
# ============================================================
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# 1️⃣ Imports
# ============================================================
import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# ============================================================
# 2️⃣ Worker Agents (Specialists)
# ============================================================

# --- Greeting Agent ---
greeting_agent = Agent(
    name="greeting_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a greeting agent. "
        "You ONLY respond to greetings like hi, hello, hey. "
        "Keep responses short and friendly."
    )
)

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


# --- Weather Agent ---
weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a weather agent. "
        "Answer questions about weather in cities. "
        "If the city is unknown, say you don't have data."
    ),
    tools=[get_weather]
)

# ============================================================
# 3️⃣ Orchestrator Agent (Manager)
# ============================================================

orchestrator_agent = Agent(
    name="orchestrator_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are an orchestrator agent.\n"
        "Your job is to decide which sub-agent should handle the request"
        "Rules:\n"
        "- If the user greets, delegate to greeting_agent.\n"
        "- If the user asks about weather, delegate to weather_agent.\n"
        "-Tell user which subagent was used and why"
        "- You may delegate to multiple agents if needed.\n"
        "- Combine all sub-agent responses into ONE final response.\n"
        "- Only YOU talk to the user.\n"
    ),
    sub_agents=[greeting_agent, weather_agent]
)

# ============================================================
# 4️⃣ Session Service + Runner
# ============================================================

session_service = InMemorySessionService()

runner = Runner(
    agent=orchestrator_agent,
    app_name="agent_team_app",
    session_service=session_service
)

# ============================================================
# 5️⃣ Run Function (NO CLI)
# ============================================================

async def run():
    # Create session
    await session_service.create_session(
        app_name="agent_team_app",
        user_id="user1",
        session_id="session1"
    )

    # User input
    user_message = types.Content(
        role="user",
        parts=[types.Part(text="Hi")]
    )

    # Run agent team
    async for event in runner.run_async(
        user_id="user1",
        session_id="session1",
        new_message=user_message
    ):
        if event.is_final_response():
            print("\n================ FINAL RESPONSE ================\n")
            print(event.content)
            # print(event.content.parts[0].text)
            print("\n================================================\n")
            break

# ============================================================
# 6️⃣ Entry Point
# ============================================================

if __name__ == "__main__":
    asyncio.run(run())
