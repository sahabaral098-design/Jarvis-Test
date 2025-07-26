from TTS.api import TTS

# Test

speak_sample= "/assets/Kira.wav"
text = "I might not be jutstice but. I. AM. INSANE!"
out = "output.wav"

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
