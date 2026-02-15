import torch
from diffusers import StableDiffusionPipeline
import os
import subprocess

# --- HELPER: LOADING THE BRAIN ---
def load_pipeline():
    """Initializes the Stable Diffusion pipeline for CPU."""
    try:
        model_id = "runwayml/stable-diffusion-v1-5"
        print(f"📡 Loading model: {model_id} (CPU Mode)...")
        
        # We use float32 because float16 often crashes on CPUs
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id, 
            torch_dtype=torch.float32
        )
        
        # Force it to use CPU
        pipe = pipe.to("cpu")
        return pipe
    except Exception as e:
        print(f"❌ Pipeline Error: {e}")
        return None

# --- MAIN ENGINE ---
def generate_avatar(prompt: str, output_path: str = "assets/avatar_face.png"):
    try:
        # Now 'load_pipeline' is defined and can be called
        pipe = load_pipeline()
        if pipe is None:
            return "Error: Pipeline initialization failed."

        print(f"🎨 Forging image: '{prompt}'")
        # Generating the image
        image = pipe(prompt, num_inference_steps=20).images[0]

        # 1. Save the PNG
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path)
        print(f"✅ Warrior PNG saved to {output_path}")

        # 2. AUTOMATIC SKELETON CONVERSION
        skeleton_path = os.path.join(os.path.dirname(output_path), "face_skeleton.mp4")
        
        print("⚔️ Automatically forging face_skeleton.mp4...")
        
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-loop', '1', '-i', output_path, 
            '-c:v', 'libx264', '-t', '5', '-pix_fmt', 'yuv420p', 
            '-vf', 'scale=512:512', skeleton_path
        ]
        
        # Running FFmpeg in the background
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"✅ Skeleton Ready at {skeleton_path}")
        return output_path

    except Exception as e:
        return f"Forge Error: {str(e)}"