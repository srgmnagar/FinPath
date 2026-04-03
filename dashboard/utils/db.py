import os
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("../backend/.env"))

@st.cache_resource
def get_engine():
    return create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}"
    )