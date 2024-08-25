import requests
import tkinter as tk
from functions.online_ops import (find_my_ip, get_latest_news, get_random_advice, get_random_joke, get_trending_movies,
    get_weather_report, play_on_youtube, search_on_google, search_on_wikipedia, send_email, send_whatsapp_message)
import pyttsx3
import speech_recognition as sr
from datetime import datetime
from functions.os_ops import open_calculator, open_camera, open_cmd, open_notepad, open_discord
from random import choice
from utils import opening_text
from pprint import pprint
import logging

# Configure logging
logging.basicConfig(filename='aria_assistant.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USERNAME = "Adi"
BOTNAME = "Aria"

engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 190)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    """Used to speak whatever text is passed to it."""
    engine.say(text)
    engine.runAndWait()

def greet_user():
    """Greets the user according to the time."""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        speak(f"Good Morning {USERNAME}")
    elif 12 <= hour < 16:
        speak(f"Good Afternoon {USERNAME}")
    elif 16 <= hour < 19:
        speak(f"Good Evening {USERNAME}")
    else:
        speak(f"Good Night {USERNAME}")
    speak(f"I am {BOTNAME}. How may I assist you?")

def take_user_input():
    """Takes user input, recognizes it using Speech Recognition module, and converts it into text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening....')
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print('Recognizing...')
        query = r.recognize_google(audio, language='en-in')
        if 'exit' in query or 'stop' in query:
            hour = datetime.now().hour
            if hour >= 21 or hour < 6:
                speak("Good night sir, take care!")
            else:
                speak('Have a good day sir!')
            exit()
        else:
            speak(choice(opening_text))
    except sr.UnknownValueError:
        speak('Sorry, I could not understand. Could you please say that again?')
        logging.error("Speech recognition could not understand audio")
        query = 'None'
    except sr.RequestError as e:
        speak('Sorry, there was an error with the speech recognition service.')
        logging.error(f"Speech recognition service error: {e}")
        query = 'None'
    return query

def handle_command(query):
    """Handles commands based on user input."""
    if 'open notepad' in query:
        open_notepad()
    elif 'open discord' in query:
        open_discord()
    elif 'open command prompt' in query or 'open cmd' in query:
        open_cmd()
    elif 'open camera' in query:
        open_camera()
    elif 'open calculator' in query:
        open_calculator()
    elif 'ip address' in query:
        ip_address = find_my_ip()
        speak(f'Your IP Address is {ip_address}. For your convenience, I am printing it on the screen sir.')
        print(f'Your IP Address is {ip_address}')
    elif 'wikipedia' in query:
        speak('What do you want to search on Wikipedia, sir?')
        search_query = take_user_input().lower()
        results = search_on_wikipedia(search_query)
        speak(f"According to Wikipedia, {results}")
        speak("For your convenience, I am printing it on the screen sir.")
        print(results)
    elif 'youtube' in query:
        speak('What do you want to play on Youtube, sir?')
        video = take_user_input().lower()
        play_on_youtube(video)
    elif 'search on google' in query:
        speak('What do you want to search on Google, sir?')
        query = take_user_input().lower()
        search_on_google(query)
    elif "send whatsapp message" in query:
        speak('On what number should I send the message sir? Please enter in the console: ')
        number = input("Enter the number: ")
        speak("What is the message sir?")
        message = take_user_input().lower()
        send_whatsapp_message(number, message)
        speak("I've sent the message sir.")
    elif "send an email" in query:
        speak("On what email address do I send sir? Please enter in the console: ")
        receiver_address = input("Enter email address: ")
        speak("What should be the subject sir?")
        subject = take_user_input().capitalize()
        speak("What is the message sir?")
        message = take_user_input().capitalize()
        if send_email(receiver_address, subject, message):
            speak("I've sent the email sir.")
        else:
            speak("Something went wrong while I was sending the mail. Please check the error logs sir.")
            logging.error("Failed to send email")
    elif 'joke' in query:
        speak("Hope you like this one sir")
        joke = get_random_joke()
        speak(joke)
        speak("For your convenience, I am printing it on the screen sir.")
        pprint(joke)
    elif "advice" in query:
        speak("Here's an advice for you, sir")
        advice = get_random_advice()
        speak(advice)
        speak("For your convenience, I am printing it on the screen sir.")
        pprint(advice)
    elif "trending movies" in query:
        trending_movies = get_trending_movies()
        speak(f"Some of the trending movies are: {', '.join(trending_movies)}")
        speak("For your convenience, I am printing it on the screen sir.")
        print(*trending_movies, sep='\n')
    elif 'news' in query:
        latest_news = get_latest_news()
        speak("I'm reading out the latest news headlines, sir")
        speak(latest_news)
        speak("For your convenience, I am printing it on the screen sir.")
        print(*latest_news, sep='\n')
    elif 'weather' in query:
        ip_address = find_my_ip()
        city = requests.get(f"https://ipapi.co/{ip_address}/city/").text
        speak(f"Getting weather report for your city {city}")
        weather, temperature, feels_like = get_weather_report(city)
        speak(f"The current temperature is {temperature}, but it feels like {feels_like}")
        speak(f"Also, the weather report talks about {weather}")
        speak("For your convenience, I am printing it on the screen sir.")
        print(f"Description: {weather}\nTemperature: {temperature}\nFeels like: {feels_like}")

def create_gui():
    """Create the main window for the GUI."""
    window = tk.Tk()
    window.title("Aria Assistant")
    window.geometry("400x100")
    window.resizable(False, False)
    window.configure(bg="#f0f0f0")

    button_frame = tk.Frame(window, bg="#d3d3d3", highlightthickness=2, highlightbackground="#999999")
    button_frame.pack(padx=10, pady=10)

    return window

def create_voice_button(window):
    """Create a button to listen for commands."""
    voice_button = tk.Button(window, text="Listen", command=lambda: handle_command(take_user_input().lower()),
                             font=("Arial", 14, "bold"), bg="#cccccc", activebackground="#bbbbbb", bd=0)
    voice_button.pack(fill=tk.BOTH, expand=True)

if __name__ == '__main__':
    greet_user()
    window = create_gui()
    create_voice_button(window)
    window.mainloop()