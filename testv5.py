"""
JARVIS - AI Voice Assistant
A voice-activated assistant with wake word detection, command processing, and GUI
"""

# ============================================================================
# IMPORTS
# ============================================================================
import speech_recognition as sr
from gtts import gTTS 
import os
import pygame
import datetime
import webbrowser
import time 
import subprocess
import re
import glob
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
from google import genai
from google.genai import types 
import json 
from pathlib import Path
from dotenv import load_dotenv
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyOAuth


# ============================================================================
# CONFIGURATION & GLOBAL VARIABLES
# ============================================================================
pygame.mixer.init()
chat_history = []
CHAT_FILE = Path("chat_history.json")
client = None  # Will be initialized after env is loaded
ui_window = None  # Global UI reference

# Load existing chat history if available
if CHAT_FILE.exists():
    with CHAT_FILE.open("r") as f:
        chat_history = json.load(f)
else:
    chat_history = []

# ============================================================================
# SPOTIFY INTEGRATION
# ============================================================================

        


# ============================================================================
# CONFIGURATION FUNCTIONS
# ============================================================================
def configure_env():
    """Load environment variables and initialize Gemini client"""
    load_dotenv()
    global client
    api_key = os.getenv("api_key") or os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment variables. Please set 'api_key' or 'API_KEY' in your .env file.")
    client = genai.Client(api_key=api_key)
    


def delete_chat_history():
    """Delete the chat history file"""
    if os.path.exists("chat_history.json"):
        os.remove("chat_history.json")
        print("Chat history deleted.")
    else:
        print("No chat history file found.")


# ============================================================================
# UI CLASS
# ============================================================================
class JARVISUI:
    """Graphical User Interface for JARVIS"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("JARVIS - AI Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Status variables
        self.is_awake = False
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        """Create and layout all UI widgets"""
        # Header frame
        header_frame = tk.Frame(self.root, bg='#1a1a1a', pady=20)
        header_frame.pack(fill=tk.X)
        
        # Title
        title_label = tk.Label(header_frame, text="JARVIS", font=('Arial', 32, 'bold'), 
                              fg='#00ff00', bg='#1a1a1a')
        title_label.pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#1a1a1a', pady=10)
        status_frame.pack(fill=tk.X)
        
        # Status indicator
        self.status_label = tk.Label(status_frame, text="Sleep Mode", font=('Arial', 14),
                                     fg='#ffaa00', bg='#1a1a1a')
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Status circle (visual indicator)
        self.status_canvas = tk.Canvas(status_frame, width=20, height=20, bg='#1a1a1a', 
                                       highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=10)
        self.status_circle = self.status_canvas.create_oval(5, 5, 15, 15, fill='#ffaa00', outline='')
        
        # Listening status
        self.listening_label = tk.Label(status_frame, text="Waiting for wake word...", 
                                       font=('Arial', 10), fg='#888888', bg='#1a1a1a')
        self.listening_label.pack(side=tk.RIGHT, padx=20)
        
        # Log frame
        log_frame = tk.Frame(self.root, bg='#1a1a1a')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Log label
        log_label = tk.Label(log_frame, text="Conversation Log", font=('Arial', 12, 'bold'),
                            fg='#ffffff', bg='#1a1a1a')
        log_label.pack(anchor=tk.W)
        
        # Scrolled text for log
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=70,
                                                  bg='#2a2a2a', fg='#ffffff',
                                                  font=('Consolas', 10),
                                                  insertbackground='#00ff00',
                                                  wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Footer frame
        footer_frame = tk.Frame(self.root, bg='#1a1a1a', pady=10)
        footer_frame.pack(fill=tk.X)
        
        # Instructions
        instructions = tk.Label(footer_frame, 
                               text="Say 'Hey JARVIS' to wake me up | Say 'go to sleep' to return to sleep mode",
                               font=('Arial', 9), fg='#666666', bg='#1a1a1a')
        instructions.pack()
        
    def update_status(self, awake):
        """Update the status indicator"""
        self.is_awake = awake
        if awake:
            self.status_label.config(text="Active Mode", fg='#00ff00')
            self.status_canvas.itemconfig(self.status_circle, fill='#00ff00')
        else:
            self.status_label.config(text="Sleep Mode", fg='#ffaa00')
            self.status_canvas.itemconfig(self.status_circle, fill='#ffaa00')
    
    def update_listening_status(self, text):
        """Update the listening status text"""
        self.listening_label.config(text=text)
        self.root.update_idletasks()
    
    def add_to_log(self, speaker, message):
        """Add a message to the conversation log"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if speaker == "JARVIS":
            self.log_text.insert(tk.END, f"[{timestamp}] JARVIS: {message}\n", "jarvis")
            self.log_text.tag_config("jarvis", foreground="#00ff00")
        else:
            self.log_text.insert(tk.END, f"[{timestamp}] You: {message}\n", "user")
            self.log_text.tag_config("user", foreground="#00aaff")
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()


# ============================================================================
# VOICE FUNCTIONS (Speech Recognition & Text-to-Speech)
# ============================================================================
def speak(text):
    """Convert text to speech and play it"""
    print(f"JARVIS: {text}")
    
    # Update UI if available
    if ui_window:
        ui_window.add_to_log("JARVIS", text)
    
    try:
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        filename = "jarvis_speech.mp3"
        tts.save(filename)
        
        # Load and play audio
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        # Unload the music before deleting
        pygame.mixer.music.unload()
        time.sleep(0.1)
        
        # Delete the temp file
        if os.path.exists(filename):
            os.remove(filename)
        
    except Exception as e:
        print(f"Speech error: {e}")


def listen_for_wake_word():
    """Continuously listen for wake word (JARVIS, Hey JARVIS, etc.)"""
    recognizer = sr.Recognizer()
    wake_words = ['jarvis', 'hey jarvis', 'okay jarvis', 'ok jarvis']
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        while True:
            try:
                # Listen for wake word with shorter timeout
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                text = recognizer.recognize_google(audio, language='en-US').lower()
                print(f"[Listening...] {text}")
                
                # Update UI
                if ui_window:
                    ui_window.update_listening_status("Listening...")
                
                # Check if any wake word is in the recognized text
                for wake_word in wake_words:
                    if wake_word in text:
                        print(f" Wake word detected: '{wake_word}'")
                        if ui_window:
                            ui_window.update_listening_status(f"Wake word detected: {wake_word}")
                        return True
                        
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                if ui_window:
                    ui_window.update_listening_status("Sleep mode - Waiting for wake word...")
                continue
            except sr.UnknownValueError:
                # Couldn't understand, continue listening
                continue
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                time.sleep(1)
                continue
            except KeyboardInterrupt:
                print("\nWake word detection interrupted.")
                return False


def listen():
    """Listen to user voice for commands"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(" --Speak your command...")
        if ui_window:
            ui_window.update_listening_status("Listening for command...")
        
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
    
    try:
        query = recognizer.recognize_google(audio, language='en-US')
        print(f"You said: {query}")
        if ui_window:
            ui_window.add_to_log("You", query)
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return ""


# ============================================================================
# AI FUNCTIONS
# ============================================================================
def ask_AI(question): 
    """Ask Gemini AI for intelligent responses"""
    try:
        # Save user question
        chat_history.append({
            "role": "user",
            "parts": [{"text": question}]
        })

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=chat_history,
            config=types.GenerateContentConfig(
                system_instruction='Act as an AI assistant named JARVIS that helps with general tasks and answers questions, act like a human. keep answers short and conversational, NO asterisks.',
                max_output_tokens=200,
                temperature=0.5, 
            ),
        )
        
        answer = response.text 

        # Save model answer
        chat_history.append({
            "role": "model",
            "parts": [{"text": answer}]
        })

        # Save chat history to file
        with CHAT_FILE.open("w") as f:
            json.dump(chat_history, f, indent=2)

        return answer
    
    except Exception as e:
        print(f"AI error: {e}")
        return "I'm having trouble accessing my knowledge base right now."


def greet():
    """Greet based on time of day"""
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning, sir!")
    elif hour < 18:
        speak("Good afternoon, sir!")
    else:
        speak("Good evening, sir!")
    speak("I am JARVIS. I'm now in sleep mode. Say 'Hey JARVIS' to wake me up.")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def calculate(expression):
    """Safely evaluate mathematical expressions"""
    try:
        # Remove common words and keep only math expression
        expression = expression.lower()
        expression = re.sub(r'(calculate|what is|what\'s|compute|solve|evaluate|equals?|is equal to)', '', expression)
        expression = expression.strip()
        
        # Extract numbers and operators (allow: numbers, +, -, *, /, (, ), ., spaces)
        expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        expression = expression.strip()
        
        if not expression:
            return "I couldn't find a valid math expression."
        
        # Safely evaluate the expression
        result = eval(expression)
        return f"The answer is {result}"
    except ZeroDivisionError:
        return "Cannot divide by zero."
    except Exception as e:
        return f"I couldn't calculate that. Please try again with a valid expression."


def search_files(query):
    """Search for files in common directories"""
    try:
        # Extract search term
        query = query.lower()
        search_term = re.sub(r'(search|find|look for|files?|file named?|file called?)', '', query)
        search_term = search_term.strip()
        
        if not search_term:
            return "What file would you like me to search for?"
        
        # Common search locations
        search_paths = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Downloads"),
        ]
        
        found_files = []
        for search_path in search_paths:
            if os.path.exists(search_path):
                pattern = os.path.join(search_path, f"*{search_term}*")
                matches = glob.glob(pattern, recursive=False)
                found_files.extend(matches[:5])  # Limit to 5 per directory
        
        if found_files:
            file_list = "\n".join([os.path.basename(f) for f in found_files[:10]])
            speak(f"I found {len(found_files)} file(s) matching '{search_term}'. Here are some: {file_list}")
            return True
        else:
            speak(f"I couldn't find any files matching '{search_term}' in common locations.")
            return True
    except Exception as e:
        speak(f"Error searching for files: {str(e)}")
        return True


def open_folder(path_name):
    """Open a folder or directory"""
    try:
        # Common folder shortcuts
        folders = {
            'desktop': os.path.expanduser("~\\Desktop"),
            'documents': os.path.expanduser("~\\Documents"),
            'downloads': os.path.expanduser("~\\Downloads"),
            'pictures': os.path.expanduser("~\\Pictures"),
            'videos': os.path.expanduser("~\\Videos"),
            'music': os.path.expanduser("~\\Music"),
        }
        
        path_name = path_name.lower().strip()
        
        # Check if it's a shortcut
        if path_name in folders:
            folder_path = folders[path_name]
            os.startfile(folder_path)
            speak(f"Opening {path_name} folder")
            return True
        
        # Try to open as a direct path
        if os.path.exists(path_name):
            os.startfile(path_name)
            speak(f"Opening {path_name}")
            return True
        else:
            speak(f"I couldn't find the folder '{path_name}'")
            return True
    except Exception as e:
        speak(f"Error opening folder: {str(e)}")
        return True


def list_files(directory=None):
    """List files in a directory"""
    try:
        if not directory:
            directory = os.getcwd()
        
        if os.path.exists(directory):
            files = os.listdir(directory)
            file_count = len(files)
            speak(f"There are {file_count} items in this directory.")
            if file_count <= 10:
                file_list = ", ".join(files[:10])
                speak(f"Files: {file_list}")
            return True
        else:
            speak(f"Directory '{directory}' not found.")
            return True
    except Exception as e:
        speak(f"Error listing files: {str(e)}")
        return True


def open_app(app_name):
    """Open an application by name"""
    try:
        app_name = app_name.lower().strip()
        
        # Dictionary of common applications and their executable names/paths
        apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'wordpad': 'wordpad.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe',
            'task manager': 'taskmgr.exe',
            'control panel': 'control.exe',
            'settings': 'ms-settings:',
            'file explorer': 'explorer.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'spotify': 'spotify.exe',
            'discord': 'discord.exe',
            'steam': 'steam.exe',
            'code': 'code.exe',  # VS Code
            'visual studio code': 'code.exe',
            'vscode': 'code.exe',
            'python': 'python.exe',
            'excel': 'excel.exe',
            'word': 'winword.exe',
            'powerpoint': 'powerpnt.exe',
            'outlook': 'outlook.exe',
        }
        
        # Check if it's a known app
        if app_name in apps:
            app_path = apps[app_name]
            try:
                if app_path.startswith('ms-'):
                    os.startfile(app_path)
                else:
                    subprocess.Popen(app_path, shell=True)
                speak(f"Opening {app_name}")
                return True
            except Exception as e:
                pass
        
        # Try to find the app in common locations
        common_paths = [
            os.path.expanduser("~\\AppData\\Local\\Programs"),
            os.path.expanduser("~\\AppData\\Roaming"),
            "C:\\Program Files",
            "C:\\Program Files (x86)",
        ]
        
        app_name_clean = app_name.replace(' ', '').lower()
        found = False
        
        for base_path in common_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.lower().endswith('.exe') and app_name_clean in file.lower():
                            try:
                                subprocess.Popen(os.path.join(root, file), shell=True)
                                speak(f"Opening {app_name}")
                                found = True
                                break
                            except:
                                continue
                    if found:
                        break
                if found:
                    break
        
        if not found:
            # Try launching by name directly (Windows will search PATH)
            try:
                subprocess.Popen(app_name, shell=True)
                speak(f"Attempting to open {app_name}")
                return True
            except:
                speak(f"I couldn't find the application '{app_name}'. Please make sure it's installed and in your system PATH.")
                return True
        
        return True
    except Exception as e:
        speak(f"Error opening application: {str(e)}")
        return True


# ============================================================================
# COMMAND PROCESSING
# ============================================================================
def process_command(query):
    """Execute commands based on user query"""
    # Website commands
    if 'open youtube' in query:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
    
    elif 'open google' in query:
        speak("Opening Google")
        webbrowser.open("https://google.com")
    
    elif 'open github' in query:
        speak("Opening GitHub")
        webbrowser.open("https://github.com")
    
    # Time and date
    elif 'time' in query:
        time_str = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {time_str}")
    
    elif 'date' in query:
        date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today is {date}")
    
    # Calculator commands
    elif any(word in query for word in ['calculate', 'what is', 'what\'s', 'compute', 'solve', 'evaluate', 'plus', 'minus', 'times', 'multiply', 'divide', 'divided by']):
        result = calculate(query)
        speak(result)
    
    # File operations
    elif any(word in query for word in ['search file', 'find file', 'look for file', 'file named', 'file called']):
        search_files(query)
    
    elif 'open folder' in query or 'open directory' in query:
        folder_name = re.sub(r'(open folder|open directory|folder|directory)', '', query, flags=re.IGNORECASE).strip()
        open_folder(folder_name)
    
    elif 'list files' in query or 'show files' in query or 'files in' in query:
        directory = re.sub(r'(list files|show files|files in|in directory|in folder)', '', query, flags=re.IGNORECASE).strip()
        if not directory:
            directory = os.getcwd()
        list_files(directory)
    
    # Application commands
    elif any(phrase in query for phrase in ['open app', 'launch app', 'start app', 'run app', 'open ', 'launch ', 'start ', 'run ']):
        app_name = re.sub(r'(open app|launch app|start app|run app|^open |^launch |^start |^run )', '', query, flags=re.IGNORECASE).strip()
        app_name = re.sub(r'\s+(app|application|program)$', '', app_name, flags=re.IGNORECASE)
        if app_name and app_name not in ['youtube', 'google', 'github']:  # Avoid conflicts with website commands
            open_app(app_name)
    
    # System commands
    elif 'shutdown' in query or 'turn off' in query:
        speak("Shutting down the computer in 30 seconds. Say cancel to abort.")
        time.sleep(2)
        subprocess.run(["shutdown", "/s", "/t", "30"], shell=False)
        speak("Shutdown initiated. You can cancel by saying cancel shutdown.")
    
    elif 'cancel shutdown' in query or 'abort shutdown' in query:
        subprocess.run(["shutdown", "/a"], shell=False)
        speak("Shutdown cancelled.")
    
    elif 'restart' in query or 'reboot' in query:
        speak("Restarting the computer in 30 seconds.")
        subprocess.run(["shutdown", "/r", "/t", "30"], shell=False)
    
    elif 'lock' in query or 'lock screen' in query:
        speak("Locking the screen.")
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], shell=False)
    
    # Sleep command - return to sleep mode (check BEFORE system sleep)
    elif any(phrase in query for phrase in ['go to sleep', 'sleep mode', 'sleep jarvis', 'jarvis sleep', 'standby', 'jarvis standby']):
        speak("Going to sleep mode. Say 'Hey JARVIS' to wake me up.")
        return "sleep"
    
    # System sleep command - more specific to avoid conflict with JARVIS sleep
    elif any(phrase in query for phrase in ['put computer to sleep', 'hibernate computer', 'computer sleep', 'computer hibernate']) or ('hibernate' in query and 'jarvis' not in query):
        speak("Putting the computer to sleep.")
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], shell=False)
    
    # Exit command
    elif 'exit' in query or 'quit' in query or 'goodbye' in query:
        speak("Goodbye, sir. Have a great day!")
        client.close()
        delete_chat_history()
        return False
    
    else:
        # Default: Ask AI
        answer = ask_AI(query)
        speak(answer)
    
    return True


# ============================================================================
# MAIN PROGRAM
# ============================================================================
def run_jarvis():
    """Main JARVIS loop - runs in separate thread"""
    global ui_window
    
    configure_env()
    greet()
    
    print("\n" + "="*50)
    print("JARVIS is now in sleep mode.")
    print("Say 'Hey JARVIS', 'JARVIS', or 'Okay JARVIS' to wake me up.")
    print("Press Ctrl+C to exit completely.")
    print("="*50 + "\n")
    
    is_awake = False  # Track if JARVIS is awake or in sleep mode
    
    while True:
        try:
            if not is_awake:
                # Sleep mode: Wait for wake word
                if ui_window:
                    ui_window.update_status(False)
                if listen_for_wake_word():
                    # Wake word detected, now listen for command
                    speak("Yes, sir?")
                    is_awake = True
                    if ui_window:
                        ui_window.update_status(True)
                        ui_window.update_listening_status("Active - Ready for commands")
                    print("\n[Active mode - Listening for commands. Say 'go to sleep' to return to sleep mode.]\n")
            
            # Active mode: Listen for commands continuously
            if is_awake:
                query = listen()
                
                if query:
                    # Process the command
                    result = process_command(query)
                    
                    if result == False:
                        # Exit command was processed
                        if ui_window:
                            ui_window.root.quit()
                        break
                    elif result == "sleep":
                        # Sleep command - return to sleep mode
                        is_awake = False
                        if ui_window:
                            ui_window.update_status(False)
                            ui_window.update_listening_status("Returning to sleep mode...")
                        print("\n[Returning to sleep mode... Say 'Hey JARVIS' to wake me up.]\n")
                    # Otherwise, stay awake and continue listening
                    
        except KeyboardInterrupt:
            print("\n\nShutting down JARVIS...")
            speak("Goodbye, sir. Shutting down.")
            if client:
                client.close()
            if ui_window:
                ui_window.root.quit()
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)  # Wait before retrying
            continue


if __name__ == "__main__":
    # Create and start UI
    root = tk.Tk()
    ui_window = JARVISUI(root)
    
    # Start JARVIS in a separate thread
    jarvis_thread = threading.Thread(target=run_jarvis, daemon=True)
    jarvis_thread.start()
    
    # Run UI main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
        if client:
            client.close()
