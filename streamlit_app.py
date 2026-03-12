import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Goal Tracker", page_icon="⚽")

st.title("⚽ 5 aside Goal Tracker")

# --- Data ---
goals = pd.DataFrame({
    "Date": pd.to_datetime([
        "2026-02-01",
        "2026-02-08",
        "2026-02-15"
    ]),
    "Molly": [3, 5, 6],
    "Eleanor": [2, 4, 3],
    "Billy": [0, 0, 1]
})

players = ["Molly", "Eleanor", "Billy"]

# --- Controls ---
with st.container(border=True):
    selected_players = st.multiselect(
        "Select players",
        players,
        default=players
    )

    cumulative = st.toggle("Show cumulative goals", value=False)

# --- Prepare data ---
chart_data = goals[["Date"] + selected_players]

long_data = chart_data.melt(
    id_vars="Date",
    var_name="Player",
    value_name="Goals"
)

long_data["Cumulative Goals"] = long_data.groupby("Player")["Goals"].cumsum()

# --- Leaderboard stats ---
totals = long_data.groupby("Player")["Goals"].sum().sort_values(ascending=False)

st.subheader("🏆 Leaderboard")

cols = st.columns(len(totals))

for i, (player, score) in enumerate(totals.items()):
    cols[i].metric(player, score)

# --- Chart ---
st.subheader("📊 Goals over time")

if cumulative:
    y_col = "Cumulative Goals"
    y_title = "Total Goals"

    chart = alt.Chart(long_data).mark_bar().encode(
        x=alt.X("Date:T", title="Week"),
        y=alt.Y(f"{y_col}:Q", title=y_title),
        color="Player:N",
        xOffset="Player",
        tooltip=["Player", "Date", "Goals", "Cumulative Goals"]
    )

else:
    y_col = "Goals"
    y_title = "Goals scored"

    chart = alt.Chart(long_data).mark_bar().encode(
        x=alt.X("Date:T", title="Week"),
        y=alt.Y(f"{y_col}:Q", title=y_title),
        color="Player:N",
        xOffset="Player",
        tooltip=["Player", "Date", "Goals"]
    )

st.altair_chart(chart.properties(height=400), use_container_width=True)

# --- Raw data ---
with st.expander("View raw data"):
    st.dataframe(goals, use_container_width=True)
