import streamlit as st

st.set_page_config(page_title="992 GT3 R Kinematics Master", layout="wide")

# --- THE MASTER DATA ENGINE ---
# Mapping every adjustment point from the Porsche Technical Manual
setups = {
    "FS15 - Baseline": {
        "Reference rideheight [mm]": 50,
        "Reference toe [°]": 0,
        "Reference camber [°]": -3.0,
        "Damper ratio": 0.657,
        "Rollcenter [mm]": 14.062,
        "Antidive [%]": 164.948,
        "Caster [°]": 8.178,
        "Wheelbase vs RS25 [mm]": 2504.599,
        # --- SHIM STACKS (Chassis Side) ---
        "FP wishbone lower front [mm]": -5,
        "FP wishbone lower rear [mm]": 3,
        "FP wishbone upper front [mm]": 5,
        "FP wishbone upper rear [mm]": -5,
        # --- SHIM STACKS (Wheel Side) ---
        "LP wishbone upper [mm]": 0,
        "LP wishbone lower [mm]": 0,
        "LP tierod [mm]": 2
    },
    "FS16 - Daytona/Evo": {
        "Reference rideheight [mm]": 50,
        "Reference toe [°]": 0,
        "Reference camber [°]": -2.0,
        "Damper ratio": 0.660,
        "Rollcenter [mm]": 1.212,
        "Antidive [%]": 168.800,
        "Caster [°]": 8.133,
        "Wheelbase vs RS25 [mm]": 2504.757,
        # --- SHIM STACKS (Chassis Side) ---
        "FP wishbone lower front [mm]": -5,
        "FP wishbone lower rear [mm]": 3,
        "FP wishbone upper front [mm]": 5,
        "FP wishbone upper rear [mm]": -5,
        # --- SHIM STACKS (Wheel Side) ---
        "LP wishbone upper [mm]": -5,
        "LP wishbone lower [mm]": 0,
        "LP tierod [mm]": 0
    },
    "FS17 - Nordschleife/High RC": {
        "Reference rideheight [mm]": 70,
        "Reference toe [°]": 0,
        "Reference camber [°]": -3.0,
        "Damper ratio": 0.641,
        "Rollcenter [mm]": 51.316,
        "Antidive [%]": 161.653,
        "Caster [°]": 6.970,
        "Wheelbase vs RS25 [mm]": 2505.358,
        # --- SHIM STACKS (Chassis Side) ---
        "FP wishbone lower front [mm]": -5,
        "FP wishbone lower rear [mm]": 3,
        "FP wishbone upper front [mm]": 5,
        "FP wishbone upper rear [mm]": -5,
        # --- SHIM STACKS (Wheel Side) ---
        "LP wishbone upper [mm]": 5,
        "LP wishbone lower [mm]": 5,
        "LP tierod [mm]": 4
    }
}

st.title("🏎️ 992 GT3 R | Kinematics Change Master")
st.markdown("### Technical Transition Tool")

# --- SELECTION ---
c1, c2 = st.columns(2)
with c1:
    current = st.selectbox("Current Configuration", list(setups.keys()))
with c2:
    target = st.selectbox("Target Configuration", list(setups.keys()))

if current == target:
    st.success("✅ System check complete. Car is at current target specification.")
else:
    st.divider()
    cur_data = setups[current]
    tar_data = setups[target]

    # --- SECTION 1: TARGET GEOMETRY ---
    st.subheader("📍 Target Geometry Reference")
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Ride Height", f"{tar_data['Reference rideheight [mm]']}mm")
    g2.metric("Camber", f"{tar_data['Reference camber [°]']}°")
    g3.metric("Roll Center", f"{tar_data['Rollcenter [mm]']}mm")
    g4.metric("Antidive", f"{tar_data['Antidive [%]']}%")

    # --- SECTION 2: THE WORK ORDER ---
    st.subheader("🔧 Shim Adjustment Instructions")
    
    # Split into Chassis Side and Wheel Side to match the PDF layout
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("**Chassis Side Adjustments**")
        for key in ["FP wishbone lower front [mm]", "FP wishbone lower rear [mm]", 
                    "FP wishbone upper front [mm]", "FP wishbone upper rear [mm]"]:
            diff = tar_data[key] - cur_data[key]
            if diff > 0:
                st.warning(f"➕ **{key.split('[')[0]}:** ADD {abs(diff)}mm")
            elif diff < 0:
                st.error(f"➖ **{key.split('[')[0]}:** REMOVE {abs(diff)}mm")
            else:
                st.write(f"✅ {key.split('[')[0]}: No Change")

    with col_right:
        st.markdown("**Wheel Side Adjustments**")
        for key in ["LP wishbone upper [mm]", "LP wishbone lower [mm]", "LP tierod [mm]"]:
            diff = tar_data[key] - cur_data[key]
            if diff > 0:
                st.warning(f"➕ **{key.split('[')[0]}:** ADD {abs(diff)}mm")
            elif diff < 0:
                st.error(f"➖ **{key.split('[')[0]}:** REMOVE {abs(diff)}mm")
            else:
                st.write(f"✅ {key.split('[')[0]}: No Change")
