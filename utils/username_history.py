import os
import json

HISTORY_FILE = "username_history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def track_username(user_id, current_username):
    """
    Tracks username changes per user_id.
    """
    user_id = str(user_id)
    data = load_history()

    history = data.get(user_id, [])

    if history and history[-1] == current_username:
        return history, False  # unchanged

    history.append(current_username)
    data[user_id] = history
    save_history(data)

    return history, True
