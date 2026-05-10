def assign_recycler(location):

    mapping = {
        "Manzini": "Recycle Manzini",
        "Mbabane": "Green Mbabane",
        "Nhlangano": "Eco Swazi"
    }

    return mapping.get(location, "Eco Swazi")


def update_status(df, waste_id, status):

    df.loc[df["id"] == waste_id, "status"] = status
    return df
