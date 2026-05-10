import streamlit as st
import pandas as pd
import plotly.express as px

# 1. REPLACE THE LINK BELOW WITH YOUR GOOGLE SHEET CSV LINK
SHEET_URL = https://docs.google.com/spreadsheets/d/e/2PACX-1vTTulE0KjYP78CgSG0tBU9K21LUfrzZs2Uu9SSymBYUnXAoa2HfEsjRUsImdNpPWylDrCp5hJK-N4nD/pubhtml

st.set_page_config(page_title="9509 Dashboard", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    try:
        # Load data, skipping the first 3 rows of metadata
        df = pd.read_csv(SHEET_URL, skiprows=3)
        
        # Identify categories (ENGINE, EXHAUST, etc.)
        df['Category'] = df['Item'].where(df.iloc[:, 1:14].isna().all(axis=1)).ffill()
        
        # Select the event columns (ending hours)
        event_cols = [c for c in df.columns if 'SRO' in c or 'JAN' in c or 'FEB' in c]
        
        def get_latest(row):
            vals = pd.to_numeric(row[event_cols], errors='coerce').dropna()
            return vals.iloc[-1] if not vals.empty else 0

        # Filter for parts with limits and calculate life
        df_parts = df[df['Runtime Limit'].notnull()].copy()
        df_parts['Current_Hours'] = df_parts.apply(get_latest, axis=1)
        df_parts['Remaining_Hours'] = df_parts['Runtime Limit'] - df_parts['Current_Hours']
        df_parts['Life_Pct'] = (df_parts['Remaining_Hours'] / df_parts['Runtime Limit'] * 100).clip(0, 100)
        
        return df_parts
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is not None:
    st.title("🏎️ 992 GT3R (9509) | Component Lifelines")
    
    # --- TOP ROW: KPI CARDS ---
    urgent_df = df[df['Life_Pct'] <= 15]
    attention_df = df[(df['Life_Pct'] > 15) & (df['Life_Pct'] <= 30)]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Chassis Time", f"{df['Current_Hours'].max():.1f} hrs")
    col2.metric("Urgent Replacements", len(urgent_df))
    col3.metric("Upcoming Service", len(attention_df))

    # --- URGENT ALERTS ---
    if not urgent_df.empty:
        st.error("### ⚠️ CRITICAL SERVICE REQUIRED")
        st.table(urgent_df[['Item', 'Remaining_Hours', 'Life_Pct']].sort_values('Life_Pct'))

    # --- VISUALIZATION ---
    st.subheader("System Health Overview")
    cat_health = df.groupby('Category')['Life_Pct'].mean().reset_index()
    fig = px.bar(cat_health, x='Category', y='Life_Pct', color='Life_Pct',
                 color_continuous_scale='RdYlGn', range_color=[0,100])
    st.plotly_chart(fig, use_container_width=True)

    # --- SEARCHABLE LIST ---
    st.subheader("Full Component Tracking")
    query = st.text_input("Search for a part...")
    if query:
        df = df[df['Item'].str.contains(query, case=False)]
    
    st.dataframe(
        df[['Category', 'Item', 'Runtime Limit', 'Current_Hours', 'Life_Pct']]
        .style.background_gradient(subset=['Life_Pct'], cmap='RdYlGn', vmin=0, vmax=100)
        .format({"Life_Pct": "{:.1f}%"})
    )
else:
    st.warning("Waiting for data connection... check the SHEET_URL in the code.")
