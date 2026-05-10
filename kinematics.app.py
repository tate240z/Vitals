import streamlit as st
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw

st.set_page_config(page_title="GMG Kinematics Command", layout="wide")

# --- DATA VAULT (As derived from the Porsche PDF) ---
setup_data = {
    "FS15 - Baseline/Daytona": {
        "rideheight": 50, "camber": -3.0,
        "L_F": -5.0, "L_R": 3.0, "U_F": 5.0, "U_R": -5.0, "Tierod": 1.0,
        "Diagram_Points": ["L_F", "L_R", "U_F", "U_R", "Tierod"]
    },
    "FS16 - Evo Production": {
        "rideheight": 50, "camber": -3.0,
        "L_F": -5.0, "L_R": 3.0, "U_F": 5.0, "U_R": -5.0, "Tierod": 2.0,
        "Diagram_Points": ["L_F", "L_R", "U_F", "U_R", "Tierod"]
    },
    "FS17 - Nordschleife": {
        "rideheight": 70, "camber": -3.0,
        "L_F": -5.0, "L_R": 3.0, "U_F": 5.0, "U_R": -5.0, "Tierod": 4.0,
        "Diagram_Points": ["L_F", "L_R", "U_F", "U_R", "Tierod"]
    }
}

st.title("🛡️ 992 GT3 R | Visual Kinematics Command")

# --- SELECTION INTERFACE ---
c1, c2 = st.columns(2)
with c1: cur_name = st.selectbox("Current Setup", list(setup_data.keys()))
with c2: tar_name = st.selectbox("Target Setup", list(setup_data.keys()))

st.divider()

if cur_name == tar_name:
    st.success("✅ Technical check complete. Car is at current specification.")
    # Show clean diagrams by default
else:
    # Calculate deltas
    cur = setup_data[cur_name]
    tar = setup_data[tar_name]
    diffs = {k: tar[k] - cur[k] for k in cur.keys() if k not in ["Diagram_Points", "rideheight", "camber"]}
    
    # Identify which points need highlighting
    points_to_highlight = [k for k, v in diffs.items() if v != 0]

    # --- MAIN VIEW: MAP & INSTRUCTIONS ---
    map_col, text_col = st.columns([2, 1])
    
    with map_col:
        st.subheader("Interactive Adjustment Map")
        
        # Load your technical diagram
        try:
            img = Image.open("GT3R_front_axle.png")
            draw = ImageDraw.Draw(img)
            
            # Map of coordinates on the image for each point (X, Y, Radius)
            # You would replace these with the actual pixel coordinates from your PDF
            coords = {
                "U_F": (300, 200, 30), # Upper Front Wishbone
                "U_R": (400, 200, 30), # Upper Rear Wishbone
                "L_F": (300, 400, 30), # Lower Front Wishbone
                "L_R": (400, 400, 30), # Lower Rear Wishbone
                "Tierod": (500, 300, 30) # Tierod
            }
            
            # Draw the dynamic highlights
            for point, (x, y, r) in coords.items():
                if point in points_to_highlight:
                    color = "red" if diffs[point] < 0 else "yellow"
                    draw.ellipse((x-r, y-r, x+r, y+r), fill=None, outline=color, width=5)
            
            st.image(img, use_container_width=True)
            st.info("💡 **Glow Guide:** Red = Remove Shim, Yellow = Add Shim")
            
        except FileNotFoundError:
            st.error("Error: Diagram file 'GT3R_front_axle.png' not found in GitHub folder.")

    with text_col:
        st.subheader("Adjustment Order")
        
        # Display as a professional checklist
        for point in points_to_highlight:
            diff = diffs[point]
            label = f"**{point.replace('_', ' ')} Shim Stack:**"
            
            if diff > 0: st.warning(f"➕ {label} ADD **{abs(diff)}mm**")
            elif diff < 0: st.error(f"➖ {label} REMOVE **{abs(diff)}mm**")
