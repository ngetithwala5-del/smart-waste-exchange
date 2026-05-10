import streamlit as st
import pandas as pd
import datetime
import os

# ---------------------------
# FILE STORAGE
# ---------------------------
FILE = "waste_data.csv"

# ---------------------------
# SIMPLE USER DATABASE (TEMP)
# ---------------------------
USERS = {
    "citizen": {"password": "1234", "role": "citizen"},
    "recycler": {"password": "1234", "role": "recycler"},
    "admin": {"password": "1234", "role": "admin"}
}

# ---------------------------
# INIT SESSION STATE
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None

if "waste_data" not in st.session_state:
    if os.path.exists(FILE):
        st.session_state.waste_data = pd.read_csv(FILE)
    else:
        st.session_state.waste_data = pd.DataFrame(columns=[
            "id", "waste_type", "quantity", "location",
            "description", "recycler", "status", "time"
        ])

# ---------------------------
# LOGIN FUNCTION
# ---------------------------
def login():
    st.title("🔐 Smart Waste Platform Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = USERS[username]["role"]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# ---------------------------
# LOGOUT
# ---------------------------
def logout():
    st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.clear())

# ---------------------------
# SAVE DATA
# ---------------------------
def save_data():
    st.session_state.waste_data.to_csv(FILE, index=False)

# ---------------------------
# RECYCLERS DATABASE
# ---------------------------
recyclers = pd.DataFrame([
    {"name": "Recycle Manzini", "location": "Manzini"},
    {"name": "Green Mbabane", "location": "Mbabane"},
    {"name": "Eco Swazi", "location": "Nhlangano"},
])

# ---------------------------
# MATCHING LOGIC
# ---------------------------
def assign_recycler(location):
    match = recyclers[recyclers["location"] == location]
    if not match.empty:
        return match.iloc[0]["name"]
    return recyclers.sample(1).iloc[0]["name"]

# ---------------------------
# LOGIN GATE
# ---------------------------
if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------------------
# APP UI
# ---------------------------
st.title("♻️ Smart Waste Exchange Platform")
st.caption(f"Logged in as: {st.session_state.user} ({st.session_state.role})")

logout()

menu = st.sidebar.radio("Menu", [
    "📍 Report Waste",
    "🚛 Recycler Dashboard",
    "📊 Analytics Dashboard"
])

# ---------------------------
# CITIZEN: REPORT WASTE
# ---------------------------
if menu == "📍 Report Waste":

    if st.session_state.role not in ["citizen", "admin"]:
        st.warning("You are not allowed to access this section.")
        st.stop()

    st.subheader("Report Waste for Pickup")

    waste_type = st.selectbox("Waste Type", ["Plastic", "Glass", "Metal", "Organic"])
    quantity = st.number_input("Quantity (kg)", min_value=1)
    location = st.selectbox("Location", ["Manzini", "Mbabane", "Nhlangano"])
    description = st.text_area("Description (optional)")

    if st.button("Submit Waste"):
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
        st.success(f"Waste assigned to: {recycler}")

# ---------------------------
# RECYCLER DASHBOARD
# ---------------------------
if menu == "🚛 Recycler Dashboard":

    if st.session_state.role not in ["recycler", "admin"]:
        st.warning("You are not allowed to access this section.")
        st.stop()

    st.subheader("Available Waste for Collection")

    if st.session_state.waste_data.empty:
        st.info("No waste available yet.")
    else:
        st.dataframe(st.session_state.waste_data)

        selected_id = st.number_input("Enter Waste ID to Claim", min_value=1, step=1)

        if st.button("Claim Waste"):
            if selected_id in st.session_state.waste_data["id"].values:
                st.session_state.waste_data.loc[
                    st.session_state.waste_data["id"] == selected_id,
                    "status"
                ] = "Collected"

                save_data()
                st.success("Waste marked as collected!")
            else:
                st.error("Invalid ID")

# ---------------------------
# ANALYTICS DASHBOARD
# ---------------------------
if menu == "📊 Analytics Dashboard":

    if st.session_state.role not in ["admin"]:
        st.warning("Only admin can view analytics.")
        st.stop()

    st.subheader("Environmental Insights")

    if st.session_state.waste_data.empty:
        st.info("No data yet.")
    else:
        st.write("### Waste Type Distribution")
        st.bar_chart(st.session_state.waste_data["waste_type"].value_counts())

        st.write("### Waste by Location")
        st.bar_chart(st.session_state.waste_data["location"].value_counts())

        st.write("### Full Data")
        st.dataframe(st.session_state.waste_data)
