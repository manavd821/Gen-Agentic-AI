from decouple import config
import gradio as gr
from openai import OpenAI
from huggingface_hub import ChatCompletionOutputMessage

OPEN_ROUTER_API_KEY = config("OPEN_ROUTER_API_KEY")
GOOGLE_API_KEY = config("GOOGLE_API_KEY")
GOOGLE_GEMINI_MODEL1 = config("GOOGLE_GEMINI_MODEL1")
google_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
openrouter_base_url = "https://openrouter.ai/api/v1"

client = OpenAI(
  base_url=google_base_url,
  api_key=GOOGLE_API_KEY,
)

system_prompt = """
You are a helpful assistant for an Airline called FlightAI.
Give short, courteous answers, no more than one sentence.
Always be accurate. If you don't know the answer, say so.
"""
price_function = {
    "name" : "get_ticket_price",
    "description" : "Get the price of a return ticket to the destination city.",
    "parameters": {
        "type" : "object",
        "properties" : {
            "destination_city" : {
                "type" : "string",
                "description" : "The city that the customer wants to travel to",
            },
        },
        "required" : ["destination_city"],
        "additionalProperties": False
    },
}
tools = [{
    "type" : "function",
    "function" : price_function
}]

messages = [{'role' : 'system', 'content' : system_prompt}]

def call_llm(message):
    messages.append({'role' : 'user', 'content' : message})
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=messages,
        tools=tools,
        tool_choice="auto"
)
    output = response.choices[0].message.content
    messages.append({'role' : 'assistant', 'content' : output})
    print(f"{output=}")
    print(f"{response.choices[0].finish_reason=}")
    if response.choices[0].finish_reason == 'tool_calls':
        print(f"{response.choices[0].message.tool_calls[0].function=}")
        print(f"{response.choices[0].message.tool_calls[0].function.name=}")
        # print(f"{response.choices[0].message.tool_calls[0].function.arguments=}")
        args = response.choices[0].message.tool_calls[0].function.arguments
        print(f"{args=}")
        print(f"{type(args)=}")
        import json
        args = json.loads(args)
        print(f"{args=}")
        print(f"{type(args)=}")
        
call_llm("hello")    
call_llm("I want to go London") 


def handle_tool_calling(message : ChatCompletionOutputMessage):
    matched_tools = []
    for llm_tool in message.tool_calls:
        matched_tool = next(tool for tool in tools if tool.get('function',{}).get('name') == llm_tool.function.name) or None
        if matched_tool:
            matched_tools.append(matched_tool) 
    print(matched_tools.__len__())
    print(matched_tools)
    
    
messages = [{'role' : 'system', 'content' : system_prompt}]
def call_llm(message):
    messages.append({'role' : 'user', 'content' : message})
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    output = response.choices[0].message.content
    if output:
        messages.append({'role' : 'assistant', 'content' : output})
        print(f"{output=}")
    if response.choices[0].finish_reason == 'tool_calls':
        message = response.choices[0].message
        response = handle_tool_calling(message)
        messages.append(response)
        print(messages)
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        output = response.choices[0].message.content
        print(output)
    
call_llm("hello")    
call_llm("I want to go London.")  