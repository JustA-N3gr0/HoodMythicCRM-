import streamlit as st
import json
import os
from leads import load_leads, save_leads
from agents import load_agents
from user import load_user, save_user

st.set_page_config(page_title="Chaotic Leads CRM", page_icon="🔥", layout="wide")

# ------------------------------------------------
# LOAD SYSTEM
# ------------------------------------------------
leads = load_leads()
agents = load_agents()
user_data = load_user()

DISPO_POINTS = {
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

# ------------------------------------------------
# LOGIN SYSTEM
# ------------------------------------------------
if "agent" not in st.session_state:
    st.session_state.agent = None

if st.session_state.agent is None:
    st.title("🔐 CRM Login")

    phone = st.text_input("Enter your agent phone number")

    if st.button("Login"):
        if phone in agents:
            st.session_state.agent = agents[phone]["name"]
            user_data["active_agent"] = phone
            save_user(user_data)
        else:
            st.error("Agent not found")

    st.stop()

agent_phone = user_data["active_agent"]
agent_name = agents[agent_phone]["name"]

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------
st.sidebar.header(f"Agent: {agent_name}")
st.sidebar.write(f"Phone: {agent_phone}")

st.sidebar.subheader("Add New Lead")

new_name = st.sidebar.text_input("Lead Name")
new_phone = st.sidebar.text_input("Lead Phone")

if st.sidebar.button("Add Lead"):
    if new_phone.strip() != "":
        leads[new_phone] = {
            "name": new_name,
            "called_by": None,
            "status": None,
            "notes": ""
        }
        save_leads(leads)
        st.sidebar.success("Lead added!")

# ------------------------------------------------
# FILTERS
# ------------------------------------------------
st.title("🔥 Chaotic Lead Dashboard")

filter_status = st.selectbox("Filter by Status", ["All"] + list(DISPO_POINTS.keys()))
filter_uncalled = st.checkbox("Show only uncalled leads")
filter_my = st.checkbox("Show only leads I called")

filtered = {}

for phone, info in leads.items():
    if filter_status != "All" and info.get("status") != filter_status:
        continue
    if filter_uncalled and info.get("status") is not None:
        continue
    if filter_my and info.get("called_by") != agent_name:
        continue
    filtered[phone] = info

# ------------------------------------------------
# LEAD DISPLAY
# ------------------------------------------------
st.subheader("Lead List")

for phone, info in filtered.items():
    with st.expander(f"{info['name']} | {phone} | {info.get('status', 'No Status')}"):

        st.write(f"Name: {info['name']}")
        st.write(f"Phone: {phone}")
        st.write(f"Last Status: {info.get('status', 'None')}")
        st.write(f"Called By: {info.get('called_by', 'None')}")

        notes = st.text_area(f"Notes for {phone}", value=info.get("notes", ""))

        dispo = st.selectbox(
            f"Update Status for {phone}",
            list(DISPO_POINTS.keys()),
            index=0
        )

        if st.button(f"Save {phone}"):
            leads[phone]["status"] = dispo
            leads[phone]["called_by"] = agent_name
            leads[phone]["notes"] = notes
            save_leads(leads)

            user_data["called_leads"][phone] = {
                "name": info["name"],
                "status": dispo,
                "points": DISPO_POINTS[dispo]
            }
            user_data["points"] += DISPO_POINTS[dispo]
            save_user(user_data)

            st.success("Saved!")
            st.experimental_rerun()

# ------------------------------------------------
# LEADERBOARD
# ------------------------------------------------
st.subheader("🏆 Agent Leaderboard")

scores = {}

for phone, info in leads.items():
    ag = info.get("called_by")
    status = info.get("status")

    if ag and status in DISPO_POINTS:
        scores[ag] = scores.get(ag, 0) + DISPO_POINTS[status]

sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

for ag, pts in sorted_scores:
    st.write(f"{ag}: {pts} pts")