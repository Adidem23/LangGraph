"""
Simple LangGraph agent that decides whether to call a tool
or reply normally based on explicit intent classification
"""

import os
import time
import operator
import pyautogui as auto
from dotenv import load_dotenv
from typing import Literal
from typing_extensions import TypedDict, Annotated

from pydantic import BaseModel
from langchain.tools import tool
from langchain.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
    AnyMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph, END
from langgraph.types import Command

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_GEMINI_API_KEY"),
    temperature=0,
)

@tool
def open_calculator():
    """
    This function is used to open calculator of the user 
    """
    auto.press("win")
    time.sleep(0.3)
    auto.write("calculator")
    auto.press("enter")
    
    return "Calculator opened successfully"

llm_with_tools = llm.bind_tools([open_calculator])

class IntentSchema(BaseModel):
    user_intent: Literal["tool_call", "not_tool_call"]

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    intent: str | None
    llm_calls: int

def classifier(state: AgentState):
    classifier_llm = llm.with_structured_output(IntentSchema)
    user_text = state["messages"][-1].content

    result = classifier_llm.invoke(
        f"""
Decide whether the user wants to perform a system action
like opening an application.

User query: "{user_text}"

Return only:
- tool_call
- not_tool_call
"""
    )

    return Command(
        update={
            "intent": result.user_intent,
            "llm_calls": state.get("llm_calls", 0) + 1,
        },
        goto="llm_with_tools_node"
        if result.user_intent == "tool_call"
        else "normal_llm_call",
    )

def llm_with_tools_node(state: AgentState):
    msg = llm_with_tools.invoke(
        [
            SystemMessage(
                content="Call tools only if the user explicitly asks for an action."
            ),
            *state["messages"],
        ]
    )

    if msg.tool_calls:
        return Command(
            update={"messages": [msg]},
            goto="tool_node",
        )

    return Command(
        update={"messages": [msg]},
        goto=END,
    )

def tool_node(state: AgentState):
    tool_outputs = []

    for tc in state["messages"][-1].tool_calls:
        result = open_calculator.invoke(tc["args"])

        tool_outputs.append(
            ToolMessage(
                content=result,
                tool_call_id=tc["id"]
            )
        )

    return Command(
        update={"messages": tool_outputs},
        goto=END,
    )

def normal_llm_call(state: AgentState):
    msg = llm.invoke(
        [
            SystemMessage(content="Reply normally to the user."),
            *state["messages"],
        ]
    )

    return Command(
        update={"messages": [msg]},
        goto=END,
    )

builder = StateGraph(AgentState)

builder.add_node("classifier", classifier)
builder.add_node("llm_with_tools_node", llm_with_tools_node)
builder.add_node("tool_node", tool_node)
builder.add_node("normal_llm_call", normal_llm_call)

builder.add_edge(START, "classifier")

agent = builder.compile()

initial_state = {
    "messages": [HumanMessage(content="Heyy just wanted to do a quick calculations about something so can u open calculator app for me ")],
    "intent": None,
    "llm_calls": 0,
}

result = agent.invoke(initial_state)

for msg in result["messages"]:
    msg.pretty_print()