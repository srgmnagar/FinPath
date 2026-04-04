# dashboard/app.py
import streamlit as st

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

st.set_page_config(
    page_title="FinPath Analytics",
    page_icon="📈",
    layout="wide"
)

st.title("📈 FinPath Analytics Dashboard")
st.write("Use the sidebar to navigate between pages.")