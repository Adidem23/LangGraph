import os 
import operator
from dotenv import load_dotenv
from langchain.messages import SystemMessage,AnyMessage , ToolMessage
from langgraph.graph import START, END , StateGraph
from typing_extensions import TypedDict , Annotated
from typing import Literal
from langchain.tools import tool
from langchain.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GOOGLE_GEMINI_API_KEY=os.getenv("GOOGLE_GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",         
    google_api_key=GOOGLE_GEMINI_API_KEY,
    temperature=0.7
)


class MessagesState(TypedDict):
    messages:Annotated[list[AnyMessage],operator.add]
    llm_calls:int

@tool
def callWeatherAPI():
    """
    Weather API calling 

    """

    return {"Message":"Response From An API Endpoint is simulated successfully"}


tools = [callWeatherAPI]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = llm.bind_tools(tools)

from langchain.messages import SystemMessage


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END


def llm_call(state: dict):

    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful weather assistant which calls weather apis"
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }


def tool_node(state: dict):
    
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

agent=agent_builder.compile()

from langchain.messages import HumanMessage
messages = [HumanMessage(content="Call Weather API")]
messages = agent.invoke({"messages": messages})
print(messages)
for m in messages["messages"]:
    m.pretty_print()