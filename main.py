import os
import datetime
import pyttsx3
import speech_recognition as sr
import requests
from email.mime.text import MIMEText
import smtplib
import threading

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=30)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, I'm having trouble accessing Google's Speech Recognition service.")
            return None
        except sr.WaitTimeoutError:
            speak("Are you still there?")
            return None

def respond_to_command(command):
    if "hello" in command:
        speak("Hello! How can I assist you today?")
    elif "time" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {now}")
    elif "open" in command:
        if "notepad" in command:
            os.system("notepad")
        # TODO: ADD MORE APPLICATIONS
    elif "search for" in command:
        query = command.replace("search for", "").strip()
        result = search_web(query)
        speak(result)
    elif "send email" in command:
        speak("What is the subject?")
        subject = listen()
        speak("What should the email say?")
        body = listen()
        send_email(subject, body, "aryanchand753@gmail.com")
    elif "set reminder" in command:
        speak("When should I remind you? Please provide the time in HH:MM format.")
        time_str = listen()
        speak("What is the reminder for?")
        message = listen()
        add_reminder(time_str, message)
    elif "exit" in command:
        speak("Goodbye!")
        print("Terminating...")
        return False
    else:
        speak("Sorry, I don't know that command.")

    return True

def search_web(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['AbstractText']
    return "Sorry, I couldn't find any information on that."

def send_email(subject, body, to):
    sender = "your_email@example.com"
    password = "your_password"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    with smtplib.SMTP_SSL("smtp.example.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, to, msg.as_string())
        speak("Email sent.")

reminders = []

def add_reminder(time_str, message):
    reminder_time = datetime.datetime.strptime(time_str, "%H:%M")
    reminders.append((reminder_time, message))
    speak("Reminder added.")

def check_reminders():
    now = datetime.datetime.now()
    for reminder in reminders:
        if reminder[0] <= now:
            speak(f"Reminder: {reminder[1]}")
            reminders.remove(reminder)

if __name__ == "__main__":
    speak("Jarvis activated")
    try:
        while True:
            command = listen()
            if command:
                should_continue = respond_to_command(command)
                if not should_continue:
                    break
            check_reminders()
    except KeyboardInterrupt:
        speak("Goodbye!")
        print("Terminating...")