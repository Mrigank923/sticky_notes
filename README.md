# 📝 Sticky Notes

A lightweight, always-on-top sticky notes app with an **animated Pokémon buddy** and **real-time mobile sync**. Built with Python for desktop (Linux & Windows) and React Native for Android.

---

## ✨ Features

- 🖼️ Semi-transparent, borderless window
- 📌 Always on top & visible on all workspaces
- 💾 Auto-saves note content on close, restores on relaunch
- 🎮 Animated Pokémon buddy (random Gen 1, fetched from PokéAPI)
- 📜 Scrollable text area — window never resizes as you type
- 📱 **Real-time sync with Android phone** over local WiFi (WebSocket, no database)

---

## 🖥️ Platform Support

| Platform | Toolkit | Entry Point |
|----------|---------|-------------|
| **Linux** (X11 / XWayland) | GTK3 + PyGObject | `linux/main.py` |
| **Windows** | tkinter + Pillow | `windows/main.py` |
| **Android** | React Native (bare) | `mobile/App.js` |

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

### 📱 Android (React Native)
```bash
cd mobile
npm install
# build APK (requires Android SDK + Java 21)
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk
cd android && ./gradlew assembleDebug
# APK → android/app/build/outputs/apk/debug/app-debug.apk
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

---

## 📡 Mobile Sync Setup

The Linux app runs a **WebSocket server** on port `8765`. The Android app connects to it over your local WiFi network.

1. Run the Linux sticky notes app — it starts the sync server automatically
2. Install the Android APK on your phone
3. Open the app, tap the **PC IP** field and enter your PC's local IP — the app saves it for future sessions
4. The status bar will show **✅ Synced with PC** when connected
5. Any edit on either device syncs to the other within ~1 second

> **Offline support:** If the phone can't reach the PC, notes are saved locally with `AsyncStorage` and re-synced when the connection is restored.

---

## 💾 Save Location

Notes are saved automatically when you close the app:

| OS | Path |
|----|------|
| Linux | `~/sticky-notes/note.txt` |
| Windows | `%APPDATA%\sticky-notes\note.txt` |
| Android | AsyncStorage (internal app storage) |

---

## 📁 Project Structure

```
sticky_notes/
├── linux/
│   ├── main.py          # Linux app (GTK3)
│   ├── sync.py          # WebSocket sync server (port 8765)
│   ├── build.sh         # One-time build script
│   ├── run.sh           # Run without building
│   ├── requirements.txt
│   └── README.md
├── windows/
│   ├── main.py          # Windows app (tkinter)
│   ├── build.bat        # One-time build script
│   ├── requirements.txt
│   └── README.md
├── mobile/
│   ├── App.js           # React Native app (Android)
│   ├── index.js         # App entry point
│   ├── package.json
│   ├── babel.config.js
│   ├── metro.config.js
│   └── android/         # Android native project
├── .env                 # USER_AGENT + WS_PORT (not committed)
└── README.md
```

---

## ⚙️ Environment Variables

### Root `.env` (for Python desktop apps)
```env
USER_AGENT=sticky-notes-app/1.0 (https://github.com/Mrigank923/sticky_notes)
WS_HOST=0.0.0.0
WS_PORT=8765
RECONNECT_MS=4000
POKEAPI_BASE_URL=https://pokeapi.co/api/v2/pokemon
TOTAL_POKEMON=151
MAX_RETRIES=3
RETRY_DELAY_S=5
```

### `mobile/.env` (for Android app — bundled at build time)
```env
WS_PORT=8765
RECONNECT_MS=4000
```
> ⚠️ `mobile/.env` is read by `react-native-config` at APK build time. Do **not** put secrets here.

---

## 🛠️ Dependencies

### Linux
- `python-gobject` — GTK3 Python bindings
- `gtk3` — GUI toolkit
- `libwnck3` — Always-on-top / sticky workspace control
- `python-dotenv` — `.env` support
- `websockets` — WebSocket sync server
- `pyinstaller` — Build standalone executable

### Windows
- `pillow` — Pokémon sprite rendering
- `python-dotenv` — `.env` support
- `pyinstaller` — Build standalone executable

### Android
- `react-native` 0.73.4 — Mobile framework
- `@react-native-async-storage/async-storage` — Local persistence
