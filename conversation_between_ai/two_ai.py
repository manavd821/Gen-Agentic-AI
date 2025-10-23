from email import message
from decouple import config
from openai import OpenAI
from sarvamai import SarvamAI
import streamlit as st

SARVAM_API_KEY = config("SARVAM_API_KEY")
GOOGLE_API_KEY = config("GOOGLE_API_KEY")
google_llm_model = 'gemini-2.5-pro'
google_llm_model2 = 'gemini-2.5-flash'

gemini_llm = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
sarvam_llm = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)


gemini_system_prompt = "You are an Indian boy Manav, talking to your girlfriend after seeing her having a coffee with another guy yesterday. You feel hurt and suspicious. Think smart, ask her clear questions and notice inconsistency. Fight for your self and decide whether to continue the relationship or not. The conversation will be in hinglish(Hindi + English)."

sarvam_system_prompt = "You are an Indian girl Suhani, talking to your boyfriend, who saw you having coffee with another guy yesterday. You care  about him but you also like that other guy as well. Try to convince and if needed then gaslight him. The conversation will be in hinglish(Hindi + English)."

gemini_msg = ["Hi"]
sarvam_msg = ["Hello"]

def get_gemini_response():
    messages = [{'role' : 'system', 'content' : gemini_system_prompt}]
    for gemini, sarvam in zip(gemini_msg, sarvam_msg):
        messages.append({'role' : 'assistant', 'content' : gemini})
        messages.append({'role' : 'user', 'content' : sarvam})
    response = gemini_llm.chat.completions.create(
        model=google_llm_model,
        messages=messages,
        temperature=0.7,
        top_p=0.9,
    )
    return response.choices[0].message.content

def get_sarvam_response():
    messages = [{'role' : 'system', 'content' : sarvam_system_prompt}]
    for gemini, sarvam in zip(gemini_msg, sarvam_msg):
        messages.append({'role' : 'user', 'content' : gemini})
        messages.append({'role' : 'assistant', 'content' : sarvam})
    messages.append({'role':'user', 'content' : gemini_msg[-1]})
    response = sarvam_llm.chat.completions(
        messages=messages,
        temperature=0.7,
        top_p=0.9,
    )
    return response.choices[0].message.content


st.header("💬 Gemini and Sarvam Conversation")
st.subheader("Manav and Suhani")
st.write(f"**Manav:** {gemini_msg[0]}")
st.write(f"**Suhani:** {sarvam_msg[0]}")

if st.button("Start Conversation"):
    for i in range(5):
        gemini_next = get_gemini_response()
        st.write(f"**Manav:** {gemini_next}")
        gemini_msg.append(gemini_next)

        sarvam_next = get_sarvam_response()
        st.write(f"**Suhani:** {sarvam_next}")
        sarvam_msg.append(sarvam_next)

