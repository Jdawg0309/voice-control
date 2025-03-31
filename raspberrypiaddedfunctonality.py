from openai import OpenAI
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
from playsound import playsound
from pydub import AudioSegment
import webbrowser
import datetime
import requests
import random
from dotenv import load_dotenv
import os

# Initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=5)

    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower()
    except Exception as e:
        print("Error:", e)
        return ""

def search_google(command):
    query = command.split("search google for ")[-1]
    webbrowser.open(f"https://www.google.com/search?q={query}")
    speak(f"Searching Google for: {query}")

def search_youtube(command):
    query = command.split("search youtube for ")[-1]
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    speak(f"Searching YouTube for: {query}")

def tell_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don't skeletons fight each other? They don't have the guts."
    ]
    speak(random.choice(jokes))

def tell_time():
    now = datetime.datetime.now()
    speak(f"The current time is {now.strftime('%H:%M')}.")

def fetch_weather():
    weather_api_key = "781b79b4bdf6f5ce702f22f81c87a459"
    city = "New York"
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric")
        data = response.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            speak(f"Weather in {city}: {weather}, {temp}°C.")
        else:
            speak("Failed to fetch weather updates.")
    except Exception as e:
        speak(f"Error fetching weather: {e}")

def speak(text):
    tts = gTTS(text, lang="en", tld="co.uk")
    tts.save("output.mp3")

    audio = AudioSegment.from_mp3("output.mp3")
    audio.export("output.wav", format="wav")
    os.system("aplay output.wav")
    os.remove("output.mp3")
    os.remove("output.wav")

def handle_command(command):
    if not command:
        return
    
    if "search google for" in command:
        search_google(command)
    elif "search youtube for" in command:
        search_youtube(command)
    elif "tell me a joke" in command:
        tell_joke()
    elif "time" in command or "what time is it" in command:
        tell_time()
    elif "weather" in command:
        fetch_weather()
    else:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": command}]
        )
        response = completion.choices[0].message.content
        speak(response)

if __name__ == "__main__":
    speak("Hello! How can I help you today?")
    active = False
    while True:
        if not active:
            command = listen()
            if "exit" in command:
                speak("Goodbye!")
                break
            wake_words = ["hey assistant", "hey pi"]
            for wake_word in wake_words:
                if wake_word in command:
                    active = True
                    actual_command = command.split(wake_word, 1)[-1].strip()
                    if actual_command:
                        handle_command(actual_command)
                        active = False  # Require wake word again
                    else:
                        speak("How can I help you?")
                    break  # Process only the first detected wake word
        else:
            command = listen()
            if "exit" in command:
                speak("Goodbye!")
                break
            handle_command(command)
            active = False  # Require wake word again
