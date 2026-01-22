import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import (
    HumanMessage,
    SystemMessage,
    AnyMessage
)
import operator
from pydantic import BaseModel
from typing_extensions import Annotated , Optional , TypedDict
from langgraph.graph import START , StateGraph , END
from langgraph.types import Command

load_dotenv()

GOOGLE_GEMINI_API_KEY=os.getenv("GOOGLE_GEMINI_API_KEY","")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_GEMINI_API_KEY,
    temperature=0,
)

class itemsParsingClass(BaseModel):
    items:list[str] | None
    Quantity: list[int] | None

class AgentState(TypedDict):
    user_msg:str | None
    messages:Annotated[list[AnyMessage],operator.add]
    items: list[str] | None
    quantity:list[int] | None
    llm_calls: int | None

def parseItems(state:AgentState):
    
    parser=llm.with_structured_output(itemsParsingClass)

    user_query=state['messages'][-1].content

    result=parser.invoke(
        f"""
        You have to parse the items and their quantity from below the user query
        :{user_query} 
        """
    )

    print(result)

    return Command(update={"user_msg":user_query,"items":result.items,"quantity":result.Quantity,"llm_calls":state.get("llm_calls", 0) + 1},goto=END)



builder_graph=StateGraph(AgentState)

builder_graph.add_node("parseItems",parseItems)

builder_graph.add_edge(START,"parseItems")

graph=builder_graph.compile()

if __name__=="__main__":
    user_query=input("Enter Your Items : ")
    result=graph.invoke({"messages":[HumanMessage(content=f'{user_query}')]})
    print(result)