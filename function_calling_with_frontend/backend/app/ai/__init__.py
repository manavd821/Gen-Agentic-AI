from app.ai.dependencies import (
    inject_client,
    
)
from app.ai.functions import (
    print_name,
    get_ticket_price
)
from app.ai.tools import (
    print_name_function,
    get_ticket_price_function,
)
from app.ai.tool_registery import tools

from app.ai.utils import call_llm