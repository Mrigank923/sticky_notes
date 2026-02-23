"""
sync.py — WebSocket sync server for Sticky Notes
==================================================
Runs a lightweight WebSocket server in a background thread.
The mobile app connects to it over local WiFi.

Protocol (JSON messages):
  PC → Mobile:  { "type": "update", "text": "...", "ts": 1234567890.0 }
  Mobile → PC:  { "type": "update", "text": "...", "ts": 1234567890.0 }
  PC → Mobile:  { "type": "ping" }
  Mobile → PC:  { "type": "pong" }

Sync rule: last-write-wins (highest timestamp kept).
No database — both sides persist to their own local file.
"""

import asyncio
import json
import os
import threading
import time
import socket
import websockets
from dotenv import load_dotenv

# .env lives one level above linux/
_ENV_FILE = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=os.path.abspath(_ENV_FILE))

# ── Config ────────────────────────────────────────────────────────────────────
WS_HOST = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT = int(os.getenv("WS_PORT", "8765"))

# ── State shared with main.py ─────────────────────────────────────────────────
_connected_clients: set = set()
_on_remote_update  = None   # callback(text) → called when mobile sends new text
_get_current_text  = None   # callable() → returns current note text + timestamp
_loop              = None   # the asyncio event loop running in the bg thread

def get_local_ip() -> str:
    """Return this machine's LAN IP so the user can tell the mobile app."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# ── WebSocket handler ─────────────────────────────────────────────────────────
async def _handler(websocket):
    _connected_clients.add(websocket)
    ip = websocket.remote_address[0]
    print(f"[Sync] Mobile connected from {ip}")

    # Send current note immediately on connect
    if _get_current_text:
        text, ts = _get_current_text()
        await websocket.send(json.dumps({"type": "update", "text": text, "ts": ts}))

    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg.get("type") == "update":
                remote_text = msg.get("text", "")
                remote_ts   = msg.get("ts", 0.0)

                # Last-write-wins: only apply if remote is newer
                if _get_current_text:
                    _, local_ts = _get_current_text()
                    if remote_ts > local_ts:
                        print(f"[Sync] Received newer update from mobile (ts={remote_ts:.0f})")
                        if _on_remote_update:
                            _on_remote_update(remote_text, remote_ts)

            elif msg.get("type") == "ping":
                await websocket.send(json.dumps({"type": "pong"}))

    except websockets.exceptions.ConnectionClosedError:
        pass
    finally:
        _connected_clients.discard(websocket)
        print(f"[Sync] Mobile disconnected ({ip})")

# ── Broadcast to all connected mobile clients ─────────────────────────────────
def broadcast(text: str, ts: float):
    """Call from main.py whenever the note text changes."""
    if not _connected_clients or _loop is None:
        return
    msg = json.dumps({"type": "update", "text": text, "ts": ts})
    asyncio.run_coroutine_threadsafe(_broadcast_all(msg), _loop)

async def _broadcast_all(msg: str):
    dead = set()
    for ws in list(_connected_clients):
        try:
            await ws.send(msg)
        except Exception:
            dead.add(ws)
    _connected_clients.difference_update(dead)

# ── Start server in background thread ────────────────────────────────────────
def start(on_remote_update, get_current_text):
    """
    on_remote_update(text, ts) — called on GTK main thread when mobile sends update
    get_current_text()         — returns (text, ts) tuple of current local note
    """
    global _on_remote_update, _get_current_text, _loop
    _on_remote_update = on_remote_update
    _get_current_text = get_current_text

    def _run():
        global _loop
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)

        async def _serve():
            async with websockets.serve(_handler, WS_HOST, WS_PORT):
                ip = get_local_ip()
                print(f"[Sync] WebSocket server started.")
                print(f"[Sync] Connect mobile app to:  ws://{ip}:{WS_PORT}")
                await asyncio.Future()   # run forever

        _loop.run_until_complete(_serve())

    t = threading.Thread(target=_run, daemon=True)
    t.start()
