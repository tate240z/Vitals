import streamlit as st
import pandas as pd
import plotly.express as px

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTTulE0KjYP78CgSG0tBU9K21LUfrzZs2Uu9SSymBYUnXAoa2HfEsjRUsImdNpPWylDrCp5hJK-N4nD/pub?output=csv"

st.set_page_config(page_title="9509 Evolution", layout="wide")

@st.cache_data(ttl=60)
def load_and_process():
    df = pd.read_csv(SHEET_URL, skiprows=3)
    df.columns = df.columns.str.strip()
    df['Category'] = df['Item'].where(df['Runtime Limit'].isna()).ffill()
    
    # Identify the race event columns
    event_cols = [c for c in df.columns if any(x in c for x in ['JAN', 'FEB', 'SRO', 'TEST'])]
    
    df_parts = df[df['Runtime Limit'].notnull()].copy()
    df_parts['Runtime Limit'] = pd.to_numeric(df_parts['Runtime Limit'], errors='coerce')
    
    return df_parts, event_cols

df, event_cols = load_and_process()

st.title("🏎️ 9509 GT3R | Lifetime Evolution")

# Create Tabs: Current Status vs Historical Trend
tab1, tab2 = st.tabs(["Current Health", "Event Evolution"])

with tab1:
    # (Your existing dashboard code here...)
    st.subheader("Current Component Status")
    def get_latest(row):
        vals = pd.to_numeric(row[event_cols], errors='coerce').dropna()
        return vals.iloc[-1] if not vals.empty else 0
    df['Current_Hours'] = df.apply(get_latest, axis=1)
    df['Life_Pct'] = (1 - (df['Current_Hours'] / df['Runtime Limit'])) * 100
    st.dataframe(df[['Category', 'Item', 'Life_Pct']].style.background_gradient(subset=['Life_Pct'], cmap='RdYlGn'))

with tab2:
    st.subheader("Component 'Burn-Down' by Event")
    
    # Select which parts to track on the graph
    tracked_items = st.multiselect("Select Components to Plot", 
                                   options=df['Item'].unique(), 
                                   default=["Engine", "Drive Shaft, Left", "Wheel Hub, Left"])

    if tracked_items:
        plot_data = []
        for _, row in df[df['Item'].isin(tracked_items)].iterrows():
            limit = row['Runtime Limit']
            for event in event_cols:
                hours = pd.to_numeric(row[event], errors='coerce')
                if not pd.isna(hours):
                    pct_left = (1 - (hours / limit)) * 100
                    plot_data.append({"Event": event, "Part": row['Item'], "Life Remaining (%)": pct_left})
        
        evolution_df = pd.DataFrame(plot_data)
        
        fig = px.line(evolution_df, x="Event", y="Life Remaining (%)", color="Part",
                      markers=True, title="Life Depreciation Over Season",
                      range_y=[0, 100])
        
        # Add a "Service Limit" danger zone line
        fig.add_hline(y=10, line_dash="dot", line_color="red", annotation_text="Service Limit")
        
        st.plotly_chart(fig, use_container_width=True)
