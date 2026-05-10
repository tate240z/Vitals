import streamlit as st
import pandas as pd
import plotly.express as px

# 1. YOUR GOOGLE SHEET CSV LINK
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTTulE0KjYP78CgSG0tBU9K21LUfrzZs2Uu9SSymBYUnXAoa2HfEsjRUsImdNpPWylDrCp5hJK-N4nD/pub?output=csv"

st.set_page_config(page_title="9509 Dashboard", layout="wide")

@st.cache_data(ttl=60) # Refreshes every minute for testing
def load_data():
    try:
        # Load the data, skipping the first 3 rows of metadata
        df = pd.read_csv(SHEET_URL, skiprows=3)
        
        # Clean up column names (removes extra spaces)
        df.columns = df.columns.str.strip()
        
        # Identify categories (ENGINE, BRAKES, etc.)
        df['Category'] = df['Item'].where(df['Runtime Limit'].isna() & df['Runtime Interval'].isna()).ffill()
        
        # Identify the hours columns (Thermal, SRO, etc.)
        # We look for columns that have numeric data in them
        hour_cols = df.columns[4:]
        
        def get_latest(row):
            # Convert the event columns to numbers, find the last one entered
            vals = pd.to_numeric(row[hour_cols], errors='coerce').dropna()
            return vals.iloc[-1] if not vals.empty else 0

        # Keep only the rows that are actual parts with a limit
        df_parts = df[df['Runtime Limit'].notnull()].copy()
        df_parts['Current_Hours'] = df_parts.apply(get_latest, axis=1)
        
        # Calculate Life Remaining
        df_parts['Remaining'] = pd.to_numeric(df_parts['Runtime Limit'], errors='coerce') - df_parts['Current_Hours']
        df_parts['Life_Pct'] = (df_parts['Remaining'] / pd.to_numeric(df_parts['Runtime Limit'], errors='coerce') * 100).clip(0, 100)
        
        return df_parts
    except Exception as e:
        st.error(f"Data Connection Error: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    st.title("🏎️ 992 GT3R (9509) | Lifeline Dashboard")
    
    # KPI TOP ROW
    col1, col2, col3 = st.columns(3)
    col1.metric("Max Chassis Time", f"{df['Current_Hours'].max():.1f} hrs")
    col2.metric("Urgent Items", len(df[df['Life_Pct'] <= 15]))
    col3.metric("Fleet Status", "Race Ready" if len(df[df['Life_Pct'] <= 15]) == 0 else "Service Required")

    # URGENT LIST
    urgent_df = df[df['Life_Pct'] <= 15].sort_values('Life_Pct')
    if not urgent_df.empty:
        st.error("### ⚠️ URGENT REPLACEMENTS NEEDED")
        st.dataframe(urgent_df[['Category', 'Item', 'Life_Pct']], use_container_width=True)

    # SEARCH & TABLE
    st.subheader("Component Inventory")
    query = st.text_input("Search for a part...")
    if query:
        df = df[df['Item'].str.contains(query, case=False)]
    
    # Styled table
    st.dataframe(
        df[['Category', 'Item', 'Runtime Limit', 'Current_Hours', 'Life_Pct']]
        .style.background_gradient(subset=['Life_Pct'], cmap='RdYlGn', vmin=0, vmax=100)
        .format({"Life_Pct": "{:.1f}%"})
    )
else:
    st.warning("Connected to sheet, but no parts with 'Runtime Limits' were found. Check your Google Sheet formatting!")
