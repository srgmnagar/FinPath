import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Overview | FinPath", layout="wide")

df = pd.read_csv('data/funnel.csv')

# ── Header ───────────────────────────────────────────────────
st.title("📈 FinPath — Overview")
st.caption("End-to-end funnel performance across 250,000 simulated users (2024)")



st.divider()

# ── Funnel Chart ─────────────────────────────────────────────
stages = [
    "Total Users",
    "Signup Completed",
    "Email Verified",
    "Onboarding Completed",
    "Risk Quiz Completed",
    "KYC Completed",
    "Deposit Completed",
    "Portfolio Created"
]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Users",       f"{df['total_users'].iloc[0]:,}")
col2.metric("Signup Completed",  f"{df['signup'].iloc[0]:,}")
col3.metric("Portfolio Created", f"{df['portfolio'].iloc[0]:,}")
col4.metric("End-to-End Rate",   f"{round(100 * df['portfolio'].iloc[0] / df['total_users'].iloc[0], 1)}%")

values = [
    int(df['total_users'].iloc[0]),
    int(df['signup'].iloc[0]),
    int(df['email'].iloc[0]),
    int(df['onboarding'].iloc[0]),
    int(df['risk_quiz'].iloc[0]),
    int(df['kyc'].iloc[0]),
    int(df['deposit'].iloc[0]),
    int(df['portfolio'].iloc[0])
]

fig = go.Figure(go.Funnel(
    y=stages,
    x=values,
    textinfo="value+percent previous",
    marker=dict(color=[
        "#1565C0", "#1976D2", "#1E88E5", "#42A5F5",
        "#EF5350", "#FF7043", "#FFA726", "#66BB6A"
    ]),
    connector=dict(line=dict(color="rgba(0,0,0,0.1)", width=1))
))

fig.update_layout(
    title="User Acquisition Funnel",
    height=520,
    margin=dict(l=20, r=20, t=50, b=20),
    font=dict(size=13)
)

st.plotly_chart(fig, use_container_width=True)

# ── Biggest Drop-off Callout ──────────────────────────────────
st.divider()
st.subheader("Key Insight")

onboarded = int(df['onboarding'].iloc[0])
quiz_done  = int(df['risk_quiz'].iloc[0])
drop_pct   = round(100 - (100 * quiz_done / onboarded), 1)

st.error(
    f"**Biggest drop-off:** Onboarding → Risk Quiz — "
    f"**{drop_pct}% of users abandon** at the risk quiz step "
    f"({onboarded:,} → {quiz_done:,} users). "
    f"Users fear answering the quiz 'wrong' and second-guess their risk tolerance."
)