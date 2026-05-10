
import streamlit as st
import pandas as pd
import datetime
import os

# ---------------------------
# DATA STORAGE (CSV FILE)
# ---------------------------
FILE = "waste_data.csv"

if os.path.exists(FILE):
    waste_data = pd.read_csv(FILE)
else:
    waste_data = pd.DataFrame(columns=[
        "id", "waste_type", "quantity", "location",
        "description", "recycler", "status", "time"
    ])

# ---------------------------
# RECYCLERS DATABASE
# ---------------------------
recyclers = pd.DataFrame([
    {"name": "Recycle Manzini", "location": "Manzini"},
    {"name": "Green Mbabane", "location": "Mbabane"},
    {"name": "Eco Swazi", "location": "Nhlangano"},
])

# ---------------------------
# SAVE FUNCTION
# ---------------------------
def save_data():
    waste_data.to_csv(FILE, index=False)

# ---------------------------
# MATCHING LOGIC
# ---------------------------
def assign_recycler(location):
    match = recyclers[recyclers["location"] == location]

    if not match.empty:
        return match.iloc[0]["name"]
    else:
        return recyclers.sample(1).iloc[0]["name"]

# ---------------------------
# UI
# ---------------------------
st.title("♻️ Smart Waste Exchange Platform")
st.caption("Connecting citizens to recyclers to reduce landfill waste")

menu = st.sidebar.radio("Menu", [
    "📍 Report Waste",
    "🚛 Recycler Dashboard",
    "📊 Analytics Dashboard"
])

# ---------------------------
# REPORT WASTE
# ---------------------------
if menu == "📍 Report Waste":
    st.subheader("Report Waste for Pickup")

    waste_type = st.selectbox("Waste Type", ["Plastic", "Glass", "Metal", "Organic"])
    quantity = st.number_input("Quantity (kg)", min_value=1)
    location = st.selectbox("Location", ["Manzini", "Mbabane", "Nhlangano"])
    description = st.text_area("Description (optional)")

    if st.button("Submit Waste"):
        new_id = len(waste_data) + 1
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

        global waste_data
        waste_data = pd.concat([waste_data, pd.DataFrame([new_entry])], ignore_index=True)
        save_data()

        st.success(f"Waste assigned to: {recycler}")

# ---------------------------
# RECYCLER DASHBOARD
# ---------------------------
if menu == "🚛 Recycler Dashboard":
    st.subheader("Available Waste for Collection")

    if waste_data.empty:
        st.info("No waste available yet.")
    else:
        st.dataframe(waste_data)

        selected_id = st.number_input("Enter Waste ID to Claim", min_value=1, step=1)

        if st.button("Claim Waste"):
            if selected_id in waste_data["id"].values:
                waste_data.loc[waste_data["id"] == selected_id, "status"] = "Collected"
                save_data()
                st.success("Waste marked as collected!")
            else:
                st.error("Invalid ID")

# ---------------------------
# ANALYTICS
# ---------------------------
if menu == "📊 Analytics Dashboard":
    st.subheader("Environmental Insights")

    if waste_data.empty:
        st.info("No data yet.")
    else:
        st.write("Waste Type Distribution")
        st.bar_chart(waste_data["waste_type"].value_counts())

        st.write("Waste by Location")
        st.bar_chart(waste_data["location"].value_counts())

        st.dataframe(waste_data)
