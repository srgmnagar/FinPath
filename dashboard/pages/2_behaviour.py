# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go

# st.set_page_config(page_title="Behavior | FinPath", layout="wide")

# df_dep   = pd.read_csv('data/deposits.csv')
# df_rb    = pd.read_csv('data/risk_behavior.csv')
# df_panic = pd.read_csv('data/panic_sell.csv')

# COLORS = {'high': '#43A047', 'medium': '#FB8C00', 'low': '#E53935'}

# st.title("Behavior by Risk Profile")
# st.caption("How low, medium, and high risk users behave differently across deposits, investments, and engagement.")
# st.divider()

# # ── Row 1: 3 Metric Cards ─────────────────────────────────────
# col1, col2, col3 = st.columns(3)
# for col, (_, row) in zip([col1, col2, col3], df_rb.iterrows()):
#     col.metric(
#         f"{row['risk_profile'].title()} Risk — Avg Deposit",
#         f"₹{row['avg_deposit_amount_inr']:,.0f}",
#         f"Buy/Sell {row['buy_sell_ratio']}x"
#     )

# st.divider()

# # ── Row 2: Deposit Distribution (left) + Auto Invest (right) ──
# col_left, col_right = st.columns(2)

# with col_left:
#     st.subheader("Deposit Distribution")
#     fig_dep = go.Figure()
#     for _, row in df_dep.iterrows():
#         fig_dep.add_trace(go.Bar(
#             name=row['risk_profile'],
#             x=['P25', 'Median', 'P75', 'P90'],
#             y=[row['p25'], row['median'], row['p75'], row['p90']],
#             marker_color=COLORS.get(row['risk_profile'], '#999')
#         ))
#     fig_dep.update_layout(
#         barmode='group',
#         height=350,
#         yaxis_title='Amount (₹)',
#         legend_title='Risk Profile',
#         margin=dict(l=20, r=20, t=30, b=20)
#     )
#     st.plotly_chart(fig_dep, use_container_width=True)

# with col_right:
#     st.subheader("Auto-Invest Adoption")
#     fig_auto = go.Figure(go.Bar(
#         x=df_dep['risk_profile'],
#         y=df_dep['auto_invest_rate'],
#         marker_color=[COLORS.get(r, '#999') for r in df_dep['risk_profile']],
#         text=df_dep['auto_invest_rate'].apply(lambda x: f"{x}%"),
#         textposition='outside'
#     ))
#     fig_auto.update_layout(
#         height=350,
#         yaxis_title='% of Depositors',
#         margin=dict(l=20, r=20, t=30, b=20),
#         showlegend=False
#     )
#     st.plotly_chart(fig_auto, use_container_width=True)

# st.divider()

# # ── Row 3: Buy/Sell Ratio (left) + Panic Sell (right) ─────────
# col_left2, col_right2 = st.columns(2)

# with col_left2:
#     st.subheader("Buy / Sell Ratio")
#     fig_bs = go.Figure(go.Bar(
#         x=df_rb['risk_profile'],
#         y=df_rb['buy_sell_ratio'],
#         marker_color=[COLORS.get(r, '#999') for r in df_rb['risk_profile']],
#         text=df_rb['buy_sell_ratio'],
#         textposition='outside'
#     ))
#     fig_bs.update_layout(
#         height=350,
#         yaxis_title='Buy / Sell Ratio',
#         margin=dict(l=20, r=20, t=30, b=20),
#         showlegend=False
#     )
#     st.plotly_chart(fig_bs, use_container_width=True)

# with col_right2:
#     st.subheader("Panic Sell Rate")
#     fig_panic = go.Figure(go.Bar(
#         x=df_panic['risk_profile'],
#         y=df_panic['panic_sell_rate_pct'],
#         marker_color=[COLORS.get(r, '#999') for r in df_panic['risk_profile']],
#         text=df_panic['panic_sell_rate_pct'].apply(lambda x: f"{x}%"),
#         textposition='outside'
#     ))
#     fig_panic.update_layout(
#         height=350,
#         yaxis_title='% Who Panic Sold',
#         margin=dict(l=20, r=20, t=30, b=20),
#         showlegend=False
#     )
#     st.plotly_chart(fig_panic, use_container_width=True)

# st.divider()
# st.subheader("Key Insight")
# st.info(
#     "**High risk users are disproportionately valuable** — they deposit 32x more than low risk users, "
#     "panic sell at 1/3 the rate, and adopt auto-invest at 2.3x the rate. "
#     "Acquisition and retention efforts should be heavily weighted toward this segment."
# )

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Behavior | FinPath", layout="wide")

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
        }
    </style>
""", unsafe_allow_html=True)

df_dep   = pd.read_csv('data/deposits.csv')
df_rb    = pd.read_csv('data/risk_behavior.csv')
df_panic = pd.read_csv('data/panic_sell.csv')

COLORS = {'high': '#43A047', 'medium': '#FB8C00', 'low': '#E53935'}

# screen height for charts
CHART_H = 380

st.title("🧠 Behavior by Risk Profile")
st.caption("How low, medium, and high risk users behave differently across deposits, investments, and engagement.")
st.divider()

# ── Row 1: Metric Cards (untouched) ──────────────────────────
col1, col2, col3 = st.columns(3)
for col, (_, row) in zip([col1, col2, col3], df_rb.iterrows()):
    col.metric(
        f"{row['risk_profile'].title()} Risk",
        f"₹{row['avg_deposit_amount_inr']:,.0f}",
        f"Buy/Sell {row['buy_sell_ratio']}x"
    )

st.divider()

# ── Row 2: Deposit Distribution + Auto Invest ─────────────────
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("💰 Deposit Distribution")
    fig_dep = go.Figure()
    for _, row in df_dep.iterrows():
        fig_dep.add_trace(go.Bar(
            name=row['risk_profile'],
            x=['P25', 'Median', 'P75', 'P90'],
            y=[row['p25'], row['median'], row['p75'], row['p90']],
            marker_color=COLORS.get(row['risk_profile'], '#999')
        ))
    fig_dep.update_layout(
        barmode='group', height=CHART_H,
        yaxis_title='Amount (₹)',
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_dep, use_container_width=True)

with col_r:
    st.subheader("🤖 Auto-Invest Adoption")
    fig_auto = go.Figure(go.Bar(
        x=df_dep['risk_profile'],
        y=df_dep['auto_invest_rate'],
        marker_color=[COLORS.get(r, '#999') for r in df_dep['risk_profile']],
        text=df_dep['auto_invest_rate'].apply(lambda x: f"{x}%"),
        textposition='outside'
    ))
    fig_auto.update_layout(
        height=CHART_H, yaxis_title='% of Depositors',
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False, yaxis_range=[0, 80],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_auto, use_container_width=True)

st.divider()

# ── Row 3: Buy/Sell + Panic Sell ──────────────────────────────
col_l2, col_r2 = st.columns(2, gap="large")

with col_l2:
    st.subheader("📈 Buy / Sell Ratio")
    fig_bs = go.Figure(go.Bar(
        x=df_rb['risk_profile'],
        y=df_rb['buy_sell_ratio'],
        marker_color=[COLORS.get(r, '#999') for r in df_rb['risk_profile']],
        text=df_rb['buy_sell_ratio'],
        textposition='outside'
    ))
    fig_bs.update_layout(
        height=CHART_H, yaxis_title='Buy / Sell Ratio',
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_bs, use_container_width=True)

with col_r2:
    st.subheader("😱 Panic Sell Rate")
    fig_panic = go.Figure(go.Bar(
        x=df_panic['risk_profile'],
        y=df_panic['panic_sell_rate_pct'],
        marker_color=[COLORS.get(r, '#999') for r in df_panic['risk_profile']],
        text=df_panic['panic_sell_rate_pct'].apply(lambda x: f"{x}%"),
        textposition='outside'
    ))
    fig_panic.update_layout(
        height=CHART_H, yaxis_title='% Who Panic Sold',
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False, yaxis_range=[0, 70],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_panic, use_container_width=True)

st.divider()
st.info(
    "**High risk users are disproportionately valuable** — they deposit 32x more than low risk users, "
    "panic sell at 1/3 the rate, and adopt auto-invest at 2.3x the rate. "
    "Acquisition and retention efforts should be heavily weighted toward this segment."
)