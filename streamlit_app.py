import streamlit as st
import pandas as pd
import os
from itertools import combinations

st.set_page_config(page_title="Tournament System", layout="wide")

# -------------------------------
# MODE CONTROL
# -------------------------------
params = st.query_params
mode = params.get("mode", "public")

if isinstance(mode, list):
    mode = mode[0]

IS_ADMIN = (mode == "admin")

st.title("🔐 Tournament Admin Panel" if IS_ADMIN else "May Day Scores")

# -------------------------------
# TEAMS PER TOURNAMENT
# -------------------------------
TEAMS_BY_TOURNAMENT = {
    "Mixed Group 1": ["Republica", "Momin FC", "Tyne Sliders", "1in12"],
    "FLINTA Group 1": ["Republica", "Hyde Park", "FURD", "Rainbow Bastards"],
    # "Mixed Group 3": ["Team I", "Team J", "Team K", "Team L"],
    # "FLINTA Group 1": ["Team M", "Team N", "Team O", "Team P"],
    # "FLINTA Group 2": ["Team Q", "Team R", "Team S", "Team T"],
}

TOURNAMENTS = list(TEAMS_BY_TOURNAMENT.keys())

FILE = "tournament_data.csv"

# -------------------------------
# LOAD / SAVE (SAFE)
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
        if not st.session_state.data.empty and "id" in st.session_state.data.columns
        else 0
    )

# -------------------------------
# FIXTURES
# -------------------------------
# def fixtures(teams):
#     return list(combinations(teams, 2))

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

    # repeat for other groups...
}

# -------------------------------
# TABLE COMPUTATION (SAFE)
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
# GLOBAL ADMIN CONTROLS (IMPORTANT FIX)
# -------------------------------
if IS_ADMIN:
    st.markdown("## 🧨 Admin Controls")
    
    confirm = st.text_input(
        "Type RESET to clear all tournament data",
        key="reset_confirm_input"
    )
    
    if IS_ADMIN and confirm == "RESET":
    
        if st.button("Confirm Reset (this will delete everything)", key="final_reset_button"):
    
            st.session_state.data = pd.DataFrame(
                columns=["id", "tournament", "team1", "team2", "score1", "score2"]
            )
    
            save_data(st.session_state.data)
            st.session_state.match_id = 0
    
            st.success("All data has been reset.")
            st.rerun()
        
    # reset_clicked = st.button(
    #     "RESET ALL DATA (DANGER)",
    #     key="global_reset_button"
    # )

    # if reset_clicked:
    #     st.session_state.data = pd.DataFrame(
    #         columns=["id", "tournament", "team1", "team2", "score1", "score2"]
    #     )
    #     save_data(st.session_state.data)
    #     st.session_state.match_id = 0
    #     st.success("All data reset")
    #     st.rerun()

# -------------------------------
# TABS
# -------------------------------
tabs = st.tabs(TOURNAMENTS)

for i, tournament in enumerate(TOURNAMENTS):

    with tabs[i]:

        teams = TEAMS_BY_TOURNAMENT[tournament]

        st.subheader(f"🏆 {tournament}")

        df = st.session_state.data
        t_df = df[df["tournament"] == tournament]

        # -----------------------
        # FIXTURES
        # -----------------------
        st.markdown("### 📅 Fixtures")

        # fx = fixtures(teams)
        # played = set(zip(t_df["team1"], t_df["team2"])) if not t_df.empty else set()

        # st.dataframe(pd.DataFrame([
        #     {
        #         "Home": a,
        #         "Away": b,
        #         "Played": (a, b) in played or (b, a) in played
        #     }
        #     for a, b in fx
        # ]), use_container_width=True)

        

        
        schedule = FIXTURES_BY_TOURNAMENT[tournament]

        played = set(zip(t_df["team1"], t_df["team2"])) if not t_df.empty else set()
                
        def get_score(t1, t2, df):
                    match = df[
                        ((df["team1"] == t1) & (df["team2"] == t2)) |
                        ((df["team1"] == t2) & (df["team2"] == t1))
                    ]
                    if match.empty:
                        return ""
                    r = match.iloc[0]
                    return f'{int(r["score1"])} - {int(r["score2"])}'
                
                
        fixtures_df = pd.DataFrame([
                    {
                        "Time": m["time"],
                        "Home": m["team1"],
                        "Score": get_score(m["team1"], m["team2"], t_df),
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
        # ADMIN PANEL
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
                    existing = st.session_state.data[
                        (st.session_state.data["tournament"] == tournament) &
                        (
                            (
                                (st.session_state.data["team1"] == team1) &
                                (st.session_state.data["team2"] == team2)
                            ) |
                            (
                                (st.session_state.data["team1"] == team2) &
                                (st.session_state.data["team2"] == team1)
                            )
                        )
                    ]

                    if not existing.empty:
                        st.error("⚠️ This match already exists.")
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


        
        # -----------------------
        # TEAM-SPECIFIC FIXTURES
        # -----------------------
        st.markdown("### 🔎 Find Your Matches")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_team = st.selectbox(
                "Select your team",
                teams,
                key=f"{tournament}_team_lookup"
            )
        
        with col2:
            show_btn = st.button(
                "Show My Fixtures",
                key=f"{tournament}_show_team_btn"
            )
        
        if show_btn:
        
            schedule = FIXTURES_BY_TOURNAMENT.get(tournament, [])
        
            team_matches = []
        
            for m in schedule:
                if m["Home"] == selected_team or m["Away"] == selected_team:
        
                    opponent = m["Away"] if m["Home"] == selected_team else m["Home"]
                    home_away = "vs" if m["Home"] == selected_team else "@"
        
                    team_matches.append({
                        "Time": m["time"],
                        "Match": f"{selected_team} {home_away} {opponent}"
                    })
        
            if team_matches:
                st.success(f"Fixtures for {selected_team}")
        
                st.dataframe(
                    pd.DataFrame(team_matches),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No fixtures found.")



        # -----------------------
        # MATCH RESULTS SUMMARY (PUBLIC)
        # -----------------------
        # if not IS_ADMIN:
        #     st.markdown("### 📝 Match Results")

        #     if not t_df.empty:

        #         results_df = t_df.copy()

        #         results_df["Result"] = results_df.apply(
        #             lambda r: f'{r["team1"]} {int(r["score1"])} - {int(r["score2"])} {r["team2"]}',
        #             axis=1
        #         )

        #         # Optional: sort by most recent match (highest ID first)
        #         results_df = results_df.sort_values("id", ascending=False)

        #         st.dataframe(
        #             results_df[["Result"]],
        #             use_container_width=True,
        #             hide_index=True
        #         )

        #     else:
        #         st.info("No match results yet.")



            # -----------------------
            # EDIT MATCH
            # -----------------------
            st.markdown("### ✏️ Edit Match")

            if not t_df.empty:

                labels = t_df.apply(
                    lambda r: f'ID {r["id"]}: {r["team1"]} {r["score1"]}-{r["score2"]} {r["team2"]}',
                    axis=1
                ).tolist()

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
