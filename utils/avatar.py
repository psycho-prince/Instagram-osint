import hashlib
import os
import json
import httpx

AVATAR_DIR = "avatars"
INDEX_FILE = os.path.join(AVATAR_DIR, "index.json")


def _hash_url(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def load_index():
    if not os.path.exists(INDEX_FILE):
        return {}
    with open(INDEX_FILE, "r") as f:
        return json.load(f)


def save_index(index):
    os.makedirs(AVATAR_DIR, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)


async def track_avatar(user_id, profile_pic_url):
    """
    Tracks profile picture changes by URL hash.
    """
    index = load_index()
    user_id = str(user_id)

    current_hash = _hash_url(profile_pic_url)

    history = index.get(user_id, [])

    if history and history[-1]["hash"] == current_hash:
        return history, False  # no change

    entry = {
        "hash": current_hash,
        "url": profile_pic_url,
    }

    history.append(entry)
    index[user_id] = history
    save_index(index)

    return history, True
