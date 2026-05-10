import streamlit as st
import pandas as pd
import datetime
import os

from logic import assign_recycler, update_status
from analytics import waste_hotspots

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="Smart Waste Exchange", layout="wide")

FILE = "waste_data.csv"
ADMIN_PASSWORD = "admin123"

COLUMNS = [
    "id", "type", "quantity", "location",
    "lat", "lon", "description",
    "recycler", "status", "time"
]

# ---------------------------
# CLEAN UI STYLE
# ---------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.stButton>button {
    background-color: #16a34a;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
.stTextInput, .stNumberInput, .stSelectbox {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SAFE DATA LOAD
# ---------------------------
if "waste_data" not in st.session_state:
    if os.path.exists(FILE) and os.path.getsize(FILE) > 0:
        try:
            st.session_state.waste_data = pd.read_csv(FILE)
        except:
            st.session_state.waste_data = pd.DataFrame(columns=COLUMNS)
    else:
        st.session_state.waste_data = pd.DataFrame(columns=COLUMNS)

def save():
    st.session_state.waste_data.to_csv(FILE, index=False)

# ---------------------------
# HEADER
# ---------------------------
st.title("Smart Waste Exchange")
st.subheader("AI-powered waste reporting and recycling platform")

st.markdown("""
Welcome to a smarter way to manage waste.

- Report waste easily  
- Get connected to recyclers  
- Improve environmental sustainability  
""")

# ---------------------------
# NAVIGATION
# ---------------------------
menu = st.sidebar.radio("Navigation", [
    "Report Waste",
    "Recycler",
    "Admin"
])

# ---------------------------
# PUBLIC REPORT
# ---------------------------
if menu == "Report Waste":

    st.header("Report Waste")

    col1, col2 = st.columns(2)

    with col1:
        type_ = st.selectbox("Waste Type", ["Plastic", "Glass", "Metal", "Organic"])
        qty = st.number_input("Quantity (kg)", min_value=1)
        location = st.selectbox("Location", ["Manzini", "Mbabane", "Nhlangano"])

    with col2:
        lat = st.number_input("Latitude (optional)", value=0.0)
        lon = st.number_input("Longitude (optional)", value=0.0)
        desc = st.text_area("Description")

    if st.button("Report Waste"):

        new_id = len(st.session_state.waste_data) + 1
        recycler = assign_recycler(location)

        new_entry = {
            "id": new_id,
            "type": type_,
            "quantity": qty,
            "location": location,
            "lat": lat,
            "lon": lon,
            "description": desc,
            "recycler": recycler,
            "status": "ASSIGNED",
            "time": datetime.datetime.now()
        }

        st.session_state.waste_data = pd.concat(
            [st.session_state.waste_data, pd.DataFrame([new_entry])],
            ignore_index=True
        )

        save()

        st.success("Waste reported successfully")
        st.info(f"Recycler assigned: {recycler}")
        st.info(f"Tracking ID: {new_id}")

# ---------------------------
# RECYCLER DASHBOARD
# ---------------------------
elif menu == "Recycler":

    st.header("Recycler Dashboard")

    df = st.session_state.waste_data

    if df.empty:
        st.info("No waste reports available")
    else:
        st.dataframe(df, use_container_width=True)

    wid = st.number_input("Waste ID", min_value=1, step=1)
    status = st.selectbox("Update Status", ["ACCEPTED", "COLLECTED"])

    if st.button("Update Collection Status"):
        if wid in df["id"].values:
            st.session_state.waste_data = update_status(df, wid, status)
            save()
            st.success("Status updated")
        else:
            st.error("Invalid Waste ID")

# ---------------------------
# ADMIN DASHBOARD
# ---------------------------
elif menu == "Admin":

    st.header("Admin Access")

    password = st.text_input("Enter Admin Password", type="password")

    if password != ADMIN_PASSWORD:
        st.warning("Access restricted")
        st.stop()

    st.success("Access granted")

    df = st.session_state.waste_data

    if df.empty:
        st.info("No data available")
    else:

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Waste Types")
            st.bar_chart(df["type"].value_counts())

        with col2:
            st.subheader("Status Overview")
            st.bar_chart(df["status"].value_counts())

        st.subheader("Waste Hotspots")

        hotspots = waste_hotspots(df)

        if not hotspots.empty:
            st.map(hotspots)
        else:
            st.info("No location data available")

        st.subheader("All Data")
        st.dataframe(df, use_container_width=True)
