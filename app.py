import streamlit as st
import logging
import sys
from ft_gpt.ingest.create_engine import create_engine

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


@st.cache_data(show_spinner="Starting engine..")
def load_engine_from_cache():
    return create_engine()


if "chat_engine" not in st.session_state:
    engine = load_engine_from_cache()
    st.session_state.chat_engine = engine

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome_message = "Hej. Jeg kan besvare spørgsmål relateret til mødereferater fra Folketinget for møder. Hvad vil du gerne vide?"
    st.session_state.messages.append(
        {"role": "llm", "content": welcome_message},
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message(name="User"):
        st.write(prompt)
    with st.spinner("Tænker..."):
        response = st.session_state.chat_engine.chat(message=prompt)
    with st.chat_message(name="LLM"):
        st.write(response.response)

    st.session_state.messages.append(
        {"role": "user", "content": prompt},
    )
    st.session_state.messages.append(
        {"role": "llm", "content": response.response},
    )
