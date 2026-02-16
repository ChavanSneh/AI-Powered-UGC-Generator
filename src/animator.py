import os
import subprocess

def generate_warrior_video(image_path, audio_path, nosmooth=False, pads=[0, 20, 0, 0]):
    # Get the base project directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 🔱 THE ULTIMATE TACTICAL PATHING
    skeleton_path = os.path.normpath(os.path.join(project_root, "assets", "face_skeleton.mp4"))
    output_path = os.path.normpath(os.path.join(project_root, "assets", "warrior_video.mp4"))
    checkpoint_path = os.path.normpath(os.path.join(project_root, "Wav2Lip", "checkpoints", "wav2lip_fixed.pth"))
    inference_script = os.path.normpath(os.path.join(project_root, "Wav2Lip", "inference.py"))
    
    # Ensure audio_path is clean and absolute
    if not audio_path:
        audio_path = os.path.normpath(os.path.join(project_root, "assets", "voice_gen.wav"))
    else:
        audio_path = os.path.normpath(audio_path)

    # Force the use of the virtual environment's Python
    venv_python = os.path.normpath(os.path.join(project_root, "venv", "Scripts", "python.exe"))

    try:
        print(f"🚀 Engaging Lip-Sync Mech...")
        print(f"📍 Checkpoint: {checkpoint_path}")
        print(f"📍 Audio: {audio_path}")

        # THE TACTICAL COMMAND
        # '-u' forces unbuffered output so we see the progress bars in real-time
        # Clean and simple paths for Sneh_Python
        cmd = [
            venv_python, "-u", inference_script, 
            '--checkpoint_path', checkpoint_path,
            '--face', skeleton_path,
            '--audio', audio_path,
            '--outfile', output_path,
            '--pads', str(pads[0]), str(pads[1]), str(pads[2]), str(pads[3]),
            '--resize_factor', '1',
            '--device', 'cpu'
        ]

        if nosmooth:
            cmd.append('--nosmooth')

        # Run process and pipe output to terminal in real-time
        # This prevents the 'stuck' feeling by showing the Wav2Lip progress bars
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # Print logs as they happen
        for line in process.stdout:
            print(f"📟 {line.strip()}")

        process.wait()

        if process.returncode != 0:
            return f"Mech Error: Process exited with code {process.returncode}. Check terminal logs."

        if os.path.exists(output_path):
            return f"Success: Video saved to {output_path}"
        else:
            return "Mech Error: Output file was not generated."

    except Exception as e:
        return f"System Error: {str(e)}"