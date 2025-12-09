import streamlit as st
import json
import os

st.set_page_config(page_title="Hood Mythic CRM", page_icon="😈", layout="wide")

# ---------------------------------------------------------------------------
# 1. LOAD + SAVE SYSTEM (NO MORE DATA LOSS)
# ---------------------------------------------------------------------------

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

leads = load_data()

# ---------------------------------------------------------------------------
# 2. DISPOSITION SYSTEM (CALL LABELS)
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

# ---------------------------------------------------------------------------
# 3. LOGIN SYSTEM (AGENT NAMES)
# ---------------------------------------------------------------------------

if "agent" not in st.session_state:
    st.session_state.agent = None

if st.session_state.agent is None:
    st.title("😈 Hood Mythic CRM Login")
    agent_name = st.text_input("Enter your agent name:")
    if st.button("Login"):
        if agent_name.strip() != "":
            st.session_state.agent = agent_name.strip()
    st.stop()

agent = st.session_state.agent

# ---------------------------------------------------------------------------
# 4. ADD NEW LEADS (BUILT-IN + OPTIONAL UPLOAD)
# ---------------------------------------------------------------------------

st.sidebar.header(f"😎 Agent: {agent}")

st.sidebar.subheader("Add New Lead")

name = st.sidebar.text_input("Lead Name")
phone = st.sidebar.text_input("Phone Number")

if st.sidebar.button("Add Lead"):
    if phone.strip() != "":
        leads[phone] = {
            "name": name,
            "called_by": None,
            "status": None,
            "notes": ""
        }
        save_data(leads)
        st.sidebar.success("Lead added!")

# ---------------------------------------------------------------------------
# 5. FILTER SYSTEM
# ---------------------------------------------------------------------------

st.title("🏡 Hood Mythic CRM Dashboard")

filter_dispo = st.selectbox("Filter by status:", ["All"] + list(DISPOSITIONS.keys()))
filter_uncalled = st.checkbox("Show only uncalled leads")
filter_my_leads = st.checkbox("Show only leads assigned to me")

filtered = {}

for phone, info in leads.items():
    if filter_dispo != "All" and info.get("status") != filter_dispo:
        continue
    if filter_uncalled and info.get("status") is not None:
        continue
    if filter_my_leads and info.get("called_by") != agent:
        continue
    filtered[phone] = info

# ---------------------------------------------------------------------------
# 6. LEAD LIST DISPLAY (CLICK TO VIEW)
# ---------------------------------------------------------------------------

st.subheader("Lead List")

for phone, info in filtered.items():
    with st.expander(f"{info['name']} | 📞 {phone} | {info.get('status', 'No Status')}"):
        
        st.write(f"**Name:** {info['name']}")
        st.write(f"**Phone:** {phone}")
        st.write(f"**Last Status:** {info.get('status', 'None')}")
        st.write(f"**Agent Assigned:** {info.get('called_by', 'None')}")
        
        notes = st.text_area(f"Notes for {phone}", value=info.get("notes", ""))
        
        dispo = st.selectbox(
            f"Update status for {phone}",
            ["No Answer", "Not Interested", "Cold Lead", "Interested", "Hot Lead", 
             "Wrong Number", "Left Voicemail", "Call Back Later", "Closed Deal"],
            index=0
        )

        if st.button(f"Save {phone}"):
            leads[phone]["status"] = dispo
            leads[phone]["called_by"] = agent
            leads[phone]["notes"] = notes
            save_data(leads)
            st.success("Saved!")
            st.experimental_rerun()

# ---------------------------------------------------------------------------
# 7. LEADERBOARD
# ---------------------------------------------------------------------------

st.subheader("🏆 Agent Leaderboard")

scores = {}

for phone, info in leads.items():
    ag = info.get("called_by")
    status = info.get("status")
    
    if ag and status in DISPOSITIONS:
        scores[ag] = scores.get(ag, 0) + DISPOSITIONS[status]

sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

for agent_name, pts in sorted_scores:
    st.write(f"**{agent_name}:** {pts} pts")

# ---------------------------------------------------------------------------
# END
# ---------------------------------------------------------------------------