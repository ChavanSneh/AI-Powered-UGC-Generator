import os
import subprocess
import re
import streamlit as st

def generate_ugc_video(image_path, audio_path, nosmooth=False, pads=[0, 20, 0, 0]):
    """
    Triggers the Wav2Lip inference engine to animate a generated persona.
    Optimized for Windows CPU-only environments with robust error filtering.
    """
    
    # 1. DEFINE PROJECT ROOT
    # Assumes animator.py is located in the 'src/' folder
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 2. DEFINE TACTICAL PATHS
    output_path = os.path.normpath(os.path.join(project_root, "assets", "ugc_video.mp4"))
    checkpoint_path = os.path.normpath(os.path.join(project_root, "Wav2Lip", "checkpoints", "wav2lip_fixed.pth"))
    inference_script = os.path.normpath(os.path.join(project_root, "Wav2Lip", "inference.py"))
    
    # Path to the virtual environment's Python executable
    venv_python = os.path.normpath(os.path.join(project_root, "venv", "Scripts", "python.exe"))

    # 3. UI PROGRESS INITIALIZATION
    progress_bar = st.progress(0, text="🚀 Initializing UGC Animation Engine...")
    status_text = st.empty()

    try:
        # THE COMMAND
        # '-u' forces unbuffered output so we see progress in real-time
        cmd = [
            venv_python, "-u", inference_script, 
            '--checkpoint_path', checkpoint_path,
            '--face', image_path,
            '--audio', audio_path,
            '--outfile', output_path,
            '--pads', str(pads[0]), str(pads[1]), str(pads[2]), str(pads[3]),
            '--resize_factor', '1' 
        ]

        if nosmooth:
            cmd.append('--nosmooth')

        # 4. EXECUTE SUBPROCESS
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )

        # 📟 REAL-TIME UI UPDATES
        for line in process.stdout:
            clean_line = line.strip()
            print(f"📟 {clean_line}") # Logs to VS Code Terminal
            
            # 🎯 STRICT REGEX: Only catches 1-3 digit percentages or frame fractions
            match = re.search(r"(\d{1,3})%|(\d+)\s*/\s*(\d+)", clean_line)
            
            if match:
                try:
                    p_val = 0.0
                    
                    # Case A: Percentage (e.g., 50%)
                    if match.group(1): 
                        p_val = float(match.group(1)) / 100.0
                    
                    # Case B: Frame count (e.g., 50/150)
                    elif match.group(2) and match.group(3): 
                        curr = int(match.group(2))
                        total = int(match.group(3))
                        p_val = curr / total if total > 0 else 0.0
                    
                    # 🛡️ THE GUARDRAIL: Clip values to [0.0, 1.0] to prevent Streamlit crashes
                    p_val = max(0.0, min(p_val, 1.0))
                    
                    # Only update if we have a valid float
                    progress_bar.progress(p_val, text=f"🎬 Processing: {int(p_val * 100)}%")

                except Exception:
                    # If math fails on a weird line, skip it and keep the engine running
                    continue
            
            # Status milestones
            if "Reading video frames" in clean_line:
                status_text.info("🎞️ Loading Persona Image...")
            elif "Model loaded" in clean_line:
                status_text.info("🧠 AI Model Ready. Starting CPU Render...")

        process.wait()
        
        # 5. FINAL VALIDATION
        if process.returncode != 0:
            return f"Animation Error: Engine exited with code {process.returncode}."

        if os.path.exists(output_path):
            progress_bar.empty()
            status_text.empty()
            return "Success"
        else:
            return "Animation Error: Video file not generated."

    except Exception as e:
        return f"System Error: {str(e)}"