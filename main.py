import streamlit as st

from utils.faiss_store import get_store
from utils.chain import create_conversational_chain, use_conversational_chain

index_name = "blubasilico-ai"


def run_chat_app():
    st.title("BluBasilico-ai")
    st.caption(
        """<a
            href="https://github.com/AlessandroAnnini/blubasilico-ai"
            style="text-decoration:none; color:inherit"
            target="_blank"
            alt="blubasilico-ai">
                blubasilico-ai
            </a>""",
        unsafe_allow_html=True,
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Consigliami un primo veloce con la zucca"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Return the answer from the database
            answer = use_conversational_chain(prompt, st.session_state.chain)

            for response in answer:
                full_response += response
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


def create_update_chain():
    return create_conversational_chain(st.session_state.db, model)


if __name__ == "__main__":
    try:
        if "openai_api_key" not in st.session_state:
            st.session_state.openai_api_key = ""

        st.session_state.openai_api_key = st.sidebar.text_input(
            "OpenAI API Key", type="password"
        )

        st.sidebar.caption(
            """<a
            href="https://beta.openai.com/account/api-keys"
            style="text-decoration:none; color:inherit"
            target="_blank"
            alt="openai api key">
                Click here to get your OpenAi api key
            </a>""",
            unsafe_allow_html=True,
        )

        if "model" not in st.session_state:
            st.session_state.model = "gpt-4"

        folder = "recipes"
        if "db" not in st.session_state and st.session_state.openai_api_key:
            st.session_state.db = get_store(
                [index_name], st.session_state.openai_api_key
            )

        model = st.sidebar.selectbox(
            "Model",
            ("gpt-4", "gpt-3.5-turbo"),
            on_change=create_update_chain,
            key="model",
        )

        if "chain" not in st.session_state and st.session_state.openai_api_key:
            st.session_state.chain = create_conversational_chain(
                st.session_state.db,
                st.session_state.openai_api_key,
                st.session_state.model,
            )

        run_chat_app()
    except Exception as e:
        st.write("Fatal Error!")
        st.write(e)
