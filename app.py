"""
PSC Consumer Record Search -- Web Frontend
Run:  python app.py
Then share the printed public URL on WhatsApp.
"""

import os
import sys
import threading
import time

from flask import Flask, render_template, request, jsonify
import search as search_module
from search import search

app = Flask(__name__)

FIELD_OPTIONS = [
    ("Auto-detect",       ""),
    ("Consumer No",       "cons"),
    ("DTS ID",            "dts"),
    ("Feeder Name",       "feeder"),
    ("Feeder ID",         "feeder_id"),
    ("IBC Name",          "ibc"),
    ("AMR Status",        "amr"),
    ("Meter Type",        "meter_type"),
    ("Tariff",            "tariff"),
    ("PMT Name",          "pmt"),
    ("Meter No",          "meter"),
    ("Contract Account",  "account"),
    ("Install No",        "install"),
    ("GIC Code",          "gic"),
]

DISPLAY_COLS = [
    "Cons_No", "Contract_Ac", "Meter_No", "Meter_Typ", "Tariff",
    "IBC_Name", "AMR_STATUS", "DTS_ID", "PMT_Name", "Feeder_Name", "FeederID"
]

COL_LABELS = {
    "Cons_No":     "Consumer No",
    "Contract_Ac": "Contract Ac",
    "Meter_No":    "Meter No",
    "Meter_Typ":   "Meter Type",
    "Tariff":      "Tariff",
    "IBC_Name":    "IBC",
    "AMR_STATUS":  "AMR Status",
    "DTS_ID":      "DTS ID",
    "PMT_Name":    "PMT Name",
    "Feeder_Name": "Feeder",
    "FeederID":    "Feeder ID",
}

AMR_BADGE = {
    "AMR":      "badge-amr",
    "NON AMR":  "badge-nonamr",
    "INACTIVE": "badge-inactive",
    "ACTIVE":   "badge-active",
}

METER_BADGE = {
    "CTO":      "badge-cto",
    "THREE":    "badge-three",
    "HOOK":     "badge-hook",
    "INACTIVE": "badge-inactive",
}

# Will be set once ngrok tunnel is created
PUBLIC_URL = None


@app.route("/")
def index():
    return render_template("index.html",
                           field_options=FIELD_OPTIONS,
                           public_url=PUBLIC_URL or "")


@app.route("/public-url")
def get_public_url():
    return jsonify({"url": PUBLIC_URL or ""})


@app.route("/search")
def do_search():
    query = request.args.get("q", "").strip()
    field = request.args.get("field", "").strip() or None
    limit = min(int(request.args.get("limit", 50)), 500)
    exact = request.args.get("exact", "false").lower() == "true"

    if not query:
        return jsonify({"error": "Please enter a search term.", "results": [], "total": 0})

    try:
        results, resolved_field, _ = search(query, field=field, limit=limit, exact=exact)
    except SystemExit:
        return jsonify({"error": "Data file not found or invalid field.", "results": [], "total": 0})

    rows = [{col: row.get(col, "") for col in DISPLAY_COLS} for row in results]

    return jsonify({
        "results":        rows,
        "total":          len(results),
        "truncated":      len(results) >= limit,
        "field_searched": resolved_field or "All fields",
        "columns":        DISPLAY_COLS,
        "col_labels":     COL_LABELS,
        "amr_badge":      AMR_BADGE,
        "meter_badge":    METER_BADGE,
    })


def start_tunnel(port):
    """Create a public URL via Cloudflare Tunnel (cloudflared)."""
    global PUBLIC_URL
    import subprocess, re, queue

    time.sleep(2)

    # Matches both trycloudflare.com and *.cfargotunnel.com URLs
    pattern = re.compile(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com')

    cmd = ['cloudflared', 'tunnel', '--url', f'http://localhost:{port}',
           '--no-autoupdate']
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        print("\n  cloudflared not found. Install it with:")
        print("    winget install --id Cloudflare.cloudflared")
        print("  Falling back to localhost.run...\n")
        _start_tunnel_localhostrun(port)
        return
    except Exception as e:
        print(f"\n  Failed to start cloudflared: {e}")
        return

    q = queue.Queue()

    def _reader():
        try:
            for line in iter(proc.stdout.readline, b''):
                q.put(line)
        except Exception:
            pass
        q.put(None)

    threading.Thread(target=_reader, daemon=True).start()

    buffer = ""
    deadline = time.time() + 60

    while time.time() < deadline:
        try:
            chunk = q.get(timeout=1)
        except queue.Empty:
            continue
        if chunk is None:
            break
        buffer += chunk.decode('utf-8', errors='ignore')
        match = pattern.search(buffer)
        if match:
            PUBLIC_URL = match.group(0)
            border = "=" * 58
            print(f"\n{border}", flush=True)
            print(f"  PUBLIC URL (share on WhatsApp):", flush=True)
            print(f"  {PUBLIC_URL}", flush=True)
            print(f"{border}\n", flush=True)
            return

    print("\n  Could not get public URL from cloudflared.", flush=True)


def _start_tunnel_localhostrun(port):
    """Fallback: localhost.run SSH tunnel."""
    global PUBLIC_URL
    import subprocess, re, queue

    pattern = re.compile(r'https://[a-zA-Z0-9\-]+\.lhr\.life')

    cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ServerAliveInterval=30',
           '-R', f'80:localhost:{port}', 'nokey@localhost.run']
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL)
    except Exception as e:
        print(f"\n  Failed to start SSH tunnel: {e}")
        return

    q = queue.Queue()

    def _reader():
        try:
            for line in iter(proc.stdout.readline, b''):
                q.put(line)
        except Exception:
            pass
        q.put(None)

    threading.Thread(target=_reader, daemon=True).start()

    buffer = ""
    deadline = time.time() + 40

    while time.time() < deadline:
        try:
            chunk = q.get(timeout=1)
        except queue.Empty:
            continue
        if chunk is None:
            break
        buffer += chunk.decode('utf-8', errors='ignore')
        clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]|\[7m|\[0m|\[49m', '', buffer)
        match = pattern.search(clean)
        if match:
            PUBLIC_URL = match.group(0)
            border = "=" * 58
            print(f"\n{border}", flush=True)
            print(f"  PUBLIC URL (share on WhatsApp):", flush=True)
            print(f"  {PUBLIC_URL}", flush=True)
            print(f"{border}\n", flush=True)
            return

    print("\n  Could not get public URL -- tunnel may still be connecting.", flush=True)


if __name__ == "__main__":
    port = 5000
    print(f"\n  Starting PSC Search on http://localhost:{port}")
    print(f"  Creating public link via Cloudflare Tunnel...")

    # Start Cloudflare tunnel in background thread
    t = threading.Thread(target=start_tunnel, args=(port,), daemon=True)
    t.start()

    # Start Flask (use_reloader=False so ngrok thread isn't forked twice)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
