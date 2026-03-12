import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Goal Tracker", page_icon="⚽")

st.title("⚽ Weekly Goal Tracker")

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

    cumulative = st.toggle("Show cumulative goals")

# --- Prepare data ---
chart_data = goals[["Date"] + selected_players]

long_data = chart_data.melt(
    id_vars="Date",
    var_name="Player",
    value_name="Goals"
)

long_data["Cumulative Goals"] = long_data.groupby("Player")["Goals"].cumsum()
long_data["Week"] = long_data["Date"].dt.strftime("%d %b")

# --- Leaderboard ---
st.subheader("🏆 Leaderboard")

totals = long_data.groupby("Player")["Goals"].sum().sort_values(ascending=False)

cols = st.columns(len(totals))

for i, (player, score) in enumerate(totals.items()):
    cols[i].metric(player, score)

# --- Chart ---
st.subheader("📊 Goals by week")

if cumulative:
    y_col = "Cumulative Goals"
    y_title = "Total Goals"
else:
    y_col = "Goals"
    y_title = "Goals scored"

chart = alt.Chart(long_data).mark_bar().encode(
    x=alt.X("Week:N", title="Week"),
    xOffset=alt.XOffset("Player:N"),
    y=alt.Y(f"{y_col}:Q", title=y_title),
    color=alt.Color("Player:N", legend=alt.Legend(title="Player")),
    tooltip=["Player", "Week", "Goals", "Cumulative Goals"]
).properties(height=400)


st.altair_chart(chart, use_container_width=True)

# --- Raw data ---
with st.expander("View raw data"):
    st.dataframe(goals, use_container_width=True)
