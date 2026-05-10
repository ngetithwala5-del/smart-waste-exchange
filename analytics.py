def waste_hotspots(df):

    if df.empty:
        return df

    valid = df[(df["lat"] != 0) & (df["lon"] != 0)]

    return valid.groupby(["lat","lon"]).size().reset_index(name="count")
