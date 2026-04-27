import streamlit as st
import pandas as pd
import os
from itertools import combinations

st.set_page_config(page_title="MAY DAY 2026", layout="wide")

# -------------------------------
# MODE CONTROL
# -------------------------------
params = st.query_params
mode = params.get("mode", "public")

if isinstance(mode, list):
    mode = mode[0]

IS_ADMIN = (mode == "admin")

st.title("MAY DAY 2026 (ADMIN)" if IS_ADMIN else "🏟️ MAY DAY 2026")

# -------------------------------
# TEAMS PER TOURNAMENT
# -------------------------------
TEAMS_BY_TOURNAMENT = {
    "Mixed Group 1": ["Republica 1", "Momin FC", "Tyne Sliders", "1in12"],
    "Mixed Group 2": ["Republica 2", "Mount Pleasant", "Suma", "BBBC"],
    "Mixed Group 3": ["Republica 3", "Republica 4", "Hadjuk Splint", "YSP"],
    "FLINTA Group 1": ["Republica", "Rainbow Bastards", "Hyde Park", "Cows 1", "Glasgow Pride"],
    "FLINTA Group 2": ["Cows 2", "FURD", "Cathkin Blazes", "DIY", "Bradford Baddies"],
}

TOURNAMENTS = list(TEAMS_BY_TOURNAMENT.keys())

FILE = "tournament_data.csv"

# -------------------------------
# LOAD / SAVE (SAFE)
# -------------------------------
def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)

        # Ensure correct types
        for col in ["score1", "score2"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        return df

    return pd.DataFrame(columns=["tournament", "team1", "team2", "score1", "score2"])


def save_data(df):
    df.to_csv(FILE, index=False)


if "data" not in st.session_state:
    st.session_state.data = load_data()

# -------------------------------
# FIXTURES
# -------------------------------
def fixtures(teams):
    return list(combinations(teams, 2))

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

        # 🔥 SAFETY CHECK (prevents KeyError)
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

        st.subheader(f"🏆 {tournament}")

        df = st.session_state.data
        t_df = df[df["tournament"] == tournament]

        # -----------------------
        # FIXTURES
        # -----------------------
        st.markdown("### 📅 Fixtures")

        fx = fixtures(teams)

        played = set(zip(t_df["team1"], t_df["team2"])) if not t_df.empty else set()

        st.dataframe(pd.DataFrame([
            {
                "Home": a,
                "Away": b,
                "Played": (a, b) in played or (b, a) in played
            }
            for a, b in fx
        ]), use_container_width=True)

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
                    st.session_state.data = pd.concat([
                        st.session_state.data,
                        pd.DataFrame([{
                            "tournament": tournament,
                            "team1": team1,
                            "team2": team2,
                            "score1": score1,
                            "score2": score2
                        }])
                    ], ignore_index=True)

                    save_data(st.session_state.data)
                    st.rerun()
