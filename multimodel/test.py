import pyttsx3

engine = pyttsx3.init()  # Initialize TTS engine
engine.say("Maru naam Manav Che. Tu kon che?")  # Convert text to audio
engine.runAndWait()  # Play audio