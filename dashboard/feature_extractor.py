import pandas as pd
import numpy as np
import re
# from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from nltk.sentiment import SentimentIntensityAnalyzer
# from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
# from collections import Counter
import nltk

nltk.download('vader_lexicon')

class ConversationFeatureExtractor:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.vectorizer = CountVectorizer()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.topic_modeler = TfidfVectorizer(max_features=50)

        self.preprocess()
    
    def preprocess(self):
        # Convert timestamps to datetime objects
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])

        # Sort by course_id, activity_id, user_id and timestamp
        self.data.sort_values(by=['course_id', 'activity_id', 'user_id', 'timestamp'], inplace=True)

        # Preprocess messages (lowercase, remove special characters)
        self.data['clean_message'] = self.data['content'].apply(self._clean_text)
        
    def _clean_text(self, text):
        # Lowercase and remove special characters
        return re.sub(r'[^a-zA-Z0-9áéíóúñü¿¡? ]', '', text.lower())
    
    def _get_sentiment(self, message):
        # Use VADER to get the compound sentiment score
        sentiment = self.sentiment_analyzer.polarity_scores(message)
        return sentiment['compound']
    
    def extract_features(self):
        # Initialize an empty list to store aggregated conversation features
        aggregated_features = []

        # Group by user_id, activity_id, and course_id to extract features per conversation
        groupby_list = ['user_id']
        if 'activity_id' in self.data.columns:
            groupby_list.append('activity_id')
        if 'course_id' in self.data.columns:
            groupby_list.append('course_id')
        grouped = self.data.groupby(groupby_list)

        for (user_id, activity_id, course_id), group in grouped:
            group = group.reset_index(drop=True)

            # Calculate basic metrics for the entire conversation
            total_turns = len(group)
            user_turns  = len(group[group['role'] == 'user'])
            model_turns = len(group[group['role'] == 'model'])
            turn_ratio  = user_turns / model_turns if model_turns != 0 else np.nan
            
            # Calculate response times between consecutive user and model messages
            response_times = group['timestamp'].diff().dt.total_seconds().fillna(0)
            avg_response_time_seconds = response_times[1:].mean() if len(response_times) > 1 else np.nan
            total_conversation_duration_seconds = response_times.sum()

            # Calculate average response lengths
            avg_user_response_length    = group[group['role'] == 'user']['clean_message'].apply(lambda x: len(x.split())).mean()
            median_user_response_length = group[group['role'] == 'user']['clean_message'].apply(lambda x: len(x.split())).median()
            avg_model_response_length   = group[group['role'] == 'model']['clean_message'].apply(lambda x: len(x.split())).mean()
            median_model_response_length = group[group['role'] == 'model']['clean_message'].apply(lambda x: len(x.split())).median()
            # Calculate total conversation length in terms of words
            total_user_conversation_length = group[group['role'] == 'user']['clean_message'].apply(lambda x: len(x.split())).sum()

            # calculate the vocabulary size
            vocabulary_size = len(set(' '.join(group['clean_message']).split()))
            
            # message_sequence = self.label_messages(group)

            # Aggregate features into a dictionary
            features = {
                'user_id': user_id,
                'activity_id': activity_id,
                'course_id': course_id,
                'total_turns': total_turns,
                'user_turns': user_turns,
                'model_turns': model_turns,
                'turn_ratio': turn_ratio,
                'vocabulary_size': vocabulary_size,
                'avg_response_time_seconds': avg_response_time_seconds,
                'total_conversation_duration_seconds': total_conversation_duration_seconds,
                'total_user_conversation_length': total_user_conversation_length,
                'avg_user_response_length': avg_user_response_length,
                'avg_model_response_length': avg_model_response_length,
                'median_user_response_length': median_user_response_length,
                'median_model_response_length': median_model_response_length,
                # 'user_message_sequence': message_sequence,
            }

            # Append aggregated features to the list
            aggregated_features.append(features)
        
        # Convert aggregated features to DataFrame
        aggregated_df = pd.DataFrame(aggregated_features)
        return aggregated_df

    