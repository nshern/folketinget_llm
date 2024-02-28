import streamlit as st

from ft_gpt.ingest.create_engine import create_engine
from ft_gpt import utils


def reset_chat():
    st.session_state.chat_engine.reset()
    init_chat()


def show_info_text():
    st.header("Folketinget GPT")
    dates = utils.get_dates_of_sittings(reverse=True)
    st.markdown("Hej 👋")
    st.markdown(
        "Jeg er en LLM (Large language model), som kan hjælpe dig med at afsøge information om hvad der er forgået på folketingets møder."
    )
    st.markdown(
        f"Jeg har adgang til mødereferater i datospændet :red[**{dates[-1]}**] til og med :red[**{dates[0]}**]"
    )

    st.markdown("Indskriv dit spørgsmål i feltet placeret i bunden af siden 👇")
    st.markdown("")


# reset_button = st.button(label="Nulstil samtalehistorik", type="secondary")
# if reset_button:
#     reset_chat()


def init_chat():
    st.session_state.messages = []
    st.session_state.chat_engine.reset()


#     welcome_message = "Hej. Jeg kan besvare spørgsmål relateret til mødereferater fra Folketinget for møder. Hvad vil du gerne vide?"
#     st.session_state.messages.append(
#         {"role": "llm", "content": welcome_message},
#     )

show_info_text()


@st.cache_resource(show_spinner="Starting engine..")
def load_engine_from_cache():
    return create_engine()


if "chat_engine" not in st.session_state:
    engine = load_engine_from_cache()
    st.session_state.chat_engine = engine


# Initialize chat history
if "messages" not in st.session_state:
    init_chat()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Hvad har x sagt om y...")

if prompt:
    with st.chat_message(name="User"):
        st.write(prompt)
    with st.spinner("Tænker..."):
        response = st.session_state.chat_engine.chat(prompt)
        references = [i.metadata["url"] for i in response.source_nodes]
    with st.chat_message(name="LLM"):
        enhanced_response = f"{response.response}\n"
        if references != []:
            for i in references:
                enhanced_response = enhanced_response + f"- :gray[*[{i}]({i})*]\n"
        st.markdown(enhanced_response)

    st.session_state.messages.append(
        {"role": "user", "content": prompt},
    )
    st.session_state.messages.append(
        {"role": "llm", "content": enhanced_response},
    )
