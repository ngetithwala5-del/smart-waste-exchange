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

COLUMNS = [
    "id", "type", "quantity", "location",
    "lat", "lon", "description",
    "recycler", "status", "time"
]

# ---------------------------
# SAFE DATA LOADING (FIXED)
# ---------------------------
if "waste_data" not in st.session_state:

    if os.path.exists(FILE) and os.path.getsize(FILE) > 0:
        try:
            st.session_state.waste_data = pd.read_csv(FILE)
        except pd.errors.EmptyDataError:
            st.session_state.waste_data = pd.DataFrame(columns=COLUMNS)
    else:
        st.session_state.waste_data = pd.DataFrame(columns=COLUMNS)

# ---------------------------
# SAVE FUNCTION
# ---------------------------
def save():
    try:
        st.session_state.waste_data.to_csv(FILE, index=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# ---------------------------
# UI HEADER
# ---------------------------
st.title("♻️ Smart Waste Exchange System")
st.caption("AI-Driven Civic Waste Management Platform for Eswatini")

menu = st.sidebar.radio("Navigation", [
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
    qty = st.number_input("Quantity (kg)", min_value=1)
    location = st.selectbox("Location", ["Manzini", "Mbabane", "Nhlangano"])

    lat = st.number_input("Latitude (optional)", value=0.0)
    lon = st.number_input("Longitude (optional)", value=0.0)

    desc = st.text_area("Description (optional)")

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

    st.subheader("Recycler Operations Panel")

    df = st.session_state.waste_data

    if df.empty:
        st.info("No waste reports yet.")
    else:
        st.dataframe(df)

    wid = st.number_input("Enter Waste ID", min_value=1, step=1)
    status = st.selectbox("Update Status", ["ACCEPTED", "COLLECTED"])

    if st.button("Update Status"):
        if wid in df["id"].values:
            st.session_state.waste_data = update_status(df, wid, status)
            save()
            st.success("Status updated successfully")
        else:
            st.error("Invalid Waste ID")

# ---------------------------
# 🛠 ADMIN DASHBOARD
# ---------------------------
elif menu == "🛠 Admin Dashboard":

    st.subheader("System Analytics Dashboard")

    df = st.session_state.waste_data

    if df.empty:
        st.info("No data available yet.")
    else:

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Waste Type Distribution")
            st.bar_chart(df["type"].value_counts())

        with col2:
            st.write("### Status Distribution")
            st.bar_chart(df["status"].value_counts())

        st.write("### 📍 Waste Hotspots (AI Insight)")

        hotspots = waste_hotspots(df)

        if not hotspots.empty:
            st.map(hotspots)
        else:
            st.info("No location data available yet.")

        st.write("### Full Dataset")
        st.dataframe(df)
