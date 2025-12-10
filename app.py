import streamlit as st
from leads import load_leads, save_leads, DISPOSITIONS
from user import load_user, save_user

st.set_page_config(page_title="Chaotic Leads CRM", page_icon="😈", layout="wide")

# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------
user_data = load_user()

if "agent" not in st.session_state:
    st.session_state.agent = None

if st.session_state.agent is None:
    st.title("😈 CRM Login")
    agent_name = st.text_input("Enter your agent name:")
    if st.button("Login"):
        if agent_name.strip() != "":
            st.session_state.agent = agent_name.strip()
    st.stop()

agent = st.session_state.agent
st.sidebar.header(f"😎 Agent: {agent}")

# ---------------------------------------------------------------------------
# LOAD LEADS
# ---------------------------------------------------------------------------
leads = load_leads()

# ---------------------------------------------------------------------------
# ADD NEW LEAD
# ---------------------------------------------------------------------------
st.sidebar.subheader("Add New Lead")
name = st.sidebar.text_input("Lead Name")
phone = st.sidebar.text_input("Phone Number")
if st.sidebar.button("Add Lead"):
    if phone.strip() != "":
        leads[phone] = {"name": name, "called_by": None, "status": None, "notes": ""}
        save_leads(leads)
        st.sidebar.success("Lead added!")

# ---------------------------------------------------------------------------
# FILTER LEADS
# ---------------------------------------------------------------------------
st.title("🏡 CRM Dashboard")
filter_dispo = st.selectbox("Filter by status:", ["All"] + list(DISPOSITIONS.keys()))
filter_uncalled = st.checkbox("Show only uncalled leads")
filter_my_leads = st.checkbox("Show only my leads")

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
# DISPLAY LEADS
# ---------------------------------------------------------------------------
st.subheader("Lead List")
for phone, info in filtered.items():
    with st.expander(f"{info['name']} | 📞 {phone} | {info.get('status', 'No Status')}"):
        st.write(f"**Name:** {info['name']}")
        st.write(f"**Phone:** {phone}")
        st.write(f"**Status:** {info.get('status', 'None')}")
        st.write(f"**Called By:** {info.get('called_by', 'None')}")
        notes = st.text_area(f"Notes for {phone}", value=info.get("notes", ""))
        dispo = st.selectbox(
            f"Update status for {phone}",
            list(DISPOSITIONS.keys()),
            index=0
        )
        if st.button(f"Save {phone}"):
            leads[phone]["status"] = dispo
            leads[phone]["called_by"] = agent
            leads[phone]["notes"] = notes
            save_leads(leads)
            st.success("Saved!")
            st.experimental_rerun()

# ---------------------------------------------------------------------------
# LEADERBOARD
# ---------------------------------------------------------------------------
st.subheader("🏆 Agent Leaderboard")
scores = {}
for phone, info in leads.items():
    ag = info.get("called_by")
    status = info.get("status")
    if ag and status in DISPOSITIONS:
        scores[ag] = scores.get(ag, 0) + DISPOSITIONS[status]

sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
for ag_name, pts in sorted_scores:
    st.write(f"**{ag_name}:** {pts} pts")