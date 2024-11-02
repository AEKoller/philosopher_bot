import tkinter as tk
from tkinter import scrolledtext
import main

def send_to_ai():
    philosopher_name = philosopher_name_entry.get()
    philosopher_text = philosopher_text_entry.get("1.0", tk.END)
    user_question = user_question_entry.get("1.0", tk.END)
    
    # Replace placeholders with actual input
    message_content = main.message.content.replace("{{PHILOSOPHER_NAME}}", philosopher_name)
    message_content = message_content.replace("{{PHILOSOPHER_TEXT}}", philosopher_text)
    message_content = message_content.replace("{{USER_QUESTION}}", user_question)
    
    # Display the response in the text area
    response_text_area.delete("1.0", tk.END)
    response_text_area.insert(tk.END, message_content)

# Create the main window
root = tk.Tk()
root.title("Philosopher Bot")

# Philosopher's name input
tk.Label(root, text="Philosopher's Name:").pack()
philosopher_name_entry = tk.Entry(root, width=50)
philosopher_name_entry.pack()

# Philosopher's text input
tk.Label(root, text="Philosopher's Text:").pack()
philosopher_text_entry = scrolledtext.ScrolledText(root, width=50, height=10)
philosopher_text_entry.pack()

# User's question input
tk.Label(root, text="Your Question:").pack()
user_question_entry = scrolledtext.ScrolledText(root, width=50, height=5)
user_question_entry.pack()

# Send button
send_button = tk.Button(root, text="Send", command=send_to_ai)
send_button.pack()

# Response display area
tk.Label(root, text="Response:").pack()
response_text_area = scrolledtext.ScrolledText(root, width=50, height=10)
response_text_area.pack()

# Run the application
root.mainloop()
