from decouple import config
from google import genai
from google.genai import types
from pydantic import BaseModel
import aiohttp
import asyncio
import streamlit as st
from bs4 import BeautifulSoup
from readability import Document

GOOGLE_API_KEY = config("GOOGLE_API_KEY")
GOOGLE_CLOUD_PROJECT = config("GOOGLE_CLOUD_PROJECT")

client = genai.Client(
    api_key=GOOGLE_API_KEY,
)

def get_gemini_summary(user_prompt : str, system_prompt : str):
    response = client.models.generate_content(
        model = "gemini-2.5-pro",
        config= types.GenerateContentConfig(
            system_instruction=system_prompt
        ),
        contents=user_prompt
    )
    return response.text

class Website(BaseModel):
    url: str

    async def get_content(self, session: aiohttp.ClientSession):
        try:
            res = await session.get(self.url.strip())
            content = await res.text()
            return res.status, content
        except Exception as e:
            return None, None, f"Error: {e}"

# Synchronous wrapper for Streamlit
def fetch_html(url):
    async def _inner():
        async with aiohttp.ClientSession() as session:  # create session manually
            site = Website(url=url)
            return await site.get_content(session)

    return asyncio.run(_inner())

def make_user_prompt(title : str, content : str):
    user_prompt = f"You are looking at a website titled {title}"
    user_prompt += """
            \nThe contents of this website is as follows;
            please provide a short summary of this website
            If it includes news or announcements, then summarize these too.\n\n
        """
    user_prompt += content
    return user_prompt

# Streamlit UI
st.title("Website Content Viewer")
url_input = st.text_input("Enter website URL", "https://edwarddonner.com")

if st.button("Fetch Content"):
    status, html_content = fetch_html(url_input)
    if not status == 200:
        st.text("Status code is not 200")
    else:
        soup = BeautifulSoup(html_content,'lxml')
        doc = Document(html_content)
        title = soup.title.string
        body = soup.body
        for tag in body.select("script, style, input, img"):
            tag.decompose()    
        content= body.get_text(separator='\n',strip=True)
        system_prompt = """
            You are an assistant that analyzes the contents of a website 
            and provides a short summary, ignoring text that might be navigation related.
            Respond in markdown.
        """
        user_prompt = make_user_prompt(title=title, content=content)

        summary = get_gemini_summary(user_prompt, system_prompt)
        st.text(f"Title: {title}")
        st.text(f"{summary}")
    
