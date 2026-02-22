#!/usr/bin/env python3
import gi
import os
import sys
import json
import random
import threading
import urllib.request
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env into os.environ
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, Gdk, GdkX11, Wnck, GLib, GdkPixbuf

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

# ── Pokémon buddy ─────────────────────────────────────────────────────────────
TOTAL_POKEMON = 151   # Gen 1 — feel free to raise up to 1025

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

            GLib.idle_add(callback, name, img_bytes)
        except Exception as e:
            print(f"[Pokémon] Could not fetch: {e}")
    threading.Thread(target=_fetch, daemon=True).start()


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
    background-color: rgba(207, 207, 200, 0.30);
    color: #0118cc;
    font-size: 20px;
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

# ── Main layout ──────────────────────────────────────────────────────────────
# Overlay lets us float the Pokémon sprite over the text area
overlay = Gtk.Overlay()
window.add(overlay)

# Text area for note content — wrapped in a ScrolledWindow so the
# window never grows; scrollbars appear when content overflows.
scrolled = Gtk.ScrolledWindow()
scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
scrolled.set_hexpand(True)
scrolled.set_vexpand(True)

textview = Gtk.TextView()
textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)  # wrap at word boundaries, then chars
textview.set_hexpand(False)                      # don't request extra horizontal space
textview.set_size_request(0, -1)                 # allow textview to shrink horizontally
textview.set_left_margin(5)
textview.set_right_margin(5)

# Load previously saved note text
buf = textview.get_buffer()
buf.set_text(load_note())
scrolled.add(textview)
overlay.add(scrolled)

# ── Pokémon corner widget ─────────────────────────────────────────────────────
poke_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
poke_box.set_halign(Gtk.Align.END)
poke_box.set_valign(Gtk.Align.END)
poke_box.set_margin_end(4)
poke_box.set_margin_bottom(2)

poke_image = Gtk.Image()

poke_box.pack_start(poke_image, False, False, 0)
overlay.add_overlay(poke_box)
overlay.set_overlay_pass_through(poke_box, True)  # clicks pass through to textview

def on_pokemon_loaded(name, img_bytes):
    try:
        loader = GdkPixbuf.PixbufLoader()
        loader.write(img_bytes)
        loader.close()
        pixbuf = loader.get_pixbuf()
        # Scale to double sprite size (128×128)
        pixbuf = pixbuf.scale_simple(128, 128, GdkPixbuf.InterpType.BILINEAR)
        poke_image.set_from_pixbuf(pixbuf)
        window.set_title(f"Sticky Note  •  {name}")

        # ── Animation: bob up/down + breathe opacity ──────────────────────
        import math
        anim_step = [0]   # mutable counter shared with closure

        def animate():
            t = anim_step[0] * 0.1          # time in radians

            # Bob: shift margin_bottom between 2 px and 14 px (smooth sine)
            bob = int(8 + 6 * math.sin(t))
            poke_box.set_margin_bottom(bob)

            # Breathe: opacity oscillates between 0.65 and 1.0
            opacity = 0.825 + 0.175 * math.sin(t * 0.7)
            poke_image.set_opacity(opacity)

            anim_step[0] += 1
            return GLib.SOURCE_CONTINUE   # keep repeating

        # Tick every 50 ms → ~20 fps, smooth enough without heavy CPU use
        GLib.timeout_add(50, animate)

    except Exception as e:
        print(f"[Pokémon] Render error: {e}")

# Fetch a Pokémon in the background so startup isn't delayed
fetch_pokemon(on_pokemon_loaded)

# Save note text when the window is closed
def on_destroy(widget):
    start, end = buf.get_bounds()
    save_note(buf.get_text(start, end, False))
    Gtk.main_quit()

window.connect("destroy", on_destroy)

# Show window and start GTK loop
window.show_all()
Gtk.main()