import streamlit as st
import pandas as pd
import logging
import gettext
import options

from authentication import authenticate, initSession

import plotly.figure_factory as ff
from dashboard.database_api_client import DataClient
from dashboard import dsh_students_page, dsh_rawdata_page, dsh_overview_page

_ = gettext.gettext

_ = options.translate(_)

if "authentication_status" not in st.session_state or st.session_state["authentication_status"]==False:
    authenticate()
else:
    initSession()
    if (st.session_state["UserRole"]=="teacher" or st.session_state["UserRole"]=="admin"):
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)

        # Use full width of the page
        # st.set_page_config(layout="wide")

        client = DataClient("https://simba.irit.fr")
        data = client.get_data("conversations")
        df   = pd.DataFrame(data)
        df['course_id'] = 'thermo-2024-1'
        logging.info(f'loaded data: {df.shape[0]} rows')

        if df.empty:
            st.write("No data available.")
            st.stop()
        
        classes = ['Greeting', 'Question', 'Answer', 'Feedback']
        # assign a random class to each message
        df['class'] = df['content'].apply(lambda x: classes[hash(x) % 4])


        with st.container():
            st.title("Student Interaction Dashboard")
            # Create two tabs
            tab1, tab2, tab3 = st.tabs(["Conversation Stats", "Student Stats", "Raw Data"])
            with tab1:
                overview = dsh_overview_page.ConversationStats(df)
                overview.create_overview()
            with tab2:
                dsh_students_page.create_student_stats(df)
            with tab3:
                dsh_rawdata_page.create_raw_data(df)
    else :
        st.write("You were not supposed to access this page, please go back.")

