import streamlit as st
import pandas as pd
import plotly.express as px

# Setup page config for mobile/web responsiveness
st.set_page_config(page_title="9509 Lifeline Dashboard", layout="wide")

# Load the data we processed from your CSV
@st.cache_data
def load_data():
    df = pd.read_csv('app_backend_data.csv')
    return df

df = load_data()

st.title("🏎️ Porsche 992 GT3R (9509) | Component Lifelines")
st.markdown("---")

# --- SIDEBAR: LOG NEW HOURS ---
st.sidebar.header("Log New Session")
last_event = "COTA SRO" # Example based on your sheet
added_hours = st.sidebar.number_input("Add Hours from Last Session", min_value=0.0, step=0.1)

if st.sidebar.button("Update Fleet Hours"):
    st.sidebar.success(f"Added {added_hours} hrs to all components.")
    # In a live app, this would write back to a Google Sheet or Database

# --- TOP ROW: KPI CARDS ---
urgent_count = len(df[df['Life_Pct'] <= 15])
attention_count = len(df[(df['Life_Pct'] > 15) & (df['Life_Pct'] <= 30)])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Chassis Hours", "41.7 hrs", "+5.6")
col2.metric("Urgent Replacements", urgent_count, delta="-2", delta_color="inverse")
col3.metric("Upcoming Service", attention_count)
col4.metric("Status", "Race Ready", delta_color="normal")

# --- MIDDLE ROW: CRITICAL ALERTS ---
if urgent_count > 0:
    st.error("### ⚠️ CRITICAL: PARTS EXCEEDING SAFETY LIMITS")
    urgent_df = df[df['Life_Pct'] <= 15].sort_values('Life_Pct')
    st.dataframe(urgent_df[['Category', 'Item', 'Remaining_Hours', 'Life_Pct']], use_container_width=True)

# --- VISUALIZATION: SYSTEM HEALTH ---
st.subheader("System Health Overview")
# Group by category for a high-level view
cat_health = df.groupby('Category')['Life_Pct'].mean().reset_index()
fig = px.bar(cat_health, x='Category', y='Life_Pct', 
             title="Avg Life Remaining by System",
             color='Life_Pct', color_continuous_scale='RdYlGn', range_color=[0,100])
st.plotly_chart(fig, use_container_width=True)

# --- BOTTOM ROW: SEARCHABLE INVENTORY ---
st.subheader("Full Component Tracking")
search_query = st.text_input("Search for a part (e.g., 'Axle', 'Brake', 'Filter')...")

if search_query:
    display_df = df[df['Item'].str.contains(search_query, case=False)]
else:
    display_df = df

# Styled table with color-coded bars
st.dataframe(
    display_df.style.background_gradient(subset=['Life_Pct'], cmap='RdYlGn', vmin=0, vmax=100)
    .format({"Life_Pct": "{:.1f}%", "Remaining_Hours": "{:.1f} hrs"}),
    use_container_width=True
)
