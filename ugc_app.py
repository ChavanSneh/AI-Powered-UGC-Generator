import streamlit as st
import os
import shutil
import time

# --- IMPORTS ---
# Ensure these exist in your /src folder
try:
    from src.image_gen import generate_avatar
    from src.voice_gen import generate_voice
    from src.animator import generate_ugc_video 
except ImportError as e:
    st.error(f"Module Import Error: {e}. Please ensure /src files are present.")

# --- Configuration & Paths ---
ASSETS_DIR = "assets"
TEMP_DIR = "temp"
OUTPUT_VIDEO_NAME = "ugc_video.mp4"
AVATAR_IMAGE_NAME = "persona_avatar.png"
VOICE_AUDIO_NAME = "persona_voice.wav"

project_root = os.path.dirname(os.path.abspath(__file__))
avatar_output_path = os.path.join(project_root, ASSETS_DIR, AVATAR_IMAGE_NAME)
audio_output_path = os.path.join(project_root, ASSETS_DIR, VOICE_AUDIO_NAME)
output_video_path = os.path.join(project_root, ASSETS_DIR, OUTPUT_VIDEO_NAME)
temp_path = os.path.join(project_root, TEMP_DIR)

# Ensure directories exist
os.makedirs(os.path.join(project_root, ASSETS_DIR), exist_ok=True)
os.makedirs(temp_path, exist_ok=True)

# --- GLOBAL DICTIONARIES ---
PERSONA_ATTRIBUTES = {
    "Everyday Consumer Testimonial": {
        "Age Range": {"20s": "person in their 20s", "30s": "person in their 30s", "40s": "person in their 40s"},
        "Gender": ["Female", "Male", "Non-binary"],
        "Hair Length": ["Short hair", "Medium-length hair", "Long hair", "Bald/Shaved"],
        "Ethnicity": ["Caucasian", "Black", "Asian", "Hispanic", "Middle Eastern"],
        "Clothing Style": {"Casual": "casual t-shirt", "Smart Casual": "blouse/button-down", "Activewear": "gym gear"},
        "Emotional Expression": {"Subtle Smile": "gentle smile", "Engaging Smile": "warm smile", "Neutral/Calm": "calm", "Enthusiastic": "energetic grin", "Thoughtful": "pensive"},
    },
    "Lifestyle Product Demo": {
        "Age Range": {"20s": "person in their 20s", "30s": "person in their 30s", "40s": "person in their 40s"},
        "Gender": ["Female", "Male", "Non-binary"],
        "Hair Length": ["Short hair", "Medium-length hair", "Long hair", "Pixie cut"],
        "Ethnicity": ["Caucasian", "Black", "Asian", "Hispanic", "Middle Eastern"],
        "Clothing Style": {"Fitness Creator": "activewear", "Beauty Guru": "stylish casual", "Tech Reviewer": "hoodie", "Home Decor Blogger": "cozy sweater"},
        "Emotional Expression": {"Enthusiastic": "excited", "Informative": "focused", "Friendly": "approachable"},
    },
    "Influencer-Style Recommendation": {
        "Age Range": {"20s": "person in their 20s", "30s": "person in their 30s", "40s": "person in their 40s"},
        "Gender": ["Female", "Male", "Non-binary"],
        "Hair Length": ["Short hair", "Medium-length hair", "Long hair", "Stylish undercut"],
        "Ethnicity": ["Caucasian", "Black", "Asian", "Hispanic", "Middle Eastern"],
        "Clothing Style": {"Streetwear": "fashion-forward", "Chic": "stylish tops", "Wellness": "minimalist chic", "Travel": "layered practical outfit"},
        "Emotional Expression": {"Confident": "poised", "Engaging": "animated", "Aspirational": "polished"},
    }
}

SCENARIO_ATTRIBUTES = {
    "Everyday Consumer Testimonial": {
        "Background/Setting": {"Home - Living Room": "cozy living room", "Home - Kitchen": "modern kitchen", "Simple Studio": "neutral grey studio", "Office": "clean office desk"},
        "Lighting": {"Natural": "daylight", "Soft": "diffused studio", "Bright": "crisp professional"},
        "Camera Angle/Framing": {"Headshot": "close-up", "Waist-up": "medium shot", "Full Body": "standing shot"},
    },
    "Lifestyle Product Demo": {
        "Background/Setting": {"Fitness - Home Gym": "home gym", "Beauty - Vanity Table": "vanity table", "Tech - Modern Desk": "tech setup", "Home Decor - Living Room": "stylish living room"},
        "Lighting": {"Bright": "vivid", "Studio-like": "crisp professional", "Soft": "warm diffused"},
        "Camera Angle/Framing": {"Close-up": "tight shot", "Waist-up": "medium shot"},
    },
    "Influencer-Style Recommendation": {
        "Background/Setting": {"Urban Apartment": "modern urban apartment", "Chic Café": "trendy cafe", "Travel Spot": "scenic outdoor", "Minimalist Studio": "clean studio background"},
        "Lighting": {"Bright Natural": "airy window light", "Professional Studio": "polished studio"},
        "Camera Angle/Framing": {"Medium": "waist-up shot", "Dynamic": "lifestyle tilt angle"},
    }
}

# --- HELPER FUNCTIONS ---
def clear_assets():
    st.session_state.final_prompt = ""
    st.session_state.final_negative = ""
    st.session_state.current_avatar = None
    st.session_state.current_audio = None
    st.session_state.current_video = None
    for folder in [os.path.join(project_root, ASSETS_DIR), temp_path]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                try: os.remove(os.path.join(folder, f))
                except Exception as e: st.error(f"Cleanup Error: {e}")

# --- APP LAYOUT ---
st.set_page_config(page_title="AI-Powered UGC Generator", layout="wide", page_icon="📈")

# Session State Initialization
for key in ['final_prompt', 'final_negative', 'current_avatar', 'current_audio', 'current_video']:
    if key not in st.session_state: st.session_state[key] = None if 'current' in key else ""

st.title("📈 AI-Powered UGC Generator")
tab_image, tab_voice, tab_animate = st.tabs(["🎨 Persona Image", "🎙️ Craft Voice", "🚀 Animate Content"])

# --- TAB 1: IMAGE ---
with tab_image:
    st.header("1. Design Your AI Persona")
    prompt_mode = st.radio("Select Generation Mode:", ["Presets (Guided)", "Manual (Full Control)", "Hybrid"], horizontal=True)
    default_neg = "ugly, deformed, bad anatomy, cartoon, anime, 3d render, watermark, text, logo, blurry"
    
    refinement = ""
    if prompt_mode == "Hybrid":
        refinement = st.text_input("Add specific details (e.g. 'holding a phone'):")

    if prompt_mode == "Manual (Full Control)":
        img_p = st.text_area("Enter Custom Image Prompt:", height=150)
        neg_p = st.text_area("Negative Prompt:", value=default_neg, height=100)
    else:
        selected_scenario = st.selectbox("Select Marketing Scenario:", list(PERSONA_ATTRIBUTES.keys()))
        p_attr = PERSONA_ATTRIBUTES[selected_scenario]
        s_attr = SCENARIO_ATTRIBUTES[selected_scenario]

        c1, c2, c3 = st.columns(3)
        with c1:
            age_key = st.selectbox("Age Range:", list(p_attr["Age Range"].keys()))
            gender = st.radio("Gender:", p_attr["Gender"], horizontal=True)
        with c2:
            ethnicity = st.selectbox("Ethnicity:", p_attr["Ethnicity"])
            hair = st.selectbox("Hair Style:", p_attr["Hair Length"])
        with c3:
            cloth = st.selectbox("Clothing Style:", list(p_attr["Clothing Style"].keys()))
            emo = st.selectbox("Expression:", list(p_attr["Emotional Expression"].keys()))
            intensity = st.slider("Emotion Strength:", 0.5, 1.5, 1.0, 0.1)

        st.divider()
        bg = st.selectbox("Background Setting:", list(s_attr["Background/Setting"].keys()))
        lit = st.selectbox("Lighting:", list(s_attr["Lighting"].keys()))
        cam = st.selectbox("Camera Angle:", list(s_attr["Camera Angle/Framing"].keys()))

        with st.expander("🛠️ Advanced Image Settings"):
            neg_p = st.text_area("Negative Prompt:", value=default_neg)

        if st.button("📝 Generate Prompt", use_container_width=True):
            emo_desc = f"({p_attr['Emotional Expression'][emo]}:{intensity})"
            base = f"Photorealistic portrait of a {p_attr['Age Range'][age_key]} {ethnicity} {gender} with {hair.lower()}, wearing {p_attr['Clothing Style'][cloth]}, {emo_desc} expression, {s_attr['Background/Setting'][bg]}, {lit}, {s_attr['Camera Angle/Framing'][cam]}."
            st.session_state.final_prompt = f"{base}, {refinement}" if refinement else base
            st.session_state.final_negative = neg_p
            st.success("Prompt Prepared!")

    if st.session_state.final_prompt:
        st.info(f"**Current Prompt:** {st.session_state.final_prompt}")
        if st.button("🎨 Forge Persona Image", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            start_time = time.time()
            steps = 20
            for step in range(1, steps + 1):
                elapsed = time.time() - start_time
                percent = int((step / steps) * 100)
                if elapsed > 0:
                    it_per_sec = step / elapsed
                    rem = (steps - step) / it_per_sec
                    it_str = f"{1/it_per_sec:.2f}s/it"
                else: rem, it_str = 0, "Calculating..."
                bar = "█" * (percent // 4) + " " * (25 - (percent // 4))
                status_text.code(f"{percent}%|{bar}| {step}/{steps} [{elapsed:.2f}s<{rem:.2f}s, {it_str}]")
                progress_bar.progress(percent)
                time.sleep(0.2)
            
            res = generate_avatar(st.session_state.final_prompt, st.session_state.final_negative, output_path=avatar_output_path)
            if res and "Error" not in res:
                st.session_state.current_avatar = res
                status_text.success("✅ Forge Complete!")
            else: st.error(f"Forge Error: {res}")

    if st.session_state.current_avatar and os.path.exists(avatar_output_path):
        st.image(st.session_state.current_avatar, width=450)
        with open(avatar_output_path, "rb") as f:
            st.download_button("💾 Download Persona", data=f, file_name="persona.png", mime="image/png", use_container_width=True)

# --- TAB 2: VOICE ---
with tab_voice:
    st.header("2. Craft Persona Voice")
    v_text = st.text_area("Script:", "Hi! I love this product.")
    v_gen = st.radio("Voice Gender:", ["Male", "Female"], horizontal=True)
    if st.button("🎙️ Generate Audio"):
        with st.spinner("Synthesizing..."):
            res = generate_voice(v_text, gender=v_gen, output_path=audio_output_path)
            if res: st.session_state.current_audio = res; st.success("Voice Ready!")
    if st.session_state.current_audio and os.path.exists(audio_output_path):
        st.audio(st.session_state.current_audio)

# --- TAB 3: ANIMATION ---
with tab_animate:
    st.header("3. Animate Content")
    if st.session_state.current_avatar and st.session_state.current_audio:
        if st.button("🚀 START FINAL ANIMATION", type="primary", use_container_width=True):
            try:
                if os.path.exists(temp_path): shutil.rmtree(temp_path)
                os.makedirs(temp_path, exist_ok=True)
                result = generate_ugc_video(st.session_state.current_avatar, st.session_state.current_audio)
                if "Success" in result: st.session_state.current_video = output_video_path; st.balloons()
                else: st.error(result)
            except Exception as e: st.error(f"Error: {e}")
        
        if st.session_state.current_video and os.path.exists(output_video_path):
            st.video(st.session_state.current_video)
            with open(output_video_path, "rb") as f:
                st.download_button("📥 Download Video", data=f, file_name="ugc_video.mp4", mime="video/mp4", use_container_width=True)
    else: st.warning("⚠️ Missing Assets: Please generate an Image and Voice first.")

with st.sidebar:
    st.header("Settings")
    if st.button("🔴 RESET ALL"): clear_assets(); st.rerun()