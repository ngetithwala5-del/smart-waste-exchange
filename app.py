import streamlit as st
import pandas as pd
import datetime
import os

from logic import assign_recycler, update_status
from analytics import waste_hotspots

# ---------------------------
# FILE SETUP
# ---------------------------
FILE = "data/waste_data.csv"

os.makedirs("data", exist_ok=True)

# ---------------------------
# SESSION STATE
# ---------------------------
if "waste_data" not in st.session_state:
    if os.path.exists(FILE):
        st.session_state.waste_data = pd.read_csv(FILE)
    else:
        st.session_state.waste_data = pd.DataFrame(columns=[
            "id","type","quantity","location",
            "lat","lon","description",
            "recycler","status","time"
        ])

def save():
    st.session_state.waste_data.to_csv(FILE, index=False)

# ---------------------------
# UI
# ---------------------------
st.set_page_config(page_title="Smart Waste Exchange", layout="wide")

st.title("♻️ Smart Waste Exchange System")
st.caption("Civic AI Waste Management Platform for Eswatini")

menu = st.sidebar.radio("Navigation", [
    "🌍 Public Report",
    "🚛 Recycler Dashboard",
    "🛠 Admin Dashboard"
])

# ---------------------------
# PUBLIC
# ---------------------------
if menu == "🌍 Public Report":

    st.subheader("Report Waste (Public Access)")

    type_ = st.selectbox("Waste Type", ["Plastic", "Glass", "Metal", "Organic"])
    qty = st.number_input("Quantity (kg)", 1)
    location = st.selectbox("Location", ["Manzini", "Mbabane", "Nhlangano"])

    lat = st.number_input("Latitude", value=0.0)
    lon = st.number_input("Longitude", value=0.0)

    desc = st.text_area("Description")

    if st.button("Submit Report"):
        new_id = len(st.session_state.waste_data) + 1

        recycler = assign_recycler(location)

        new = {
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
            [st.session_state.waste_data, pd.DataFrame([new])],
            ignore_index=True
        )

        save()
        st.success("Waste submitted successfully!")
        st.info(f"Assigned Recycler: {recycler}")
        st.info(f"Tracking ID: {new_id}")

# ---------------------------
# RECYCLER
# ---------------------------
elif menu == "🚛 Recycler Dashboard":

    st.subheader("Recycler Operations Panel")

    df = st.session_state.waste_data
    st.dataframe(df)

    wid = st.number_input("Waste ID", 1, step=1)
    status = st.selectbox("Update Status", ["ACCEPTED", "COLLECTED"])

    if st.button("Update"):
        st.session_state.waste_data = update_status(df, wid, status)
        save()
        st.success("Status updated")

# ---------------------------
# ADMIN
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
            st.write("Status Flow")
            st.bar_chart(df["status"].value_counts())

        st.write("📍 Waste Hotspots")

        hotspots = waste_hotspots(df)

        if not hotspots.empty:
            st.map(hotspots)

        st.write("Full Dataset")
        st.dataframe(df)
