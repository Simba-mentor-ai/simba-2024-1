import streamlit as st
import pandas as pd
from dashboard.feature_extractor import ConversationFeatureExtractor
import logging

logger = logging.getLogger(__name__)

class RawDataTab():
    
    def __init__(self, df: pd.DataFrame, user_stats: pd.DataFrame = None):
        self.df = df
        if user_stats is None:
            cfe = ConversationFeatureExtractor(df, user_id_col='user_id')
            cfe.preprocess_messages()
            self.user_stats = cfe.extract_conversation_features().fillna(0)
        else:
            self.user_stats = user_stats

    def create(self):
        st.write("### Raw Data")
        with st.expander("Show Raw Conversations"):
            st.write(self.df)
        with st.expander("Show Conversation Stats"):
            logger.info(f'user_stats: {self.user_stats.columns}')
            user_stats = self.user_stats\
                .loc[:, 
                   ['user_id', 'total_turns', 'user_turns', 'model_turns', 'turn_ratio',
                    'num_activities', 'total_conversation_duration_seconds', 'activity_id',
                    'user_num_tokens', 'user_num_sents',
                    'user_num_chars', 'user_vocab_size', 'user_lexical_diversity',
                    'user_avg_word_length', 'user_avg_sent_length',
                    'user_median_word_length', 'user_median_sent_length',
                    'mean_user_turns_per_activity', 'mean_user_num_tokens_per_activity',
                    'mean_user_num_sents_per_activity', 'mean_user_num_chars_per_activity']]\
                .rename(columns={'total_turns': 'Total Turns', 'user_turns': 'User Turns', 'model_turns': 'Model Turns', 
                                'turn_ratio': 'Turn Ratio', 
                                'total_conversation_duration_seconds': 'Total Duration (s)', 
                                'avg_model_response_length': 'Avg Model Response Length'})

            st.write(user_stats)
