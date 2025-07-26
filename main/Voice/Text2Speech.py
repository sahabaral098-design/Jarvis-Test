from TTS.api import TTS

speak_sample = "main/Voice/assets/Kira.wav"

def test():
    text = "The curious cat tiptoed across the piano, accidentally playing a haunting melody. But.... why.."
    out = "output.wav"

    text= """
    "I don't know what those motherfuckers were thinking. WHO WOULD THINK COMBINING O35 AND 610 AS A 'TEST' IS A GOOD IDEA?? DON'T THEY KNOW HOW DANGEROUS 610 IS?? Oh god... Some insane researcher suggested to see what will happen if 035 tries to possess a host of 610. God curse him AND THOSE BITCHES. Oh. My. God. WHO THE HELL WITH THEIR RIGHT MIND WOULD APPROVE THIS STUPID PROPOSAL. Oh... My... Before it's too late. DO NOT. NEVER.  EVER send anyone for investigation or backup. JUST DONT. I don't want this nightmare to spread. It started Dr. James out of all possible things suggested TO COMBINE 035 AND A HOST OF 610 IN A SO CALLED 'CONTROLLED AND SECURE' CHAMBER. God curse him. AND THEY APPROVED THIS PROPOSAL! God curse those bastards. WHY LITERALLY WHY IN THE UNIVERSE. So. As per the proposal D-3163 was first infected with 610 and D-2973 with an explosive collar was instructed to put 035 on 3163's face. AND THAT FUCKER ACTUALLY DID SO. Oh my... Can't blame him.. he did what he was told... Who's fault is this really.... Anyways. THEY SHOULD HAVE BEEN AWARE OF THE DANGERS OF 610. IT'S KETER CLASS FOR A FUCKING REASON. As soon 035 came in contact with D-3163, it... Cracked.. i guess? THEN OH MY FUCKING GOD. THE WHOLE CHAMBER WAS FILLED WITH 035'S GOO THEN THE FLESH OF 610 TRIED TO SWEEP OUT. We could hear the screams of 2973... Then silence. Dead silence. Then my god I can never forget that laughter. Mocking. Terrifying. Amused. Then disappointed... Then my goodness.. everything blacked out. Power outage. Then RED FLASHES EVERYONE. RED ALERT. THE SPEAKER WAS SCREAMING INTO EVERYONE'S SOUL 'Evacuation is under progress' THEN THE SAME LAUGHTER. BUT MORE DISTORTED. I know I can't get out of this mess. It'll get me no matter what. Anyways, then the walls of the building started to bleed the flesh of 610. The goo of 035 was leaking along with it... Oh my god... The gaurds... The guards... Some started shooting like crazy at everyone. Even themselves and laughing... Oh my god. That amusing laughter... It sounded artificial...
    """

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