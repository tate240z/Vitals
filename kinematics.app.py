import streamlit as st

# --- DASHBOARD CONFIG ---
st.set_page_config(page_title="GT3R Kinematics", layout="wide")

# --- DATA VAULT (Directly from your Porsche PDF) ---
# Each setup includes: Lower Front (LF), Lower Rear (LR), Upper Front (UF), Upper Rear (UR), Tierod (TR)
# Values are in millimeters
setup_specs = {
    "FS15 (Baseline/Daytona)": {
        "LF Lower WB": -5.0, "LR Lower WB": 3.0, 
        "UF Upper WB": 5.0, "UR Upper WB": -5.0, "Tierod": 1.0
    },
    "FS15-NSL (Nordschleife)": {
        "LF Lower WB": -5.0, "LR Lower WB": 3.0, 
        "UF Upper WB": 5.0, "UR Upper WB": -5.0, "Tierod": 2.0
    },
    "FS16 (Evo Production)": {
        "LF Lower WB": -5.0, "LR Lower WB": 3.0, 
        "UF Upper WB": 5.0, "UR Upper WB": -5.0, "Tierod": 2.0
    },
    "FS17 (High Roll Center)": {
        "LF Lower WB": -5.0, "LR Lower WB": 3.0, 
        "UF Upper WB": 5.0, "UR Upper WB": -5.0, "Tierod": 3.0
    }
}

st.title("🛠️ 992 GT3R Kinematics Tool")
st.markdown("Select your current shim state and your target setup to see the required changes.")

# --- SELECTION ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Current Setup")
    current_name = st.selectbox("Current Car State", list(setup_specs.keys()), label_visibility="collapsed")
    current_data = setup_specs[current_name]

with col2:
    st.subheader("Target Setup")
    target_name = st.selectbox("New Target State", list(setup_specs.keys()), label_visibility="collapsed")
    target_data = setup_specs[target_name]

st.divider()

# --- CALCULATION LOGIC ---
if current_name == target_name:
    st.success("✅ Car is currently at the target setup. No changes required.")
else:
    st.header(f"🔧 Adjustment Order: {current_name} ➡️ {target_name}")
    
    # We create a big checklist for the mechanics
    for part in current_data.keys():
        diff = target_data[part] - current_data[part]
        
        # UI Styling based on action required
        if diff == 0:
            st.write(f"⚪ **{part}:** No change (Target: {target_data[part]}mm)")
        elif diff > 0:
            st.warning(f"➕ **{part}:** ADD **{abs(diff)}mm** of shims")
        else:
            st.error(f"➖ **{part}:** REMOVE **{abs(diff)}mm** of shims")

# --- TECHNICAL REFERENCE ---
with st.expander("Reference Diagram"):
    st.write("Ensure all spacers are seated correctly in the spherical bearings before torquing.")
    # You can add a placeholder for an image here
    #
