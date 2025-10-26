from google.genai.types import FunctionDeclaration, Schema

print_name_function = FunctionDeclaration(
    name="print_name",
    description="Print a name to the console ONLY when the user explicitly asks to print, display, or show their name. Do not call this for simple introductions or greetings.",
    parameters= Schema(
        type="object",
        properties={
            'name' : Schema(
                type='string',
                description='The name to be printed',
            ),
        },
        required=["name"],
    ),
)

get_ticket_price_function = FunctionDeclaration(
    name="get_ticket_price",
    description="Retrieve the ticket price for the given city only if needed.",
    parameters= Schema(
        type="object",
        properties={
            'location' : Schema(
                type='string',
                description='The name of the city to retrieve the ticket price for.',
            ),
        },
        required=["location"],
    ),
)