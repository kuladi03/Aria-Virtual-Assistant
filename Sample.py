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
            self.log_event("Logged in to email.")

            server.sendmail(email, to, content)
            self.log_event(f"Email sent to: {to}")

            server.close()
            self.speak("Email has been sent!")
        except Exception as e:
            print(e)
            self.speak("Sorry. I am not able to send this email at the moment.")
            self.log_event("Error sending email.")

    def get_wiki_info(self, query):
        self.speak("Searching Wikipedia...")
        query = query.replace("wikipedia", "")
        results = wikipedia.summary(query, sentences=2)
        self.speak("According to Wikipedia")
        self.speak(results)

    def get_weather(self, query):
        api_key = os.environ.get('WEATHER_API_KEY')
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        city_name = query.split("in")[-1].strip()
        complete_url = f"{base_url}?q={city_name}&appid={api_key}"

        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] != "404":
            main_data = data["main"]
            temperature = main_data["temp"]
            humidity = main_data["humidity"]

            self.speak(f"The temperature in {city_name} is {temperature} Kelvin with humidity {humidity}%.")
            self.log_event(f"Requested weather information for: {city_name}")
        else:
            self.speak("Sorry, I couldn't find the weather information for the specified location.")
            self.log_event(f"Error getting weather information for: {city_name}")

    def translate_text(self, query):
        translator = Translator()
        query = query.replace("translate", "")
        translation = translator.translate(query, dest='en')
        self.speak(f"The translated text is: {translation.text}")
        self.log_event(f"Translated text: {query}")

    def run_command(self, command):
        if 'wikipedia' in command:
            self.get_wiki_info(command)
        elif 'open' in command or 'search' in command or '.com' in command or 'video' in command:
            self.open_website(command)
        elif 'play music' in command:
            self.play_music()
        elif 'time' in command:
            self.get_time()
        elif 'send email' in command:
            self.speak("Whom should I send the email to?")
            to = input("Enter the email address: ")
            self.log_event(f"Entered email recipient: {to}")
            self.speak("What should I say?")
            content = input("Enter the email content: ")
            self.send_email(to, content)
        elif 'weather' in command:
            self.get_weather(command)
        elif 'translate' in command:
            self.translate_text(command)
        elif 'logout' in command:
            self.logout()

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aria - Your Virtual Assistant")
        self.geometry("500x300")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text="Aria - Your Virtual Assistant", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.login_button = ttk.Button(self, text="Login", command=self.show_login)
        self.login_button.pack(pady=10)

        self.signup_button = ttk.Button(self, text="Sign Up", command=self.show_signup)
        self.signup_button.pack(pady=10)

        self.logout_button = ttk.Button(self, text="Logout", command=self.logout)
        self.stop_button = ttk.Button(self, text="Stop Listening", command=self.stop_listening)

        self.text_var = tk.StringVar()
        self.text_var.set("Press Login to continue...")
        self.text_label = tk.Label(self, textvariable=self.text_var, wraplength=400)
        self.text_label.pack(pady=20)

        self.assistant_backend = Assistant_Backend()

    def show_login(self):
        self.login_window = tk.Toplevel(self)
        self.login_window.title("Login")
        self.login_window.geometry("300x200")

        self.login_label = tk.Label(self.login_window, text="Enter your credentials:")
        self.login_label.pack(pady=10)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.username_entry = tk.Entry(self.login_window, textvariable=self.username_var, width=30)
        self.password_entry = tk.Entry(self.login_window, textvariable=self.password_var, width=30, show="*")

        self.username_entry.pack(pady=10)
        self.password_entry.pack(pady=10)

        self.login_button = ttk.Button(self.login_window, text="Login", command=self.login)
        self.login_button.pack(pady=10)

    def show_signup(self):
        self.signup_window = tk.Toplevel(self)
        self.signup_window.title("Sign Up")
        self.signup_window.geometry("300x200")

        self.signup_label = tk.Label(self.signup_window, text="Create a new account:")
        self.signup_label.pack(pady=10)

        self.new_username_var = tk.StringVar()
        self.new_password_var = tk.StringVar()

        self.new_username_entry = tk.Entry(self.signup_window, textvariable=self.new_username_var, width=30)
        self.new_password_entry = tk.Entry(self.signup_window, textvariable=self.new_password_var, width=30, show="*")

        self.new_username_entry.pack(pady=10)
        self.new_password_entry.pack(pady=10)

        self.signup_button = ttk.Button(self.signup_window, text="Sign Up", command=self.signup)
        self.signup_button.pack(pady=10)

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if self.assistant_backend.login(username, password):
            self.login_button.pack_forget()
            self.logout_button.pack(pady=10)
            self.text_var.set(f"Welcome, {username}!")
            self.assistant_backend.wish_me()
        else:
            self.text_var.set("Invalid credentials. Please try again.")

    def signup(self):
        new_username = self.new_username_var.get()
        new_password = self.new_password_var.get()

        if self.assistant_backend.signup_user(new_username, new_password):
            self.login_button.pack_forget()
            self.logout_button.pack(pady=10)
        else:
            self.text_var.set("User registration failed. Please try again.")

    def logout(self):
        self.login_button.pack(pady=10)
        self.logout_button.pack_forget()
        self.text_var.set("Press Login to continue...")
        self.assistant_backend.logout()

    def start_listening(self):
        self.start_button = ttk.Button(self, text="Start Listening", command=self.assistant_backend.start_listening)
        self.start_button.pack(pady=10)

    def stop_listening(self):
        if hasattr(self, 'listening_thread') and self.listening_thread.is_alive():
            self.stop_button.pack_forget()
            self.start_button.pack(pady=10)
            self.text_var.set("Press Login to continue...")
            self.assistant_backend.logout()

if __name__ == "__main__":
    app = GUI()
    app.start_listening()
    app.mainloop()
