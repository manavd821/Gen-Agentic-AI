from bs4 import BeautifulSoup
from decouple import config
from google.genai import Client
from pydantic import BaseModel, HttpUrl
import asyncio
from httpx import AsyncClient
import json
from typing import List
import streamlit as st

GOOGLE_API_KEY = config("GOOGLE_API_KEY")
client = Client(
    api_key=GOOGLE_API_KEY
)

def extract_clean_text(body : BeautifulSoup):
    for irrelevent_tag in body.select("script, style , img , input"):
        irrelevent_tag.decompose()
    return body.get_text(strip=True)

class Website(BaseModel):
    
    url : HttpUrl
    title : str = ""
    content : str = ""
    links : List[str] = []
    
    async def fetch(self, client : AsyncClient):
            res = await client.get(str(self.url))
            html_content = res.text
            soup = BeautifulSoup(html_content, 'lxml')
            self.title = soup.title.string if soup.title else "No title found"
            self.content = extract_clean_text(soup.body)
            self.links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
    
    @classmethod
    async def create(cls, url : HttpUrl):
        instance = cls(url=url)
        async with AsyncClient() as client:
            await instance.fetch(client)
        return instance
    
    def display(self) -> str:
        return f"title : {self.title}\n content : {self.content[:200]}"

def create_system_instruction() -> str:
    link_system_prompt = "You are provided with a list of links found on a webpage.You are able to decide which of the links would be most relevant to include in a brochure about the company,such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
    link_system_prompt += "You should respond in JSON as in this example:"
    link_system_prompt += """
    {
        "links": [
            {"type": "about page", "url": "https://full.url/goes/here/about"},
            {"type": "careers page", "url": "https://another.full.url/careers"}
        ]
    }
    """    
    return link_system_prompt

def get_link_user_prompt(website : Website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt

class Links(BaseModel):
    type : str
    url : HttpUrl
    
async def get_gemini_response(
        *,
        model : str = 'gemini-2.5-flash',
        user_prompt : str, 
        system_instruction : str, 
        response_mime_type : str = None, 
        response_schema : BaseModel = None
    ):
    res = await client.aio.models.generate_content(
        model=model,
        config={
            "system_instruction" : system_instruction,
            "response_mime_type" : response_mime_type ,
            "response_schema" :  response_schema,
            },
        contents=user_prompt
    )
    return res.text

async def get_gemini_stream_response(
        *,
        model : str = 'gemini-2.5-flash',
        user_prompt : str, 
        system_instruction : str = "", 
        response_mime_type : str = None, 
        response_schema : BaseModel = None
):
    stream = await client.aio.models.generate_content_stream(
        model=model,
        config={
            "system_instruction" : system_instruction,
            "response_mime_type" : response_mime_type ,
            "response_schema" :  response_schema,
            },
        contents=user_prompt
    )
    async for chunk in stream:
        if chunk.text:
            yield chunk.text

async def get_relevant_links(website : Website):
    link_system_prompt = create_system_instruction()
    user_prompt = get_link_user_prompt(website)
    response = await get_gemini_response(model='gemini-2.5-pro',user_prompt=user_prompt,system_instruction= link_system_prompt,response_mime_type= 'application/json', response_schema= list[Links])
    res_dict_list = json.loads(response)
    return res_dict_list

async def fetch_website_content(url : HttpUrl):
    website =await Website.create(url)
    return website.content

async def fetch_page_and_all_relevant_links(website : Website, links : List[dict[str, HttpUrl]]):
    result = f"##Landing Page:\n\n{website.content}\n##Relevant Links:\n"
    for link in links:
        result += f"\n## Link : {link['type']}\n"
        result += await fetch_website_content(link['url'])
    return result

def get_broucher_user_and_system_prompt(company_name : str, all_content_of_website: str):
    brochure_system_prompt = """
    You are an assistant that analyzes the contents of several relevant pages from a company website
    and creates a short, humorous, entertaining, witty brochure about the company for prospective customers, investors and recruits.
    Respond in markdown without code blocks.
    Include details of company culture, customers and careers/jobs if you have the information.
    """
    user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.\n\n
"""
    user_prompt += all_content_of_website[:5000]
    return brochure_system_prompt, user_prompt

async def process_website(url : str, website_name: str = ""):
    website = await Website.create(url=url)
    relevant_links : list[dict] = await get_relevant_links(website)
    all_content_of_website = await fetch_page_and_all_relevant_links(website, relevant_links)
    brochure_system_prompt, user_prompt = get_broucher_user_and_system_prompt(website_name, all_content_of_website)
    return brochure_system_prompt, user_prompt
    
def main():
    st.set_page_config(page_title="AI Web Broucher Generator", layout="wide")
    st.title("📘 Website → AI Brochure Generator")

    # url = st.text_input("Enter Website URL", "https://huggingface.co")
    with st.form(key="url_form"):
        url = st.text_input("Enter Website URL", "https://huggingface.co")
        submit_button = st.form_submit_button(label="Generate Brochure")
    # if st.button("Generate Brochure"):
    if submit_button:
        st.info(f"Fetching and generating brochure for: {url}")
        placeholder = st.empty()
        async def run_stream():
            brochure_system_prompt, user_prompt = await process_website(url, website_name = "OpenAI")
            try:
                collected_text = ""
                async for output in get_gemini_stream_response(user_prompt=user_prompt, system_instruction=brochure_system_prompt):
                    collected_text += output
                    placeholder.markdown(collected_text)
                    await asyncio.sleep(0.1)  
                st.success("✅ Brochure generated successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                print(f"Error bhai: {e}")
        asyncio.run(run_stream())
        
if __name__ == '__main__':
    main()