import streamlit as st
import requests
import random

st.title("MY AI IMAGE GENERATOR")

st.sidebar.header("SETTINGS")

art_style = st.sidebar.selectbox(
    "Select desired Art Style",
    ["Photorealistic", "Anime", "Vintage Victorian", "Sketch", "3D Render"]
)

width = st.sidebar.slider("Image width", min_value=256, max_value=1024, value=768)
height = st.sidebar.slider("Image height", min_value=256, max_value=1024, value=768)

magic_enhance = st.sidebar.checkbox("✨ Enable Magic Enhance")

surprise_prompts = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo",
    "A dragon sipping coffee at a Parisian cafe",
    "A robot painting a self-portrait in a forest",
    "A underwater city powered by glowing jellyfish"
]

user_prompt = st.text_input("Describe the image you want to generate")

col1, col2 = st.columns(2)
with col1:
    generate_clicked = st.button("Generate Image")
with col2:
    surprise_clicked = st.button("🎲 Surprise Me!")

final_prompt = None

if generate_clicked:
    if user_prompt:
        final_prompt = user_prompt
    else:
        st.warning("Please enter a prompt.")

if surprise_clicked:
    final_prompt = random.choice(surprise_prompts)
    st.info(f"Surprise prompt: {final_prompt}")

if final_prompt:
    with st.spinner("Rendering the image"):
        full_prompt = f"{final_prompt}, make the art style: {art_style}"

        if magic_enhance:
            full_prompt += ", masterpiece, 8k resolution, highly detailed, trending on artstation, unreal engine 5 render"

        url = f"https://image.pollinations.ai/prompt/{full_prompt}?width={width}&height={height}"
        response = requests.get(url)

        if response.status_code == 200:
            st.success("Image Generated")
            st.image(response.content, caption=full_prompt)

            st.download_button(
                label="Download Image",
                data=response.content,
                file_name=f"{art_style}_image.png",
                mime="image/png"
            )
        else:
            st.error("API is not working")