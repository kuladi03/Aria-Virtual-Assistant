import tkinter as tk
from tkinter import scrolledtext
import threading
from AssistantBackend import Assistant_Backend  # Import the backend module

class AssistantGUI:
    def __init__(self, master):
        self.master = master
        master.title("Aadhya Assistant")

        self.text_input = tk.Entry(master, width=50)
        self.text_input.pack(pady=10)

        self.response_display = scrolledtext.ScrolledText(master, width=60, height=10)
        self.response_display.pack(pady=10)

        self.action_label = tk.Label(master, text="Listening...")
        self.action_label.pack()

        self.backend = Assistant_Backend()  # Create an instance of the backend

        self.submit_button = tk.Button(master, text="Submit", command=self.process_query)
        self.submit_button.pack()

    def update_action_label(self, action):
        self.action_label.config(text=action)

    def process_query(self):
        query = self.text_input.get()
        self.response_display.insert(tk.END, f"User: {query}\n")

        self.update_action_label("Speaking...")
        threading.Thread(target=self.process_query_backend, args=(query,), daemon=True).start()

    def process_query_backend(self, query):
        response = self.backend.process_query(query)
        self.response_display.insert(tk.END, f"Aadhya: {response}\n")
        self.update_action_label("Listening...")

if __name__ == "__main__":
    root = tk.Tk()
    gui = AssistantGUI(root)
    root.mainloop()
