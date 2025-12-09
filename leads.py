import json
import os

LEADS_FILE = "global_leads.json"

# ---------------------------------------------------------------------------
# LOAD + SAVE LEADS
# ---------------------------------------------------------------------------

def load_leads():
    if not os.path.exists(LEADS_FILE):
        return {}
    try:
        with open(LEADS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_leads(leads):
    with open(LEADS_FILE, "w") as f:
        json.dump(leads, f, indent=4)

# ---------------------------------------------------------------------------
# ADD NEW LEAD
# ---------------------------------------------------------------------------

def add_lead(name, phone):
    leads = load_leads()
    if phone.strip() == "":
        return False
    leads[phone] = {
        "name": name,
        "called_by": None,
        "status": None,
        "notes": ""
    }
    save_leads(leads)
    return True

# ---------------------------------------------------------------------------
# UPDATE LEAD STATUS
# ---------------------------------------------------------------------------

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

def update_lead(phone, agent, status, notes=""):
    leads = load_leads()
    if phone not in leads:
        return False
    leads[phone]["status"] = status
    leads[phone]["called_by"] = agent
    leads[phone]["notes"] = notes
    save_leads(leads)
    return True

# ---------------------------------------------------------------------------
# GET FILTERED LEADS
# ---------------------------------------------------------------------------

def get_filtered_leads(agent=None, filter_dispo=None, uncalled_only=False, my_leads_only=False):
    leads = load_leads()
    filtered = {}
    for phone, info in leads.items():
        if filter_dispo and filter_dispo != "All" and info.get("status") != filter_dispo:
            continue
        if uncalled_only and info.get("status") is not None:
            continue
        if my_leads_only and info.get("called_by") != agent:
            continue
        filtered[phone] = info
    return filtered

# ---------------------------------------------------------------------------
# LEADERBOARD
# ---------------------------------------------------------------------------

def get_leaderboard():
    leads = load_leads()
    scores = {}
    for phone, info in leads.items():
        ag = info.get("called_by")
        status = info.get("status")
        if ag and status in DISPOSITIONS:
            scores[ag] = scores.get(ag, 0) + DISPOSITIONS[status]
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

# ---------------------------------------------------------------------------
# UTILITY
# ---------------------------------------------------------------------------

def total_points():
    leaderboard = get_leaderboard()
    return sum(leaderboard.values())