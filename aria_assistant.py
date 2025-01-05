import requests
from functions.online_ops import (
    find_my_ip, get_latest_news, get_random_advice, get_random_joke, get_trending_movies,
    get_weather_report, play_on_youtube, search_on_google, search_on_wikipedia, send_email, send_whatsapp_message
)
import pyttsx3
import speech_recognition as sr
from datetime import datetime
from functions.os_ops import open_calculator, open_camera, open_cmd, open_notepad, open_discord
from random import choice
from utils import opening_text
from pprint import pprint
import logging
from transformers import pipeline

# Configure logging
logging.basicConfig(filename='aria_assistant.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USERNAME = "Adi"
BOTNAME = "Aria"

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen for user input."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        logging.error(f"Error recognizing speech: {e}")
        speak("Sorry, I didn't catch that. Could you please repeat?")
        return "None"
    return query

# Initialize Hugging Face pipeline for question answering
qa_pipeline = pipeline("question-answering")

def ask_huggingface(question):
    """Use Hugging Face model to generate a response to the question."""
    context = "This is a virtual assistant named Aria. It can perform various tasks such as fetching the latest news, getting weather reports, playing videos on YouTube, and more."
    result = qa_pipeline(question=question, context=context)
    return result['answer']

def handle_query(query):
    """Handle user query using AI agents."""
    if 'ip address' in query:
        ip_address = find_my_ip()
        speak(f"Your IP address is {ip_address}")
    elif 'latest news' in query:
        news = get_latest_news()
        speak("Here are the latest news headlines")
        pprint(news)
    elif 'advice' in query:
        advice = get_random_advice()
        speak(advice)
    elif 'joke' in query:
        joke = get_random_joke()
        speak(joke)
    elif 'trending movies' in query:
        movies = get_trending_movies()
        speak("Here are the trending movies")
        pprint(movies)
    elif 'weather' in query:
        speak("Please tell me the city name")
        city = listen()
        weather = get_weather_report(city)
        speak(weather)
    elif 'play on youtube' in query:
        speak("What do you want to play on YouTube?")
        video = listen()
        play_on_youtube(video)
    elif 'search on google' in query:
        speak("What do you want to search on Google?")
        search_query = listen()
        search_on_google(search_query)
    elif 'search on wikipedia' in query:
        speak("What do you want to search on Wikipedia?")
        search_query = listen()
        summary = search_on_wikipedia(search_query)
        speak(summary)
    elif 'send email' in query:
        speak("To whom do you want to send the email?")
        recipient = listen()
        speak("What is the subject of the email?")
        subject = listen()
        speak("What should be the content of the email?")
        content = listen()
        send_email(recipient, subject, content)
    elif 'send whatsapp message' in query:
        speak("To whom do you want to send the WhatsApp message?")
        recipient = listen()
        speak("What should be the content of the message?")
        content = listen()
        send_whatsapp_message(recipient, content)
    elif 'open calculator' in query:
        open_calculator()
    elif 'open camera' in query:
        open_camera()
    elif 'open command prompt' in query:
        open_cmd()
    elif 'open notepad' in query:
        open_notepad()
    elif 'open discord' in query:
        open_discord()
    else:
        # Use Hugging Face for handling unknown queries
        response = ask_huggingface(query)
        speak(response)

def main():
    """Main function to run the assistant."""
    speak(f"Hello {USERNAME}, I am {BOTNAME}. How can I assist you today?")
    while True:
        query = listen().lower()
        if 'exit' in query or 'stop' in query:
            speak("Goodbye!")
            break
        handle_query(query)

if __name__ == "__main__":
    main()