from mcp.server.fastmcp import FastMCP

mcp=FastMCP("MATH_AI_AGENT_SERVER")

@mcp.tool
def addition(num1:int,num2:int)->int:
    """Tool for Adding Two Numbers"""
    result=num1+num2
    return result


@mcp.tool
def subtract(num1:int,num2:int)->int:
    """Tool for Substracting Two Numbers"""
    result=num1-num2
    return result

@mcp.tool
def multiply(num1:int,num2:int)->int:
    """"Tool for Multiplying Two Numbers"""
    result=num1*num2
    return result

@mcp.tool
def division(num1:int,num2:int)->int:
    """Tool for Divisio of Two numbers """
    result=num1/num2
    return result


if __name__=="__main__":
    mcp.run(transport="stdio")