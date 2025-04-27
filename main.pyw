import os
import sys

os.system(f"{sys.executable} -m pip uninstall -y googlesearch-python")

def install_and_import(module_name, package_name=None):
    package_name = package_name if package_name else module_name
    try:
        __import__(module_name)
    except ImportError:
        os.system(f"{sys.executable} -m pip install --upgrade {package_name}")
        __import__(module_name)

install_and_import("tkinter", "tk")
install_and_import("googlesearch", "googlesearch-python")
install_and_import("requests")
install_and_import("bs4", "beautifulsoup4")

import random
import re
import tkinter as tk
from tkinter import scrolledtext
from googlesearch import search
import requests
from bs4 import BeautifulSoup

def fetch_code_snippet(query):
    search_query = f"{query} site:stackoverflow.com OR site:github.com OR site:geeksforgeeks.org OR site:w3schools.com"
    try:
        results = search(search_query, num_results=5)
        for url in results:
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                if any(word in soup.text.lower() for word in ["accept cookies", "cookies", "subscribe", "sign-up", "free trial", "cookies"]):
                    continue  
                code_blocks = soup.find_all("code")
                for code in code_blocks:
                    code_text = clean_text(code.get_text())
                    if len(code_text.split()) > 5:
                        return f"Here's a possible solution from {url}:\n\n```{code_text}```"
            except Exception:
                continue
    except Exception:
        return "I couldn't find an exact code snippet, but I can help guide you!"
    return "I searched but didn't find an exact match. Try rephrasing!"

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\[.*?\]", "", text)
    return text.strip()

def fetch_reddit_response(query):
    search_query = f"{query} site:reddit.com"
    try:
        results = search(search_query, num_results=5)
        for url in results:
            try:
                response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, "html.parser")
                if any(word in soup.text.lower() for word in ["accept cookies", "sign-up", "free trial", "subscribe", "log in"]):
                    continue  
                comments = soup.find_all("p")
                for comment in comments:
                    text = clean_text(comment.get_text())
                    if len(text.split()) > 10:
                        return f"Here's a Reddit response from {url}:\n\n{text}"
            except Exception:
                continue
    except Exception:
        return "I couldn't find any relevant Reddit posts."
    return "I searched Reddit but didn't find a perfect answer. Try rephrasing!"

def generate_response(user_input):
    if re.search(r"\b(hi|hello|hey)\b", user_input, re.IGNORECASE):
        return random.choice(["Hey there!", "Hello! How can I assist you today?", "Hi! Need help with something?"])
    elif re.search(r"\b(how are you)\b", user_input, re.IGNORECASE):
        return "I'm just a chatbot, but I'm here to help! How about you?"
    elif re.search(r"\b(who are you|what is your name)\b", user_input, re.IGNORECASE):
        return "I'm Google AI, your chatbot assistant!"
    elif re.search(r"\b(exit|quit|bye)\b", user_input, re.IGNORECASE):
        root.destroy()
        return "Goodbye! Have a great day!"
    if re.search(r"\b(code|example|script|program|how to)\b", user_input, re.IGNORECASE):
        return fetch_code_snippet(user_input)
    if "reddit" in user_input.lower():
        return fetch_reddit_response(user_input)
    return fetch_google_response(user_input)

def fetch_google_response(query):
    try:
        results = search(query, num_results=5)
        for url in results:
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                if any(word in soup.text.lower() for word in ["accept cookies", "subscribe", "sign-up", "cookies"]):
                    continue  
                paragraphs = soup.find_all("p")
                for p in paragraphs:
                    text = clean_text(p.get_text())
                    if len(text.split()) > 10 and "subscribe" not in text.lower():
                        return text
            except Exception:
                continue
    except Exception:
        return "I couldn't find an exact answer, but I can help figure it out!"
    return "I searched but didn't find a perfect match. Try rephrasing!"

def send_message(event=None):
    user_text = user_input.get().strip()
    if user_text == "":
        return
    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, f"You: {user_text}\n", "user")
    chat_window.insert(tk.END, "Google AI is thinking...\n", "thinking")
    chat_window.see(tk.END)
    root.update()
    response = generate_response(user_text)
    chat_window.delete("thinking.first", "thinking.last")
    chat_window.insert(tk.END, f"Google AI: {response}\n\n", "bot")
    chat_window.config(state=tk.DISABLED)
    user_input.delete(0, tk.END)

root = tk.Tk()
root.title("Google AI Chatbot")
root.geometry("500x600")
root.configure(bg="#2C3E50")

chat_window = scrolledtext.ScrolledText(root, height=20, width=60, bg="#34495E", fg="white", font=("Helvetica", 12), wrap=tk.WORD, bd=0, relief=tk.FLAT)
chat_window.tag_config("user", foreground="cyan")
chat_window.tag_config("bot", foreground="lightgreen")
chat_window.tag_config("thinking", foreground="yellow")
chat_window.config(state=tk.DISABLED)
chat_window.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

input_frame = tk.Frame(root, bg="#34495E")
input_frame.pack(fill=tk.X, padx=20, pady=5)

user_input = tk.Entry(input_frame, width=50, font=("Helvetica", 12), bg="#ECF0F1", fg="#2C3E50", bd=0, relief=tk.FLAT)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)

send_button = tk.Button(input_frame, text="Send", command=send_message, bg="#2980B9", fg="white", font=("Helvetica", 12, "bold"), relief=tk.FLAT)
send_button.pack(side=tk.RIGHT, padx=10, pady=5)

root.bind("<Return>", send_message)
user_input.focus()
root.mainloop()
