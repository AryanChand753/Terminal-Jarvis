import os
import datetime
import json
import pyttsx3
import speech_recognition as sr
import requests
from email.mime.text import MIMEText
import smtplib

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

def respond_to_command(command, commands_data):
    for key in commands_data:
        for sub_key in commands_data[key]:
            if sub_key in command:
                if key == "greetings":
                    speak(commands_data[key][sub_key])
                elif key == "time":
                    now = datetime.datetime.now()
                    response = commands_data[key][sub_key].replace("{{time}}", now.strftime("%H:%M")) \
                                                        .replace("{{date}}", now.strftime("%Y-%m-%d")) \
                                                        .replace("{{day}}", now.strftime("%A")) \
                                                        .replace("{{month}}", now.strftime("%B")) \
                                                        .replace("{{year}}", now.strftime("%Y"))
                    speak(response)
                elif key == "open":
                    os.system(commands_data[key][sub_key])
                elif key == "search for":
                    query = command.replace("search for", "").strip()
                    result = search_web(query)
                    speak(result)
                elif key == "email":
                    speak(commands_data[key]["prompt_subject"])
                    subject = listen()
                    speak(commands_data[key]["prompt_body"])
                    body = listen()
                    speak(commands_data[key]["recipient"])
                    recipient = listen()
                    send_email(subject, body, recipient)
                elif key == "reminder":
                    speak(commands_data[key]["prompt_time"])
                    time_str = listen()
                    speak(commands_data[key]["prompt_message"])
                    message = listen()
                    add_reminder(time_str, message)
                elif key == "exit":
                    speak(commands_data[key][sub_key])
                    print("Terminating...")
                    return False
                return True
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
    try:
        reminder_time = datetime.datetime.strptime(time_str, "%H:%M")
    except ValueError:
        speak("Invalid time format. Please provide the time in HH:MM format.")
        return

    reminders.append((reminder_time, message))
    speak("Reminder added.")

def check_reminders():
    global reminders
    now = datetime.datetime.now()
    new_reminders = []
    for reminder in reminders:
        if reminder[0] <= now:
            speak(f"Reminder: {reminder[1]}")
        else:
            new_reminders.append(reminder)
    reminders = new_reminders

if __name__ == "__main__":
    with open('commands.json', 'r') as f:
        commands_data = json.load(f)

    speak("Jarvis activated")
    try:
        while True:
            command = listen()
            if command:
                should_continue = respond_to_command(command, commands_data)
                if not should_continue:
                    break
            check_reminders()
    except KeyboardInterrupt:
        speak("Goodbye!")
        print("Terminating...")