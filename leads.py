import json
import os

LEADS_FILE = "global_leads.json"

DISPOSITIONS = {
    "No Answer": 0,
    "Not Interested": 0,
    "Cold Lead": 1,
    "Interested": 3,
    "Hot Lead": 5,
    "Wrong Number": -1,
    "Left Voicemail": 0,
    "Call Back Later": 0,
    "Closed Deal": 10
}

def load_leads():
    if not os.path.exists(LEADS_FILE):
        return {}
    with open(LEADS_FILE, "r") as f:
        return json.load(f)

def save_leads(data):
    with open(LEADS_FILE, "w") as f:
        json.dump(data, f, indent=4)