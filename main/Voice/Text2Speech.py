from TTS.api import TTS

speak_sample = "main/Voice/assets/Kira.wav"

def test():
    text = "The curious cat tiptoed across the piano, accidentally playing a haunting melody."
    out = "output.wav"

    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
    tts.tts_to_file(
        text=text,
            speaker_wav=speak_sample,
                language="en",
                    file_path=out
                    )
    print(f" Done ")

if __name__ == "__main__":
    test()