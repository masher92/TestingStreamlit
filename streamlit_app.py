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
import os

st.set_page_config(page_title="May Day 2026", layout="wide")

st.title("⚽ May Day 2026")

# -------------------------------
# Teams (placeholder for ALL groups)
# -------------------------------
TEAMS = ["Republica", "Momin FC", "Tyne Sliders", "1in12"]

# -------------------------------
# Tournaments
# -------------------------------
TOURNAMENTS = [
    "Mixed Group 1",
    "Mixed Group 2",
    "Mixed Group 3",
    "FLINTA Group 1",
    "FLINTA Group 2"
]

DATA_FILE = "matches_all_tournaments.csv"

# -------------------------------
# Load / Save
# -------------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["tournament", "team1", "team2", "score1", "score2"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# -------------------------------
# Init state
# -------------------------------
if "data" not in st.session_state:
    st.session_state.data = load_data()

# -------------------------------
# Compute table per tournament
# -------------------------------
def compute_table(df, teams):
    table = pd.DataFrame(index=teams, columns=[
        "P", "W", "D", "L", "GF", "GA", "GD", "Pts"
    ]).fillna(0).astype(int)

    for _, m in df.iterrows():
        t1, t2 = m["team1"], m["team2"]
        s1, s2 = int(m["score1"]), int(m["score2"])

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
# Tabs
# -------------------------------
tabs = st.tabs(TOURNAMENTS)

for i, tournament in enumerate(TOURNAMENTS):

    with tabs[i]:
        st.subheader(f"🏆 {tournament}")

        df = st.session_state.data
        t_data = df[df["tournament"] == tournament]

        # -----------------------
        # Input match
        # -----------------------
        st.markdown("### 📥 Add Match Result")

        col1, col2 = st.columns(2)

        with col1:
            team1 = st.selectbox("Team 1", TEAMS, key=f"{tournament}_t1")

        with col2:
            team2 = st.selectbox("Team 2", TEAMS, key=f"{tournament}_t2")

        col3, col4 = st.columns(2)

        with col3:
            score1 = st.number_input("Score Team 1", min_value=0, step=1, key=f"{tournament}_s1")

        with col4:
            score2 = st.number_input("Score Team 2", min_value=0, step=1, key=f"{tournament}_s2")

        if st.button("Submit Result", key=f"{tournament}_btn"):
            if team1 == team2:
                st.error("A team cannot play itself.")
            else:
                new_row = pd.DataFrame([{
                    "tournament": tournament,
                    "team1": team1,
                    "team2": team2,
                    "score1": score1,
                    "score2": score2
                }])

                st.session_state.data = pd.concat(
                    [st.session_state.data, new_row],
                    ignore_index=True
                )

                save_data(st.session_state.data)
                st.rerun()

        # -----------------------
        # Table
        # -----------------------
        st.markdown("### 📊 League Table")

        if not t_data.empty:
            table = compute_table(t_data, TEAMS)
            st.dataframe(table, use_container_width=True)
        else:
            st.info("No matches yet.")

        # -----------------------
        # History
        # -----------------------
        with st.expander("📜 Match History"):
            st.dataframe(t_data)
