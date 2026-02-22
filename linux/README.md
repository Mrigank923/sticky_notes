# 📝 Sticky Notes — Linux

A lightweight, always-on-top sticky notes app with a Pokémon buddy. Built with Python + GTK3 for Linux (X11 / XWayland).

---

## 🚀 Quick Start — Build Once, Click Forever

Run the build script **once**. It installs everything and produces a standalone executable.

```bash
chmod +x build.sh
./build.sh
```

After the build finishes, your executable is at:
```
dist/sticky_notes
```

Just double-click it or run `./dist/sticky_notes` — no Python or terminal needed again.

---

## 📦 What `build.sh` does

| Step | Action |
|------|--------|
| 1 | Installs GTK3 + PyGObject system packages (auto-detects Arch / Debian / Fedora) |
| 2 | Creates a Python virtual environment |
| 3 | Installs Python packages (`PyGObject`, `python-dotenv`, `pyinstaller`) |
| 4 | Builds a single-file executable with PyInstaller |

---

## ✨ Features

- 🖼️ Semi-transparent borderless window
- 📌 Always on top & visible on all workspaces
- 💾 Auto-saves on close → `~/.local/share/sticky-notes/note.txt`
- 🎮 Animated Pokémon buddy (fetched from PokéAPI)
- 🔁 Restores last note on relaunch

---

## 📁 Structure

```
linux/
├── main.py          # Application source
├── build.sh         # One-time build script
├── requirements.txt # Python dependencies
└── README.md
```
