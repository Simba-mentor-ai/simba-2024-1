import streamlit as st
import pandas as pd
import sqlalchemy

url = st.secrets["MARIADBURL"]
engine = sqlalchemy.create_engine(url+"traces")

def loadDashboard(activity_id):
    st.write(activity_id)