import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import os
import subprocess

_cached_pipe = None

def load_pipeline():
    global _cached_pipe
    if _cached_pipe is not None:
        return _cached_pipe
    
    # Switch to a CPU-friendly version of v1.5
    model_id = "runwayml/stable-diffusion-v1-5" 
    
    print("📡 Loading Engine on CPU... (Attention Slicing Enabled)")
    
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, 
        torch_dtype=torch.float32, 
        use_safetensors=True
    )
    
    # CRITICAL FOR NO-GPU USERS:
    # Attention slicing trades a tiny bit of speed for a massive reduction in RAM usage.
    pipe.enable_attention_slicing()
    
    # Optimization: Using DPM++ 2M Karras (Great quality in fewer steps)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    
    pipe = pipe.to("cpu")
    _cached_pipe = pipe
    return _cached_pipe

def generate_avatar(prompt, negative_prompt="", output_path="assets/persona_avatar.png", callback=None):
    try:
        pipe = load_pipeline()
        
        def pipe_callback(step, timestep, latents):
            if callback:
                callback(step)

        # Generating on CPU
        # 12-15 steps is the "Goldilocks" zone for CPUs.
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=15, 
            guidance_scale=7.0, # Slightly lower guidance is often better for CPU math
            callback=pipe_callback,
            callback_steps=1
        ).images[0]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path)
        
        # FFmpeg logic: Creating the 1-second base for the animator
        skeleton_path = os.path.join(os.path.dirname(output_path), "face_skeleton.mp4")
        
        # On Windows, we ensure the command is handled correctly
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-loop', '1', '-i', output_path, 
            '-t', '1', '-pix_fmt', 'yuv420p', # Ensure compatibility
            '-vf', 'scale=512:512', skeleton_path
        ]
        
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        
        return output_path
    except Exception as e:
        print(f"❌ Forge Error: {e}")
        return f"Error: {str(e)}"