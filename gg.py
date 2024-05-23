import ctypes
import os
import sys
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
from googlesearch import search
from gtts import gTTS
import requests
from bs4 import BeautifulSoup
import pyglet

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        status_label.config(text="Silakan berbicara...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        status_label.config(text="Mengenali suara...")
        query = recognizer.recognize_google(audio, language="id-ID")
        status_label.config(text=f"Anda berkata: {query}")
        return query
    except sr.RequestError:
        status_label.config(text="Tidak dapat meminta hasil dari layanan Google Speech Recognition")
    except sr.UnknownValueError:
        status_label.config(text="Tidak dapat mengenali ucapan Anda")
    return None

# Add is_admin check here
if not is_admin():
    try:
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()
    except Exception as e:
        print(f"Kesalahan: {e}")
        sys.exit()

def google_search(query, num_results=1):
    try:
        search_results = list(search(query, num_results=num_results))
        return search_results
    except Exception as e:
        print("Error:", e)
        return []

def get_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs[:5]])  # Mengambil lima paragraf pertama
        return text
    except Exception as e:
        print("Error fetching text from URL:", e)
        return "Tidak dapat mengambil teks dari URL."

def speak_text(text):
    if text:
        tts = gTTS(text=text, lang='id')
        tts.save("result.mp3")
        os.system("start result.mp3")
    else:
        print("Tidak ada teks untuk diucapkan")

def perform_search(query):
    if query:
        urls = google_search(query)
        if urls:
            url = urls[0]
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"Mengambil informasi dari: {url}\n\n")
            result = get_text_from_url(url)
            result_text.insert(tk.END, result)
            result_text.config(state=tk.DISABLED)
            speak_text(result)
        else:
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "Tidak ada hasil pencarian.")
            result_text.config(state=tk.DISABLED)

def search_by_text():
    query = text_entry.get()
    perform_search(query)

def search_by_voice():
    query = recognize_speech_from_mic()
    if query:
        text_entry.delete(0, tk.END)
        text_entry.insert(0, query)
        perform_search(query)

def toggle_fullscreen():
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

root = tk.Tk()
root.title("Google Lite v1.0 by Yogi Ario")

# Mengatur ukuran jendela
root.geometry("800x600")

title_label = tk.Label(root, text="Google Lite v1.0", font=("Arial", 24))
title_label.pack(pady=10)

subtitle_label = tk.Label(root, text="by Yogi Ario", font=("Arial", 14))
subtitle_label.pack(pady=5)

frame = tk.Frame(root)
frame.pack(pady=10)

text_entry = tk.Entry(frame, width=50, font=("Arial", 14))
text_entry.pack(side=tk.LEFT, padx=10)

text_search_button = tk.Button(frame, text="Cari Teks", command=search_by_text, font=("Arial", 14))
text_search_button.pack(side=tk.LEFT)

voice_search_button = tk.Button(root, text="Cari Suara", command=search_by_voice, font=("Arial", 14))
voice_search_button.pack(pady=10)

status_label = tk.Label(root, text="", font=("Arial", 12))
status_label.pack(pady=5)

result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 12))
result_text.pack(expand=True, fill='both', padx=10, pady=10)

# Menambahkan tombol toggle fullscreen
fullscreen_button = tk.Button(root, text="Toggle Fullscreen", command=toggle_fullscreen, font=("Arial", 14))
fullscreen_button.pack(pady=10)

root.mainloop()
