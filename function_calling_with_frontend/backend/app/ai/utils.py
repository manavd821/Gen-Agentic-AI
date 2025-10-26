import asyncio
from typing import AsyncGenerator
from google.genai.client import AsyncClient
from google.genai.chats import AsyncChat
from google.genai.types import GenerateContentConfig, Part, FunctionResponse
from app.ai import inject_client, tools
from app.ai import print_name, get_ticket_price
from pathlib import Path
# types.tool
system_instructions = """
You are a helpful assistant.
Give detail, courteous answers.
Always be accurate. If you don't know the answer, say so.
if you use any tool, don't tell it to user.
"""
def execute_function(function_name : str, args : dict):
    if function_name == 'print_name':
        result= print_name(**args)
        return result
    if function_name == 'get_ticket_price':
        result = get_ticket_price(**args)
        return result

    return {"error": f"Unknown function: {function_name}"}

async def handle_function_call(chat : AsyncChat, function_calls : list[dict[str, any]]):
    print(f"Executing {len(function_calls)} function(s)...\n")
    for fn in function_calls:
        print(f"Calling: {fn["name"]}\n")
        print(f"Args: {fn["args"]}\n")
        
        result = execute_function(fn["name"], fn["args"])
        print(f"✅ Result: {result}\n")
        try:
            response = await chat.send_message_stream(
                Part(function_response=FunctionResponse(
                        name=fn["name"],
                        response=result,
                    )
                )
            )
            async for chunk in response:
                # print(chunk.text, end = '', flush=True)
                if chunk.candidates:  # ✅ Check candidates
                    for part in chunk.candidates[0].content.parts:
                        if hasattr(part, 'text') and part.text:
                            yield part.text  # ✅ Yield text parts
            # print()
        except Exception as e:
            print("Error in processing info: ",{e})
            yield f"[Error: {e}]"

async def process_message(chat : AsyncChat, user_input : str) -> AsyncGenerator[str, None]:
    """Process a message and handle function calls."""
    response = await chat.send_message_stream(user_input)
    text_parts = []
    function_calls = []
    async for chunk in response:
        try:
            if not chunk.candidates:
                continue
            for part in chunk.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls.append({
                        'name' : part.function_call.name,
                        'args' : dict(part.function_call.args),
                    })
                if hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
                    # print(part.text, end='', flush=True)  
                    yield part.text
        except Exception as e:
            print(f"Error: {e}")
            yield f"[Error: {e}]"
            
    if function_calls:
        async for followed_up_text in handle_function_call(chat, function_calls):
            yield followed_up_text
    # if text_parts:
    #     print()

@inject_client
async def call_llm(client : AsyncClient, user_input : str) :
    
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=GenerateContentConfig(
            system_instruction=system_instructions,
            tools=[tools],
        )
    )
    async for text_chunk in process_message(chat, user_input):
        yield text_chunk