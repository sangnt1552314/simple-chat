import streamlit as st
from openai import OpenAI

st.title("Chat with an AI assistant")

api_key = st.sidebar.text_input("API KEY", None)
base_url = st.sidebar.text_input("Base URL", None)

client = OpenAI(api_key=api_key, base_url=base_url)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model='meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})