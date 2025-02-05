import streamlit as st
import pandas as pd
import logging
import gettext
import options
import database_manager as dbm

from authentication import authenticate, initSession

import plotly.figure_factory as ff
import nltk
from dashboard.database_api_client import DataClient
from dashboard.feature_extractor import ConversationFeatureExtractor
from dashboard import dsh_students_page, dsh_rawdata_page, dsh_overview_page

logger = logging.getLogger(__name__)

nltk.download('vader_lexicon')
nltk.download('punkt')


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

        actIds = dbm.getActivitiesWorkshop(st.session_state["username"])
        client = DataClient("https://simba.irit.fr")
        logger.info(f'activities: {actIds}')
        
        data = client.get_data("conversations", activities=actIds)

        df = pd.DataFrame(data)
        df['course_id'] = df['activity_course'].apply(lambda x: hash(x) % 1000)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        df = df.loc[df["activity_id"].isin(actIds)]

        if df.empty:
            st.write("No data available.")
            st.stop()
        else:
            logger.info(f'loaded data: {df.shape[0]} rows')
            
        st.title("SIMBA Interactions Dashboard")
        
        courses = df["activity_course"].sort_values().unique().tolist()
        courses.insert(0,"All courses")

        course,activity = st.columns([0.5,0.5])
        with course :
            selectedCourse = st.selectbox("Course", courses, index=0)

        if selectedCourse != "All courses":
            activityNames = df.loc[df["activity_course"] == selectedCourse]["activity_name"].unique().tolist()
        else :
            activityNames = df["activity_name"].sort_values().unique().tolist()

        activityNames.insert(0,"All activities")
        with activity :
            selectedActivity = st.selectbox("Activity", activityNames, index=0)
        overviewDf = df

        if selectedCourse != "All courses":
            overviewDf = overviewDf.loc[overviewDf["activity_course"] == selectedCourse]
        if selectedActivity != "All activities":
            overviewDf = overviewDf.loc[overviewDf["activity_name"] == selectedActivity]

        cfe = ConversationFeatureExtractor(overviewDf, user_id_col='user_id')
        cfe.preprocess_messages()
        df_features = cfe.extract_conversation_features()

        with st.container():
            
            # Create two tabs
            tab1, tab2, tab3 = st.tabs(["Conversation Stats", "Student Stats", "Raw Data"])
            with tab1:
                overview = dsh_overview_page.ConversationStats(overviewDf, df_features)
                overview.create()
            with tab2:
                students_tab = dsh_students_page.StudentStatsTab(overviewDf, selectedActivity)
                students_tab.create()
            with tab3:
                raw_data = dsh_rawdata_page.RawDataTab(df, df_features)
                raw_data.create()
    else :
        st.write("You were not supposed to access this page, please go back.")

