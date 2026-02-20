# 📝 Sticky Notes

A lightweight, always-on-top sticky notes app built with **Python + GTK3**, for Linux (X11 / XWayland). Notes are transparent, draggable, and persist across sessions.

> ⚠️ **Linux only.** Requires X11 or XWayland. Native Wayland sessions may have limited support.

---

## ✨ Features

- 🖼️ Semi-transparent, borderless window
- 📌 Always on top & visible on all workspaces
- 💾 Auto-saves note content on close
- 🔁 Restores your last note on relaunch

---

## �� Installation

### Arch / Manjaro
```bash
sudo pacman -S python-gobject gtk3 libwnck3
```

### Debian / Ubuntu / Mint
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-wnck-3.0
```

### Fedora
```bash
sudo dnf install python3-gobject gtk3 libwnck3
```

---

## 🚀 Usage

### Option 1 — Shell script (recommended)
```bash
./run.sh
```
Automatically checks for dependencies and launches the app.

### Option 2 — Direct
```bash
python3 main.py
```

---

## 💾 Save Location

Notes are saved automatically when you close the app:

```
~/sticky-notes/note.txt
```

---

## 📁 Project Structure

```
sticky_notes/
├── main.py          # Application entry point
├── run.sh           # Linux launcher script
├── requirements.txt # Python dependencies
└── README.md
```

---

## 🛠️ Dependencies

- `python-gobject` — Python bindings for GTK3
- `gtk3` — GUI toolkit
- `libwnck3` — Window manager control (always-on-top, sticky)
