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
        update_chat(f"Aria: Good Morning {USERNAME}", "left")
    elif 12 <= hour < 16:
        speak(f"Good Afternoon {USERNAME}")
        update_chat(f"Aria: Good Afternoon {USERNAME}", "left")
    elif 16 <= hour < 19:
        speak(f"Good Evening {USERNAME}")
        update_chat(f"Aria: Good Evening {USERNAME}", "left")
    else:
        speak(f"Good Night {USERNAME}")
        update_chat(f"Aria: Good Night {USERNAME}", "left")
    speak(f"I am {BOTNAME}. How may I assist you?")
    update_chat(f"Aria: I am {BOTNAME}. How may I assist you?", "left")

def take_user_input():
    """Takes user input, recognizes it using Speech Recognition module, and converts it into text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        update_chat('Aria: Listening...', "left")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        update_chat('Aria: Recognizing...', "left")
        query = r.recognize_google(audio, language='en-in')
        update_chat(f"You: {query}", "right")
        if 'exit' in query or 'stop' in query:
            hour = datetime.now().hour
            if hour >= 21 or hour < 6:
                speak("Good night sir, take care!")
                update_chat("Aria: Good night sir, take care!", "left")
            else:
                speak('Have a good day sir!')
                update_chat("Aria: Have a good day sir!", "left")
            exit()
        else:
            speak(choice(opening_text))
    except sr.UnknownValueError:
        speak('Sorry, I could not understand. Could you please say that again?')
        update_chat("Aria: Sorry, I could not understand. Could you please say that again?", "left")
        logging.error("Speech recognition could not understand audio")
        query = 'None'
    except sr.RequestError as e:
        speak('Sorry, there was an error with the speech recognition service.')
        update_chat("Aria: Sorry, there was an error with the speech recognition service.", "left")
        logging.error(f"Speech recognition service error: {e}")
        query = 'None'
    return query

def update_chat(message, alignment):
    """Updates the chat window with messages."""
    chat_window.config(state=tk.NORMAL)
    chat_bubble = tk.Frame(chat_window, bg='#EEE', bd=5)
    
    # Adjust the alignment based on the sender
    if alignment == "left":
        chat_bubble.pack(anchor="w", padx=5, pady=5)
    else:
        chat_bubble.pack(anchor="e", padx=5, pady=5)
    
    label = tk.Label(chat_bubble, text=message, bg="#F7F7F7", font=("Helvetica", 14), wraplength=400)
    label.pack()

    chat_window.window_create(tk.END, window=chat_bubble)
    chat_window.insert(tk.END, "\n")
    chat_window.config(state=tk.DISABLED)
    chat_window.yview(tk.END)

def handle_command(query):
    """Handles commands based on user input."""
    if 'open notepad' in query:
        open_notepad()
        update_chat(f"Aria: Opening Notepad", "left")
    elif 'open discord' in query:
        open_discord()
        update_chat(f"Aria: Opening Discord", "left")
    elif 'open command prompt' in query or 'open cmd' in query:
        open_cmd()
        update_chat(f"Aria: Opening Command Prompt", "left")
    elif 'open camera' in query:
        open_camera()
        update_chat(f"Aria: Opening Camera", "left")
    elif 'open calculator' in query:
        open_calculator()
        update_chat(f"Aria: Opening Calculator", "left")
    elif 'ip address' in query:
        ip_address = find_my_ip()
        speak(f'Your IP Address is {ip_address}. For your convenience, I am printing it on the screen sir.')
        update_chat(f"Aria: Your IP Address is {ip_address}", "left")
    elif 'wikipedia' in query:
        speak('What do you want to search on Wikipedia, sir?')
        update_chat("Aria: What do you want to search on Wikipedia, sir?", "left")
        search_query = take_user_input().lower()
        results = search_on_wikipedia(search_query)
        speak(f"According to Wikipedia, {results}")
        update_chat(f"Aria: According to Wikipedia, {results}", "left")
    elif 'youtube' in query:
        speak('What do you want to play on Youtube, sir?')
        update_chat("Aria: What do you want to play on Youtube, sir?", "left")
        video = take_user_input().lower()
        play_on_youtube(video)
        update_chat(f"Aria: Playing {video} on YouTube", "left")
    elif 'search on google' in query:
        speak('What do you want to search on Google, sir?')
        update_chat("Aria: What do you want to search on Google, sir?", "left")
        search_query = take_user_input().lower()
        search_on_google(search_query)
        update_chat(f"Aria: Searching {search_query} on Google", "left")
    elif "send whatsapp message" in query:
        speak('On what number should I send the message sir? Please enter in the console: ')
        update_chat("Aria: On what number should I send the message sir? Please enter in the console.", "left")
        number = input("Enter the number: ")
        speak("What is the message sir?")
        update_chat("Aria: What is the message sir?", "left")
        message = take_user_input().lower()
        send_whatsapp_message(number, message)
        speak("I've sent the message sir.")
        update_chat("Aria: I've sent the message.", "left")
    elif "send an email" in query:
        speak("On what email address do I send sir? Please enter in the console: ")
        update_chat("Aria: On what email address do I send sir? Please enter in the console.", "left")
        receiver_address = input("Enter email address: ")
        speak("What should be the subject sir?")
        update_chat("Aria: What should be the subject sir?", "left")
        subject = take_user_input().capitalize()
        speak("What is the message sir?")
        update_chat("Aria: What is the message sir?", "left")
        message = take_user_input().capitalize()
        if send_email(receiver_address, subject, message):
            speak("I've sent the email sir.")
            update_chat("Aria: I've sent the email.", "left")
        else:
            speak("Something went wrong while I was sending the mail. Please check the error logs sir.")
            update_chat("Aria: Something went wrong while I was sending the mail. Please check the error logs sir.", "left")
            logging.error("Failed to send email")
    elif 'joke' in query:
        speak("Hope you like this one sir")
        update_chat("Aria: Hope you like this one sir", "left")
        joke = get_random_joke()
        speak(joke)
        update_chat(f"Aria: {joke}", "left")
    elif "advice" in query:
        speak("Here's an advice for you, sir")
        update_chat("Aria: Here's an advice for you, sir", "left")
        advice = get_random_advice()
        speak(advice)
        update_chat(f"Aria: {advice}", "left")
    elif "trending movies" in query:
        speak(f"Some of the trending movies are: {get_trending_movies()}")
        update_chat(f"Aria: Some of the trending movies are: {get_trending_movies()}", "left")
    elif 'news' in query:
        speak(f"I'm reading out the latest news headlines, sir")
        update_chat("Aria: I'm reading out the latest news headlines, sir", "left")
        speak(get_latest_news())
    elif 'weather' in query:
        speak(f"Which city's weather report you'd like to know?")
        update_chat("Aria: Which city's weather report you'd like to know?", "left")
        city = take_user_input()
        report = get_weather_report(city)
        speak(report)
        update_chat(f"Aria: {report}", "left")
    elif 'ip address' in query:
        ip_address = find_my_ip()
        speak(f'Your IP Address is {ip_address}')
        update_chat(f"Aria: Your IP Address is {ip_address}", "left")
    else:
        speak("Sorry, I don't know that yet.")
        update_chat("Aria: Sorry, I don't know that yet.", "left")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Aria Chat Interface")

    # Frame for the chat window
    chat_window_frame = tk.Frame(root)
    chat_window_frame.pack(expand=True, fill=tk.BOTH)

    # Scrollbar for the chat window
    chat_scrollbar = tk.Scrollbar(chat_window_frame)
    chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Chat window text widget
    chat_window = tk.Text(chat_window_frame, yscrollcommand=chat_scrollbar.set, state=tk.DISABLED, wrap=tk.WORD)
    chat_window.pack(expand=True, fill=tk.BOTH)
    chat_scrollbar.config(command=chat_window.yview)

    greet_user()

    # Frame for user input
    input_frame = tk.Frame(root)
    input_frame.pack()

    # Entry widget for typing input
    user_input = tk.Entry(input_frame, font=("Helvetica", 14), width=50)
    user_input.pack(side=tk.LEFT, padx=10, pady=10)

    # Button to send input
    send_button = tk.Button(input_frame, text="Send", command=lambda: handle_command(user_input.get()), bg="lightblue")
    send_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Button to listen for voice input
    listen_button = tk.Button(input_frame, text="Listen", command=take_user_input, bg="lightgreen")
    listen_button.pack(side=tk.RIGHT, padx=10, pady=10)

    root.mainloop()
