from TTS.api import TTS

# Test

speak_sample= "/assets/Kira.wav"
text = "I might not be jutstice but. I. AM. INSANE!"
out = "output.wav"

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

tts.save_to_file(
  text = text,
  speaker_wav = speak_sample,
  language= "en",
  file_path= out,
)

print("done")