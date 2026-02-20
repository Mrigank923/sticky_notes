#!/usr/bin/env bash
# ── Sticky Notes launcher ─────────────────────────────────────────────────────
# Installs system dependencies if missing, then runs the app.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Detect distro and install dependencies if needed ─────────────────────────
if ! python3 -c "import gi" &>/dev/null; then
    echo "[INFO] PyGObject not found. Installing dependencies..."

    if command -v pacman &>/dev/null; then
        # Arch / Manjaro
        sudo pacman -S --needed python-gobject gtk3 libwnck3

    elif command -v apt &>/dev/null; then
        # Debian / Ubuntu / Mint
        sudo apt install -y python3-gi python3-gi-cairo \
            gir1.2-gtk-3.0 gir1.2-wnck-3.0

    elif command -v dnf &>/dev/null; then
        # Fedora
        sudo dnf install -y python3-gobject gtk3 libwnck3

    else
        echo "[ERROR] Unsupported distro. Please install PyGObject and GTK3 manually."
        exit 1
    fi
else
    echo "[INFO] Dependencies already satisfied."
fi

# ── Run the app ───────────────────────────────────────────────────────────────
echo "[INFO] Starting Sticky Notes..."
python3 "$SCRIPT_DIR/main.py"
