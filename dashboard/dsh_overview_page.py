#######################
# Import libraries
import altair as alt
import pandas as pd
import streamlit as st

import logging

# from dashboard import cluster_students
from dashboard.feature_extractor import ConversationFeatureExtractor
from scipy.stats import zscore
from streamlit_echarts import st_echarts
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle


logger = logging.getLogger(__name__)
class ConversationStats():

    def __init__(self, df: pd.DataFrame, user_stats: pd.DataFrame = None):
        self.df = df
        self.all_students = df.loc[:, ['user_id', 'email']]\
            .drop_duplicates(subset='user_id')\
            .reset_index(drop=True)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        if user_stats is None:
            cfe = ConversationFeatureExtractor(self.df, user_id_col='user_id')
            cfe.preprocess_messages()
            self.user_stats = cfe.extract_conversation_features().fillna(0)
        else:
            self.user_stats = user_stats

        num_activities = self.user_stats.num_activities.max()

        self.user_stats['mean_user_turns_per_activity']       = self.user_stats['user_turns'] / num_activities
        self.user_stats['mean_user_num_tokens_per_activity']  = self.user_stats['user_num_tokens'] / num_activities
        self.user_stats['mean_user_num_sents_per_activity']   = self.user_stats['user_num_sents'] / num_activities
        self.user_stats['mean_user_num_chars_per_activity']   = self.user_stats['user_num_chars'] / num_activities

    def get_top_students(self, n:int = 5):
        return self.user_stats\
            .drop_duplicates(subset='user_id')\
            .merge(self.all_students, on='user_id', how='left')\
            .loc[:, ['user_id', 'email', 'mean_user_turns_per_activity']]
            # .nlargest(n, 'mean_user_turns_per_activity')

    def get_no_messages_students(self):
        # Obter contagem de mensagens por usuário
        users_with_messages = self.user_stats[self.user_stats['user_turns'] > 0]
        
        #return students with no messages
        return self.all_students[~self.all_students['user_id'].isin(users_with_messages['user_id'])]
        

    def create(self):

        # 1st row - Overall statistics
        with st.container():
            self.get_overall_stats()

        # 2nd row - Top 25%, Bottom 25%, and suggested chart
        with st.container():

            col1, col2 = st.columns(2)
            with col1:
                top_students = self.get_top_students()
                top_students.rename(columns={
                    'user_id': 'Student ID', 
                    'mean_user_turns_per_activity': 'Average Messages per Activity',
                    'email': 'Email'
                }, inplace=True)
                top_students.reset_index(inplace=True, drop=True)
                top_students['Rank'] = top_students.index + 1
                top_students = top_students.loc[:, ['Rank', 'Student ID', 'Email', 'Average Messages per Activity']]
                st.write(f"#### Top {len(top_students)} Students (Longest Conversations) :clap:")
                st.dataframe(top_students.sort_values(by='Average Messages per Activity', ascending=False), height=250, hide_index=True, use_container_width=True)

            with col2:
                self.get_activity_stats()
                # no_messages_students = self.get_no_messages_students()
                # st.write(f"#### Students with no messages :bangbang:")
                # st.dataframe(no_messages_students, height=250, hide_index=True, use_container_width=True)

        #     self.get_conversation_stats()

        # with st.container():
        #     self.get_activity_stats()

        # 3rd row - Conversation grid and tree
        with st.container():
            # col1, col2 = st.columns(2)
            # with col1:
            #     # self.get_conversation_tree()
            #     # self.get_activity_graph()
            #     self.get_activity_stats()

            # with col2:
            self.get_conversation_grid()

    def get_activity_stats(self):
        # plot a bar chart of the number of messages per activity and the total conversation length, ordered by the date of the first message
        st.write("### Activity Statistics")
                
        # Calculate activity stats and merge with timestamps
        activity_stats = self.user_stats\
            .loc[:, ['activity_id', 'user_turns', 'mean_user_num_chars_per_activity']]\
            .groupby('activity_id')\
            .agg(total_student_messages=('user_turns', 'sum'),
                 mean_num_chars=('mean_user_num_chars_per_activity', 'mean'))
        
        # merge with activity names
        activity_stats = activity_stats.merge(self.df.loc[:, ['activity_id', 'activity_name']].drop_duplicates(), on='activity_id', how='left')
        
        # Set activity_name as index for x-axis labels
        activity_stats = activity_stats.set_index('activity_name')
        activity_stats.drop(columns=['activity_id'], inplace=True)
        
        st.bar_chart(activity_stats)


    # def get_conversation_stats(self):
    #     # 2nd Row - Top 25%, Bottom 25%, and suggested chart
    #     st.write("### Conversation Statistics")

    #     col1, col2, col3 = st.columns(3)

    #     with col1:
    #         # Top 5 students by message length
    #         top_5 = self.get_top_students()
    #         col1.dataframe(top_5, height=250, hide_index=True, use_container_width=True)
            
    #     with col2:
    #         # student with no messages
    #         no_messages = self.get_no_messages_students()
    #         col2.write("Students with no messages :bangbang:")
    #         col2.dataframe(no_messages, height=250, hide_index=True, use_container_width=True)   
        
    #     with col3:    
            # self.get_activity_stats()


    def get_overall_stats(self):
        total_students = self.df['user_id'].nunique()
        total_activities = self.df['activity_id'].nunique()
        total_user_turns = self.df[self.df['role'] == 'user'].shape[0]
        total_model_turns = self.df[self.df['role'] == 'model'].shape[0]
        median_user_response_length = self.df[self.df['role'] == 'user']['content'].str.len().median()
        median_model_response_length = self.df[self.df['role'] == 'model']['content'].str.len().median()
        average_conversation_duration = self.df.groupby('user_id')['timestamp'].apply(lambda x: x.max() - x.min()).mean()
        average_conversation_duration = average_conversation_duration.total_seconds() / total_students

        # Display metrics
        col1, col2, col3, col4, col5, col6,  = st.columns(6)
        col1.metric("Total Students", total_students)
        col2.metric("Total Activities", total_activities)
        col3.metric("Total Number of \n\nStudents Messages", total_user_turns)
        # col4.metric("Total SIMBA Messages", total_model_turns)
        col4.metric("Median Number of \n\nCharacters in Student \n\nMessages", median_user_response_length)
        col5.metric("Median Number of \n\nCharacters in SIMBA \n\nMessages", median_model_response_length)
        average_conversation_duration_hours     = average_conversation_duration // 3600
        average_conversation_duration_minutes   = (average_conversation_duration % 3600) // 60
        col6.metric("Avg. time spent \n\nin conversations \n\nper student", f"{int(average_conversation_duration_hours)}h {int(average_conversation_duration_minutes)}m")

    def get_conversation_grid(self):
        st.write("#### Student Segmentation by Engagement")
        # Calculate average conversation length and number of turns
        avg_conversation_length = self.user_stats['user_num_chars'].mean()
        avg_turns = self.user_stats['user_turns'].mean()

        # Create a new column to classify students into quadrants
        self.user_stats['quadrant'] = self.user_stats.apply(
            lambda row: (
            'Many Long messages' if row['user_num_chars'] > avg_conversation_length and row['user_turns'] > avg_turns else
            'Few Long messages' if row['user_num_chars'] > avg_conversation_length and row['user_turns'] <= avg_turns else
            'Many Short messages' if row['user_num_chars'] <= avg_conversation_length and row['user_turns'] > avg_turns else
            'Few Short messages'
            ), axis=1
        )

        # Scatter plot of students in quadrants
        scatter_plot = alt.Chart(self.user_stats).mark_circle(size=60).encode(
            x=alt.X('user_num_chars', title='Total Conversation Length'),
            y=alt.Y('user_turns', title='Number of Messages'),
            color=alt.Color('quadrant', title='Legend'),
            tooltip=['user_id', 'user_num_chars', 'user_turns']
        ).properties(
            width=600,
            height=400
        )

        st.altair_chart(scatter_plot, use_container_width=True)

    # def get_activity_graph(self):
    #     """
    #     Create an interactive graph visualization of the interactions of students with activities
    #     """
    #     # Group by activity_id and user_id to create the hierarchical structure
    #     grouped = self.df.groupby(['activity_id', 'user_id'])
    #     elements = { "nodes": [],
    #                  "edges": [] }
        
    #     for (activity_id, user_id), group in grouped:
    #         if group[group['role'] == 'user'].shape[0] > 3:
    #             activity_node = {"data": {"id": f"A{activity_id}", "label": "Activity", "name": f"{activity_id}"}}
    #             user_node = {"data": {"id": f"U{user_id}", "label": "User", "name": f"{user_id}"}}
    #             edge = {"data": {"id": f"{activity_id}-{user_id}", "source": f"U{user_id}", "target": f"A{activity_id}"}, "label": "INTERACTS"}

    #             elements["nodes"].append(activity_node)
    #             elements["nodes"].append(user_node)
    #             elements["edges"].append(edge)

    #     # Style node & edge groups
    #     node_styles = [
    #         NodeStyle("User", "#FF7F3E", "name", "person"),
    #         NodeStyle("Activity", "#2A629A", "content", "description"),
    #     ]

    #     edge_styles = [
    #         EdgeStyle("INTERACTS", caption='label', directed=False),
    #     ]

    #     # Render the component
    #     st.markdown("### Student-Activity Interaction Graph")
    #     st.write("This graph shows the interactions between students and activities (#interactions > 3).")
    #     st_link_analysis(elements, "fcose", node_styles, edge_styles)
                                   

    # def get_conversation_tree(self):
    #     st.write("### Conversations Overview")

    #     # Create a hierarchical data structure for the tree chart
    #     data = {
    #         "name": f"Course ",
    #         "children": []
    #     }

    #     # add activities as children
    #     activities = []
    #     for activity_id, group in self.df.groupby('activity_id'):
    #         activities.append(activity_id)

    #         activity_data = self.df[self.df['activity_id'] == activity_id]
    #         activity_node = {"name": f"Activity {activity_id}",
    #                         "children": [],
    #                         "collapsed": False,
    #                         "symbolSize": 10}
    #                         # "symbolSize": len(activity_data) / 10}
            
    #         # group by user_id
    #         grouped = activity_data.groupby('user_id')
    #         for user_id, user_group in grouped:
    #             user_node = {"name": f"User {user_id}",
    #                         "children": [],
    #                         "collapsed": True,
    #                         "symbolSize": len(user_group) / 10}

    #             # sort by timestamp
    #             user_group = user_group.sort_values('timestamp')
    #             for i, row in user_group.iterrows():
    #                 # set different colors for user and model messages
    #                 if row['role'] == 'user':
    #                     symbol = "circle"
    #                     itemStyle = {"color": "#228B22", "borderColor": "#228B22"}
    #                 else:
    #                     symbol = "rect"
    #                     itemStyle = {"color": "#FF6347", "borderColor": "#FF6347"}

    #                 message_node = {"name": "", #f"Message {row['message_num']}", 
    #                                 "value": len(row['content']),
    #                                 "children": [],
    #                                 "symbol": symbol,
    #                                 "symbolSize": 5, #len(row['content']) / 100,
    #                                 "itemStyle": itemStyle,
    #                                 "collapsed": False}
    #                 user_node["children"].append(message_node)
                
    #             activity_node["children"].append(user_node)

    #         data["children"].append(activity_node)

    #     opts = {
    #         "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
    #         "series": [
    #             {
    #                 "type": "tree",
    #                 "data": [data],
    #                 "top": "1%",
    #                 "left": "7%",
    #                 "bottom": "1%",
    #                 "right": "20%",
    #                 "symbolSize": 7,
    #                 "label": {
    #                     "position": "left",
    #                     "verticalAlign": "middle",
    #                     "align": "right",
    #                     "fontSize": 9,
    #                 },
    #                 "leaves": {
    #                     "label": {
    #                         "position": "right",
    #                         "verticalAlign": "middle",
    #                         "align": "left",
    #                     }
    #                 },
    #                 "expandAndCollapse": True,
    #                 "animationDuration": 550,
    #                 "animationDurationUpdate": 750,
    #             }
    #         ],
    #     }

    #     st_echarts(opts, height=800)
