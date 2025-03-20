#import the packages
import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from gradio_client import Client
from dotenv import load_dotenv
import os
# from openai import OpenAI

# Load environment variables
load_dotenv()

# using microphone to take input
recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = os.getenv("NEWS_API_KEY")

# taking input via voice
def speak(text):
    engine.say(text)
    engine.runAndWait()

# using wikipedia ai to get details
def aiProcess(command):
    try:
        # Wikipedia API URL
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + command.replace(" ", "_")
        
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'extract' in data:
                return data['extract']
            else:
                return "No information found."
        else:
            return "Sorry, I couldn't process that."

    except Exception as e:
        return f"Error: {str(e)}"

# activating chatbot to reply user requests
def botlibre_chat(command):
    try:
        # Correct Bot Libre API endpoint
        api_url = "https://www.botlibre.com/rest/json/chat"
        
        # Application ID (replace with your own or leave empty for public bots)
        app_id =  os.getenv("BOTLIBRE_APP_ID")  # Replace with your app ID if needed

        # Bot ID (replace with your own bot ID)
        bot_id = os.getenv("BOTLIBRE_BOT_ID")


        # Payload for the API
        payload = {
            "application": app_id,
            "instance": bot_id,
            "message": command,
            "conversation": "12345",  # Optional: Tracks conversation
            "avatar": "false",
            "format": "json"
        }

        # Send POST request
        response = requests.post(api_url, json=payload)

        # Handle response
        if response.status_code == 200:
            data = response.json()
            if 'message' in data:
                return data['message']
            else:
                return "No response from Bot Libre."
        else:
            return f"Error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error: {str(e)}"

#already defined commands
def processCommand(c):
    print(c)
    if 'open google' in c.lower():
        webbrowser.open('https://google.com')
    elif 'open youtube' in c.lower():
        webbrowser.open('https://youtube.com')
    elif 'open facebook' in c.lower():
        webbrowser.open('https://facebook.com')
    elif 'open spacex' in c.lower():
        webbrowser.open('https://spacex.com')
    elif c.lower().startswith('play'):
        song = c.lower().split(' ')[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)
    elif 'news' in c.lower():
        try:
            url = f'https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey={newsapi}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])

                if articles:
                    speak("Here are the latest news headlines.")
                    for i, article in enumerate(articles[:5], 1):  # Limit to 5 headlines
                        speak(f"News {i}: {article['title']}")
                else:
                    speak("Sorry, no news articles were found.")
            else:
                speak("Failed to fetch news. Please check your API key or internet connection.")
        except Exception as e:
            speak(f"An error occurred: {str(e)}")




    elif c.lower().endswith('detail'):
        word = c.lower().split(' ')[0]
        output = aiProcess(word)
        speak(output)

    else:
        speak('Chatbot is active')
        while True:
            try:
                with sr.Microphone() as source:
                    print("Chatbot Active. Listening...")
                    audio = recognizer.listen(source)
                    user_input = recognizer.recognize_google(audio)

                    if 'deactivate chatbot' in user_input.lower():
                        speak("Chatbot deactivated.")
                        break

                    response = botlibre_chat(user_input)
                    print("Chatbot:", response)
                    speak(response)

            except Exception as e:
                print("Error:", e)
                speak("An error occurred while processing your request.")

        

if __name__ == '__main__':
    speak('Initializing Jarvis....')
    while True:
        # Listen for the wake word "Jarvis"
        # obtain audio from the microphone
        r = sr.Recognizer()
        # print('recognizing')
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source)
            word = r.recognize_google(audio)
            if word.lower() == 'jarvis':
                speak('how may i help you')
                #listen for above command
                with sr.Microphone() as source:
                    print("Jarvis Active...")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)

                    processCommand(command)


        except Exception as e:
            print(" error; {0}".format(e))
