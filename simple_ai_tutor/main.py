from os import system
from decouple import config
from google import genai
from google.genai import types

GOOGLE_API_KEY = config("GOOGLE_API_KEY")
GOOGLE_GEMINI_MODEL1 = config("GOOGLE_GEMINI_MODEL1")
GOOGLE_GEMINI_MODEL2 = config("GOOGLE_GEMINI_MODEL2")

client = genai.Client(
    api_key = GOOGLE_API_KEY
)
llm = client.chats.create(model=GOOGLE_GEMINI_MODEL1)
system_prompt = "You are a helpful and knowledgeable teaching assistant. \
Your goal is to clearly explain the concept asked by the user in a simple, structured, and engaging way. \
"
History= []
while True:
    user_input = (str(input("Ask question: "))).strip()
    if(user_input == '-1'):
        break
    res = llm.send_message(
        message=user_input,
        config={
            "system_instruction" : system_prompt
        }
    )
    print(f"\n{res.text}", end='\n\n')

for msg in llm.get_history():
    print(f'role : {msg.role}')
    print(f'msg : {msg.parts[0].text}')
    