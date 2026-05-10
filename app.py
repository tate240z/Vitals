import streamlit as st
import pandas as pd
import plotly.express as px

# 1. LINK TO YOUR MASTER GOOGLE SHEET
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTTulE0KjYP78CgSG0tBU9K21LUfrzZs2Uu9SSymBYUnXAoa2HfEsjRUsImdNpPWylDrCp5hJK-N4nD/pub?output=csv"

st.set_page_config(page_title="GMG Racing Command", layout="wide")

@st.cache_data(ttl=60)
def load_master_data():
    df = pd.read_csv(SHEET_URL, skiprows=3)
    df.columns = df.columns.str.strip()
    df['Category'] = df['Item'].where(df['Runtime Limit'].isna()).ffill()
    event_cols = [c for c in df.columns if any(x in c for x in ['JAN', 'FEB', 'SRO', 'TEST'])]
    
    df_parts = df[df['Runtime Limit'].notnull()].copy()
    df_parts['Runtime Limit'] = pd.to_numeric(df_parts['Runtime Limit'], errors='coerce')
    
    def get_latest(row):
        vals = pd.to_numeric(row[event_cols], errors='coerce').dropna()
        return vals.iloc[-1] if not vals.empty else 0
    
    df_parts['Current_Hours'] = df_parts.apply(get_latest, axis=1)
    df_parts['Life_Pct'] = (1 - (df_parts['Current_Hours'] / df_parts['Runtime Limit'])) * 100
    return df_parts, event_cols

df, event_cols = load_master_data()

# --- SIDEBAR: GLOBAL FLEET STATUS ---
st.sidebar.title("🏁 GMG Fleet Status")
st.sidebar.success("992 GT3R (9509): Race Ready")
st.sidebar.warning("992 Cup: Prep Required")
st.sidebar.error("LMP3: Gearbox Timeout")

st.title("🛡️ 9509 GT3R | Technical Director's Command")

# --- NAVIGATION TABS ---
tabs = st.tabs(["📊 Fleet Health", "📈 Duty Cycle", "📋 Tech Audit", "📦 Logistics"])

with tabs[0]:
    st.subheader("Critical Component Status")
    st.dataframe(df[['Category', 'Item', 'Current_Hours', 'Life_Pct']].style.background_gradient(subset=['Life_Pct'], cmap='RdYlGn'))

with tabs[1]:
    st.subheader("System Duty Cycle Analysis")
    # Radar chart showing system-level stress
    cat_health = df.groupby('Category')['Life_Pct'].mean().reset_index()
    fig = px.line_polar(cat_health, r='Life_Pct', theta='Category', line_close=True,
                        title="System Reliability Confidence", range_r=[0,100])
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.subheader("Pre-Event Technical Reconciliation")
    if st.button("Generate LaTeX Prep Report"):
        st.write("Compiling parts data into LaTeX template...")
        # This would link to a script to generate your formal PDFs
        st.download_button("Download PDF Audit", "Sample Report Data", "Prep_Report.pdf")

with tabs[3]:
    st.subheader("Inventory & Staging")
    pick_list = df[df['Life_Pct'] <= 20]
    if not pick_list.empty:
        st.write("The following items should be pulled from shop inventory for the next prep:")
        st.table(pick_list[['Item', 'Life_Pct']])
