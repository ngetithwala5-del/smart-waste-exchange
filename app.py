import streamlit as st
import pandas as pd
import datetime
import os

# ---------------------------
# FILE
# ---------------------------
FILE = "waste_data.csv"

# ---------------------------
# ROLE USERS (ONLY STAFF ROLES)
# ---------------------------
USERS = {
    "recycler": {"password": "1234", "role": "recycler"},
    "admin": {"password": "1234", "role": "admin"}
}

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "waste_data" not in st.session_state:
    if os.path.exists(FILE):
        st.session_state.waste_data = pd.read_csv(FILE)
    else:
        st.session_state.waste_data = pd.DataFrame(columns=[
            "id", "waste_type", "quantity", "location",
            "description", "recycler", "status", "time"
        ])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None

# ---------------------------
# LOGIN (ONLY STAFF)
# ---------------------------
def login():
    st.sidebar.title("Staff Login")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = USERS[username]["role"]
            st.rerun()
        else:
            st.sidebar.error("Invalid login")

# ---------------------------
# LOGOUT
# ---------------------------
def logout():
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

# ---------------------------
# RECYCLERS DB
# ---------------------------
recyclers = pd.DataFrame([
    {"name": "Recycle Manzini", "location": "Manzini"},
    {"name": "Green Mbabane", "location": "Mbabane"},
    {"name": "Eco Swazi", "location": "Nhlangano"},
])

# ---------------------------
# ASSIGN LOGIC
# ---------------------------
def assign_recycler(location):
    match = recyclers[recyclers["location"] == location]
    if not match.empty:
        return match.iloc[0]["name"]
    return recyclers.sample(1).iloc[0]["name"]

# ---------------------------
# SAVE
# ---------------------------
def save_data():
    st.session_state.waste_data.to_csv(FILE, index=False)

# ---------------------------
# PUBLIC WASTE REPORT (NO LOGIN)
# ---------------------------
st.title("♻️ Smart Waste Exchange Platform")
st.caption("Public Waste Reporting System for Eswatini")

menu = st.sidebar.radio("Menu", [
    "📍 Report Waste (Public)",
    "🚛 Recycler Dashboard",
    "📊 Analytics (Admin)"
])

# ---------------------------
# PUBLIC REPORT FORM
# ---------------------------
if menu == "📍 Report Waste (Public)":

    st.subheader("Report Waste (No Login Required)")

    waste_type = st.selectbox("Waste Type", ["Plastic", "Glass", "Metal", "Organic"])
    quantity = st.number_input("Quantity (kg)", min_value=1)
    location = st.selectbox("Location", ["Manzini", "Mbabane", "Nhlangano"])
    description = st.text_area("Description (optional)")

    if st.button("Submit Report"):
        new_id = len(st.session_state.waste_data) + 1
        recycler = assign_recycler(location)

        new_entry = {
            "id": new_id,
            "waste_type": waste_type,
            "quantity": quantity,
            "location": location,
            "description": description,
            "recycler": recycler,
            "status": "Assigned",
            "time": datetime.datetime.now()
        }

        st.session_state.waste_data = pd.concat(
            [st.session_state.waste_data, pd.DataFrame([new_entry])],
            ignore_index=True
        )

        save_data()

        st.success("Waste submitted successfully!")
        st.info(f"Your assigned recycler: {recycler}")
        st.info(f"Your Waste ID: {new_id} (save this for tracking)")

# ---------------------------
# LOGIN FOR STAFF ONLY
# ---------------------------
if not st.session_state.logged_in:
    login()
    st.stop()

logout()

# ---------------------------
# RECYCLER DASHBOARD
# ---------------------------
if menu == "🚛 Recycler Dashboard":

    if st.session_state.role != "recycler" and st.session_state.role != "admin":
        st.warning("Not allowed")
        st.stop()

    st.subheader("Assigned Waste")

    st.dataframe(st.session_state.waste_data)

    selected_id = st.number_input("Enter Waste ID to Mark Collected", min_value=1, step=1)

    if st.button("Mark Collected"):
        if selected_id in st.session_state.waste_data["id"].values:
            st.session_state.waste_data.loc[
                st.session_state.waste_data["id"] == selected_id,
                "status"
            ] = "Collected"

            save_data()
            st.success("Marked as collected")
        else:
            st.error("Invalid ID")

# ---------------------------
# ADMIN DASHBOARD
# ---------------------------
if menu == "📊 Analytics (Admin)":

    if st.session_state.role != "admin":
        st.warning("Admin only section")
        st.stop()

    st.subheader("System Analytics")

    if st.session_state.waste_data.empty:
        st.info("No data yet")
    else:
        st.write("Waste Types")
        st.bar_chart(st.session_state.waste_data["waste_type"].value_counts())

        st.write("Locations")
        st.bar_chart(st.session_state.waste_data["location"].value_counts())

        st.write("All Data")
        st.dataframe(st.session_state.waste_data)
