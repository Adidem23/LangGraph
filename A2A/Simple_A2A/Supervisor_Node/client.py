from client_class import Agent_Client_Class
import asyncio

def print_welcome_message() -> None:
    print('Welcome to the generic A2A client!')
    print("Please enter your query (type 'exit' to quit):")


def get_user_query() -> str:
    return input('\n> ')


async def main(BASE_URL,user_query):   
    client=Agent_Client_Class()

    response=await client.create_connection(BASE_URL,user_query)

    return {"text":str(response)}


if __name__=="__main__":

    print_welcome_message()

    user_input = get_user_query()

    SUPERVISOR_NODE_BASE_URL="http://localhost:8004"

    fun_response=asyncio.run(main(SUPERVISOR_NODE_BASE_URL,user_input))

    print(fun_response)