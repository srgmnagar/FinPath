import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Retention | FinPath", layout="wide")

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


df = pd.read_csv('data/cohort_retention.csv')

st.title("Retention — Cohort Analysis")
st.caption("Weekly retention rates across signup cohorts throughout 2024.")
st.divider()

# ── Row 1: Key Metrics ────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cohorts",    f"{df['cohort_week'].nunique()}")
col2.metric("Avg Week 0",       f"{df['pct_w0'].mean():.1f}%")
col3.metric("Avg Week 1",       f"{df['pct_w1'].mean():.1f}%")
col4.metric("Avg Week 12",      f"{df['pct_w12'].mean():.1f}%")

st.write("")

# ── Row 2: Heatmap (left) + Retention Curve (right) ──────────
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("Cohort Retention Heatmap")

    pct_cols   = ['pct_w0', 'pct_w1', 'pct_w2', 'pct_w4', 'pct_w8', 'pct_w12']
    week_labels = ['Week 0', 'Week 1', 'Week 2', 'Week 4', 'Week 8', 'Week 12']

    z = df[pct_cols].values
    y = df['cohort_week'].astype(str).tolist()

    fig_heat = go.Figure(go.Heatmap(
        z=z,
        x=week_labels,
        y=y,
        colorscale='Blues',
        text=np.round(z, 1),
        texttemplate='%{text}%',
        showscale=True,
        colorbar=dict(title='%')
    ))
    fig_heat.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title='Cohort Week', autorange='reversed')
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col_r:
    st.subheader("Average Retention Curve")

    avg_retention = df[pct_cols].mean().values
    fig_curve = go.Figure(go.Scatter(
        x=week_labels,
        y=avg_retention,
        mode='lines+markers',
        line=dict(color='#2196F3', width=3),
        marker=dict(size=8, color='#2196F3'),
        fill='tozeroy',
        fillcolor='rgba(33,150,243,0.15)'
    ))
    fig_curve.update_layout(
        height=320,
        yaxis_title='Avg Retention (%)',
        yaxis_range=[0, 110],
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_curve, use_container_width=True)


st.info(
    "Retention drops 62% from Week 0 to Week 1 — the sharpest fall in the cohort lifecycle. "
    "By Week 8 it stabilises at ~2%, indicating a loyal core user base. "
    "Early activation interventions (within the first 7 days) would have the highest retention impact."
)