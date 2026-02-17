# ⚔️ AI-Powered UGC Generator
**Forge High-Conversion AI Personas Locally.**

AI-Powered UGC Generator is a streamlined, local-first application designed to generate User-Generated Content (UGC) style marketing videos. By combining Stable Diffusion, Neural Voice Synthesis, and Lip-Sync animation, it allows creators to "forge" digital personas and animate them for product testimonials and lifestyle ads—all running locally on your CPU.

---

## 🚀 Core Capabilities

* **🎨 Persona Forge:** Generate photorealistic avatars based on specific marketing scenarios (Consumer Testimonial, Lifestyle Demo, Influencer Recommendation).
* **🎙️ Neural Vocalization:** High-fidelity voice synthesis using `edge-tts` with selectable gender profiles.
* **🚀 Content Animation:** Synchronized lip-syncing via `Wav2Lip`, specifically optimized for Windows CPU performance.
* **🛡️ Tactical UI:** A clean, tab-based Streamlit interface with real-time progress tracking.

---

## 🛠️ Hardware Optimization (CPU Only)

This project is engineered to run on **Windows CPUs**. It utilizes several optimizations to handle AI heavy-lifting without a dedicated graphics card:

* **Attention Slicing:** Dramatically reduces RAM usage during image generation.

* **CPU-Specific PyTorch:** Avoids the 5GB+ CUDA overhead.

* **Resize Factors:** Optimized frame processing for faster animation cycles.

---

## 📂 Project Structure

AI-Powered-UGC-Generator/
├── assets/              # Output directory for images, audio, and video
├── src/                 # Core logic modules
│   ├── image_gen.py     # Stable Diffusion pipeline (CPU)
│   ├── voice_gen.py     # Edge-TTS implementation
│   └── animator.py      # Wav2Lip subprocess controller
├── Wav2Lip/             # Facial animation engine
├── venv/                # Local Python environment
├── ugc_app.py           # Main Streamlit command center
└── requirements.txt     # CPU-optimized dependencies

## 📥 Installation & Setup

Clone the Repository:

git clone <repository-url>
cd AI-Powered-UGC-Generator

## Initialize the Virtual Environment:
python -m venv venv
.\venv\Scripts\activate

## Install CPU-Optimized Dependencies:

pip install -r requirements.txt

## External Dependencies:

* FFmpeg: Must be installed and added to your Windows System PATH.
* Wav2Lip Checkpoints: Place wav2lip_fixed.pth in Wav2Lip/checkpoints/.

## ⚡ Usage

Run the engine from your VS Code terminal:

streamlit run ugc_app.py

* Tab 1: Select your marketing scenario and attributes to forge your persona.

* Tab 2: Enter your marketing script and generate the voice.

* Tab 3: Finalize the assembly and animate the content.

## 📜 Acknowledgments
* Stable Diffusion: For the visual forge.

* Wav2Lip: For the gift of speech.

* Edge-TTS: For the neural vocals.