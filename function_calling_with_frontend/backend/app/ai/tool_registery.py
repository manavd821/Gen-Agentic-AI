from google.genai.types import Tool
from app.ai import (
    print_name_function,
    get_ticket_price_function,
)
tools = Tool(
    function_declarations=[
        print_name_function,
        get_ticket_price_function,
    ]
)
