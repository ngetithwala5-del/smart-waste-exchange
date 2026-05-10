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

# USERS (simple auth)
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "recycler": {"password": "recycler123", "role": "recycler"}
}

COLUMNS = [
    "id", "type", "quantity", "location",
    "lat", "lon", "description",
    "recycler", "status", "time"
]

# ---------------------------
# UI STYLE (GREEN THEME)
# ---------------------------
st.markdown("""
<style>
body {
    background-color: #f0fdf4;
}
.block-container {
    padding-top: 2rem;
}
.stButton>button {
    background-color: #16a34a;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SESSION INIT
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

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
st.title("♻️ Smart Waste Exchange")
st.caption("Smart waste reporting and recycling system")

# ---------------------------
# LOGIN (SIDEBAR)
# ---------------------------
st.sidebar.subheader("Staff Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username in USERS and USERS[username]["password"] == password:
        st.session_state.logged_in = True
        st.session_state.role = USERS[username]["role"]
        st.success("Login successful")
        st.rerun()
    else:
        st.sidebar.error("Invalid credentials")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()

# ---------------------------
# NAVIGATION
# ---------------------------
menu_options = ["Report Waste"]

if st.session_state.logged_in:
    if st.session_state.role == "recycler":
        menu_options.append("Recycler Dashboard")
    if st.session_state.role == "admin":
        menu_options.append("Admin Dashboard")

menu = st.sidebar.radio("Navigation", menu_options)

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
elif menu == "Recycler Dashboard":

    st.header("Recycler Dashboard")

    df = st.session_state.waste_data

    if df.empty:
        st.info("No waste available")
    else:
        st.dataframe(df, use_container_width=True)

    wid = st.number_input("Waste ID", min_value=1)
    status = st.selectbox("Update Status", ["ACCEPTED", "COLLECTED"])

    if st.button("Update Status"):
        if wid in df["id"].values:
            st.session_state.waste_data = update_status(df, wid, status)
            save()
            st.success("Updated")
        else:
            st.error("Invalid ID")

# ---------------------------
# ADMIN DASHBOARD
# ---------------------------
elif menu == "Admin Dashboard":

    st.header("Admin Dashboard")

    df = st.session_state.waste_data

    if df.empty:
        st.info("No data yet")
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

        st.dataframe(df, use_container_width=True)
