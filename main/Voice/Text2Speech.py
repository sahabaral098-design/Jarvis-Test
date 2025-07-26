from TTS.api import TTS
import torch

gpu= torch.cuda.is_available()

speak_sample = "./assets/Kira.wav"
text = "I might not be justice... but I. AM. INSANE!"
out = "output.wav"

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=gpu)
tts.tts_to_file(
    text=text,
    speaker_wav=speak_sample,
    language="en",
    file_path=out
)

print(f" Done ")