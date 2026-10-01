import os
import json
import requests
from io import BytesIO
from urllib.parse import quote
from dotenv import load_dotenv
import streamlit as st
from google import genai
from gtts import gTTS

load_dotenv()

st.title("Visual Novel Engine")

st.sidebar.header("Story Settings")
story_genre = st.sidebar.selectbox("Story Genre", ["Fantasy", "Sci-Fi", "Mystery", "Horror", "Cyberpunk"])
art_style = st.sidebar.selectbox("Art Style", ["Anime", "Photorealistic", "Vintage Victorian", "Sketch", "3D Render"])

@st.cache_resource(show_spinner=False)
def get_ai_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found in environment.")
        st.stop()
    return genai.Client(api_key=api_key)

client = get_ai_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = client.chats.create(model="gemini-2.5-flash")

if "previous_genre" not in st.session_state:
    st.session_state.previous_genre = story_genre
if "previous_style" not in st.session_state:
    st.session_state.previous_style = art_style

if st.session_state.previous_genre != story_genre or st.session_state.previous_style != art_style:
    st.session_state.messages = []
    st.session_state.gemini_chat = client.chats.create(model="gemini-2.5-flash")
    st.session_state.previous_genre = story_genre
    st.session_state.previous_style = art_style
    st.rerun()


def generate_image(image_prompt):
    full_prompt = f"{image_prompt}, art style: {art_style}"
    encoded_prompt = quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=768"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except requests.exceptions.RequestException:
        return None


def generate_audio(story_text):
    try:
        tts = gTTS(text=story_text, lang="en")
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception:
        return None


def ask_gemini(user_action):
    instructions = f"""
You are a visual novel narrator.
Genre: {story_genre}
Art Style: {art_style}

Always respond ONLY with valid JSON in this exact format, and nothing else:
{{
  "story_text": "A paragraph of narrative describing what happens next.",
  "image_prompt": "A detailed prompt describing the scene visually for an AI image generator.",
  "options": ["Choice 1", "Choice 2", "Choice 3"]
}}

User's action: {user_action}
"""

    with st.spinner("Thinking..."):
        try:
            response = st.session_state.gemini_chat.send_message(instructions)
        except Exception as e:
            st.toast("API rate limit or network error. Please try again in a moment...", icon="⚠️")
            return

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        st.error("Gemini did not return valid JSON.")
        st.stop()

    with st.spinner("Rendering the scene..."):
        image_bytes = generate_image(data["image_prompt"])

    with st.spinner("Recording narration..."):
        audio_bytes = generate_audio(data["story_text"])

    data["image_bytes"] = image_bytes
    data["audio_bytes"] = audio_bytes

    st.session_state.messages.append({"role": "user", "content": user_action})
    st.session_state.messages.append({"role": "assistant", "content": data})


for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant"):
            if msg["content"]["image_bytes"]:
                st.image(msg["content"]["image_bytes"])
            else:
                st.toast("Image server is busy, skipping visual...")

            st.write(msg["content"]["story_text"])

            if msg["content"]["audio_bytes"]:
                st.audio(msg["content"]["audio_bytes"], format="audio/mp3")
            else:
                st.toast("Narration failed, skipping audio...")


if not st.session_state.messages:
    if st.button("Begin the story"):
        ask_gemini("Start the story.")
        st.rerun()
else:
    last_msg = st.session_state.messages[-1]
    if last_msg["role"] == "assistant":
        options = last_msg["content"]["options"]

        st.write("What do you do?")
        for i, option in enumerate(options):
            if st.button(option, key=f"option_{len(st.session_state.messages)}_{i}"):
                ask_gemini(option)
                st.rerun()