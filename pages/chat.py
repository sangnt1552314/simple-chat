import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

import weaviate
from weaviate.classes.init import Auth

load_dotenv()

wcd_api_key = st.secrets['WEAVIATE_API_KEY']
wcd_url = st.secrets[]'WEAVIATE_URL']
hugginface_api_key = st.secrets['HUGGINFACE_API_KEY']

COLLECTION_NAME = "Question"

# Connect to Weaviate Cloud
wcd_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=wcd_url,
    auth_credentials=Auth.api_key(wcd_api_key),
    headers = {
        "X-HuggingFace-Api-Key": hugginface_api_key,
    }
)

collection = wcd_client.collections.get(COLLECTION_NAME)

st.title("Chat with an AI assistant")

api_key = st.sidebar.text_input("API KEY", None)
base_url = st.sidebar.text_input("Base URL", 'https://api.together.xyz/v1')

client = OpenAI(api_key=api_key, base_url=base_url)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    wcd_client.connect()

    wcd_collection = wcd_client.collections.get(COLLECTION_NAME)

    wcd_response = collection.query.near_text(
        query=prompt,  
        limit=2
    )

    wcd_obj = wcd_response.objects[0]
    retrieved_ans = wcd_obj.properties['answer']

    user_prompt = f"""
    Given the prompt: "{prompt}", the answer is: "{retrieved_ans}"
    """

    st.session_state.messages.append({"role": "user", "content": user_prompt})
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