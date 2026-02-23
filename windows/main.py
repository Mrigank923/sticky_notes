#!/usr/bin/env python3
"""
Sticky Notes — Windows version
================================
Uses tkinter (built into Python on Windows) — no GTK or extra system libs needed.

Features:
  ✅ Semi-transparent window
  ✅ Always on top
  ✅ Draggable (click and drag anywhere)
  ✅ Resizable
  ✅ Animated Pokémon buddy (bob + breathe)
  ✅ Persistent notes (saves on close, loads on open)
  ✅ Pokémon fetched from PokéAPI

Install deps:
  pip install python-dotenv pillow requests

Run:
  python main_windows.py
"""

import os
import sys
import json
import math
import random
import threading
import urllib.request
from io import BytesIO

# ── Load .env ─────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    # .env lives in the repo root (one level above windows/)
    _ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    load_dotenv(dotenv_path=_ENV_FILE)
except ImportError:
    pass   # dotenv optional — falls back to default User-Agent

import tkinter as tk
from tkinter import scrolledtext
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[WARN] Pillow not installed — Pokémon sprite will not show. Run: pip install pillow")

# ── Persistence ───────────────────────────────────────────────────────────────
DATA_DIR  = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "sticky-notes")
NOTE_FILE = os.path.join(DATA_DIR, "note.txt")
os.makedirs(DATA_DIR, exist_ok=True)
print(f"[INFO] Notes saved to: {NOTE_FILE}")

def load_note():
    if os.path.exists(NOTE_FILE):
        with open(NOTE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_note(text):
    with open(NOTE_FILE, "w", encoding="utf-8") as f:
        f.write(text)

# ── Pokémon fetch ─────────────────────────────────────────────────────────────
TOTAL_POKEMON = 151  # Gen 1 — raise to 1025 for all generations

def fetch_pokemon(callback):
    """Fetch a random Pokémon sprite + name in a background thread."""
    def _fetch():
        try:
            poke_id    = random.randint(1, TOTAL_POKEMON)
            api_url    = f"https://pokeapi.co/api/v2/pokemon/{poke_id}"
            headers    = {"User-Agent": os.getenv("USER_AGENT", "sticky-notes-app/1.0")}

            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())

            name       = data["name"].capitalize()
            sprite_url = data["sprites"]["front_default"]

            req2 = urllib.request.Request(sprite_url, headers=headers)
            with urllib.request.urlopen(req2, timeout=5) as r:
                img_bytes = r.read()

            # Schedule UI update on main thread
            root.after(0, lambda: callback(name, img_bytes))
        except Exception as e:
            print(f"[Pokémon] Could not fetch: {e}")
    threading.Thread(target=_fetch, daemon=True).start()

# ── Main window ───────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Sticky Note")
root.geometry("320x240")
root.resizable(True, True)
root.configure(bg="#ffd740")

# Always on top
root.wm_attributes("-topmost", True)

# Semi-transparent window (0.0 = invisible, 1.0 = opaque)
root.wm_attributes("-alpha", 0.88)

# Remove default title bar for a cleaner look
root.overrideredirect(True)

# ── Custom title bar (drag handle) ───────────────────────────────────────────
title_bar = tk.Frame(root, bg="#c89600", height=28, cursor="fleur")
title_bar.pack(fill=tk.X, side=tk.TOP)

title_lbl = tk.Label(title_bar, text="📝 Sticky Note", bg="#c89600",
                     fg="#2b1800", font=("Segoe UI", 10, "bold"))
title_lbl.pack(side=tk.LEFT, padx=6)

close_btn = tk.Button(title_bar, text="✕", bg="#c89600", fg="#2b1800",
                      font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                      activebackground="#e05050", activeforeground="white",
                      command=root.destroy)
close_btn.pack(side=tk.RIGHT, padx=4)

# Drag logic — works by tracking mouse delta on the title bar
_drag_x = _drag_y = 0

def on_drag_start(event):
    global _drag_x, _drag_y
    _drag_x = event.x_root - root.winfo_x()
    _drag_y = event.y_root - root.winfo_y()

def on_drag_motion(event):
    root.geometry(f"+{event.x_root - _drag_x}+{event.y_root - _drag_y}")

title_bar.bind("<ButtonPress-1>",  on_drag_start)
title_bar.bind("<B1-Motion>",      on_drag_motion)
title_lbl.bind("<ButtonPress-1>",  on_drag_start)
title_lbl.bind("<B1-Motion>",      on_drag_motion)

# ── Text area ─────────────────────────────────────────────────────────────────
text_area = tk.Text(root, wrap=tk.WORD, bg="#ffeea0", fg="#0118cc",
                    font=("Segoe UI", 13), bd=0, padx=6, pady=6,
                    insertbackground="#0118cc", relief=tk.FLAT,
                    yscrollcommand=lambda *a: scrollbar.set(*a))
text_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

scrollbar = tk.Scrollbar(root, command=text_area.yview, bg="#ffd740")
scrollbar.pack(fill=tk.Y, side=tk.RIGHT)

# Load saved note
text_area.insert(tk.END, load_note())

# ── Pokémon overlay canvas ────────────────────────────────────────────────────
poke_canvas = tk.Canvas(root, width=128, height=148, bg="#ffd740",
                        highlightthickness=0)
poke_canvas.place(relx=1.0, rely=1.0, anchor="se", x=-4, y=-4)
poke_canvas.lift()     # keep above text area
# Pass clicks through to the text area below
poke_canvas.bind("<Button-1>", lambda e: text_area.focus_set())

_poke_img_ref = None   # keep reference so GC doesn't collect it
_poke_img_id  = None
_anim_step    = [0]

def on_pokemon_loaded(name, img_bytes):
    global _poke_img_ref, _poke_img_id
    if not HAS_PIL:
        return
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGBA")
        img = img.resize((128, 128), Image.NEAREST)
        _poke_img_ref = ImageTk.PhotoImage(img)
        _poke_img_id  = poke_canvas.create_image(64, 64, image=_poke_img_ref, anchor="center")
        root.title(f"Sticky Note  •  {name}")
        title_lbl.config(text=f"📝 Sticky Note  •  {name}")
        start_animation()
    except Exception as e:
        print(f"[Pokémon] Render error: {e}")

def start_animation():
    """Bob up/down + breathe opacity at ~20 fps."""
    def animate():
        if _poke_img_id is None:
            return
        t = _anim_step[0] * 0.1

        # Bob: move image up and down on canvas
        bob = 64 + int(6 * math.sin(t))          # centre y oscillates 58–70
        poke_canvas.coords(_poke_img_id, 64, bob)

        # Breathe: change canvas background alpha isn't natively supported,
        # so we simulate it by adjusting canvas stipple / transparency via a
        # semi-transparent rectangle overlay on the canvas
        opacity = 0.65 + 0.35 * ((math.sin(t * 0.7) + 1) / 2)   # 0.65 → 1.0
        # Tkinter doesn't support per-widget alpha, so we lighten the bg instead
        intensity = int(255 * opacity)
        bg_color  = f"#{intensity:02x}{min(intensity+20,255):02x}{max(intensity-60,0):02x}"
        # Just animate the canvas bg subtly as a breathing glow
        r = int(0xff * opacity)
        g = int(0xee * opacity)
        b = int(0x60 * opacity)
        poke_canvas.config(bg=f"#{r:02x}{g:02x}{b:02x}")

        _anim_step[0] += 1
        root.after(50, animate)   # 50 ms → 20 fps

    animate()

fetch_pokemon(on_pokemon_loaded)

# ── Save on close ─────────────────────────────────────────────────────────────
def on_close():
    save_note(text_area.get("1.0", tk.END).rstrip("\n"))
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
close_btn.config(command=on_close)

# ── Run ───────────────────────────────────────────────────────────────────────
root.mainloop()
