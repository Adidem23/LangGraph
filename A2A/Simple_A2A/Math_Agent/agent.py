import os
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import SystemMessage, ToolMessage, AnyMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing_extensions import TypedDict , Annotated
import operator
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

GOOGLE_GEMINI_API_KEY=os.getenv("GOOGLE_GEMINI_API_KEY","")


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_GEMINI_API_KEY,
    temperature=0.7,
)

class AgentState(TypedDict):
    query: str
    messages: Annotated[list[AnyMessage],operator.add]
    llm_calls: int
    output: str | None


async def process_user_request(state: AgentState):
    """
    LLM node:
    - Decides whether to call a tool
    - Or produces final answer
    """

    server_script_path = "./MCP/server.py"
    command = "python"
        
    server_params = StdioServerParameters(
                command=command,
                args=[server_script_path],
                env=None
        )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools=await load_mcp_tools(session)

        llm_with_tools = llm.bind_tools(tools)

        messages = state['messages']

        result = await llm_with_tools.ainvoke([
            SystemMessage(content=f"""
                        You are a helpful assiatant which process mathematical queries of user : {state['query']} and calls appropiate tools when ever required
            """),
            *state['messages']
        ])

        if result.tool_calls:
            return Command(
                update={
                    "messages": messages + [result],
                    "llm_calls": state.get("llm_calls", 0) + 1,
                },
                goto="tool_node",
            )

        return Command(
            update={
                "messages": messages + [result],
                "llm_calls": state.get("llm_calls", 0) + 1,
                "output": result.content,
            },
            goto=END,
        )


async def tool_node(state: AgentState):
    """
    Executes MCP tools and sends result back to LLM
    """

    server_script_path = "./MCP/server.py"
    command = "python"
        
    server_params = StdioServerParameters(
                command=command,
                args=[server_script_path],
                env=None
        )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            tools=await load_mcp_tools(session)

            tools_by_name = {tool.name: tool for tool in tools}

            last_message= state["messages"][-1]
            tool_messages = []

            for tool_call in last_message.tool_calls:
                tool = tools_by_name[tool_call["name"]]
                observation =await tool.ainvoke(tool_call["args"])

                tool_messages.append(
                    ToolMessage(
                        content=str(observation),
                        tool_call_id=tool_call["id"],
                    )
                )

            return Command(
                update={
                    "messages": state["messages"] + tool_messages,
                    "llm_calls": state.get("llm_calls", 0) + 1,
                },
                goto=END,
            )

builder = StateGraph(AgentState)

builder.add_node("process_user_request", process_user_request)
builder.add_node("tool_node", tool_node)

builder.add_edge(START, "process_user_request")

math_agent = builder.compile()

# async def runMain(user_query):

#     messages=[HumanMessage(content=f'{user_query}')]

#     result = await math_agent.ainvoke(
#     {
#         "query": f'{user_query}',
#         "messages":messages
#     }
#     )
    
#     print(result)


# if __name__=="__main__":
#     user_query=input("Enter: ")
#     asyncio.run(runMain(user_query))
