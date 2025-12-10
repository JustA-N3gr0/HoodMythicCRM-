import json
import os

USER_FILE = "user.json"

def load_user():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_user(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f, indent=4)