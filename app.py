# 🔥 Hood Mythic Realtor CRM - Mythic Chaos + Bonus Pack 😎💀🤑
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
import time

# 🏷 App title + browser tab title
st.set_page_config(page_title="🏡 Hood Mythic Realtor CRM", layout="wide")
st.title("🔥 Hood Mythic Realtor CRM - Mythic Mode 😈💀🤑")
st.markdown("Upload your leads and unleash chaos. Points, emojis, RNG fortune, leaderboard, perks. Hood mythic vibes only 🙆‍♂️💥")

# 📂 File uploader
uploaded_files = st.file_uploader(
    "Upload CSV/TXT leads (Name + Phone + Extras 😎🔥)", type=["csv","txt"], accept_multiple_files=True
)

# 📊 Load and merge multiple files
def load_and_merge(files):
    combined_df = pd.DataFrame()
    for f in files:
        try:
            f.seek(0)
            df = pd.read_csv(f, sep=None, engine='python')
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except Exception as e:
            st.warning(f"Skipping {f.name} due to read error: {e}")
    return combined_df

# ✨ Add perks & chaos columns
def enhance_leads(df):
    if 'Vibe' not in df.columns:
        df['Vibe'] = np.random.choice(['🔥 Hot','🟡 Medium','💀 Cold'], size=len(df))
    if 'Points' not in df.columns:
        df['Points'] = 0
    if 'Randomizer' not in df.columns:
        df['Randomizer'] = np.random.rand(len(df))
    if 'Notes/Emoji' not in df.columns:
        df['Notes/Emoji'] = np.random.choice(['😎','💀','🤑','🤯','😂'], size=len(df))
    if 'QuickCopy' not in df.columns:
        df['QuickCopy'] = df.apply(lambda x: f"{x.get('Name','Unknown')} - {x.get('Phone','NoPhone')} {x.get('Notes/Emoji','')}", axis=1)
    return df

# ✨ Highlight numeric cells
def highlight_numbers(val):
    try:
        float(val)
        return 'background-color: #ffeb3b; font-weight: bold;'
    except:
        return ''

# 🎲 Random tips/fortunes for calls
fortunes = [
    "💥 Call the hottest lead first! 🔥",
    "😂 Drop emoji on cold leads to lighten mood",
    "🤑 Random lead today = double points",
    "😎 Smile, they can hear it through the phone",
    "💀 Shuffle leads, chaos style"
]

# 🚀 Main dashboard loop
def run_dashboard(df):
    placeholder = st.empty()
    while True:
        st.subheader("🎲 Hood Mythic Fortune")
        st.info(random.choice(fortunes))
        
        filtered_df = df.copy()
        for col in filtered_df.select_dtypes(include=['object']).columns:
            options = filtered_df[col].dropna().unique()
            if len(options) <= 50:
                selected = st.multiselect(col, options, default=list(options))
                if selected:
                    filtered_df = filtered_df[filtered_df[col].isin(selected)]

        filtered_df = filtered_df.sample(frac=1).reset_index(drop=True)  # shuffle

        with placeholder.container():
            st.subheader("Leads Table 😎")
            
            for idx, row in filtered_df.iterrows():
                col1, col2, col3 = st.columns([4,4,2])
                with col1:
                    st.markdown(f"**{row.get('Name','Unknown')}** - {row.get('Phone','NoPhone')} {row.get('Notes/Emoji','')}")
                with col2:
                    st.markdown(f"Vibe: **{row.get('Vibe','')}**")
                with col3:
                    if st.button(f"✅ +1 Point", key=f"points_{idx}"):
                        df.at[idx,'Points'] += 1
            
            st.text_area(
                '📱 Quick Copy Leads (Name - Phone - Emoji 📝):',
                value='\n'.join(filtered_df['QuickCopy'].tolist()),
                height=200
            )
            
            numeric_cols = filtered_df.select_dtypes(include=['float','int']).columns
            if len(numeric_cols) >= 2:
                x_col, y_col = numeric_cols[0], numeric_cols[1]
                st.subheader("Numeric Insights 💥")
                fig = px.scatter(filtered_df, x=x_col, y=y_col, hover_data=filtered_df.columns)
                st.plotly_chart(fig)
            
            top_leads = filtered_df.sort_values(by='Points', ascending=False).head(10)
            st.subheader("🔥 Top 10 Leads by Points 🔥")
            st.dataframe(top_leads.style.applymap(highlight_numbers))
            
            st.balloons()
            st.success("Dashboard refreshed ⚡ Stack points, stay hood mythic!")
        
        time.sleep(5)

# 🟢 Upload check + start dashboard
if uploaded_files:
    df = load_and_merge(uploaded_files)
    df = enhance_leads(df)
    run_dashboard(df)
else:
    st.info("Upload your leads to activate chaos + bonus pack mode 🔥")
