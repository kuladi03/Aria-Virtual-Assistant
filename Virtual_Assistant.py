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
import tkinter as tk
from tkinter import ttk
from googletrans import Translator
import cv2
import mysql.connector
from typing import Optional
import threading
import logging
from logging.handlers import RotatingFileHandler


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Assistant_Backend:
    def __init__(self):
        self.current_user = None
        self.connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME')
        )
        self.cursor = self.connection.cursor()
        logging.basicConfig(filename='Aria_log.txt', level=logging.INFO)
        self.engine = pyttsx3.init('sapi5')
        indian_voice = None

        for voice in self.voices:
            if 'indian' in voice.languages[0].lower():
                indian_voice = voice.id
                break

        if indian_voice:
            self.engine.setProperty('voice', indian_voice)
        else:
            self.engine.setProperty('voice', self.voices[1].id)
        self.gui = None  
        self.signup_window = None  
        log_file = 'Aria_log.txt'
        handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def start_listening(self, gui): 
        self.gui = gui
        self.gui.start_button.pack_forget()
        self.gui.stop_button.pack(pady=10)

        self.listening_thread = threading.Thread(target=self.listen_continuous)
        self.listening_thread.start()

    def listen_continuous(self):
        while True:
            try:
                query = self.take_command()
                self.gui.text_var.set(f"User said: {query}")
                self.process_command(query)

                if hasattr(self.gui, 'stop_button') and self.gui.stop_button.winfo_ismapped():
                    continue
                else:
                    break 
            except KeyboardInterrupt:
                break


    def create_user_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    password VARCHAR(50)
                )
            """)
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")


    def authorize_user(self, username, password):
        try:
            self.cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = self.cursor.fetchone()

            if user:
                self.current_user = User(username=user[1], password=user[2])
                return True
            else:
                return False
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False

    def add_user(self, username, password):
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.connection.commit()
            self.current_user = User(username=username, password=password)
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
        
    def signup_user(self, username, password):
        if self.add_user(username, password):
            self.gui.text_var.set(f"User {username} registered successfully.")
            self.signup_window.destroy()  
            self.gui.login_button.pack_forget()
            self.gui.logout_button.pack(pady=10)
            self.wish_me()
            return True
        else:
            self.gui.text_var.set("User registration failed. Please try again.")
            return False

    def speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    def log_event(self, event):
        logging.info(f"[{datetime.datetime.now()}] {event}")

    def wish_me(self):
        if self.current_user:
            self.speak(f"Hello, {self.current_user.username}! How may I assist you?")
            self.log_event(f"{self.current_user.username} started the session.")
        else:
            self.speak("Hello! I am Aria. Please log in to continue.")
            self.log_event("Aria started.")

    def login(self, username, password):
        if self.authorize_user(username, password):
            return True
        return False


    def logout(self):
        if self.current_user:
            self.log_event(f"{self.current_user.username} ended the session.")
            self.current_user = None

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.pause_threshold = 1
            audio = r.listen(source, timeout=5)

        try:
            query = r.recognize_google(audio, language='en-in')
            self.log_event(f"User said: {query}")
        except Exception as e:
            self.speak("Say that again please...")
            self.log_event("Voice recognition error.")
            return "None"
        return query.lower()

    def open_website(self, query):
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
        music_dir = 'C:\\Users\\Aditya\\Music'
        songs = os.listdir(music_dir)

        if songs:
            os.startfile(os.path.join(music_dir, songs[0]))
            self.log_event("Played music.")
        else:
            self.speak("No music files found.")
            self.log_event("No music files found.")

    def get_time(self):
        str_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.speak(f"Aria here. The time is {str_time}")
        self.log_event(f"Requested the time.")

    def send_email(self, to, content):
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
        try:
            self.speak("Please enter the city for weather information:")
            city = input("Enter city: ")
            self.log_event(f"Requested weather information for city: {city}")

            API_KEY = 'YOUR_OPENWEATHERMAP_API_KEY'
            BASE_URL = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'

            response = requests.get(BASE_URL)
            response.raise_for_status() 
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
        except requests.RequestException as req_err:
            print(f"Request error: {req_err}")
            self.speak("Sorry, there was an error fetching weather information.")
            self.log_event(f"Error fetching weather information: {req_err}")
        except Exception as e:
            print(f"Error: {e}")
            self.speak("Sorry, I couldn't find weather information.")
            self.log_event("Error finding Weather.")


    def play_spotify(self, search_query):
        try:
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

    def search_wikipedia(self, query):
        try:
            result = wikipedia.summary(query, sentences=2)
            self.speak(f"According to Wikipedia, {result}")
            self.log_event(f"Looked up {query} on Wikipedia.")
        except Exception as e:
            print(e)
            self.speak(f"Sorry, I couldn't find information about {query} on Wikipedia.")
            self.log_event(f"Error searching Wikipedia for {query}.")

    def set_reminder(self, reminder_text, reminder_time):
        try:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            if reminder_time > current_time:
                self.speak(f"Reminder set for {reminder_time}.")
                self.log_event(f"Set a reminder: {reminder_text} at {reminder_time}")
            else:
                self.speak("Sorry, I can't set a reminder for the past.")
        except Exception as e:
            print(e)
            self.speak("Sorry, I couldn't set the reminder.")
            self.log_event("Error setting reminder.")

    def search_news(self):
        try:
            news_url = "https://newsapi.org/v2/top-headlines"
            API_KEY = 'YOUR_NEWSAPI_ORG_API_KEY'
            parameters = {'country': 'us', 'apiKey': API_KEY}

            response = requests.get(news_url, params=parameters)
            data = response.json()

            articles = data['articles'][:5]  
            self.speak("Here are the top news headlines:")
            for i, article in enumerate(articles, start=1):
                title = article['title']
                self.speak(f"{i}. {title}")
                self.log_event(f"Read news headline: {title}")
        except Exception as e:
            print(e)
            self.speak("Sorry, I couldn't fetch the latest news.")
            self.log_event("Error fetching news.")

    def open_system_application(self, application_name):
        try:
            system_apps = {
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'calendar': 'outlookcal.exe'
                
            }

            if application_name.lower() in system_apps:
                os.system(system_apps[application_name.lower()])
                self.speak(f"Opening {application_name}.")
                self.log_event(f"Opened system application: {application_name}")
            else:
                self.speak(f"Sorry, I don't know how to open {application_name}.")
        except Exception as e:
            print(e)
            self.speak(f"Sorry, I couldn't open {application_name}.")
            self.log_event(f"Error opening system application: {application_name}")
    
    def tell_joke(self):
        joke_url = "https://official-joke-api.appspot.com/random_joke"
        response = requests.get(joke_url)
        joke_data = response.json()

        if 'setup' in joke_data and 'delivery' in joke_data:
            setup = joke_data['setup']
            delivery = joke_data['delivery']
            joke = f"{setup}\n{delivery}"
            self.speak(joke)
            self.log_event("Told a joke.")
        else:
            self.speak("Sorry, I couldn't fetch a joke at the moment.")
            self.log_event("Error fetching joke.")

    def search_youtube(self, query):
        search_url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(search_url)
        self.log_event(f"Searching YouTube for: {query}")

    def search_google(self, query):
        search_url = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_url)
        self.log_event(f"Performed a Google search for: {query}")

    def get_location(self):
        try:
            ip_url = "https://api64.ipify.org?format=json"
            response = requests.get(ip_url)
            ip_data = response.json()
            ip_address = ip_data.get("ip", "Unknown")

            location_url = f"http://ip-api.com/json/{ip_address}"
            location_data = requests.get(location_url).json()

            city = location_data.get("city", "Unknown")
            country = location_data.get("country", "Unknown")

            self.speak(f"You are currently in {city}, {country}.")
            self.log_event("Fetched user's location.")
        except Exception as e:
            print(e)
            self.speak("Sorry, I couldn't determine your location.")
            self.log_event("Error fetching location.")

    def get_quote_of_the_day(self):
        quote_url = "https://quotes.rest/qod?category=inspire"
        response = requests.get(quote_url)
        quote_data = response.json()

        if 'contents' in quote_data and 'quotes' in quote_data['contents']:
            quote = quote_data['contents']['quotes'][0]['quote']
            author = quote_data['contents']['quotes'][0]['author']
            self.speak(f"Here is a quote for you: {quote} by {author}.")
            self.log_event("Fetched the quote of the day.")
        else:
            self.speak("Sorry, I couldn't fetch a quote at the moment.")
            self.log_event("Error fetching quote of the day.")

    def play_random_song(self):
        try:
            search_url = "https://www.youtube.com/watch?v="  
            webbrowser.open(search_url)
            self.speak("Playing a random song for you.")
            self.log_event("Played a random song.")
        except Exception as e:
            print(e)
            self.speak("Sorry, I couldn't play a random song at the moment.")
            self.log_event("Error playing a random song.")
    
    def translate_text(self, text, target_language='en'):
        """
        Translate the given text to the target language using Google Translate API.
        Requires the 'googletrans' library. Install it using: pip install googletrans==4.0.0-rc1
        """
        try:
            from googletrans import Translator

            translator = Translator()
            translated_text = translator.translate(text, dest=target_language).text
            self.speak(f"The translation is: {translated_text}")
            self.log_event(f"Translated text: {text} to {target_language}")
        except Exception as e:
            print(e)
            self.speak("Sorry, I couldn't perform the translation at the moment.")
            self.log_event("Error translating text.")

    def identify_object(self):
        """
        Use the computer's camera to identify objects in real-time.
        Requires the 'opencv-python' library. Install it using: pip install opencv-python
        """
        try:
            import cv2

            camera = cv2.VideoCapture(0)
            _, image = camera.read()
            cv2.imwrite("object_identification.jpg", image)
            camera.release()

            self.speak("I captured an image. Let me identify the objects.")
            self.log_event("Captured image for object identification.")

        except Exception as e:
            print(e)
            self.speak("Sorry, I couldn't identify objects at the moment.")
            self.log_event("Error identifying objects.")

    def face_recognition(self):
        """
        Use the computer's camera for face recognition.
        Requires the 'opencv-python' library. Install it using: pip install opencv-python
        """
        try:
            import cv2

            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            camera = cv2.VideoCapture(0)
            _, frame = camera.read()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                self.speak("I see a face!")
            else:
                self.speak("I couldn't find any faces.")

            camera.release()
            self.log_event("Performed face recognition.")
        except Exception as e:
            print(e)
            self.speak("Sorry, I couldn't perform face recognition at the moment.")
            self.log_event("Error performing face recognition.")



class Assistant_GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Aria - Virtual Assistant")
        self.geometry("400x400")

        self.assistant = Assistant_Backend()

        self.label = ttk.Label(self, text="Virtual Assistant", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.response_label = ttk.Label(self, text="", font=("Helvetica", 12))
        self.response_label.pack(pady=10)

        self.text_var = tk.StringVar()
        self.text_var.set("Listening...")

        self.text_label = ttk.Label(self, textvariable=self.text_var, font=("Helvetica", 12))
        self.text_label.pack(pady=10)

        self.login_button = ttk.Button(self, text="Login", command=self.show_login_window)
        self.login_button.pack(pady=10)

        self.signup_button = ttk.Button(self, text="Sign Up", command=self.show_signup_window)
        self.signup_button.pack(pady=10)

        self.start_button = ttk.Button(self, text="Start", command=self.start_assistant)
        self.start_button.pack(pady=10)
        self.start_button.pack_forget()

        self.stop_button = ttk.Button(self, text="Stop", command=self.stop_assistant)
        self.stop_button.pack(pady=10)
        self.stop_button.pack_forget()

        self.listen_button = ttk.Button(self, text="Listen", command=self.listen_command)
        self.listen_button.pack(pady=10)

        self.login_window = None
        self.signup_window = None

    def show_login_window(self):
        self.login_window = tk.Toplevel(self)
        self.login_window.title("Login")

        ttk.Label(self.login_window, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(self.login_window, text="Password:").grid(row=1, column=0, padx=10, pady=10)

        username_entry = ttk.Entry(self.login_window)
        password_entry = ttk.Entry(self.login_window, show='*')

        username_entry.grid(row=0, column=1, padx=10, pady=10)
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        login_button = ttk.Button(self.login_window, text="Login", command=lambda: self.perform_login(username_entry.get(), password_entry.get()))
        login_button.grid(row=2, column=1, pady=10)

    def show_signup_window(self):
        self.signup_window = tk.Toplevel(self)
        self.signup_window.title("Sign Up")

        ttk.Label(self.signup_window, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(self.signup_window, text="Password:").grid(row=1, column=0, padx=10, pady=10)

        username_entry = ttk.Entry(self.signup_window)
        password_entry = ttk.Entry(self.signup_window, show='*')

        username_entry.grid(row=0, column=1, padx=10, pady=10)
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        signup_button = ttk.Button(self.signup_window, text="Sign Up", command=lambda: self.perform_signup(username_entry.get(), password_entry.get()))
        signup_button.grid(row=2, column=1, pady=10)

    def perform_login(self, username, password):
        if self.assistant.login(username, password):
            self.text_var.set(f"Logged in as: {username}")

            if self.signup_window is not None:
                self.signup_window.destroy()

            self.login_window.destroy()
            self.login_button.pack_forget()
            self.signup_button.pack_forget()
            self.start_button.pack(pady=10)
        else:
            self.text_var.set("Login failed. Please try again.")

    def perform_signup(self, username, password):
        if self.assistant.add_user(username, password):
            self.text_var.set(f"User {username} registered successfully!")
            if self.signup_window:
                self.signup_window.destroy()  
        else:
            self.text_var.set("Sign Up failed. Please try again.")

    def start_assistant(self):
        self.start_button.pack_forget()
        self.stop_button.pack(pady=10)
        self.display_assistant_response("Hello! How may I assist you?")  
        self.listen_command()  

    def stop_assistant(self):
        
        self.stop_button.pack_forget()
        self.start_button.pack(pady=10)
        self.text_var.set("Assistant stopped.")

    def listen_command(self):
        query = self.assistant.take_command()
        self.text_var.set(f"User said: {query}")
        self.process_command(query)

        if hasattr(self, 'stop_button') and self.stop_button.winfo_ismapped():
            self.after(1000, self.listen_command)  

    def display_assistant_response(self, response):
        self.response_label.config(text=response)

    def process_command(self, query):
        if 'open' in query or 'what is' in query or 'video' in query or 'search' in query:
            self.assistant.open_website(query)
        elif 'play music' in query:
            self.assistant.play_music()
        elif 'time' in query:
            self.assistant.get_time()
        elif 'send email' in query:
            self.assistant.speak("What should I say?")
            content = self.assistant.take_command()
            self.assistant.speak("To whom I am supposed to send this email, please type their Email: ")
            to = input("")
            self.assistant.send_email(to, content)
        elif 'weather' in query:
            self.assistant.get_weather()
        elif 'spotify' in query and 'play' in query:
            search_query = query.replace('spotify', '').replace('play', '')
            self.assistant.play_spotify(search_query)
        elif 'search' in query and 'wikipedia' in query:
            search_query = query.replace('search wikipedia', '')
            self.assistant.search_wikipedia(search_query)
        elif 'set reminder' in query:
            self.assistant.speak("What should be the reminder text?")
            reminder_text = self.assistant.take_command()
            self.assistant.speak("At what time should I remind you? (format: HH:MM:SS)")
            reminder_time = input("")  
            self.assistant.set_reminder(reminder_text, reminder_time)
        elif 'search news' in query:
            self.assistant.search_news()
        elif 'open' in query and 'application' in query:
            app_name = query.replace('open application', '')
            self.assistant.open_system_application(app_name)
        elif 'tell me a joke' in query:
            self.assistant.tell_joke()
        elif 'help' in query:
            self.assistant.speak("I can assist you with opening websites, playing music, checking the time, sending emails, "
                                 "getting weather information, searching Wikipedia, setting reminders, fetching news, "
                                 "opening system applications, and telling jokes. How may I help you?")
        elif 'search youtube' in query:
            search_query = query.replace('search youtube', '')
            self.assistant.search_youtube(search_query)
        elif 'google' in query:
            search_query = query.replace('search google', '')
            self.assistant.search_google(search_query)
        elif 'get location' in query:
            self.assistant.get_location()
        elif 'quote of the day' in query:
            self.assistant.get_quote_of_the_day()
        elif 'play random song' in query:
            self.assistant.play_random_song()
        elif 'translate' in query:
            text_to_translate = query.replace('translate', '')
            self.assistant.translate_text(text_to_translate)

        elif 'identify objects' in query:
            self.assistant.identify_object()

        elif 'face recognition' in query:
            self.assistant.face_recognition()
        elif 'log out' in query:
            self.text_var.set("Logged out.")
            self.assistant.logout()
            self.login_button.pack(pady=10)
            self.logout_button.pack_forget()
        else:
            self.assistant.speak("Sorry, I didn't understand that. How may I assist you?")

        self.assistant.speak("Is there anything else I can help you with?")

        new_query = self.assistant.take_command()
        self.text_var.set(f"User said: {new_query}")
        self.process_command(new_query)


if __name__ == "__main__":
    gui = Assistant_GUI()
    gui.assistant.wish_me()
    gui.mainloop()