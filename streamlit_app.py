# import streamlit as st
# import pandas as pd
# import altair as alt

# st.set_page_config(page_title="Goal Tracker", page_icon="⚽")

# st.title("⚽ Weekly Goal Tracker")

# # --- Data ---
# goals = pd.DataFrame({
#     "Date": pd.to_datetime([
#         "2026-02-01",
#         "2026-02-08",
#         "2026-02-15"
#     ]),
#     "Molly": [3, 5, 6],
#     "Eleanor": [2, 4, 3],
#     "Billy": [0, 0, 1]
# })

# players = ["Molly", "Eleanor", "Billy"]

# # --- Controls ---
# with st.container(border=True):

#     selected_players = st.multiselect(
#         "Select players",
#         players,
#         default=players
#     )

#     cumulative = st.toggle("Show cumulative goals")

# # --- Prepare data ---
# chart_data = goals[["Date"] + selected_players]

# long_data = chart_data.melt(
#     id_vars="Date",
#     var_name="Player",
#     value_name="Goals"
# )

# long_data["Cumulative Goals"] = long_data.groupby("Player")["Goals"].cumsum()
# long_data["Week"] = long_data["Date"].dt.strftime("%d %b")

# # --- Leaderboard ---
# st.subheader("🏆 Leaderboard")

# totals = long_data.groupby("Player")["Goals"].sum().sort_values(ascending=False)

# cols = st.columns(len(totals))

# for i, (player, score) in enumerate(totals.items()):
#     cols[i].metric(player, score)

# # --- Chart ---
# st.subheader("📊 Goals by week")

# if cumulative:
#     y_col = "Cumulative Goals"
#     y_title = "Total Goals"
# else:
#     y_col = "Goals"
#     y_title = "Goals scored"

# chart = alt.Chart(long_data).mark_bar().encode(
#     x=alt.X("Week:N", title="Week"),
#     xOffset=alt.XOffset("Player:N"),
#     y=alt.Y(f"{y_col}:Q", title=y_title),
#     color=alt.Color("Player:N", legend=alt.Legend(title="Player")),
#     tooltip=["Player", "Week", "Goals", "Cumulative Goals"]
# ).properties(height=400)


# st.altair_chart(chart, use_container_width=True)

# # --- Raw data ---
# with st.expander("View raw data"):
#     st.dataframe(goals, use_container_width=True)


import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tournament Tracker", layout="wide")

st.title("⚽ Football Tournament Tracker")

# -------------------------------
# Hardcoded teams
# -------------------------------
TEAMS = ["Republica", "Momin FC", "Tyne Sliders", "1in12"]

# -------------------------------
# Session state
# -------------------------------
if "matches" not in st.session_state:
    st.session_state.matches = []

# -------------------------------
# Match entry (front-facing only)
# -------------------------------
st.header("📥 Add Match Result")

col1, col2 = st.columns(2)

with col1:
    team1 = st.selectbox("Team 1", TEAMS)

with col2:
    team2 = st.selectbox("Team 2", TEAMS)

score_col1, score_col2 = st.columns(2)

with score_col1:
    score1 = st.number_input("Score (Team 1)", min_value=0, step=1)

with score_col2:
    score2 = st.number_input("Score (Team 2)", min_value=0, step=1)

if st.button("➕ Submit Result"):
    if team1 == team2:
        st.error("A team cannot play itself.")
    else:
        st.session_state.matches.append({
            "team1": team1,
            "team2": team2,
            "score1": score1,
            "score2": score2
        })
        st.success("Result added!")

# -------------------------------
# Table computation
# -------------------------------
def compute_table(teams, matches):
    table = pd.DataFrame(index=teams, columns=[
        "P", "W", "D", "L", "GF", "GA", "GD", "Pts"
    ]).fillna(0)

    table = table.astype(int)

    for m in matches:
        t1, t2 = m["team1"], m["team2"]
        s1, s2 = m["score1"], m["score2"]

        table.loc[t1, "P"] += 1
        table.loc[t2, "P"] += 1

        table.loc[t1, "GF"] += s1
        table.loc[t1, "GA"] += s2
        table.loc[t2, "GF"] += s2
        table.loc[t2, "GA"] += s1

        if s1 > s2:
            table.loc[t1, "W"] += 1
            table.loc[t2, "L"] += 1
            table.loc[t1, "Pts"] += 3
        elif s2 > s1:
            table.loc[t2, "W"] += 1
            table.loc[t1, "L"] += 1
            table.loc[t2, "Pts"] += 3
        else:
            table.loc[t1, "D"] += 1
            table.loc[t2, "D"] += 1
            table.loc[t1, "Pts"] += 1
            table.loc[t2, "Pts"] += 1

    table["GD"] = table["GF"] - table["GA"]

    return table.sort_values(
        by=["Pts", "GD", "GF"],
        ascending=[False, False, False]
    )

# -------------------------------
# League table
# -------------------------------
st.header("🏆 League Table")

table = compute_table(TEAMS, st.session_state.matches)
st.dataframe(table, use_container_width=True)

# -------------------------------
# Match history (collapsed)
# -------------------------------
with st.expander("📜 Match History"):
    if st.session_state.matches:
        st.dataframe(pd.DataFrame(st.session_state.matches))
    else:
        st.write("No matches recorded yet.")
