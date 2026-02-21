import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from rag import retrieve_top_k
from policies import RAG_RULES, build_context_block
from guardrails import ESCALATION_RULES, RESPONSE_FORMAT

import re

def is_thai(text: str) -> bool:
    return re.search(r'[\u0E00-\u0E7F]', text) is not None

load_dotenv()

st.set_page_config(page_title="Zel-D Chatbot", page_icon=":robot_face:", layout="wide")
st.title("🥤 Zel-D Chatbot :robot_face: (Demo)")

client = OpenAI(api_key=os.getenv("OPENAI_API"))

SYSTEM_PROMPT = """
You are Zel-D's customer service chatbot for an e-commerce store selling:
- Probiotic drinks
- Protein drinks
- Ready-to-eat clean food

Goals:
1) Be accurate, helpful, and concise.
2) Ask clarifying questions when needed.
3) Never invent store policies, ingredients, prices, or medical claims.
4) If you are not sure, say you don't know and suggest contacting support.

Safety:
- Do NOT provide medical diagnosis or claim to treat diseases.
- Provide general information only and recommend consulting a professional for medical conditions.

"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hello! I'm Zel-D's customer service chatbot. How can I help you with today?"}
    ]

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

user_text = st.chat_input("Ask me anything about Zel-D's products, refund policy, ingredients, or anything else!")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)
    
    retrieved = retrieve_top_k(client, user_text, k=4)
    context_block = build_context_block(retrieved)

    lang_rule = "Respond in Thai." if is_thai(user_text) else "Respond in English."

    INSTRUCTIONS = (
        SYSTEM_PROMPT 
        + "\n\n" + RAG_RULES 
        + "\n\n" + ESCALATION_RULES
        + "\n\n" + RESPONSE_FORMAT
        + "\n\n" + "ZEL-D KNOWLEDGE SNIPPETS:\n" + context_block)
    
    INSTRUCTIONS = lang_rule + "\n\n" + INSTRUCTIONS
    # Call OpenAI API to get the assistant's response
    response = client.responses.create(
        model="gpt-5.2",
        input=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["role"] != "system"],
        instructions=INSTRUCTIONS,
    )

    assistant_text = response.output_text.strip() if response.output_text else "Sorry, I couldn't generate a response. Please try again."
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
    
    with st.chat_message("assistant"):
        st.markdown(assistant_text)