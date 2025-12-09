import streamlit as st
import pandas as pd
import json
import random
import os
import time

# Set page
st.set_page_config(page_title="Hood Mythic CRM", layout="wide")
st.title("😈 Hood Mythic Realtor CRM - Chaos Mode 🔥")

# Ensure storage files exist
if not os.path.exists("global_leads.json"):
    with open("global_leads.json", "w") as f:
        json.dump({}, f)

if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

# Load storage
with open("global_leads.json", "r") as f:
    global_leads = json.load(f)

with open("users.json", "r") as f:
    users = json.load(f)

# --- Login System ---
st.subheader("Agent Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_btn = st.button("Login")

if login_btn:
    if username in users and users[username]["password"] == password:
        st.success(f"Welcome back {username} 😎")
        if not os.path.exists(f"{username}_data.json"):
            # Create agent data file if not exist
            agent_data = {"called_leads": {}, "uncalled_leads": [], "points": 0}
            # populate uncalled_leads from global_leads
            for phone, info in global_leads.items():
                if "called_by" not in info or info["called_by"] is None:
                    agent_data["uncalled_leads"].append({"phone": phone, "name": info["name"]})
            with open(f"{username}_data.json", "w") as f:
                json.dump(agent_data, f)
        else:
            with open(f"{username}_data.json", "r") as f:
                agent_data = json.load(f)
    else:
        st.error("Invalid username or password 😤")
        st.stop()
else:
    st.stop()

# --- Lead Upload ---
uploaded_files = st.file_uploader(
    "Upload CSV / TXT / XLSX / ODS leads", 
    type=["csv", "txt", "xlsx", "ods"], 
    accept_multiple_files=True
)

def load_file(f):
    try:
        if f.name.endswith(".csv") or f.name.endswith(".txt"):
            df = pd.read_csv(f, sep=None, engine="python")
        elif f.name.endswith(".xlsx"):
            import openpyxl
            df = pd.read_excel(f, engine="openpyxl")
        elif f.name.endswith(".ods"):
            import odf
            df = pd.read_excel(f, engine="odf")
        else:
            return None
        return df
    except Exception as e:
        st.warning(f"Skipping {f.name} due to read error: {e}")
        return None

if uploaded_files:
    for f in uploaded_files:
        df = load_file(f)
        if df is not None and "Name" in df.columns and "Phone" in df.columns:
            for _, row in df.iterrows():
                phone = str(row["Phone"])
                name = str(row["Name"])
                if phone not in global_leads:
                    global_leads[phone] = {"name": name, "called_by": None, "status": None}
            with open("global_leads.json", "w") as fjson:
                json.dump(global_leads, fjson)
        else:
            st.warning(f"No valid data in {f.name} or missing 'Name'/'Phone' columns")

# --- Load Agent Data ---
with open(f"{username}_data.json", "r") as f:
    agent_data = json.load(f)

# --- Shuffle uncalled leads ---
random.shuffle(agent_data["uncalled_leads"])

# --- Show next lead ---
if agent_data["uncalled_leads"]:
    lead = agent_data["uncalled_leads"].pop(0)
    st.subheader("Next Lead")
    st.write(f"**{lead['name']}**: {lead['phone']}")

    status = st.radio("Call Outcome", ["Picked Up", "Convo Went Well", "No Answer"])
    submit = st.button("Submit Outcome")

    if submit:
        agent_data["called_leads"][lead["phone"]] = {
            "name": lead["name"],
            "status": status,
            "points": 1 if status=="Picked Up" else 5 if status=="Convo Went Well" else 0
        }
        agent_data["points"] = sum([v["points"] for v in agent_data["called_leads"].values()])
        global_leads[lead["phone"]]["called_by"] = username
        global_leads[lead["phone"]]["status"] = status

        # Save both
        with open(f"{username}_data.json", "w") as f:
            json.dump(agent_data, f)
        with open("global_leads.json", "w") as f:
            json.dump(global_leads, f)

        st.success(f"Lead updated! Total Points: {agent_data['points']} 🎯")
else:
    st.info("No more leads left! 🏁")

# --- Quick Copy Section ---
st.subheader("📱 Quick Copy Leads")
quick_copy = "\n".join([f"{v['name']}: {k}" for k,v in agent_data["called_leads"].items()])
st.text_area("Copy these:", value=quick_copy, height=150)

# --- Leaderboard ---
st.subheader("🏆 Leaderboard")
leaderboard = []
for file in os.listdir():
    if file.endswith("_data.json"):
        with open(file, "r") as f:
            data = json.load(f)
        leaderboard.append({"agent": file.replace("_data.json",""), "points": data.get("points",0)})
leaderboard.sort(key=lambda x: x["points"], reverse=True)
st.table(leaderboard)

# --- Fun RNG Tips ---
tips = ["Keep it chill 😎", "Talk fast, sell faster 💨", "Use emojis in texts 📱", "Shuffle leads before calling 🔀"]
st.subheader("🎲 RNG Call Tips")
st.write(random.choice(tips))