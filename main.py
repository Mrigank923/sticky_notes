#!/usr/bin/env python3
import gi
import os
import sys
import json
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, Gdk, GdkX11, Wnck

# ── Persistence — OS-aware save location ─────────────────────────────────────

def _get_data_dir():
    if sys.platform == "win32":
        # Windows: C:\Users\<user>\AppData\Roaming\sticky-notes
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/sticky-notes
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        # Linux / other Unix: ~/sticky-notes  (XDG default)
        base = os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~")))
    return os.path.join(base, "sticky-notes")

DATA_DIR  = _get_data_dir()
NOTE_FILE = os.path.join(DATA_DIR, "note.txt")
os.makedirs(DATA_DIR, exist_ok=True)
print(f"[INFO] Notes saved to: {NOTE_FILE}")

def load_note():
    if os.path.exists(NOTE_FILE):
        with open(NOTE_FILE, "r") as f:
            return f.read()
    return ""

def save_note(text):
    with open(NOTE_FILE, "w") as f:
        f.write(text)

# ── Transparency via RGBA visual ──────────────────────────────────────────────

def apply_rgba_visual(widget, *_):
    screen = widget.get_screen()
    visual = screen.get_rgba_visual()
    if visual and screen.is_composited():
        widget.set_visual(visual)

# ── CSS: semi-transparent yellow background ───────────────────────────────────

css = b"""
window {
    background-color: rgba(255, 218, 65, 0);
    border-radius: 8px;
}
textview, textview text {
    background-color: rgba(255, 218, 65, 0.08);
    color: #d4ecfa;
    font-size: 13px;
}
"""
prov = Gtk.CssProvider()
prov.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), prov,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

# Create's the main window
window = Gtk.Window(title="Sticky Note")
window.set_default_size(300, 200)
window.set_border_width(1)
window.set_resizable(True)
window.set_app_paintable(True)          
window.connect("screen-changed", apply_rgba_visual)
apply_rgba_visual(window)               # apply immediately

# Make the window always on top and sticky (all workspaces)
window.set_keep_above(True)   # GTK asks WM to keep it above others:contentReference[oaicite:2]{index=2}
window.stick()                # GTK asks WM to keep it on all desktops:contentReference[oaicite:3]{index=3}

# (Optional) Use libwnck to enforce sticky/above as an X11 hint:
screen = Wnck.Screen.get_default()
screen.force_update()  # Populate Wnck window list
# Get the X11 window ID (XID) of our Gtk.Window
gdk_window = window.get_window()
if gdk_window:
    xid = gdk_window.get_xid()
    wnck_win = Wnck.Window.get(xid)
    if wnck_win:
        wnck_win.stick()         # Set the Wnck sticky state
        wnck_win.make_above()    # Set the Wnck above state

# Text area for note content
textview = Gtk.TextView()
textview.set_wrap_mode(Gtk.WrapMode.WORD)
textview.set_left_margin(5)
textview.set_right_margin(5)

# Load previously saved note text
buf = textview.get_buffer()
buf.set_text(load_note())

window.add(textview)

# Save note text when the window is closed
def on_destroy(widget):
    start, end = buf.get_bounds()
    save_note(buf.get_text(start, end, False))
    Gtk.main_quit()

window.connect("destroy", on_destroy)

# Show window and start GTK loop
window.show_all()
Gtk.main()