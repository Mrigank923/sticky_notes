#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  Sticky Notes — Linux one-time build script
#  Produces a single executable: dist/sticky_notes
#  After building, just double-click or run ./dist/sticky_notes
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Sticky Notes — Linux Builder           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Step 1: Install system dependencies ──────────────────────────────────────
echo "[1/4] Installing system packages..."
if command -v pacman &>/dev/null; then
    sudo pacman -S --needed python-gobject gtk3 libwnck3
elif command -v apt &>/dev/null; then
    sudo apt install -y python3-gi python3-gi-cairo \
        gir1.2-gtk-3.0 gir1.2-wnck-3.0
elif command -v dnf &>/dev/null; then
    sudo dnf install -y python3-gobject gtk3 libwnck3
else
    echo "[WARN] Unknown distro — please install GTK3 + PyGObject manually."
fi

# ── Step 2: Set up Python virtual environment ────────────────────────────────
echo ""
echo "[2/4] Setting up virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# ── Step 3: Install Python dependencies ─────────────────────────────────────
echo ""
echo "[3/4] Installing Python packages..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# ── Step 4: Build executable with PyInstaller ────────────────────────────────
echo ""
echo "[4/4] Building executable..."
pyinstaller \
    --onefile \
    --name "sticky_notes" \
    --noconsole \
    main.py

echo ""
echo "✅ Build complete!"
echo "   Executable → $SCRIPT_DIR/dist/sticky_notes"
echo ""
echo "   Run it anytime with:"
echo "     ./dist/sticky_notes"
echo ""
echo "   Or copy it anywhere and double-click it."
