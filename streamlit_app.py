```python
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Tournament System", layout="wide")

# -------------------------------
# MODE CONTROL
# -------------------------------
params = st.query_params
mode = params.get("mode", "public")

if isinstance(mode, list):
    mode = mode[0]

IS_ADMIN = (mode == "admin")

st.title("🔐 Admin" if IS_ADMIN else "May Day Scores")

# -------------------------------
# TEAMS PER TOURNAMENT
# -------------------------------
TEAMS_BY_TOURNAMENT = {
    "Mixed Group 1": ["Republica", "Momin FC", "Tyne Sliders", "1in12"],
    "FLINTA Group 1": ["Republica", "Hyde Park", "FURD", "Rainbow Bastards"],
}

TOURNAMENTS = list(TEAMS_BY_TOURNAMENT.keys())

FILE = "tournament_data.csv"

# -------------------------------
# LOAD / SAVE
# -------------------------------
def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)

        for col in ["score1", "score2"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        if "id" not in df.columns:
            df["id"] = range(1, len(df) + 1)

        return df

    return pd.DataFrame(columns=["id", "tournament", "team1", "team2", "score1", "score2"])


def save_data(df):
    df.to_csv(FILE, index=False)


if "data" not in st.session_state:
    st.session_state.data = load_data()

if "match_id" not in st.session_state:
    st.session_state.match_id = (
        int(st.session_state.data["id"].max())
        if not st.session_state.data.empty else 0
    )

# -------------------------------
# FIXTURES
# -------------------------------
FIXTURES_BY_TOURNAMENT = {
    "Mixed Group 1": [
        {"time": "10:00", "team1": "Republica", "team2": "Momin FC"},
        {"time": "10:20", "team1": "Tyne Sliders", "team2": "1in12"},
        {"time": "10:40", "team1": "Republica", "team2": "Tyne Sliders"},
        {"time": "11:00", "team1": "Momin FC", "team2": "1in12"},
        {"time": "11:20", "team1": "Republica", "team2": "1in12"},
        {"time": "11:40", "team1": "Momin FC", "team2": "Tyne Sliders"},
    ],
    "FLINTA Group 1": [
        {"time": "10:00", "team1": "Republica", "team2": "FURD"},
        {"time": "10:20", "team1": "Hyde Park", "team2": "Rainbow Bastards"},
        {"time": "10:40", "team1": "Republica", "team2": "Hyde Park"},
        {"time": "11:00", "team1": "FURD", "team2": "Rainbow Bastards"},
        {"time": "11:20", "team1": "Republica", "team2": "Rainbow Bastards"},
        {"time": "11:40", "team1": "FURD", "team2": "Hyde Park"},
    ],
}

# -------------------------------
# TABLE COMPUTATION
# -------------------------------
def compute_table(df, teams):
    table = pd.DataFrame(index=teams, columns=[
        "P", "W", "D", "L", "GF", "GA", "GD", "Pts"
    ]).fillna(0).astype(int)

    for _, m in df.iterrows():
        t1, t2 = m["team1"], m["team2"]
        s1, s2 = int(m["score1"]), int(m["score2"])

        if t1 not in table.index or t2 not in table.index:
            continue

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
    return table.sort_values(["Pts", "GD", "GF"], ascending=False)

# -------------------------------
# TABS
# -------------------------------
tabs = st.tabs(TOURNAMENTS)

for i, tournament in enumerate(TOURNAMENTS):

    with tabs[i]:

        teams = TEAMS_BY_TOURNAMENT[tournament]
        df = st.session_state.data
        t_df = df[df["tournament"] == tournament]

        st.subheader(f"🏆 {tournament}")

        # -----------------------
        # ADMIN (TOP)
        # -----------------------
        if IS_ADMIN:

            st.markdown("### 🔐 Enter Match Result")

            col1, col2 = st.columns(2)
            with col1:
                team1 = st.selectbox("Team 1", teams, key=f"{tournament}_t1")
            with col2:
                team2 = st.selectbox("Team 2", teams, key=f"{tournament}_t2")

            col3, col4 = st.columns(2)
            with col3:
                score1 = st.number_input("Score 1", min_value=0, step=1, key=f"{tournament}_s1")
            with col4:
                score2 = st.number_input("Score 2", min_value=0, step=1, key=f"{tournament}_s2")

            if st.button("Submit Result", key=f"{tournament}_btn"):
                if team1 == team2:
                    st.error("A team cannot play itself.")
                else:
                    st.session_state.match_id += 1

                    st.session_state.data = pd.concat([
                        st.session_state.data,
                        pd.DataFrame([{
                            "id": st.session_state.match_id,
                            "tournament": tournament,
                            "team1": team1,
                            "team2": team2,
                            "score1": score1,
                            "score2": score2
                        }])
                    ], ignore_index=True)

                    save_data(st.session_state.data)
                    st.success("Result saved!")
                    st.rerun()

            # EDIT
            if not t_df.empty:
                st.markdown("### ✏️ Edit Match")

                labels = t_df.apply(
                    lambda r: f'ID {r["id"]}: {r["team1"]} {r["score1"]}-{r["score2"]} {r["team2"]}',
                    axis=1
                )

                selected = st.selectbox("Select match", labels, key=f"{tournament}_edit")

                match_id = int(selected.split(":")[0].replace("ID", "").strip())
                row = t_df[t_df["id"] == match_id].iloc[0]

                new_s1 = st.number_input("New Score 1", value=int(row["score1"]), key=f"{tournament}_es1")
                new_s2 = st.number_input("New Score 2", value=int(row["score2"]), key=f"{tournament}_es2")

                if st.button("Update Match", key=f"{tournament}_update"):
                    idx = st.session_state.data[
                        st.session_state.data["id"] == match_id
                    ].index[0]

                    st.session_state.data.loc[idx, "score1"] = new_s1
                    st.session_state.data.loc[idx, "score2"] = new_s2

                    save_data(st.session_state.data)
                    st.success("Match updated!")
                    st.rerun()

        # -----------------------
        # FIXTURES
        # -----------------------
        st.markdown("### 📅 Fixtures")

        schedule = FIXTURES_BY_TOURNAMENT.get(tournament, [])

        def get_score(t1, t2):
            match = t_df[
                ((t_df["team1"] == t1) & (t_df["team2"] == t2)) |
                ((t_df["team1"] == t2) & (t_df["team2"] == t1))
            ]
            if match.empty:
                return ""
            r = match.iloc[0]
            return f'{int(r["score1"])} - {int(r["score2"])}'

        fixtures_df = pd.DataFrame([
            {
                "Time": m["time"],
                "Home": m["team1"],
                "Score": get_score(m["team1"], m["team2"]),
                "Away": m["team2"],
            }
            for m in schedule
        ])

        st.dataframe(fixtures_df, use_container_width=True, hide_index=True)

        # -----------------------
        # TABLE
        # -----------------------
        st.markdown("### 📊 League Table")

        if not t_df.empty:
            st.dataframe(compute_table(t_df, teams), use_container_width=True)
        else:
            st.info("No matches yet.")

        # -----------------------
        # TEAM LOOKUP (PUBLIC)
        # -----------------------
        if not IS_ADMIN:
            st.markdown("### 🔎 Find Your Matches")

            selected_team = st.selectbox("Select your team", teams, key=f"{tournament}_lookup")

            if st.button("Show My Fixtures", key=f"{tournament}_btn_lookup"):

                team_matches = []

                for m in schedule:
                    if m["team1"] == selected_team or m["team2"] == selected_team:

                        opponent = m["team2"] if m["team1"] == selected_team else m["team1"]

                        team_matches.append({
                            "Time": m["time"],
                            "Match": f"{selected_team} vs {opponent}"
                        })

                st.dataframe(pd.DataFrame(team_matches), use_container_width=True, hide_index=True)

# -------------------------------
# RESET (BOTTOM)
# -------------------------------
if IS_ADMIN:
    st.markdown("## 🧨 Reset scores")

    confirm = st.text_input("Type RESET to clear all data")

    if confirm == "RESET":
        if st.button("Confirm Reset"):
            st.session_state.data = pd.DataFrame(
                columns=["id", "tournament", "team1", "team2", "score1", "score2"]
            )
            save_data(st.session_state.data)
            st.session_state.match_id = 0
            st.success("All data reset")
            st.rerun()
```
