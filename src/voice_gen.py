import os
import asyncio
import edge_tts
import nest_asyncio

# Apply the nest to allow edge-tts to run inside Streamlit's loop
nest_asyncio.apply()

def generate_voice(text: str, gender: str, output_path: str = "assets/voice_gen.wav"):
    try:
        # Tactical Reset of the audio file
        if os.path.exists(output_path):
            os.remove(output_path)

        voice = "en-US-GuyNeural" if gender == "Male" else "en-US-JennyNeural"
        print(f"🎙️ Synthesizing {gender} Voice...")

        # The actual async work
        async def _save_audio():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)

        # Execute the async function within the current loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_save_audio())
        
        print(f"✅ Voice saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Voice Error: {str(e)}")
        return f"Voice Error: {str(e)}"