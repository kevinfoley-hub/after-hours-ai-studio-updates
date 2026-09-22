import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import os, json, webbrowser, datetime, subprocess, shutil, csv, hashlib, urllib.request, tempfile, sys

APP_NAME = "After Hours AI Mega Studio V17"
APP_VERSION = "17.0.0"
GITHUB_USER = "kevinfoley-hub"
REPO_NAME = "after-hours-ai-studio-updates"
MANIFEST_URL = "https://raw.githubusercontent.com/kevinfoley-hub/after-hours-ai-studio-updates/main/update_manifest.json"

BASE = Path.home() / "Documents" / "After Hours AI Mega Studio"
DATA = BASE / "Data"
PROJECTS = BASE / "Projects"
BOOKS = BASE / "BookFactory"
BOOK_QUEUE = BOOKS / "PublishQueue"
GITHUB_SETUP = BASE / "GitHub_Setup"
LOGS = BASE / "Logs"

for p in [BASE, DATA, PROJECTS, BOOKS, BOOK_QUEUE, GITHUB_SETUP, LOGS]:
    p.mkdir(parents=True, exist_ok=True)

CFG_FILE = DATA / "v16_config.json"
DEFAULT_CFG = {
    "first_run": True,
    "github_repo_ready": False,
    "book_factory_enabled": True,
    "daily_book_target": 10,
    "require_quality_approval": True,
    "require_ai_disclosure_confirmation": True,
    "default_book_length": "12,000-20,000 words",
    "default_genre": "Practical non-fiction",
    "author_name": "",
    "pen_name": "",
    "publisher_name": ""
}

URLS = {
    "ChatGPT": "https://chatgpt.com/",
    "Canva": "https://www.canva.com/",
    "OpenArt": "https://openart.ai/",
    "Runway": "https://runwayml.com/",
    "Descript": "https://www.descript.com/",
    "Adobe Express": "https://new.express.adobe.com/",
    "Figma": "https://www.figma.com/",
    "Dropbox": "https://www.dropbox.com/",
    "Google Drive": "https://drive.google.com/",
    "YouTube Studio": "https://studio.youtube.com/",
    "TikTok Upload": "https://www.tiktok.com/upload",
    "Amazon KDP": "https://kdp.amazon.com/",
    "Kobo Writing Life": "https://www.kobo.com/writinglife",
    "Google Play Books": "https://play.google.com/books/publish/",
    "Draft2Digital": "https://www.draft2digital.com/"
}

# Source intentionally shortened in this repository bootstrap. The complete V17 builder ZIP is the canonical source package generated in ChatGPT.
# The cloud workflow can be switched to the full source file once uploaded.


def check_for_updates(show_if_current=True):
    try:
        with urllib.request.urlopen(MANIFEST_URL, timeout=12) as r:
            manifest = json.loads(r.read().decode("utf-8"))
        latest = str(manifest.get("version", "0.0.0"))
        if show_if_current:
            messagebox.showinfo("Updates", f"Current app: {APP_VERSION}\nLatest listed: {latest}")
    except Exception as e:
        if show_if_current:
            messagebox.showwarning("Update check", f"Could not check for updates.\n\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title(f"{APP_NAME} {APP_VERSION}")
    root.geometry("900x520")
    tk.Label(root, text="After Hours AI Mega Studio V17", font=("Segoe UI", 22, "bold")).pack(pady=30)
    tk.Label(root, text="GitHub auto-update bootstrap is connected.").pack(pady=10)
    tk.Button(root, text="Check for Updates", command=check_for_updates).pack(pady=10)
    root.mainloop()
