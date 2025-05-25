from gtts import gTTS
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import queue
import sounddevice as sd
import webbrowser
import pyttsx3
import json
from vosk import Model, KaldiRecognizer
import musicLybrary
import requests
import time
import sys
import contextlib
from pydub import AudioSegment
from pydub.playback import play
from transformers import pipeline, set_seed, logging

# Path to Vosk model
model_path = "D:\\Prottoy\\Codes\\PS FOLDERs\\MP-1\\vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    raise FileNotFoundError("Vosk model not found! Please check the path.")

model = Model(model_path)
engine = pyttsx3.init() 
newsapi="bdb98aedb87045aebaac73047f7596b6"

@contextlib.contextmanager
def suppress_stdout_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

with suppress_stdout_stderr():
    pygame.mixer.init()

# For audio input
samplerate = 16000
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def speak_old(text):
    engine.say(text)
    engine.runAndWait()

def speak(text, speed=1.1):  # speed > 1 is faster, < 1 is slower
    tts = gTTS(text)
    tts.save("temp.mp3")

    sound = AudioSegment.from_file("temp.mp3")
    faster_sound = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    }).set_frame_rate(sound.frame_rate)

    play(faster_sound)

    os.remove("temp.mp3")

def processCommand(c):
    #Opening links
    if "open google" in c.lower():
        webbrowser.open("https://www.google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://www.facebook.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com")
    # elif "open linkedin" or "open linked in" in c.lower():
    #     webbrowser.open("https://www.linkedin. or com")

    #opening musics from musicLybrary
    elif c.lower().startswith("play"):
        song = c.lower().split(" ", 1)[1].strip()  # split only once!
        link = musicLybrary.music.get(song)
        if link:
            webbrowser.open(link)
        else:
            speak(f"Sorry, '{song}' not found in your music library.")

    #fetch news
    elif "news" in c.lower():
        r= requests.get("https://newsapi.org/v2/top-headlines?country=us&apiKey=bdb98aedb87045aebaac73047f7596b6")
        if r.status_code == 200:
            data = r.json()
            articles = data.get("articles", [])
            titles = [article.get("title") for article in articles if article.get("title")]
            speak(titles)
        else:
            speak(f"Error fetching data: {r.status_code}")

    else:
        from transformers import pipeline, set_seed, logging

        # 🔇 Disable annoying logs and warnings
        logging.set_verbosity_error()

        def generate_text(prompt):
            generator = pipeline("text-generation", model="distilgpt2")
            set_seed(42)
            result = generator(
                prompt,
                max_new_tokens=50,
                truncation=True,
                pad_token_id=50256
            )
            return result[0]['generated_text']

        # CLI loop
        while True:
            if command.lower() == "exit":
                break
            print(generate_text(command), "\n")


if __name__ == "__main__":
    speak("Initializing Jarvis....")

    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16', channels=1, callback=callback):
            recognizer = KaldiRecognizer(model, samplerate)
            print("Listening for wake word...")
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    command = result.get("text", "")
                    print("Heard:", command)
                    if "jarvis" in command.lower():
                        speak("Yes?")
                        print("Jarvis Active...")
                        # Listen for the next command
                        collected_text = ""
                        while True:
                            data = q.get()
                            if recognizer.AcceptWaveform(data):
                                result = json.loads(recognizer.Result())
                                collected_text = result.get("text", "")
                                break
                        print("Command:", collected_text)
                        processCommand(collected_text)
    except KeyboardInterrupt:
        print("Exiting...")
