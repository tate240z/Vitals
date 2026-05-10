import streamlit as st
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="GMG Engineering Command", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_base_data():
    # In a full setup, we'd write back to GitHub, but for now, we use a local CSV
    return pd.read_csv("data.csv")

if 'df' not in st.session_state:
    st.session_state.df = load_base_data()

# --- HEADER ---
st.title("🛡️ 9509 GT3R | Engineering Command")

# --- TAB 1: LIVE LIFELINES ---
tab1, tab2 = st.tabs(["⏱️ Hour Log & Lifing", "🛠️ Kinematics Adjuster"])

with tab1:
    st.subheader("Component Health")
    
    # Editable Dataframe - Update hours directly in the table!
    edited_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Current_Hours": st.column_config.NumberColumn("Chassis Hours", format="%.1f hrs"),
            "Runtime Limit": st.column_config.NumberColumn("Limit", format="%d hrs"),
        },
        disabled=["Category", "Item"],
        use_container_width=True
    )

    # Calculate Life % on the fly
    edited_df['Life_Pct'] = (1 - (edited_df['Current_Hours'] / edited_df['Runtime Limit'])) * 100
    
    if st.button("Save Changes to Chassis Log"):
        st.session_state.df = edited_df
        st.success("Internal Log Updated!")

import streamlit as st
import pandas as pd

# 1. THE DATA VAULT (Baking the Porsche Sheet into the code)
# Values represent mm thickness for each shim location
setup_data = {
    "FS15 (Daytona)": {
        "Ride Height (mm)": 50, "Camber (deg)": -2.0,
        "Lower WB Front": -5.0, "Lower WB Rear": 3.0,
        "Upper WB Front": 5.0, "Upper WB Rear": -5.0,
        "Tierod": 1.0
    },
    "FS15 (Nordschleife)": {
        "Ride Height (mm)": 70, "Camber (deg)": -3.0,
        "Lower WB Front": -5.0, "Lower WB Rear": 3.0,
        "Upper WB Front": 5.0, "Upper WB Rear": -5.0,
        "Tierod": 2.0
    },
    "FS16 (Evo Production)": {
        "Ride Height (mm)": 50, "Camber (deg)": 0,
        "Lower WB Front": -5.0, "Lower WB Rear": 3.0,
        "Upper WB Front": 5.0, "Upper WB Rear": -5.0,
        "Tierod": 2.0
    }
}

st.title("🛠️ 9509 Setup & Kinematics")

# 2. SELECTION INTERFACE
col1, col2 = st.columns(2)
with col1:
    current_setup = st.selectbox("Current Car Setup", list(setup_data.keys()))
with col2:
    target_setup = st.selectbox("Target Technical Setup", list(setup_data.keys()))

# 3. THE CALCULATION ENGINE
if current_setup != target_setup:
    st.divider()
    st.subheader(f"Setup Change: {current_setup} ➡️ {target_setup}")
    
    current_vals = setup_data[current_setup]
    target_vals = setup_data[target_setup]
    
    # Mechanics Instruction List
    st.info("💡 **Instructions for Crew:** (Positive = Add Shim, Negative = Remove Shim)")
    
    for key in current_vals.keys():
        diff = target_vals[key] - current_vals[key]
        
        # Formatting the output for clarity in a loud garage
        if diff == 0:
            st.write(f"✅ **{key}:** No change required ({target_vals[key]})")
        elif diff > 0:
            st.warning(f"➕ **{key}:** ADD **{abs(diff)}mm** (Target: {target_vals[key]})")
        else:
            st.error(f"➖ **{key}:** REMOVE **{abs(diff)}mm** (Target: {target_vals[key]})")

else:
    st.success("Current setup is already at the target specification.")
