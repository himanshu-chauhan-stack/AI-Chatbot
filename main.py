import win32com.client
import speech_recognition as sr
import os
import webbrowser
import datetime
import google.generativeai as genai
from config import api_key

speaker = win32com.client.Dispatch("SAPI.SPVoice")

def say(text):
    """Convert text to speech"""
    speaker.Speak(text)


genai.configure(api_key=api_key)

def ai(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    folder_path = "gemini"
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, "output.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"Content saved to {file_path}")
    return response.text


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except Exception:
            return "Some Error Occurred. Sorry from Ritesh A.I."


if __name__ == "__main__":
    print("PyCharm")
    say("Hello I am Ritesh A.I.")

    sites = [
        ["youtube", "https://www.youtube.com"],
        ["wikipedia", "https://wikipedia.com"],
        ["google", "https://google.com"],
        ["linkedin", "https://linkedin.com"],
        ["instagram", "https://instagram.com"],
        ["github", "https://github.com"]
    ]

    gemini_mode = False   

    while True:
        query = takeCommand().lower()

        
        if "gemini" in query and not gemini_mode:
            say("Gemini mode activated, ask me anything...")
            gemini_mode = True
            continue

        
        if "exit gemini" in query and gemini_mode:
            say("Exiting Gemini mode...")
            gemini_mode = False
            continue

        
        if gemini_mode:
            response = ai(query)
            say(response)
            continue

        
        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Opening {site[0]} Ritesh...")
                webbrowser.open(site[1])

        if "the time" in query:
            hour = datetime.datetime.now().strftime("%H")
            minute = datetime.datetime.now().strftime("%M")
            say(f"Sir, the time is {hour} bajke {minute} minutes")

        if "open visual studio code" in query:
            code_path = r"D:\Microsoft VS Code\Code.exe"
            os.startfile(code_path)
            say("Opening Visual Studio Code Ritesh...")
