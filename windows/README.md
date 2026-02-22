# 📝 Sticky Notes — Windows

A lightweight, always-on-top sticky notes app with a Pokémon buddy. Built with Python + tkinter for Windows.

---

## 🚀 Quick Start — Build Once, Click Forever

Run the build script **once**. It installs everything and produces a standalone `.exe`.

1. Make sure **Python 3.10+** is installed → https://python.org
2. Double-click `build.bat` (or run it in Command Prompt)

After the build finishes, your executable is at:
```
dist\sticky_notes.exe
```

Just double-click it — no Python or terminal needed again.

---

## 📦 What `build.bat` does

| Step | Action |
|------|--------|
| 1 | Checks Python is installed |
| 2 | Installs Python packages (`pillow`, `python-dotenv`, `pyinstaller`) |
| 3 | Builds a single `.exe` with PyInstaller (no console window) |

---

## ✨ Features

- 🖼️ Semi-transparent borderless window
- 📌 Always on top
- 💾 Auto-saves on close → `%APPDATA%\sticky-notes\note.txt`
- 🎮 Animated Pokémon buddy (fetched from PokéAPI)
- 🔁 Restores last note on relaunch
- 🖱️ Draggable custom title bar

---

## 📁 Structure

```
windows\
├── main.py          # Application source
├── build.bat        # One-time build script
├── requirements.txt # Python dependencies
└── README.md
```
