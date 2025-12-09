import streamlit as st
import pandas as pd
import json
import random
import os

# -------------------
# CONFIG
# -------------------
st.set_page_config(page_title="🏡 Hood Mythic Realtor CRM", layout="wide")
LEADS_FILE = "global_leads.json"
USERS_FILE = "users.json"

# -------------------
# UTILS
# -------------------
def load_json(file_path, default={}):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

tips = [
    "Start the call with a joke 😎",
    "Listen more than you talk 👂",
    "Use their name 3 times 🧠",
    "Smile while you talk 😁",
    "Random fortune: Big deal today! 🍀"
]

# -------------------
# LOGIN SYSTEM
# -------------------
users = load_json(USERS_FILE)
st.sidebar.title("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_btn = st.sidebar.button("Login")

if login_btn:
    if username in users and users[username]["password"] == password:
        st.session_state["user"] = username
        st.success(f"Welcome, {username} 😈🔥")
    else:
        st.error("Wrong login, try again!")

if "user" in st.session_state:
    agent = st.session_state["user"]

    # Load leads and agent data
    global_leads = load_json(LEADS_FILE, default={})
    agent_file = f"{agent}_data.json"
    agent_data = load_json(agent_file, default={"called_leads": {}, "points":0, "uncalled_leads":[]})

    # -------------------
    # UPLOAD NEW LEADS
    # -------------------
    uploaded_files = st.file_uploader(
        "Upload Leads CSV/TXT/XLSX/ODS", type=["csv","txt","xlsx","ods"], accept_multiple_files=True
    )
    for f in uploaded_files:
        try:
            if f.name.endswith(".csv") or f.name.endswith(".txt"):
                df = pd.read_csv(f)
            else:
                df = pd.read_excel(f, engine="openpyxl")

            # Normalize columns
            df.columns = [c.strip().lower() for c in df.columns]

            # Check for phone
            if 'phone' not in df.columns:
                st.warning(f"{f.name} missing 'Phone' column! Skipping...")
                continue
            if 'name' not in df.columns:
                st.warning(f"{f.name} missing 'Name' column! Filling with 'Unknown'")
                df['name'] = 'Unknown'

            # Add to leads
            for idx, row in df.iterrows():
                phone = str(row["phone"])
                name = row.get("name", "Unknown")
                if phone not in global_leads:
                    global_leads[phone] = {"name": name, "called_by": None, "status": None}
                    agent_data["uncalled_leads"].append({"phone": phone, "name": name})

        except Exception as e:
            st.warning(f"Skipping {f.name} due to read error: {e}")
            continue

    # Save updates
    save_json(LEADS_FILE, global_leads)
    save_json(agent_file, agent_data)

    # -------------------
    # DASHBOARD
    # -------------------
    st.title("🔥 Hood Mythic Realtor CRM")

    # Shuffle uncalled leads
    random.shuffle(agent_data["uncalled_leads"])
    for lead in agent_data["uncalled_leads"]:
        phone = lead["phone"]
        name = lead["name"]
        st.write(f"📞 {name} - {phone}")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Pick Up ✅ ({phone})"):
                agent_data["called_leads"][phone] = {"name": name, "status":"Picked Up", "points":1}
                agent_data["points"] += 1
                global_leads[phone]["called_by"] = agent
                global_leads[phone]["status"] = "Picked Up"
                agent_data["uncalled_leads"] = [l for l in agent_data["uncalled_leads"] if l["phone"] != phone]
        with col2:
            if st.button(f"Convo Went Well 💥 ({phone})"):
                agent_data["called_leads"][phone] = {"name": name, "status":"Convo Went Well", "points":5}
                agent_data["points"] += 5
                global_leads[phone]["called_by"] = agent
                global_leads[phone]["status"] = "Convo Went Well"
                agent_data["uncalled_leads"] = [l for l in agent_data["uncalled_leads"] if l["phone"] != phone]
        with col3:
            if st.button(f"No Answer ❌ ({phone})"):
                agent_data["called_leads"][phone] = {"name": name, "status":"No Answer", "points":0}
                global_leads[phone]["called_by"] = agent
                global_leads[phone]["status"] = "No Answer"
                agent_data["uncalled_leads"] = [l for l in agent_data["uncalled_leads"] if l["phone"] != phone]

    # Quick copy with names
    st.subheader("📋 Quick Copy Leads")
    copy_list = [f"{v['name']} - {k}" for k,v in global_leads.items() if v["called_by"] is None]
    st.text_area("Click to Copy:", value="\n".join(copy_list), height=200)

    # RNG Tip
    st.subheader("💡 Call Tip")
    st.write(random.choice(tips))

    # Leaderboard
    st.subheader("🏆 Multi-Agent Leaderboard")
    leaderboard = []
    for u in users.keys():
        user_data = load_json(f"{u}_data.json", default={"points":0})
        leaderboard.append((u, user_data.get("points",0)))
    leaderboard.sort(key=lambda x:x[1], reverse=True)
    for i, (u,p) in enumerate(leaderboard,1):
        st.write(f"{i}. {u} - {p} pts")

    # Save all changes at the end
    save_json(LEADS_FILE, global_leads)
    save_json(agent_file, agent_data)