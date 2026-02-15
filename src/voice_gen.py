import os
import asyncio
import edge_tts

def generate_voice(text: str, gender: str, output_path: str = "assets/voice_gen.wav"):
    try:
        # TACTICAL RESET
        if os.path.exists(output_path):
            os.remove(output_path)

        # 🔱 ASSIGNING REAL VOICES
        # 'Guy' is a deep male voice, 'Jenny' is a clear female voice
        voice = "en-US-GuyNeural" if gender == "Male" else "en-US-JennyNeural"
        
        print(f"🎙️ Synthesizing {gender} Warrior via {voice}...")

        # Since edge-tts is asynchronous, we run it in a small loop
        communicate = edge_tts.Communicate(text, voice)
        
        # This is the 'Warrior's Way' of running async code inside a sync function
        asyncio.run(communicate.save(output_path))
        
        print(f"✅ Voice saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Voice Error: {str(e)}")
        return f"Voice Error: {str(e)}"