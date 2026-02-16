import streamlit as st
import os
import shutil
import time

# --- COMMAND CENTER IMPORTS ---
from src.image_gen import generate_avatar
from src.voice_gen import generate_voice
from src.animator import generate_warrior_video

# --- CONFIGURATION & PATHS ---
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

# Ensure the battlefield is ready
for folder in [ASSETS_DIR, TEMP_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- MARKETING ATTRIBUTES DICTIONARY ---
# (I am keeping your PERSONA_ATTRIBUTES and SCENARIO_ATTRIBUTES as they are perfect)
PERSONA_ATTRIBUTES = {
    "Everyday Consumer Testimonial": {
        "Age Range": ["20s", "30s", "40s"],
        "Gender": ["Female", "Male", "Non-binary"],
        "Ethnicity": ["Caucasian", "Black", "Asian", "Hispanic", "Middle Eastern"],
        "Clothing Style": {"Casual": "casual t-shirt", "Smart Casual": "blouse/button-down", "Activewear": "gym gear"},
        "Emotional Expression": {"Friendly": "warm smile", "Enthusiastic": "energetic", "Thoughtful": "calm"}
    },
    "Lifestyle Product Demo": {
        "Age Range": ["20s", "30s", "40s"],
        "Gender": ["Female", "Male", "Non-binary"],
        "Ethnicity": ["Caucasian", "Black", "Asian", "Hispanic", "Middle Eastern"],
        "Clothing Style": {"Fitness": "activewear", "Tech": "smart casual hoodie", "Home": "cozy sweater"},
        "Emotional Expression": {"Enthusiastic": "excited", "Informative": "focused", "Friendly": "approachable"}
    },
    "Influencer-Style Recommendation": {
        "Age Range": ["20s", "30s", "40s"],
        "Gender": ["Female", "Male", "Non-binary"],
        "Ethnicity": ["Caucasian", "Black", "Asian", "Hispanic", "Middle Eastern"],
        "Clothing Style": {"Streetwear": "fashion-forward", "Chic": "stylish tops", "Wellness": "minimalist chic"},
        "Emotional Expression": {"Confident": "poised", "Engaging": "smiling", "Aspirational": "polished"}
    }
}

SCENARIO_ATTRIBUTES = {
    "Everyday Consumer Testimonial": {
        "Background/Setting": {"Living Room": "cozy living room", "Kitchen": "modern kitchen", "Office": "clean office"},
        "Lighting": {"Natural": "daylight", "Soft": "diffused studio", "Bright": "crisp professional"},
        "Camera Angle": {"Headshot": "close-up", "Waist-up": "medium shot"}
    },
    "Lifestyle Product Demo": {
        "Background/Setting": {"Home Gym": "gym background", "Vanity": "makeup table", "Desk": "tech setup", "Kitchen": "kitchen counter"},
        "Lighting": {"Bright": "vivid", "Studio": "polished", "Soft": "warm diffused"},
        "Camera Angle": {"Close-up": "tight shot", "Waist-up": "medium shot"}
    },
    "Influencer-Style Recommendation": {
        "Background/Setting": {"Urban Apartment": "modern apartment", "Cafe": "trendy cafe", "Travel": "scenic outdoor"},
        "Lighting": {"Bright Natural": "airy window light", "Studio": "professional polished"},
        "Camera Angle": {"Medium Personality": "waist-up shot", "Dynamic": "lifestyle tilt"}
    }
}

# --- PROMPT ENGINE ---
def build_image_prompt_ui():
    st.subheader("Choose Your Marketing Scenario & Persona")
    selected_scenario = st.selectbox("Select Scenario:", list(PERSONA_ATTRIBUTES.keys()), key="scen_sel")
    
    st.divider()
    p_attr = PERSONA_ATTRIBUTES[selected_scenario]
    s_attr = SCENARIO_ATTRIBUTES[selected_scenario]

    col1, col2 = st.columns(2)
    with col1:
        age = st.selectbox("Age Range:", p_attr["Age Range"])
        gender = st.radio("Gender:", p_attr["Gender"], horizontal=True)
        eth = st.selectbox("Ethnicity:", p_attr["Ethnicity"])
    
    with col2:
        cloth = st.selectbox("Clothing Style:", list(p_attr["Clothing Style"].keys()))
        emotion = st.selectbox("Expression:", list(p_attr["Emotional Expression"].keys()))
        bg = st.selectbox("Setting:", list(s_attr["Background/Setting"].keys()))
        light = st.selectbox("Lighting:", list(s_attr["Lighting"].keys()))
        cam = st.selectbox("Framing:", list(s_attr["Camera Angle"].keys()))

    pos_prompt = f"A high-quality, photorealistic portrait of a {age} year old {eth} {gender}, wearing {p_attr['Clothing Style'][cloth]}, with a {p_attr['Emotional Expression'][emotion]} expression. Setting: {s_attr['Background/Setting'][bg]}, {s_attr['Lighting'][light]} lighting, {s_attr['Camera Angle'][cam]} angle. Professional marketing content, social media ready, natural skin texture."
    
    neg_prompt = "ugly, deformed, cartoon, anime, 3d render, painting, warrior, helmet, armor, chrome, futuristic, vintage, sci-fi, blurry, low resolution, watermark, text"
    
    return pos_prompt, neg_prompt

# --- MAIN APP ---
st.set_page_config(page_title="UGC Content Engine", layout="wide", page_icon="📈")

# Session State Initialization
if 'current_avatar_path' not in st.session_state: st.session_state.current_avatar_path = None
if 'current_audio_path' not in st.session_state: st.session_state.current_audio_path = None
if 'current_video_path' not in st.session_state: st.session_state.current_video_path = None

st.title("📈 UGC Marketing Content Generator")

# --- SIDEBAR: TECHNICAL OVERRIDES ---
with st.sidebar:
    st.title("🛡️ Warrior Settings")
    st.info("Fine-tune the animation engine below.")
    
    animator_nosmooth = st.checkbox("Disable Smoothing", value=False)
    st.write("Mouth Padding (Pads):")
    p_top = st.slider("Top", 0, 20, 0)
    p_bottom = st.slider("Bottom", 0, 20, 10)
    p_left = st.slider("Left", 0, 20, 0)
    p_right = st.slider("Right", 0, 20, 0)
    animator_pads = [p_top, p_bottom, p_left, p_right]
    
    st.divider()
    if st.button("🧹 Clear All Assets"):
        target_dirs = [os.path.join(project_root, ASSETS_DIR), temp_path]
        for folder in target_dirs:
            if os.path.exists(folder): shutil.rmtree(folder)
            os.makedirs(folder, exist_ok=True)
        st.session_state.clear()
        st.rerun()

# --- TABS (Single Declaration) ---
tab_image, tab_voice, tab_animate = st.tabs([
    "🎨 Generate Persona Image", 
    "🎙️ Craft Persona Voice", 
    "🚀 Animate Content"
])

# --- PHASE 1: IMAGE ---
with tab_image:
    st.header("1. Design Your AI Persona & Scene")
    img_prompt, neg_prompt = build_image_prompt_ui()

    if st.button("🎨 Generate AI Persona Image", use_container_width=True):
        progress_bar = st.progress(0, text="Igniting AI Engine...")
        def update_ui_progress(step):
            percent = int((step / 15) * 100)
            progress_bar.progress(percent, text=f"Forging Persona: Step {step}/15")

        with st.spinner("Processing Pixels (CPU Mode)..."):
            result_path = generate_avatar(
                img_prompt, 
                neg_prompt, 
                output_path=avatar_output_path,
                callback=update_ui_progress
            )
            if result_path and "Error" not in result_path:
                progress_bar.empty()
                st.session_state.current_avatar_path = result_path 
                st.success("AI Persona Image Ready!")
            else:
                st.error(f"Forge Error: {result_path}")

    if st.session_state.current_avatar_path and os.path.exists(st.session_state.current_avatar_path):
        st.image(st.session_state.current_avatar_path, width=400, caption="Current Persona")

# --- PHASE 2: VOICE ---
with tab_voice:
    st.header("2. Craft Persona Voice & Script")
    v_text = st.text_area("Marketing Script:", "Hi! I just tried this and it's incredible. You need to see the results for yourself!")
    v_gender = st.radio("Voice Profile:", ["Male", "Female"], horizontal=True)

    if st.button("🎙️ Generate Persona Voice", use_container_width=True):
        if v_text:
            with st.spinner(f"Synthesizing {v_gender} Voice..."):
                res = generate_voice(v_text, gender=v_gender, output_path=audio_output_path)
                if res and "Error" not in res:
                    st.session_state.current_audio_path = res 
                    st.success(f"Voice Ready: {v_gender} profile applied.")
                else:
                    st.error(f"Voice failure: {res}")

    if st.session_state.current_audio_path and os.path.exists(st.session_state.current_audio_path):
        st.audio(st.session_state.current_audio_path)

# --- PHASE 3: ANIMATION ---
with tab_animate:
    st.header("3. Final Content Assembly")
    if st.session_state.current_avatar_path and st.session_state.current_audio_path:
        st.info("✅ Ready to animate.")
        if st.button("🔥 START CONTENT ANIMATION", use_container_width=True):
            if os.path.exists(temp_path): shutil.rmtree(temp_path)
            os.makedirs(temp_path, exist_ok=True)

            with st.spinner("Running Lip-Sync (Wav2Lip)..."):
                result = generate_warrior_video(
                    image_path=st.session_state.current_avatar_path,
                    audio_path=st.session_state.current_audio_path,
                    nosmooth=animator_nosmooth,
                    pads=animator_pads
                )
                if "Success" in result or os.path.exists(output_video_path):
                    st.session_state.current_video_path = output_video_path
                    st.success("Marketing Content Animation Complete!")
                    st.balloons()
                else:
                    st.error(f"Animation failed: {result}")

        if st.session_state.current_video_path and os.path.exists(st.session_state.current_video_path):
            st.divider()
            st.video(st.session_state.current_video_path, loop=True, autoplay=True)
            with open(st.session_state.current_video_path, "rb") as file:
                st.download_button("📥 Download Marketing Video", data=file, file_name="ugc_video.mp4")
    else:
        st.warning("⚠️ You must generate both a Persona Image (Tab 1) and a Voice (Tab 2) first.")