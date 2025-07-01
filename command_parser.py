# === assistant/command_parser.py (updated) ===
from dist import search_amazon
from dist import play_youtube_video
from dist import shutdown, restart, open_app

def parse_and_execute(command: str):
    command = command.lower()

    if "amazon" in command:
        product = command.replace("search", "").replace("on amazon", "").strip()
        search_amazon(product)
    elif "youtube" in command or "play" in command:
        video = command.replace("play", "").replace("on youtube", "").strip()
        play_youtube_video(video)
    elif "shutdown" in command:
        shutdown()
    elif "restart" in command:
        restart()
    elif "open" in command:
        app = command.replace("open", "").strip()
        open_app(app)
    else:
        print("❌ Command not recognized.")
