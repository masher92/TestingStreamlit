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

st.set_page_config(page_title="Football Tournament Tracker", layout="wide")

st.title("⚽ Football Tournament Score Tracker")

# -------------------------------
# Initialize session state
# -------------------------------
if "teams" not in st.session_state:
    st.session_state.teams = []

if "matches" not in st.session_state:
    st.session_state.matches = []

# -------------------------------
# Add teams
# -------------------------------
st.sidebar.header("Add Team")
new_team = st.sidebar.text_input("Team name")

if st.sidebar.button("Add Team"):
    if new_team and new_team not in st.session_state.teams:
        st.session_state.teams.append(new_team)

st.sidebar.write("Teams:")
st.sidebar.write(st.session_state.teams)

# -------------------------------
# Record match
# -------------------------------
st.header("Record Match")

if len(st.session_state.teams) >= 2:
    col1, col2, col3 = st.columns(3)

    with col1:
        team1 = st.selectbox("Team 1", st.session_state.teams, key="team1")

    with col2:
        team2 = st.selectbox("Team 2", st.session_state.teams, key="team2")

    with col3:
        st.write("")

    score_col1, score_col2 = st.columns(2)

    with score_col1:
        score1 = st.number_input("Score Team 1", min_value=0, step=1)

    with score_col2:
        score2 = st.number_input("Score Team 2", min_value=0, step=1)

    if st.button("Submit Result"):
        if team1 != team2:
            st.session_state.matches.append({
                "team1": team1,
                "team2": team2,
                "score1": score1,
                "score2": score2
            })
        else:
            st.error("A team cannot play itself.")

# -------------------------------
# Build league table
# -------------------------------
def compute_table(teams, matches):
    table = pd.DataFrame({
        "Team": teams,
        "P": 0, "W": 0, "D": 0, "L": 0,
        "GF": 0, "GA": 0, "GD": 0, "Pts": 0
    })

    table.set_index("Team", inplace=True)

    for match in matches:
        t1, t2 = match["team1"], match["team2"]
        s1, s2 = match["score1"], match["score2"]

        # Played
        table.loc[t1, "P"] += 1
        table.loc[t2, "P"] += 1

        # Goals
        table.loc[t1, "GF"] += s1
        table.loc[t1, "GA"] += s2
        table.loc[t2, "GF"] += s2
        table.loc[t2, "GA"] += s1

        # Results
        if s1 > s2:
            table.loc[t1, "W"] += 1
            table.loc[t2, "L"] += 1
            table.loc[t1, "Pts"] += 3
        elif s1 < s2:
            table.loc[t2, "W"] += 1
            table.loc[t1, "L"] += 1
            table.loc[t2, "Pts"] += 3
        else:
            table.loc[t1, "D"] += 1
            table.loc[t2, "D"] += 1
            table.loc[t1, "Pts"] += 1
            table.loc[t2, "Pts"] += 1

    table["GD"] = table["GF"] - table["GA"]

    table = table.sort_values(
        by=["Pts", "GD", "GF"],
        ascending=[False, False, False]
    )

    return table

# -------------------------------
# Display table
# -------------------------------
st.header("🏆 League Table")

if st.session_state.teams:
    table = compute_table(st.session_state.teams, st.session_state.matches)
    st.dataframe(table, use_container_width=True)

# -------------------------------
# Match history
# -------------------------------
st.header("Match History")

if st.session_state.matches:
    st.write(pd.DataFrame(st.session_state.matches))
