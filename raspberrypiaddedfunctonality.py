from openai import OpenAI
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import webbrowser
import datetime
import requests
import random
from dotenv import load_dotenv
import os
import RPi.GPIO as GPIO
from time import sleep

# GPIO Configuration
RED_PIN = 26
GREEN_PIN = 20
BLUE_PIN = 21
PWM_FREQ = 100

# PWM objects
red_pwm = None
green_pwm = None  # Fixed typo from 'green_pmw'
blue_pwm = None

# Initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def setup_led():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_PIN, GPIO.OUT)
    GPIO.setup(GREEN_PIN, GPIO.OUT)
    GPIO.setup(BLUE_PIN, GPIO.OUT)
    
    global red_pwm, green_pwm, blue_pwm
    red_pwm = GPIO.PWM(RED_PIN, PWM_FREQ)
    green_pwm = GPIO.PWM(GREEN_PIN, PWM_FREQ)
    blue_pwm = GPIO.PWM(BLUE_PIN, PWM_FREQ)
    
    red_pwm.start(0)
    green_pwm.start(0)
    blue_pwm.start(0)

def set_color(red, green, blue):
    red_pwm.ChangeDutyCycle(red / 255 * 100)
    green_pwm.ChangeDutyCycle(green / 255 * 100)
    blue_pwm.ChangeDutyCycle(blue / 255 * 100)

def turn_off():
    red_pwm.ChangeDutyCycle(0)
    green_pwm.ChangeDutyCycle(0)
    blue_pwm.ChangeDutyCycle(0)

def cleanup():
    turn_off()
    red_pwm.stop()
    green_pwm.stop()
    blue_pwm.stop()
    GPIO.cleanup()

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
        query = command.split("search google for ")[-1]
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak(f"Searching Google for: {query}")
    
    elif "search youtube for" in command:
        query = command.split("search youtube for ")[-1]
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        speak(f"Searching YouTube for: {query}")
    
    elif "tell me a joke" in command:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why don't skeletons fight each other? They don't have the guts."
        ]
        speak(random.choice(jokes))
    
    elif "time" in command or "what time is it" in command:
        now = datetime.datetime.now()
        speak(f"The current time is {now.strftime('%H:%M')}.")
    
    elif "weather" in command:
        fetch_weather()
    
    elif "red" in command:
        set_color(255, 0, 0)
        speak("Setting color to red")
    
    elif "green" in command:
        set_color(0, 255, 0)
        speak("Setting color to green")
    
    elif "blue" in command:
        set_color(0, 0, 255)
        speak("Setting color to blue")
    
    elif "yellow" in command:
        set_color(255, 255, 0)
        speak("Setting color to yellow")
    
    elif "purple" in command:
        set_color(128, 0, 128)
        speak("Setting color to purple")
    
    elif "turn off led" in command:
        turn_off()
        speak("LED turned off")
    
    else:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": command}]
        )
        response = completion.choices[0].message.content
        speak(response)

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

if __name__ == "__main__":
    setup_led()
    speak("Hello! How can I help you today?")
    
    try:
        while True:
            command = listen()
            if "exit" in command:
                speak("Goodbye!")
                break
            handle_command(command)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
