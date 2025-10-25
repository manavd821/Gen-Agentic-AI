import requests
import gradio as gr
from decouple import config

API_KEY = config("OPEN_ROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/models"

def fetch_tool_models():
    if not API_KEY:
        return "❌ ERROR: Set OPENROUTER_API_KEY first."

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(BASE_URL, headers=headers)
        data = response.json()

        free_tool_models = []
        for model in data.get("data", []):
            pricing = model.get("pricing", {}).get("prompt", "paid")
            caps = model.get("capabilities", {})

            supports_tools = caps.get("tools", False) or caps.get("function_calling", False)

            if pricing == "free" and supports_tools:
                free_tool_models.append(model["id"])

        if not free_tool_models:
            return "⚠️ No free tool-calling models found."

        return "\n".join(free_tool_models)

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def run_search():
    return fetch_tool_models()

# Gradio UI
ui = gr.Interface(
    fn=run_search,
    inputs=None,
    outputs="text",
    title="Free Tool-Calling Models on OpenRouter",
    description="Click the button to fetch list of models."
)

if __name__ == "__main__":
    ui.launch()
