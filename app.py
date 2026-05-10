import streamlit as st
import pandas as pd
import datetime
import os

from logic import assign_recycler, update_status
from analytics import waste_hotspots

# ---------------------------
# FILE PATH (NO FOLDER CREATION)
# ---------------------------
FILE = "waste_data.csv"

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "waste_data" not in st.session_state:
    if os.path.exists(FILE):
        st.session_state.waste_data = pd.read_csv(FILE)
    else:
        st.session_state.waste_data = pd.DataFrame(columns=[
            "id", "type", "quantity", "location",
            "lat", "lon", "description",
            "recycler", "status", "time"
        ])

def save():
    st.session_state.waste_data.to_csv(FILE, index=False)

# ---------------------------
# APP UI
# ---------------------------
st.set_page_config(page_title="Smart Waste Exchange", layout="wide")

st.title("♻️ Smart Waste Exchange System")
st.caption("Public Civic Waste Reporting Platform")

menu = st.sidebar.radio("Menu", [
    "🌍 Public Report",
    "🚛 Recycler Dashboard",
    "🛠 Admin Dashboard"
])

# ---------------------------
# 🌍 PUBLIC REPORT (NO LOGIN)
# ---------------------------
if menu == "🌍 Public Report":

    st.subheader("Report Waste (Public Access)")

    type_ = st.selectbox("Waste Type", ["Plastic", "Glass", "Metal", "Organic"])
    qty = st.number_input("Quantity (kg)", 1)
    location = st.selectbox("Location", ["Manzini", "Mbabane", "Nhlangano"])

    lat = st.number_input("Latitude (optional)", value=0.0)
    lon = st.number_input("Longitude (optional)", value=0.0)

    desc = st.text_area("Description")

    if st.button("Submit Report"):

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

        st.success("Waste submitted successfully!")
        st.info(f"Assigned Recycler: {recycler}")
        st.info(f"Tracking ID: {new_id}")

# ---------------------------
# 🚛 RECYCLER DASHBOARD
# ---------------------------
elif menu == "🚛 Recycler Dashboard":

    st.subheader("Recycler Panel")

    df = st.session_state.waste_data
    st.dataframe(df)

    wid = st.number_input("Waste ID", 1, step=1)
    status = st.selectbox("Update Status", ["ACCEPTED", "COLLECTED"])

    if st.button("Update Status"):
        st.session_state.waste_data = update_status(df, wid, status)
        save()
        st.success("Status updated successfully")

# ---------------------------
# 🛠 ADMIN DASHBOARD
# ---------------------------
elif menu == "🛠 Admin Dashboard":

    st.subheader("System Analytics")

    df = st.session_state.waste_data

    if df.empty:
        st.info("No data yet")
    else:

        col1, col2 = st.columns(2)

        with col1:
            st.write("Waste Types")
            st.bar_chart(df["type"].value_counts())

        with col2:
            st.write("Status Distribution")
            st.bar_chart(df["status"].value_counts())

        st.write("📍 Waste Hotspots")

        hotspots = waste_hotspots(df)

        if not hotspots.empty:
            st.map(hotspots)

        st.write("Full Data")
        st.dataframe(df)
