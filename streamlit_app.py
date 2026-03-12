import streamlit as st
import pandas as pd
import altair as alt

st.title("⚽ 5-aside goal tracker")

st.write("Track how many goals everyone scored each week!")

# --- Data ---
goals = pd.DataFrame({
    "Date": pd.to_datetime([
        "2026-02-01",
        "2026-02-08",
        "2026-02-15"
    ]),
    "Molly": [3, 5, 6],
    "Eleanor": [2, 4, 3],
    "Billy": [0, 0, 0]
})

all_users = ["Molly", "Eleanor", "Billy"]

with st.container(border=True):
    users = st.multiselect(
        "Select players",
        all_users,
        default=all_users
    )

    cumulative = st.toggle("Show cumulative goals", value=True)

# --- Prepare data ---
chart_data = goals[["Date"] + users]

long_data = chart_data.melt(
    id_vars="Date",
    var_name="Player",
    value_name="Goals"
)

long_data["Cumulative Goals"] = long_data.groupby("Player")["Goals"].cumsum()

# Choose what to plot
if cumulative:
    y_col = "Cumulative Goals"
    y_title = "Total Goals"
else:
    y_col = "Goals"
    y_title = "Goals Scored"

# --- Tabs ---
tab1, tab2 = st.tabs(["📈 Chart", "📋 Data"])

with tab1:

    chart = alt.Chart(long_data).mark_line(point=True).encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y(f"{y_col}:Q", title=y_title),
        color="Player:N",
        tooltip=["Player", "Date", "Goals", "Cumulative Goals"]
    ).properties(
        height=350
    )

    st.altair_chart(chart, use_container_width=True)

with tab2:
    st.dataframe(goals, use_container_width=True)
