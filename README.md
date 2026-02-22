# 📝 Sticky Notes

A lightweight, always-on-top sticky notes app with an **animated Pokémon buddy**. Built with Python — available for both **Linux** and **Windows**.

---

## ✨ Features

- 🖼️ Semi-transparent, borderless window
- �� Always on top & visible on all workspaces
- 💾 Auto-saves note content on close, restores on relaunch
- 🎮 Animated Pokémon buddy (random Gen 1, fetched from PokéAPI)
- 📜 Scrollable text area — window never resizes as you type

---

## 🖥️ Platform Support

| Platform | Toolkit | Entry Point |
|----------|---------|-------------|
| **Linux** (X11 / XWayland) | GTK3 + PyGObject | `linux/main.py` |
| **Windows** | tkinter + Pillow | `windows/main.py` |

---

## 🚀 Quick Start — Build Once, Click Forever

Each platform has a **one-time build script** that installs all dependencies and produces a standalone executable. After that, just double-click to launch — no terminal needed.

### 🐧 Linux
```bash
cd linux
chmod +x build.sh
./build.sh
```
Executable → `linux/dist/sticky_notes`

### 🪟 Windows
```
cd windows
double-click build.bat
```
Executable → `windows\dist\sticky_notes.exe`

---

## 💾 Save Location

Notes are saved automatically when you close the app:

| OS | Path |
|----|------|
| Linux | `~/sticky-notes/note.txt` |
| Windows | `%APPDATA%\sticky-notes\note.txt` |

---

## 📁 Project Structure

```
sticky_notes/
├── linux/
│   ├── main.py          # Linux app (GTK3)
│   ├── build.sh         # One-time build script
│   ├── run.sh           # Run without building
│   ├── requirements.txt
│   └── README.md
├── windows/
│   ├── main.py          # Windows app (tkinter)
│   ├── build.bat        # One-time build script
│   ├── requirements.txt
│   └── README.md
├── .env                 # USER_AGENT for PokéAPI (not committed)
└── README.md
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root with:
```env
USER_AGENT= "enter your value"
```

---

## 🛠️ Dependencies

### Linux
- `python-gobject` — GTK3 Python bindings
- `gtk3` — GUI toolkit
- `libwnck3` — Always-on-top / sticky workspace control
- `python-dotenv` — `.env` support
- `pyinstaller` — Build standalone executable

### Windows
- `pillow` — Pokémon sprite rendering
- `python-dotenv` — `.env` support
- `pyinstaller` — Build standalone executable
- `tkinter` — Built into Python (no install needed)
