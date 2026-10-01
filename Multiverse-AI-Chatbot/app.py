import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("THE MULTIVERSE OF CHATBOTS")

st.sidebar.title("App Settings")

personality = st.sidebar.selectbox(
    "Who do you want to talk to?",
    [
        "Virat Kohli",
        "An angry Ravi Shastri",
        "A crazy Ronaldo fan",
        "A panicked college student at 3 AM",
        "A 1920s Mafia Boss",
        "A highly sarcastic fitness coach"
    ]
)

intensity = st.sidebar.slider(
    "Intensity Level",
    1,
    10,
    5
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_message := st.chat_input("Say something..."):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message("user"):
        st.write(user_message)

    ai_instructions = f"""
You are acting as {personality}.

Stay completely in character.

Act with an intensity level of {intensity}/10.

Respond to the user's message while staying true to your personality.

User: {user_message}
"""

    with st.spinner("Connecting to the multiverse..."):

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=ai_instructions
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.text
        }
    )

    with st.chat_message("assistant"):
        st.write(response.text)