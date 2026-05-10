import streamlit as st
import pandas as pd
import plotly.express as px

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTTulE0KjYP78CgSG0tBU9K21LUfrzZs2Uu9SSymBYUnXAoa2HfEsjRUsImdNpPWylDrCp5hJK-N4nD/pub?output=csv"

st.set_page_config(page_title="9509 Pro-Engineer", layout="wide")

@st.cache_data(ttl=60)
def load_pro_data():
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

df, event_cols = load_pro_data()

st.title("🏎️ 9509 GT3R | Professional Engineering Dashboard")

# --- PROACTIVE STRATEGY TAB ---
tab1, tab2, tab3 = st.tabs(["Current Health", "Event Evolution", "Proactive Strategy"])

with tab1:
    # Existing Health View
    st.subheader("Component Inventory")
    st.dataframe(df[['Category', 'Item', 'Runtime Limit', 'Current_Hours', 'Life_Pct']].style.background_gradient(subset=['Life_Pct'], cmap='RdYlGn'))

with tab2:
    # Evolution Chart
    st.subheader("Life Depreciation by Event")
    tracked = st.multiselect("Parts to Plot", df['Item'].unique(), default=["Engine", "Drive Shaft, Left"])
    # (Plotly logic from previous step goes here)

with tab3:
    st.subheader("🔧 Service Projection Tool")
    st.info("Predict which parts will expire based on upcoming track time.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        next_event_hours = st.number_input("Projected Hours for Next Event (e.g. VIR):", value=10.0)
        track_severity = st.slider("Track Severity Multiplier (1.0 = Standard, 1.2 = Rough/Sebring):", 1.0, 1.5, 1.0)
    
    # Calculate Projection
    effective_added = next_event_hours * track_severity
    df['Projected_Hours'] = df['Current_Hours'] + effective_added
    df['Projected_Life_Pct'] = (1 - (df['Projected_Hours'] / df['Runtime Limit'])) * 100
    
    # Show "At Risk" parts
    at_risk = df[df['Projected_Life_Pct'] <= 5].sort_values('Projected_Life_Pct')
    
    if not at_risk.empty:
        st.warning(f"### ⚠️ {len(at_risk)} Parts will expire during the next event!")
        st.table(at_risk[['Category', 'Item', 'Projected_Life_Pct']])
    else:
        st.success("All components are projected to clear the next event safely.")
