import tkinter as tk
from tkinter import messagebox
import subprocess
import re
import os
from openai import OpenAI
from PIL import Image, ImageTk
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ICON_PATH = "/Users/bhavi/Lyra/assests/jarvis_icon.png"

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_gpt_for_action(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a macOS assistant. Only reply with commands like: 'open terminal', 'open system settings'. No extra words."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        messagebox.showerror("OpenAI Error", f"Failed to contact GPT:\n{str(e)}")
        return ""

def open_any_app(app_name):
    app_name_lower = app_name.lower()
    if app_name_lower in ["system settings", "system preferences"]:
        for name in ["System Settings", "System Preferences"]:
            try:
                subprocess.run(["open", "-a", name], check=True)
                return True
            except subprocess.CalledProcessError:
                continue
        return False

    script = f'''
    tell application "System Events"
        try
            launch application "{app_name}"
        on error
            do shell script "open -a " & quoted form of "{app_name}"
        end try
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def play_youtube_video(query):
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    options = Options()
    options.add_argument("--start-maximized")
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(search_url)
        time.sleep(2)
        first_video = driver.find_elements(By.ID, "video-title")
        if first_video:
            first_video[0].click()
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False

def open_url_in_chrome(url):
    script = f'''
    tell application "Google Chrome"
        if it is running then
            tell window 1 to make new tab with properties {{URL:"{url}"}}
            activate
        else
            open location "{url}"
            activate
        end if
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def clean_command(cmd):
    return cmd.strip().rstrip(",.").strip()

def handle_direct_command(cmd):
    cmd = clean_command(cmd.lower())
    app_map = {
        "terminal": "Terminal",
        "music": "Music",
        "messages": "Messages",
        "safari": "Safari",
        "system settings": "System Settings",
        "calendar": "Calendar",
        "notes": "Notes",
        "whatsapp": "WhatsApp",
        "chrome": "Google Chrome",
        "outlook": "Microsoft Outlook",
    }

    if cmd.startswith("open "):
        app_key = cmd.replace("open ", "").strip()
        if app_key.startswith("amazon"):
            match = re.search(r"amazon( for| to)? (.*)", app_key)
            if match:
                query = match.group(2).strip()
                return open_url_in_chrome(f"https://www.amazon.com/s?k={query.replace(' ', '+')}")
            return open_url_in_chrome("https://www.amazon.com")
        elif app_key == "youtube":
            return open_url_in_chrome("https://www.youtube.com")
        elif app_key in app_map:
            return open_any_app(app_map[app_key])
        return open_any_app(app_key)

    if cmd.startswith("play "):
        if "on youtube" in cmd:
            query = cmd.replace("play", "").replace("on youtube", "").strip()
            return play_youtube_video(query)
        query = cmd.replace("play", "").strip()
        return open_url_in_chrome(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")

    if "search amazon for" in cmd or "search for" in cmd and "amazon" in cmd:
        query = cmd.split("for")[-1].strip()
        return open_url_in_chrome(f"https://www.amazon.com/s?k={query.replace(' ', '+')}")

    if "search youtube for" in cmd:
        query = cmd.split("for")[-1].strip()
        return open_url_in_chrome(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")

    return False

def split_and_handle_commands(command_text):
    commands = re.split(r",| and |\.|\n", command_text)
    for cmd in commands:
        if cmd.strip():
            handled = handle_direct_command(cmd.strip())
            if not handled:
                print(f"[Skipped] Command not handled: {cmd.strip()}")

def handle_command(command):
    command = command.strip().lower()
    if any(command.startswith(kw) for kw in ["open", "play", "search"]):
        if re.search(r",| and |\.|\n", command):
            split_and_handle_commands(command)
        else:
            success = handle_direct_command(command)
            if not success:
                print(f"[Skipped] Direct command not handled: {command}")
    else:
        gpt_response = ask_gpt_for_action(command)
        split_and_handle_commands(gpt_response)

def on_submit(event=None):
    user_input = command_entry.get().strip()
    if not user_input:
        messagebox.showwarning("Input Needed", "Please enter a command.")
        return
    handle_command(user_input)
    command_entry.delete(0, tk.END)

root = tk.Tk()
root.title("Lyra AI Assistant")
root.geometry("400x360")
root.resizable(False, False)

tk.Label(root, text="Lyra AI Assistant", font=("Helvetica", 20, "bold")).pack(pady=15)

try:
    img = Image.open(ICON_PATH)
    img = img.resize((128, 128), Image.Resampling.LANCZOS)
    icon_img = ImageTk.PhotoImage(img)
    tk.Label(root, image=icon_img).pack(pady=10)
except Exception as e:
    print(f"Icon error: {e}")
    tk.Label(root, text="[Icon Missing]", font=("Helvetica", 12, "italic")).pack(pady=10)

command_entry = tk.Entry(root, font=("Helvetica", 14), width=40)
command_entry.pack(pady=10)
command_entry.focus_set()
command_entry.bind("<Return>", on_submit)

tk.Button(root, text="Submit", font=("Helvetica", 14), command=on_submit).pack(pady=10)

root.mainloop()
