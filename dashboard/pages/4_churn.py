import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Churn | FinPath", layout="wide")

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

df = pd.read_csv('data/churn.csv')

COLORS = {'high': '#43A047', 'medium': '#FB8C00', 'low': '#E53935'}

st.title("Churn Analysis")
st.caption("Hard churn, soft churn and healthy user breakdown by risk profile.")
st.divider()

# ── Row 1: Metric Cards ───────────────────────────────────────
col1, col2, col3 = st.columns(3)
for col, (_, row) in zip([col1, col2, col3], df.iterrows()):
    col.metric(
        f"{row['risk_profile'].title()} Risk — Hard Churn",
        f"{row['hard_churn_pct']}%",
        f"Healthy: {row['healthy_pct']}%"
    )

st.write("")

# ── Row 2: Churn Breakdown (left) + Healthy vs Churned (right) 
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("Churn Breakdown by Risk Profile")
    fig_stack = go.Figure()
    fig_stack.add_trace(go.Bar(
        name='Healthy',
        x=df['risk_profile'],
        y=df['healthy_users'],
        marker_color='#43A047'
    ))
    fig_stack.add_trace(go.Bar(
        name='Soft Churned',
        x=df['risk_profile'],
        y=df['soft_churned'],
        marker_color='#FB8C00'
    ))
    fig_stack.add_trace(go.Bar(
        name='Hard Churned',
        x=df['risk_profile'],
        y=df['hard_churned'],
        marker_color='#E53935'
    ))
    fig_stack.add_trace(go.Bar(
        name='Portfolio Closed',
        x=df['risk_profile'],
        y=df['portfolio_closed_only'],
        marker_color='#EF9A9A'
    ))
    fig_stack.update_layout(
        barmode='stack',
        height=320,
        yaxis_title='Users',
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_stack, use_container_width=True)

with col_r:
    st.subheader("Hard Churn Rate by Risk Profile")
    fig_churn = go.Figure(go.Bar(
        x=df['risk_profile'],
        y=df['hard_churn_pct'],
        marker_color=[COLORS.get(r, '#999') for r in df['risk_profile']],
        text=df['hard_churn_pct'].apply(lambda x: f"{x}%"),
        textposition='outside'
    ))
    fig_churn.update_layout(
        height=320,
        yaxis_title='Hard Churn Rate (%)',
        yaxis_range=[0, df['hard_churn_pct'].max() * 1.3],
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_churn, use_container_width=True)

st.write("")

# ── Row 3: Healthy % comparison ───────────────────────────────
st.subheader("Healthy User Rate by Risk Profile")
fig_healthy = go.Figure(go.Bar(
    x=df['risk_profile'],
    y=df['healthy_pct'],
    marker_color=[COLORS.get(r, '#999') for r in df['risk_profile']],
    text=df['healthy_pct'].apply(lambda x: f"{x}%"),
    textposition='outside'
))
fig_healthy.update_layout(
    height=270,
    yaxis_title='Healthy Users (%)',
    yaxis_range=[0, 115],
    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_healthy, use_container_width=True)

st.info(
    "Hard churn follows a clear risk gradient — low risk users churn at 6.5%, "
    "medium at 3.6%, high at just 1.4%. High risk users are the most loyal segment. "
    "Soft churn and portfolio closures represent recoverable users — "
    "targeted re-engagement campaigns would be highest ROI for the low risk segment."
)