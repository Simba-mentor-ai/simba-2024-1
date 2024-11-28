#######################
# Import libraries
import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd

import streamlit as st
from streamlit_echarts import st_echarts
from openai import OpenAI

openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Create a class for the Student Stats tab
class StudentStatsTab():
    def __init__(self, df, user_stats: pd.DataFrame = None):
        self.df = df
        if user_stats is None:
            cfe = ConversationFeatureExtractor(df, user_id_col='user_id')
            cfe.preprocess_messages()
            self.user_stats = cfe.extract_conversation_features().fillna(0)
        else:
            self.user_stats = user_stats
    
        self.filtered_df = None
        self.student_filter = None
        self.tab2_activity_filter = '--all--'

    def create(self):
        # 1st Row - Filter by activity_id
        self.filtered_df = self.create_filter()

        # 2nd Row - Histograms
        self.get_histograms()

        # 3rd Row - Student Conversation
        self.get_conversations()
            
    def create_filter(self):
        col1, col2 = st.columns(2)
        with col1:
            self.student_filter = st.selectbox("Select Student ID", self.df['user_id'].sort_values().unique())
        with col2:
            activity_ids = self.df.loc[self.df['user_id'] == self.student_filter, 'activity_id'].sort_values().unique()
            activity_ids = ['All Activities'] + list(activity_ids)
            self.tab2_activity_filter = st.selectbox("Select Activity ID", 
                                                activity_ids, 
                                                key='tab2_activity_filter')
        
        filtered_df = self.df[self.df['user_id'] == self.student_filter]
        if self.tab2_activity_filter != 'All Activities':
            filtered_df = filtered_df[filtered_df['activity_id'] == self.tab2_activity_filter]
            
        return filtered_df

    def get_histograms(self):
        cols = st.columns(3)
        with cols[0]:
            # Number of activities the student interacted with
            num_activities = len(self.filtered_df['activity_id'].unique())
            st.metric("Number of Activities", num_activities)

            # Number of messages the student sent
            num_messages = len(self.filtered_df)
            st.metric("Number of Messages", num_messages)

            # Conversation length
            conversation_length = self.filtered_df['content'].str.len().sum()
            st.metric("Conversation Length", conversation_length)

            # Mean messages per activity
            mean_messages_per_activity = self.user_stats['mean_user_turns_per_activity'].mean()
            st.metric("Mean Messages per Activity", mean_messages_per_activity)


        with cols[1]:
            # Create character distribution plot
            self.create_user_distribution_plot(self.df, self.filtered_df, metric='chars')
            
            # Create message count distribution plot 
            self.create_user_distribution_plot(self.df, self.filtered_df, metric='messages')

            # # Create mean messages per activity distribution plot
            # self.create_user_distribution_plot(self.df, self.filtered_df, metric='mean_messages_per_activity')
        with cols[2]:
            st.write("#### Activity Engagement")

    def create_user_distribution_plot(self, df, filtered_df, metric='chars'):
        if metric == 'chars':
            # Distribution of characters per user
            user_values = df[df['role'] == 'user'].groupby('user_id')['content'].apply(lambda x: x.str.len().sum()).values
            selected_user_value = filtered_df[filtered_df['role'] == 'user']['content'].str.len().sum()
            title = "Message Length"
        elif metric == 'messages':
            # Distribution of number of messages per user
            user_values = df[df['role'] == 'user'].groupby('user_id').size().values
            selected_user_value = filtered_df[filtered_df['role'] == 'user'].shape[0]
            title = "Number of Messages"
        else:
            # Distribution of mean messages per activity
            user_values = df[df['role'] == 'user'].groupby('user_id').apply(lambda x: len(x)/x['activity_id'].nunique().max()).values
            selected_user_value = len(filtered_df[filtered_df['role'] == 'user'])/filtered_df['activity_id'].nunique().max()
            title = "Mean Messages per Activity"

        fig = ff.create_distplot(
            [user_values],
            [''],
            show_hist=False,
            show_rug=False,
            show_curve=True,
            bin_size=200 if metric == 'chars' else 5
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis={'visible': False},
            yaxis={'visible': False},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=80
        )
        fig.update_traces(fill='tonexty', fillcolor='rgba(0,0,255,0.2)')
        
        fig.add_vline(x=selected_user_value, line_dash="dash", line_color="red")
        
        st.write(f"{title}")
        st.plotly_chart(fig, use_container_width=True)
    

    def get_conversations(self):
        # user conversation
        cols = st.columns(2)
        with cols[0]:
            st.write("### User Conversation")
            if self.tab2_activity_filter == '--all--':
                st.write("Please select an activity to view the conversation")
            else:
                with st.container(height=500):
                    for index, row in self.filtered_df.iterrows():
                        if row['role'] == 'user':
                            st.markdown(
                            f"<div style='float: right; text-align: left; background-color: #DAF7A6; border-radius: 10px; padding: 10px; margin: 5px 0; width: 75%;'><b>Student:</b>{row['content']}</div>", 
                            unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                            f"<div style='float: left; background-color: #aed6f1; border-radius: 10px; padding: 10px; margin: 5px 0; width: 75%;'><b>SIMBA:</b> {row['content']}</div>", 
                            unsafe_allow_html=True
                            )
        with cols[1]:
            st.write("#### Message Summary")
            st.button("Generate!")

            st.write("#### Summary")
            st.write("...")

            st.write("#### Feedback")
            st.write("...")
            
