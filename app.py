import streamlit as st
import pandas as pd
import plotly.express as px

# 1. REPLACE THIS WITH YOUR PUBLISHED CSV LINK
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTTulE0KjYP78CgSG0tBU9K21LUfrzZs2Uu9SSymBYUnXAoa2HfEsjRUsImdNpPWylDrCp5hJK-N4nD/pub?output=csv"

st.set_page_config(page_title="9509 Dashboard", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    try:
        # Load data, skipping the first 3 rows of metadata
        df = pd.read_csv(SHEET_URL, skiprows=3)
        
        # Identify categories (ENGINE, EXHAUST, etc.)
        df['Category'] = df['Item'].where(df.iloc[:, 1:14].isna().all(axis=1)).ffill()
        
        # Select the event columns (ending hours)
        event_cols = [c for c in df.columns if any(x in c for x in ['SRO', 'JAN', 'FEB', 'TEST'])]
        
        def get_latest(row):
            vals = pd.to_numeric(row[event_cols], errors='coerce').dropna()
            return vals.iloc[-1] if not vals.empty else 0

        # Filter for parts with limits
        df_parts = df[df['Runtime Limit'].notnull()].copy()
        df_parts['Current_Hours'] = df_parts.apply(get_latest, axis=1)
        df_parts['Remaining_Hours'] = df_parts['Runtime Limit'] - df_parts['Current_Hours']
        
        # Create the Life_Pct column manually to avoid the KeyError
        df_parts['Life_Pct'] = (df_parts['Remaining_Hours'] / df_parts['Runtime Limit'] * 100).clip(0, 100)
        
        return df_parts
    except Exception as e:
        st.error(f"Data Connection Error: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    st.title("🏎️ 992 GT3R (9509) | Lifeline Dashboard")
    
    # KPI CARDS
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Chassis Time", f"{df['Current_Hours'].max():.1f} hrs")
    col2.metric("Urgent Parts", len(df[df['Life_Pct'] <= 15]))
    col3.metric("Status", "Track Ready" if len(df[df['Life_Pct'] <= 15]) == 0 else "Service Needed")

    # URGENT LIST
    urgent_df = df[df['Life_Pct'] <= 15].sort_values('Life_Pct')
    if not urgent_df.empty:
        st.error("### ⚠️ CRITICAL SERVICE REQUIRED")
        st.dataframe(urgent_df[['Category', 'Item', 'Remaining_Hours', 'Life_Pct']], use_container_width=True)

    # VISUAL CHART
    st.subheader("System Health Overview")
    cat_health = df.groupby('Category')['Life_Pct'].mean().reset_index()
    fig = px.bar(cat_health, x='Category', y='Life_Pct', color='Life_Pct',
                 color_continuous_scale='RdYlGn', range_color=[0,100])
    st.plotly_chart(fig, use_container_width=True)

    # SEARCHABLE INVENTORY
    st.subheader("Full Component Tracking")
    query = st.text_input("Search for a part (e.g. 'Axle')")
    display_df = df[df['Item'].str.contains(query, case=False)] if query else df
    
    st.dataframe(
        display_df[['Category', 'Item', 'Runtime Limit', 'Current_Hours', 'Life_Pct']]
        .style.background_gradient(subset=['Life_Pct'], cmap='RdYlGn', vmin=0, vmax=100)
        .format({"Life_Pct": "{:.1f}%"})
    )
else:
    st.info("Searching for data... please ensure the Google Sheet is 'Published to Web' as a CSV.")
