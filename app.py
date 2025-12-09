# 🔥 Hood Mythic Realtor CRM v2.1 - Chaos + Reshuffle + Compact QuickCopy 😈💀🤑
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
import time

st.set_page_config(page_title="🏡 Hood Mythic Realtor CRM v2.1", layout="wide")
st.title("🔥 Hood Mythic Realtor CRM v2.1 - Mythic Chaos 😈💀🤑")
st.markdown("Upload leads and unleash chaos. Points, emojis, RNG fortune, leaderboard, perks. Hood mythic vibes only 🙆‍♂️💥")

# -----------------------
# 📂 File Uploader
# -----------------------
uploaded_files = st.file_uploader(
    "Upload CSV, TXT, XLSX, or ODS leads (any Name/Phone headers 😎🔥)", 
    type=["csv","txt","xlsx","ods"], accept_multiple_files=True
)

# -----------------------
# 📊 Load & merge multiple files (multi-format)
# -----------------------
def load_and_merge(files):
    combined_df = pd.DataFrame()
    for f in files:
        try:
            f.seek(0)
            fname = f.name.lower()
            if fname.endswith(('.csv','.txt')):
                df = pd.read_csv(f, sep=None, engine='python')
            elif fname.endswith('.xlsx'):
                df = pd.read_excel(f)
            elif fname.endswith('.ods'):
                df = pd.read_excel(f, engine='odf')
            else:
                st.warning(f"Unsupported file type: {f.name}")
                continue
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except Exception as e:
            st.warning(f"Skipping {f.name} due to read error: {e}")
    return combined_df

# -----------------------
# ✨ Enhance Leads
# -----------------------
def enhance_leads(df):
    name_cols = [c for c in df.columns if 'name' in c.lower()]
    phone_cols = [c for c in df.columns if 'phone' in c.lower()]
    
    df['Name'] = df[name_cols[0]] if name_cols else 'Unknown'
    df['Phone'] = df[phone_cols[0]] if phone_cols else 'NoPhone'

    if 'Vibe' not in df.columns:
        df['Vibe'] = np.random.choice(['🔥 Hot','🟡 Medium','💀 Cold'], size=len(df))
    if 'Points' not in df.columns:
        df['Points'] = 0
    if 'Randomizer' not in df.columns:
        df['Randomizer'] = np.random.rand(len(df))
    if 'Notes/Emoji' not in df.columns:
        df['Notes/Emoji'] = np.random.choice(['😎','💀','🤑','🤯','😂'], size=len(df))
    
    df['QuickCopy'] = df.apply(
        lambda x: f"{x['Name']} - {x['Phone']} {x.get('Notes/Emoji','')}",
        axis=1
    )
    return df

# -----------------------
# ✨ Highlight numbers
# -----------------------
def highlight_numbers(val):
    try:
        float(val)
        return 'background-color: #ffeb3b; font-weight: bold;'
    except:
        return ''

# -----------------------
# 🎲 Random call tips
# -----------------------
fortunes = [
    "💥 Call the hottest lead first! 🔥",
    "😂 Drop emoji on cold leads to lighten mood",
    "🤑 Random lead today = double points",
    "😎 Smile, they can hear it through the phone",
    "💀 Shuffle leads, chaos style"
]

# -----------------------
# 🚀 Dashboard loop
# -----------------------
def run_dashboard(df):
    # Session state for called / uncalled leads
    if 'uncalled_df' not in st.session_state:
        st.session_state.uncalled_df = df.copy()
    if 'called_df' not in st.session_state:
        st.session_state.called_df = pd.DataFrame(columns=df.columns)
    
    placeholder = st.empty()
    
    while True:
        st.subheader("🎲 Call Tip of the Moment")
        st.info(random.choice(fortunes))
        
        filtered_df = st.session_state.uncalled_df.copy()
        filtered_df = filtered_df.sample(frac=1).reset_index(drop=True)  # shuffle

        # 🗂 Columns filter (<=50 unique)
        for col in filtered_df.select_dtypes(include=['object']).columns:
            options = filtered_df[col].dropna().unique()
            if len(options) <= 50:
                selected = st.multiselect(col, options, default=list(options))
                if selected:
                    filtered_df = filtered_df[filtered_df[col].isin(selected)]

        with placeholder.container():
            st.subheader("Leads Table 😎")
            for idx, row in filtered_df.iterrows():
                col1, col2, col3 = st.columns([4,4,2])
                with col1:
                    st.markdown(f"**{row['Name']}** - {row['Phone']} {row.get('Notes/Emoji','')}")
                with col2:
                    st.markdown(f"Vibe: **{row.get('Vibe','')}**")
                with col3:
                    if st.button(f"✅ +1 Point", key=f"points_{idx}"):
                        df.at[idx,'Points'] += 1
            
            # 📝 Collapsible QuickCopy (compact mode)
            with st.expander("📱 Quick Copy Leads - Compact / Full 📝", expanded=True):
                compact_list = filtered_df['QuickCopy'].head(50).tolist()
                st.text_area(
                    'Top 50 Leads (Compact View):',
                    value='\n'.join(compact_list),
                    height=200
                )
                if len(filtered_df) > 50:
                    with st.expander(f"📜 Full Leads List ({len(filtered_df)} leads)"):
                        st.text_area(
                            'Full Leads List:',
                            value='\n'.join(filtered_df['QuickCopy'].tolist()),
                            height=400
                        )
            
            # 🎲 Random Lead Picker w/ called stash
            st.subheader("🎯 Random Lead Picker")
            if st.button("Pick Random Lead"):
                if not st.session_state.uncalled_df.empty:
                    pick_idx = st.session_state.uncalled_df.sample(1).index[0]
                    picked_lead = st.session_state.uncalled_df.loc[pick_idx]
                    st.success(f"Call this lead: **{picked_lead['Name']} - {picked_lead['Phone']} {picked_lead.get('Notes/Emoji','')}**")
                    
                    # Move to called stash
                    st.session_state.called_df = pd.concat([st.session_state.called_df, st.session_state.uncalled_df.loc[[pick_idx]]])
                    st.session_state.uncalled_df = st.session_state.uncalled_df.drop(pick_idx)
                else:
                    st.warning("All leads have been called! 😎💀")

            # 🔄 Reshuffle uncalled leads
            if st.button("🔄 Reshuffle Uncalled Leads"):
                st.session_state.uncalled_df = st.session_state.uncalled_df.sample(frac=1).reset_index(drop=True)
                st.success("Leads reshuffled! Chaos restored 😈🔥")
            
            # Numeric insights
            numeric_cols = filtered_df.select_dtypes(include=['float','int']).columns
            if len(numeric_cols) >= 2:
                x_col, y_col = numeric_cols[0], numeric_cols[1]
                st.subheader("Numeric Insights 💥")
                fig = px.scatter(filtered_df, x=x_col, y=y_col, hover_data=filtered_df.columns)
                st.plotly_chart(fig)
            
            # Top 10 leaderboard
            top_leads = df.sort_values(by='Points', ascending=False).head(10)
            st.subheader("🔥 Top 10 Leads by Points 🔥")
            st.dataframe(top_leads.style.applymap(highlight_numbers))
            
            st.balloons()
            st.success("Dashboard refreshed ⚡ Stack points, stay hood mythic!")
        
        time.sleep(5)

# -----------------------
# 🟢 Upload check + start
# -----------------------
if uploaded_files:
    df = load_and_merge(uploaded_files)
    df = enhance_leads(df)
    run_dashboard(df)
else:
    st.info("Upload your leads to activate chaos + bonus pack mode 🔥")