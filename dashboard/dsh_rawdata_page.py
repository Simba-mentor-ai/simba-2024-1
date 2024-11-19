import streamlit as st
from dashboard.feature_extractor import ConversationFeatureExtractor

def create_raw_data(df):
    st.write("### Raw Data")
    with st.expander("Show Raw Conversations"):
        st.write(df)
    with st.expander("Show Conversation Stats"):
        cfe = ConversationFeatureExtractor(df)
        user_stats = cfe.extract_features().fillna(0)
        user_stats = user_stats\
            .loc[:, 
                ['user_id', 'total_turns', 'user_turns', 'model_turns', 'turn_ratio', 
                    'avg_response_time_seconds', 'total_conversation_duration_seconds', 'total_user_conversation_length', 
                    'avg_user_response_length', 'avg_model_response_length', 'median_user_response_length', 'median_model_response_length']]\
            .rename(columns={'total_turns': 'Total Turns', 'user_turns': 'User Turns', 'model_turns': 'Model Turns', 
                            'turn_ratio': 'Turn Ratio', 'avg_response_time_seconds': 'Avg Response Time (s)', 
                            'total_conversation_duration_seconds': 'Total Duration (s)', 'total_user_conversation_length': 'Total Conversation Length', 
                            'avg_user_response_length': 'Avg User Response Length', 'avg_model_response_length': 'Avg Model Response Length', 
                            'median_user_response_length': 'Median User Response Length', 'median_model_response_length': 'Median Model Response Length'})

        st.write(user_stats)
