import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Features | FinPath", layout="wide")

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 1rem; }
        [data-testid="stSidebar"] { min-width: 180px; max-width: 180px; }
        /* fix metric text visibility */
        [data-testid="stMetricLabel"] { color: #888 !important; font-size: 0.85rem; }
        [data-testid="stMetricValue"] { color: #fff !important; font-size: 1.6rem; font-weight: 700; }
        [data-testid="stMetricDelta"] { font-size: 0.8rem; }
        [data-testid="stMetric"] {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 16px;
            border: 1px solid #333;
            margin-top: 7px;
        }
        hr {
            margin: 5px 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

df_adopt = pd.read_csv('data/feature_adoption.csv')
df_lift  = pd.read_csv('data/feature_lift.csv')

st.title("Feature Adoption & Retention Impact")
st.caption("Which features are used most, and which ones correlate with deeper engagement.")
st.divider()

# ── Row 1: Metric Cards ───────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Chart Views",      f"{df_adopt['chart_views_pct'].iloc[0]}%")
col2.metric("Goals",            f"{df_adopt['goals_pct'].iloc[0]}%")
col3.metric("Auto-Invest",      f"{df_adopt['auto_invest_pct'].iloc[0]}%")
col4.metric("Report Download",  f"{df_adopt['report_download_pct'].iloc[0]}%")

st.write("")

# ── Row 2: Adoption Rate (left) + Session Lift (right) ────────
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("Feature Adoption Rate")

    features = ['chart_views_pct', 'goals_pct', 'report_download_pct',
                'auto_invest_pct', 'rebalance_pct', 'support_pct']
    labels   = ['Chart Views', 'Goals', 'Report Download',
                'Auto Invest', 'Rebalance', 'Support Chat']
    values   = [df_adopt[f].iloc[0] for f in features]
    colors   = ['#43A047' if v > 50 else '#2196F3' if v > 30 else '#FB8C00'
                for v in values]

    fig_adopt = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker_color=colors,
        text=[f"{v}%" for v in values],
        textposition='outside'
    ))
    fig_adopt.update_layout(
        height=320,
        xaxis_title='% of Depositors',
        xaxis_range=[0, 110],
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_adopt, use_container_width=True)

with col_r:
    st.subheader("Session Lift — Adopters vs Non-Adopters")

    fig_lift = go.Figure()
    fig_lift.add_trace(go.Bar(
        name='Adopters',
        x=df_lift['feature'],
        y=df_lift['adopter_avg_sessions'],
        marker_color='#2196F3'
    ))
    fig_lift.add_trace(go.Bar(
        name='Non-Adopters',
        x=df_lift['feature'],
        y=df_lift['non_adopter_avg_sessions'],
        marker_color='#90CAF9'
    ))
    fig_lift.update_layout(
        barmode='group',
        height=320,
        yaxis_title='Avg Sessions',
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_lift, use_container_width=True)

st.write("")

# ── Row 3: Lift % bar ─────────────────────────────────────────
st.subheader("Retention Lift by Feature (%)")
fig_liftpct = go.Figure(go.Bar(
    x=df_lift['feature'],
    y=df_lift['lift_pct'],
    marker_color=['#43A047' if v > 0 else '#E53935' for v in df_lift['lift_pct']],
    text=df_lift['lift_pct'].apply(lambda x: f"+{x}%" if x > 0 else f"{x}%"),
    textposition='outside'
))
fig_liftpct.update_layout(
    height=220,
    yaxis_title='Session Lift (%)',
    yaxis_range=[0, df_lift['lift_pct'].max() * 1.3],
    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_liftpct, use_container_width=True)

st.info(
    "Chart views show the strongest retention signal — users who view their performance chart "
    "have 76% more sessions than those who don't. Report downloads and rebalancing follow at ~50% lift. "
    "Getting users to view their chart early is the single highest-leverage activation moment in the product."
)