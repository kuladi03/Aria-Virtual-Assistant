import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import logging
import requests
from bs4 import BeautifulSoup

class Assistant_Backend:
    def __init__(self):
        logging.basicConfig(filename='aadhya_log.txt', level=logging.INFO)

        self.engine = pyttsx3.init('sapi5')
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[1].id)

    def speak(self, audio):
        """Function to speak the given audio."""
        self.engine.say(audio)
        self.engine.runAndWait()

    def log_event(self, event):
        """Function to log events with timestamps."""
        logging.info(f"[{datetime.datetime.now()}] {event}")

    def wish_me(self):
        """Function to greet the user based on the time of day."""
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            greeting = "Good Morning!"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"

        print(greeting)
        self.speak(f"{greeting} I am Aadhya. Please tell me how may I help you")
        self.log_event("Aadhya started.")

    def take_command(self):
        """Function to take microphone input from the user and return string output."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source)

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            self.log_event(f"User said: {query}")
        except Exception as e:
            self.speak("Say that again please...")
            print("Say that again please...")
            self.log_event("Voice recognition error.")
            return "None"
        return query.lower()

    def open_website(self, query):
        """Function to open websites or perform searches based on user input."""
        if 'open' in query:
            if query[0:4] == "open":
                query = query[5:]
                webbrowser.open(query + ".com")
                self.log_event(f"Opened website: {query}")
        elif '.com' in query:
            webbrowser.open(query)
            self.log_event(f"Opened website: {query}")
        elif 'search' in query:
            search_query = query.replace('search', '')
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
            self.log_event(f"Performed web search: {search_query}")
        elif 'video' in query:
            search_query = query.replace('video', '')
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
            self.log_event(f"Searching for video: {search_query}")

    def play_music(self):
        """Function to play music from a specified directory."""
        music_dir = 'C:\\Users\\Aditya\\Music'
        songs = os.listdir(music_dir)
        print(songs)

        if songs:
            os.startfile(os.path.join(music_dir, songs[0]))
            self.log_event("Played music.")
        else:
            self.speak("No music files found.")
            self.log_event("No music files found.")

    def get_time(self):
        """Function to get the current time and speak it."""
        str_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(str_time)
        self.speak(f"Aadhya here. The time is {str_time}")
        self.log_event(f"Requested the time.")

    def send_email(self, to, content):
        """Function to send an email to the specified recipient."""
        try:
            self.speak("Please enter your email address:")
            email = input("Enter your email: ")
            self.log_event(f"Entered email address: {email}")

            self.speak("Please enter your email password:")
            password = input("Enter your email password: ")
            self.log_event("Entered email password.")

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()

            server.login(email, password)
            server.sendmail(email, to, content)
            server.close()
            self.speak("Email has been sent!")
            self.log_event(f"Sent email to: {to}")
        except Exception as e:
            print(e)
            self.speak("Sorry, I am not able to send this email")
            self.log_event("Error sending email.")

    def get_weather(self):
        """Function to get weather information for a specified city."""
        try:
            self.speak("Please enter the city for weather information:")
            city = input("Enter city: ")
            self.log_event(f"Requested weather information for city: {city}")

            # You can replace the API_KEY with your own OpenWeatherMap API key
            API_KEY = 'YOUR_OPENWEATHERMAP_API_KEY'
            BASE_URL = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'

            response = requests.get(BASE_URL)
            data = response.json()

            if data['cod'] != '404':
                main_info = data['main']
                temperature = main_info['temp']
                humidity = main_info['humidity']
                description = data['weather'][0]['description']

                self.speak(
                    f"The temperature in {city} is {temperature} Kelvin with {humidity}% humidity. The weather is {description}.")
                self.log_event(f"Received weather information for {city}.")
            else:
                self.speak(f"Sorry, I couldn't find weather information for {city}")
        except Exception as e:
            print(e)
            self.speak("Sorry, I couldn't find weather information")
            self.log_event("Error finding Weather.")

    def play_spotify(self, search_query):
        """Function to play a song on Spotify using web scraping."""
        try:
            # Searching for the song on Spotify using DuckDuckGo search
            search_url = f"https://duckduckgo.com/html/?q=site%3Aspotify.com+{search_query}+song"
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            first_result = soup.find('a', {'class': 'result__url__domain'})
            spotify_link = first_result.get('href') if first_result else None

            if spotify_link:
                webbrowser.open(spotify_link)
                self.speak(f"Playing {search_query} on Spotify.")
                self.log_event(f"Playing {search_query} on Spotify.")
            else:
                self.speak(f"Sorry, I couldn't find {search_query} on Spotify.")
                self.log_event(f"Error finding {search_query} on Spotify.")
        except Exception as e:
            print(e)
            self.speak("Sorry, I am not able to play this song on Spotify.")
            self.log_event("Error playing song on Spotify.")


if __name__ == "__main__":
    assistant = Assistant_Backend()
    assistant.wish_me()

    while True:
        query = assistant.take_command().lower()

        if 'open' in query or 'what is' in query or 'video' in query or 'search' in query:
            assistant.open_website(query)
        elif 'play music' in query:
            assistant.play_music()
        elif 'time' in query:
            assistant.get_time()
        elif 'send email' in query:
            assistant.speak("What should I say?")
            content = assistant.take_command()
            assistant.speak("To whom I am supposed to send this email, please type their Email: ")
            to = input("")
            assistant.send_email(to, content)
        elif 'weather' in query:
            assistant.get_weather()
        elif 'spotify' in query and 'play' in query:
            search_query = query.replace('spotify', '').replace('play', '')
            assistant.play_spotify(search_query)
        # Add more conditionals for other tasks...

        elif 'bye' in query:
            assistant.speak("See you later")
            print("See you later!!!")
            assistant.log_event("Aadhya stopped.")
            break
