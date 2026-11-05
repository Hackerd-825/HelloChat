import json
import os
import time
import urllib.request

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MAX_MESSAGES = 100
MAX_TEXT = 500
MAX_USER = 30
KEY_LIST = "hellochat:messages"
KEY_COUNTER = "hellochat:counter"

# Redis REST (Upstash / Vercel KV). Sans ces variables : mémoire locale (dev uniquement).
REDIS_URL = (os.environ.get("UPSTASH_REDIS_REST_URL")
             or os.environ.get("KV_REST_API_URL"))
REDIS_TOKEN = (os.environ.get("UPSTASH_REDIS_REST_TOKEN")
               or os.environ.get("KV_REST_API_TOKEN"))

_local = {"messages": [], "counter": 0}


def redis(*command):
    req = urllib.request.Request(
        REDIS_URL,
        data=json.dumps(list(command)).encode(),
        headers={"Authorization": f"Bearer {REDIS_TOKEN}",
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())["result"]


def get_messages(after=0):
    if REDIS_URL and REDIS_TOKEN:
        raw = redis("LRANGE", KEY_LIST, -MAX_MESSAGES, -1) or []
        msgs = [json.loads(m) for m in raw]
    else:
        msgs = _local["messages"]
    return [m for m in msgs if m["id"] > after]


def add_message(user, text):
    if REDIS_URL and REDIS_TOKEN:
        msg_id = redis("INCR", KEY_COUNTER)
        msg = {"id": msg_id, "user": user, "text": text, "ts": int(time.time())}
        redis("RPUSH", KEY_LIST, json.dumps(msg))
        redis("LTRIM", KEY_LIST, -MAX_MESSAGES, -1)
    else:
        _local["counter"] += 1
        msg = {"id": _local["counter"], "user": user, "text": text,
               "ts": int(time.time())}
        _local["messages"].append(msg)
        del _local["messages"][:-MAX_MESSAGES]
    return msg


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/messages", methods=["GET"])
def list_messages():
    after = request.args.get("after", 0, type=int)
    return jsonify(get_messages(after))


@app.route("/api/messages", methods=["POST"])
def post_message():
    data = request.get_json(silent=True) or {}
    user = str(data.get("user", "")).strip()[:MAX_USER]
    text = str(data.get("text", "")).strip()[:MAX_TEXT]
    if not user or not text:
        return jsonify({"error": "user et text requis"}), 400
    return jsonify(add_message(user, text)), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
