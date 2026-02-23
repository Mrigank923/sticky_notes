#!/usr/bin/env python3
import gi
import os
import sys
import json
import math
import time
import random
import threading
import urllib.request
from dotenv import load_dotenv

# .env lives in the repo root (one level above linux/)
_ENV_FILE = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=os.path.abspath(_ENV_FILE))
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

DATA_DIR   = _get_data_dir()
NOTE_FILE  = os.path.join(DATA_DIR, "note.txt")
TS_FILE    = os.path.join(DATA_DIR, "note.ts")   # stores last-modified timestamp
os.makedirs(DATA_DIR, exist_ok=True)
print(f"[INFO] Notes saved to: {NOTE_FILE}")

def load_note():
    if os.path.exists(NOTE_FILE):
        with open(NOTE_FILE, "r") as f:
            return f.read()
    return ""

def load_ts() -> float:
    if os.path.exists(TS_FILE):
        try:
            return float(open(TS_FILE).read().strip())
        except Exception:
            pass
    return 0.0

def save_note(text, ts: float = None):
    if ts is None:
        ts = time.time()
    with open(NOTE_FILE, "w") as f:
        f.write(text)
    with open(TS_FILE, "w") as f:
        f.write(str(ts))

# ── Pokémon buddy ─────────────────────────────────────────────────────────────
TOTAL_POKEMON   = int(os.getenv("TOTAL_POKEMON",   "151"))
MAX_RETRIES     = int(os.getenv("MAX_RETRIES",     "3"))
RETRY_DELAY_S   = int(os.getenv("RETRY_DELAY_S",   "5"))
POKEAPI_BASE_URL = os.getenv("POKEAPI_BASE_URL", "https://pokeapi.co/api/v2/pokemon")

# Offline fallback — shown when there's no internet connection
OFFLINE_POKEMON = [
    ("Pikachu",    "⚡\n(=·ω·=)\n  Pika!"),
    ("Charmander", "🔥\n(´•ω•`)\n Char!"),
    ("Bulbasaur",  "🌿\n(•‿•)\n Bulba!"),
    ("Squirtle",   "💧\nô‿ô\nSquirt!"),
    ("Gengar",     "👻\n(ΦωΦ)\n Boo!"),
]

def fetch_pokemon(callback):
    """Fetch a random Pokémon sprite + name in a background thread.
    Retries up to MAX_RETRIES times, then falls back to an offline placeholder."""
    def _fetch():
        headers = {"User-Agent": os.getenv("USER_AGENT", "sticky-notes-app/1.0")}
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                poke_id    = random.randint(1, TOTAL_POKEMON)
                api_url    = f"{POKEAPI_BASE_URL}/{poke_id}"

                req = urllib.request.Request(api_url, headers=headers)
                with urllib.request.urlopen(req, timeout=6) as r:
                    data = json.loads(r.read())

                name       = data["name"].capitalize()
                sprite_url = data["sprites"]["front_default"]

                req2 = urllib.request.Request(sprite_url, headers=headers)
                with urllib.request.urlopen(req2, timeout=6) as r:
                    img_bytes = r.read()

                GLib.idle_add(callback, name, img_bytes)
                return  # success — stop retrying

            except Exception as e:
                print(f"[Pokémon] Attempt {attempt}/{MAX_RETRIES} failed: {e}")
                if attempt < MAX_RETRIES:
                    import time
                    time.sleep(RETRY_DELAY_S)

        # All retries exhausted — use offline fallback
        print("[Pokémon] No internet — using offline buddy.")
        GLib.idle_add(callback, None, None)

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
    import math
    anim_step = [0]

    # ── Offline fallback: show ASCII buddy ────────────────────────────────
    if img_bytes is None:
        fallback_name, ascii_art = random.choice(OFFLINE_POKEMON)
        lbl = Gtk.Label(label=ascii_art)
        lbl.set_justify(Gtk.Justification.CENTER)
        lbl.set_opacity(0.85)
        poke_box.pack_start(lbl, False, False, 0)
        poke_box.show_all()
        window.set_title(f"Sticky Note  •  {fallback_name} (offline)")

        def animate_offline():
            t = anim_step[0] * 0.1
            bob = int(8 + 6 * math.sin(t))
            poke_box.set_margin_bottom(bob)
            opacity = 0.7 + 0.3 * ((math.sin(t * 0.7) + 1) / 2)
            lbl.set_opacity(opacity)
            anim_step[0] += 1
            return GLib.SOURCE_CONTINUE

        GLib.timeout_add(50, animate_offline)
        return

    # ── Online: render sprite ─────────────────────────────────────────────
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
        def animate():
            t = anim_step[0] * 0.1

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

# ── Sync server ───────────────────────────────────────────────────────────────
import sync as _sync

def _on_remote_update(text, ts):
    """Called from sync thread when mobile sends newer text — update GTK safely."""
    def _apply():
        buf.handler_block_by_func(_on_text_changed)   # avoid echo-back
        buf.set_text(text)
        buf.handler_unblock_by_func(_on_text_changed)
        save_note(text, ts)
    GLib.idle_add(_apply)

def _get_current_text():
    start, end = buf.get_bounds()
    return buf.get_text(start, end, False), load_ts()

_sync.start(
    on_remote_update  = _on_remote_update,
    get_current_text  = _get_current_text,
)

# Broadcast note changes to connected mobile clients
_last_broadcast = [time.time()]

def _on_text_changed(*_):
    """Debounce: broadcast to mobile 800 ms after the user stops typing."""
    _last_broadcast[0] = time.time()
    def _debounced():
        if time.time() - _last_broadcast[0] >= 0.79:
            start, end = buf.get_bounds()
            text = buf.get_text(start, end, False)
            _sync.broadcast(text, time.time())
    GLib.timeout_add(800, _debounced)

buf.connect("changed", _on_text_changed)

# Save note text when the window is closed
def on_destroy(widget):
    start, end = buf.get_bounds()
    save_note(buf.get_text(start, end, False))
    Gtk.main_quit()

window.connect("destroy", on_destroy)

# Show window and start GTK loop
window.show_all()
Gtk.main()