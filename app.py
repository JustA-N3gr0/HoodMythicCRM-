# hood_mythic_crm_v3.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

st.set_page_config(page_title="🏡 Hood Mythic CRM - Chaos Mythic Mode", layout="wide")
st.title("🏡 Hood Mythic Realtor CRM - Full Chaos Mode 🔥😈")

# -------------------------------
# File uploader
# -------------------------------
uploaded_files = st.file_uploader(
    "Upload Leads (CSV, TXT, XLSX, ODS)",
    type=["csv", "txt", "xlsx", "ods"],
    accept_multiple_files=True
)

def load_file(f):
    fname = f.name.lower()
    try:
        if fname.endswith(".csv") or fname.endswith(".txt"):
            return pd.read_csv(f, sep=None, engine='python')
        elif fname.endswith(".xlsx"):
            return pd.read_excel(f, engine='openpyxl')
        elif fname.endswith(".ods"):
            return pd.read_excel(f, engine='odf')
    except Exception as e:
        st.warning(f"Skipping {f.name} due to read error: {e}")
        return pd.DataFrame()

def load_and_merge(files):
    combined_df = pd.DataFrame()
    for f in files:
        df = load_file(f)
        if not df.empty:
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

# -------------------------------
# Load data
# -------------------------------
if uploaded_files:
    df = load_and_merge(uploaded_files)
    if df.empty:
        st.warning("No valid data loaded! Upload again.")
    else:
        # -------------------------------
        # Normalize column names
        # -------------------------------
        df.rename(columns={c: c.lower() for c in df.columns}, inplace=True)
        name_col = next((c for c in df.columns if "name" in c), None)
        phone_col = next((c for c in df.columns if "phone" in c or "cell" in c), None)
        if not name_col:
            df["name"] = "Unknown"
            name_col = "name"
        if not phone_col:
            df["phone"] = "NoPhone"
            phone_col = "phone"

        # -------------------------------
        # Session state
        # -------------------------------
        if "uncalled_df" not in st.session_state:
            st.session_state.uncalled_df = df.copy().reset_index(drop=True)
            st.session_state.called_df = pd.DataFrame(columns=df.columns)

        # -------------------------------
        # Random Lead Picker with Auto-Shuffle
        # -------------------------------
        st.subheader("🎲 Random Lead Picker (Mythic Chaos Mode)")
        if st.button("Pick a Random Lead"):
            if st.session_state.uncalled_df.empty:
                st.success("✅ All leads have been called!")
            else:
                # Shuffle uncalled leads first
                st.session_state.uncalled_df = st.session_state.uncalled_df.sample(frac=1).reset_index(drop=True)
                # Pick top lead after shuffle
                lead = st.session_state.uncalled_df.iloc[0]
                st.session_state.called_df = pd.concat(
                    [st.session_state.called_df, lead.to_frame().T], ignore_index=True
                )
                st.session_state.uncalled_df = st.session_state.uncalled_df.drop(0).reset_index(drop=True)
                st.info(f"Call this lead: {lead[name_col]} 📞 {lead[phone_col]}")

        # -------------------------------
        # Leads Table
        # -------------------------------
        st.subheader("📋 Leads Table")
        st.dataframe(st.session_state.uncalled_df.style.applymap(
            lambda x: 'background-color: #ffeb3b; font-weight: bold;' if isinstance(x, (int,float)) else ''
        ))

        # -------------------------------
        # Quick Copy Section
        # -------------------------------
        st.subheader("📱 Quick Copy Leads")
        with st.expander("Top 50 Leads (Name: Phone)"):
            quick_list = "\n".join(
                [f"{row[name_col]}: {row[phone_col]}" for _, row in st.session_state.uncalled_df.head(50).iterrows()]
            )
            st.text_area("📋 Copy & Paste:", value=quick_list, height=200, key="quickcopy_area")

        # -------------------------------
        # Numeric Insights
        # -------------------------------
        numeric_cols = st.session_state.uncalled_df.select_dtypes(include=['float','int']).columns
        if len(numeric_cols) >= 2:
            x_col, y_col = numeric_cols[:2]
            st.subheader("📊 Numeric Insights")
            fig = px.scatter(st.session_state.uncalled_df, x=x_col, y=y_col,
                             hover_data=[name_col, phone_col])
            st.plotly_chart(fig)

        # -------------------------------
        # Top Leads
        # -------------------------------
        price_cols = [c for c in st.session_state.uncalled_df.columns if "price" in c]
        if price_cols:
            top_col = price_cols[0]
            top_leads = st.session_state.uncalled_df.sort_values(by=top_col, ascending=False).head(10)
            st.subheader("🔥 Top 10 Hot Leads 🔥")
            st.dataframe(top_leads.style.applymap(
                lambda x: 'background-color: #ffeb3b; font-weight: bold;' if isinstance(x, (int,float)) else ''
            ))

        # -------------------------------
        # Fun Tips / RNG Fortune
        # -------------------------------
        st.subheader("🎉 Mythic Call Tips & RNG Fortune")
        tips = [
            "Smash that intro like a boss 😎",
            "Use their name at least 2x per call 💥",
            "Random reward: +5 points if you make them laugh 😂",
            "Shuffle your leads before calling for chaos 🌀",
            "Emoji power = +1 charisma 😈🔥"
        ]
        st.info(random.choice(tips))

        # -------------------------------
        # Leaderboard
        # -------------------------------
        st.subheader("🏆 Called Leads Leaderboard")
        leaderboard = st.session_state.called_df[[name_col, phone_col]].copy()
        leaderboard["Points"] = 1
        leaderboard = leaderboard.groupby([name_col]).sum().sort_values("Points", ascending=False)
        st.dataframe(leaderboard)

        st.success("Hood Mythic CRM Loaded! Call like a legend 😎💥")