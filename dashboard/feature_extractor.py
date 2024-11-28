import pandas as pd
import numpy as np
import re
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from typing import List

nltk.download('vader_lexicon')
nltk.download('punkt')

class ConversationFeatureExtractor:

    def __init__(self, 
                 data: pd.DataFrame, 
                 user_id_col: str = 'studentId'):
        self.data = data
        self.user_id_col = user_id_col
        # self.vectorizer     = CountVectorizer()
        # self.topic_modeler  = TfidfVectorizer(max_features=50)
        # self.stopwords      = set(nltk.corpus.stopwords.words('french'))
        self.stemmer        = nltk.stem.SnowballStemmer('french')
    
    def preprocess_timestamps(self):
        # Convert timestamps to datetime objects
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        # Sort by user_id and timestamp
        self.data.sort_values(by=[self.user_id_col, 'timestamp'], inplace=True)
        
    def preprocess_messages(self):
        # Preprocess messages (lowercase, remove special characters)
        self.data['clean_message'] = self.data['content'].apply(self._clean_text)

    def _clean_text(self, text):
        # Lowercase and remove special characters
        return re.sub(r'[^a-zA-Z0-9áéíóúñü¿¡? ]', '', text.lower())
    
    def _tokenize(self, text):
        stemmed_tokens = [self.stemmer.stem(t) for t in nltk.word_tokenize(text, language="french")]
        return stemmed_tokens
        # return nltk.word_tokenize(text, language="french")
    
    def _sentencize(self, text):
        return nltk.sent_tokenize(text, language="french")
    
    def _num_sentences(self, sents: list):
        return len(sents)
        
    def _num_tokens(self, tokens: list):
        return len(tokens)

    def _num_chars(self, text):
        return len(text)
    
    def _num_stopwords(self, tokens):
        return len([t for t in tokens if t in self.stopwords])

    def _avg_word_length(self, tokens):
        return np.mean([len(t) for t in tokens])
    
    def _avg_sent_length(self, sents):
        return np.mean([len(s) for s in sents])
    
    def median_word_length(self, tokens):
        return np.median([len(t) for t in tokens])
    
    def median_sent_length(self, sents):
        return np.median([len(s) for s in sents])
    
    def _vocab_size(self, tokens):
        return len(set(tokens))
    
    def _lexical_diversity(self, tokens):
        if len(tokens) == 0:
            return 0
        return len(set(tokens)) / len(tokens)
    
    def extract_textual_features(self, text: str, prefix: str = ''):
        # concat all messages in a conversation
        # text = ' '.join(messages)

        features = {}
        features[prefix+'tokens']          = self._tokenize(text)
        features[prefix+'sents']           = self._sentencize(text)
        features[prefix+'num_tokens']      = self._num_tokens(features[prefix+'tokens'])
        features[prefix+'num_sents']       = self._num_sentences(features[prefix+'sents'])
        features[prefix+'num_chars']       = self._num_chars(text)
        # features[prefix+'num_stopwords']   = self._num_stopwords(features[prefix+'tokens'])
        features[prefix+'vocab_size']      = self._vocab_size(features[prefix+'tokens'])
        features[prefix+'lexical_diversity'] = self._lexical_diversity(features[prefix+'tokens'])
        
        features[prefix+'avg_word_length'] = self._avg_word_length(features[prefix+'tokens'])
        features[prefix+'avg_sent_length'] = self._avg_sent_length(features[prefix+'sents'])
        features[prefix+'median_word_length'] = self.median_word_length(features[prefix+'tokens'])
        features[prefix+'median_sent_length'] = self.median_sent_length(features[prefix+'sents'])
            
        return features

    def extract_conversation_features(self, by_activity: bool = True):
        
        # Initialize an empty list to store aggregated conversation features
        aggregated_features = []

        # Group by user_id, activity_id, and course_id to extract features per conversation
        if by_activity:
            groupby_list = [self.user_id_col,  'activity_id']
            groupby_tuple = (self.user_id_col,  'activity_id')
        else:
            groupby_list = [self.user_id_col]
            groupby_tuple = (self.user_id_col)
        grouped = self.data.groupby(groupby_list)

        for groupby_tuple, group in grouped:
        # for (user_id), group in grouped:
            group = group.reset_index(drop=True)

            user_id = groupby_tuple[0]
            if by_activity:
                activity_id = groupby_tuple[1]

            # Calculate basic metrics for the entire conversation
            total_turns = len(group)
            user_turns  = len(group[group['role'] == 'user'])
            model_turns = len(group[group['role'] == 'model'])
            turn_ratio  = user_turns / model_turns if model_turns != 0 else np.nan

            # get the number of activities the student has engaged in, ie, have more than one message
            engagement = group.groupby('activity_id').size().reset_index(name='counts')
            num_activities = len(engagement[engagement['counts']>1])
            
            # Calculate response times between consecutive user and model messages
            response_times                      = group['timestamp'].diff().dt.total_seconds().fillna(0)
            # avg_response_time_seconds           = response_times[1:].mean() if len(response_times) > 1 else np.nan
            total_conversation_duration_seconds = response_times.sum()

            # Content-based features
            # Tokenize messages
            user_messages = group[group['role'] == 'user']['clean_message']
            textual_features = self.extract_textual_features(' '.join(user_messages.tolist()), prefix='user_')
            
            # extract average textual features for each activity
            # median_user_turns_per_activity = group.groupby('activity_id').size().median()
            # mean_user_chars_per_activity = group.groupby('activity_id')['user_num_chars'].mean()
            # mean_user_sents_per_activity = group.groupby('activity_id')['user_num_sents'].mean()

            features = {
                'user_id': user_id,

                'total_turns': total_turns,
                'user_turns': user_turns,
                'model_turns': model_turns,
                'turn_ratio': turn_ratio,
                'num_activities': num_activities,
                'total_conversation_duration_seconds': total_conversation_duration_seconds,
            }
            if by_activity:
                features['activity_id'] = activity_id
            features.update(textual_features)
            aggregated_features.append(features)
        
        # Convert aggregated features to DataFrame
        aggregated_df = pd.DataFrame(aggregated_features)
        return aggregated_df
