import json
import os

FILE = "global_leads.json"

def load_leads():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def save_leads(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)