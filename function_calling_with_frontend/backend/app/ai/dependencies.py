import asyncio
from functools import wraps
from typing import AsyncGenerator, Callable, Coroutine, Optional
from google import genai
from contextlib import asynccontextmanager
from google.genai.client import AsyncClient
from google.genai.chats import AsyncChat
from google.genai.types import GenerateContentConfigOrDict,ContentOrDict
from decouple import config
import inspect

GOOGLE_API_KEY = config("GOOGLE_API_KEY")
@asynccontextmanager
async def get_client(api_key : str) -> AsyncGenerator:
    client = genai.Client(
        api_key=api_key
    ).aio
    try:
        yield client
    finally:
        await client.aclose()
        
def inject_client(func : Callable) -> Callable:
    """
        Decorator that automatically inject GenAI client
        The decorator function should have client as it's first argument.
        The decoratored function must be async generator.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with get_client(api_key=GOOGLE_API_KEY) as client:
            async for item in func(client, *args, **kwargs):
                yield item
    return wrapper
