import streamlit as st
import os
import shutil
import time

# --- IMPORTS ---
from src.image_gen import generate_avatar
from src.voice_gen import generate_voice
from src.animator import generate_warrior_video

# --- Configuration ---
ASSETS_DIR = "assets"
TEMP_DIR = "temp"  # Added temp directory to config
OUTPUT_VIDEO_NAME = "warrior_video.mp4"
AVATAR_IMAGE_NAME = "avatar_face.png"
VOICE_AUDIO_NAME = "voice_gen.wav"

# --- GLOBAL PATHS ---
project_root = os.path.dirname(os.path.abspath(__file__))
avatar_output_path = os.path.join(project_root, ASSETS_DIR, AVATAR_IMAGE_NAME)
audio_output_path = os.path.join(project_root, ASSETS_DIR, VOICE_AUDIO_NAME)
output_video_path = os.path.join(project_root, ASSETS_DIR, OUTPUT_VIDEO_NAME)
temp_path = os.path.join(project_root, TEMP_DIR)

st.set_page_config(page_title="Call Warrior Hub", layout="wide", page_icon="⚔️")

# Initialize Session States
if 'current_avatar_path' not in st.session_state:
    st.session_state.current_avatar_path = None
if 'current_audio_path' not in st.session_state:
    st.session_state.current_audio_path = None
if 'current_video_path' not in st.session_state:
    st.session_state.current_video_path = None

def clear_assets():
    """Wipes assets and temp folders to reset the engine."""
    # List of directories to wipe and recreate
    target_dirs = [os.path.join(project_root, ASSETS_DIR), temp_path]
    
    for folder in target_dirs:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    
    # Reset state
    st.session_state.current_avatar_path = None
    st.session_state.current_audio_path = None
    st.session_state.current_video_path = None
    st.cache_data.clear()

st.title("⚔️ CALL WARRIOR: MODULAR ENGINE")
tab_image, tab_voice, tab_animate = st.tabs(["🎨 Generate Image", "🎙️ Generate Voice", "🚀 Animate Video"])

with st.sidebar:
    st.header("🛡️ Tactical Controls")
    if st.button("🔴 Reset Warrior Hub"):
        clear_assets()
        st.success("Warroom Cleared!")
        st.rerun()

    st.subheader("⚙️ Animator Settings")
    animator_nosmooth = st.checkbox("Disable Smoothing", value=False)
    pad_top = st.slider("Top Pad", 0, 50, 0)
    pad_bottom = st.slider("Bottom Pad", 0, 50, 20)
    animator_pads = [pad_top, pad_bottom, 0, 0]

# --- PHASE 1: IMAGE ---
with tab_image:
    st.header("1. Design Warrior Appearance")
    img_prompt = st.text_area("Describe look:", "A close-up portrait of one futuristic soldier, chrome helmet, 512x512")
    
    if st.button("🎨 Forge Image"):
        with st.spinner("Forging Avatar..."):
            result_path = generate_avatar(img_prompt, output_path=avatar_output_path)
            if result_path and "Error" not in result_path:
                st.session_state.current_avatar_path = result_path 
                st.success("Warrior Image Ready!")
            else:
                st.error(result_path)

    if st.session_state.current_avatar_path and os.path.exists(st.session_state.current_avatar_path):
        st.image(st.session_state.current_avatar_path, width=400, caption="Generated Warrior")

# --- PHASE 2: VOICE ---
with tab_voice:
    st.header("2. Craft Warrior Voice")
    v_text = st.text_area("Script:", "Target acquired. Moving to position.")
    warrior_gender = st.radio("Identity:", ["Male", "Female"], horizontal=True)
    
    if st.button("🎙️ Generate Voice"):
        with st.spinner(f"Synthesizing {warrior_gender} Voice..."):
            res = generate_voice(v_text, gender=warrior_gender, output_path=audio_output_path)
            
            if res and "Error" not in res:
                st.session_state.current_audio_path = res 
                st.success(f"Voice Ready: {warrior_gender} profile applied.")
            else:
                st.error(res)

    if st.session_state.current_audio_path and os.path.exists(st.session_state.current_audio_path):
        st.audio(st.session_state.current_audio_path)

# --- PHASE 3: ANIMATE ---
with tab_animate:
    st.header("3. Animate Warrior")
    
    if st.session_state.current_avatar_path and st.session_state.current_audio_path:
        st.info("✅ Warrior Profile Loaded. Ready for Animation.")
        
        if st.button("🔥 START ANIMATION MECH"):
            # Ensure temp is fresh before starting
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
            os.makedirs(temp_path, exist_ok=True)

            with st.spinner("Engaging Lip-Sync... (Monitor terminal for '📟 MECH LOG')"):
                result = generate_warrior_video(
                    image_path=st.session_state.current_avatar_path,
                    audio_path=st.session_state.current_audio_path,
                    nosmooth=animator_nosmooth,
                    pads=animator_pads
                )
                
                if "Success" in result:
                    st.session_state.current_video_path = output_video_path
                    st.success("Animation Complete!")
                else:
                    st.error(result)

        # --- UPDATED RESULT DISPLAY ---
        if st.session_state.current_video_path and os.path.exists(st.session_state.current_video_path):
            st.divider()
            st.subheader("🎥 Forged Warrior Preview")
            
            # Autoplay and Loop enabled for the "Character Preview" effect
            st.video(st.session_state.current_video_path, loop=True, autoplay=True)
            
            with open(st.session_state.current_video_path, "rb") as file:
                st.download_button(
                    label="📥 Download Warrior Video",
                    data=file,
                    file_name="warrior_video.mp4",
                    mime="video/mp4"
                )
    else:
        st.warning("⚠️ Access Denied: Generate both Image and Voice before animating.")