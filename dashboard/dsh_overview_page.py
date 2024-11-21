#######################
# Import libraries
import altair as alt
import pandas as pd
import streamlit as st
# from dashboard import cluster_students
from dashboard.feature_extractor import ConversationFeatureExtractor
from scipy.stats import zscore
from streamlit_echarts import st_echarts
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle


class ConversationStats():

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.user_stats = ConversationFeatureExtractor(self.df).extract_features().fillna(0)

    def create(self):

        # 1st row - Overall statistics
        with st.container():
            self.get_overall_stats()

        # 2nd row - Top 25%, Bottom 25%, and suggested chart
        with st.container():
            self.get_conversation_stats()

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
        activity_stats = self.user_stats\
            .groupby('activity_id')\
            .agg(num_student_messages=('user_turns', 'sum'),
                num_messages=('total_turns', 'sum'))
        
        st.bar_chart(activity_stats)


    def get_conversation_stats(self):
        # 2nd Row - Top 25%, Bottom 25%, and suggested chart
        st.write("### Conversation Statistics")

        col1, col2, col3 = st.columns(3)

        # Top 5 students by message length
        with col1:
            top_5 = self.user_stats.nlargest(5, 'total_user_conversation_length')
            col1.write("Top 5 Students (Longest Conversations) :clap:")
            for i, row in enumerate(top_5.itertuples(), start=1):
                col1.write(f"{i}. {row.user_id}")
        
        # bar chart of the quartiles by message length
        with col2:
            # student with no messages
            no_messages = self.user_stats[self.user_stats['user_turns'] == 0]
            no_messages['email'] = ''
            no_messages = no_messages.loc[:, ['user_id', 'email']]
            col2.write("Students with no messages :bangbang:")
            col2.dataframe(no_messages, height=250, hide_index=True)   
        
        with col3:    
            self.get_activity_stats()
        #     st.write("Conversation Length by Quartile")
        #     quartiles = self.user_stats['total_user_conversation_length'].quantile([0.25, 0.5, 0.75])
        #     quartiles = quartiles.reset_index().rename(columns={'index': 'Quartile', 'total_user_conversation_length': 'Conversation Length'})
        #     quartiles = self.user_stats.groupby(pd.qcut(self.user_stats['total_user_conversation_length'], 4))\
        #         .size().reset_index(name='count')
        #     quartiles['Quartile'] = quartiles['total_user_conversation_length'].astype(str)
        #     quartiles = quartiles.drop(columns=['total_user_conversation_length'])

        #     st.write("### Conversation Length by Quartile")
        #     bar_chart = alt.Chart(quartiles).mark_bar().encode(
        #         x='Quartile',
        #         y='count',
        #         color='Quartile'
        #     ).properties(
        #         width=400,
        #         height=300
        #     )
        #     st.altair_chart(bar_chart, use_container_width=True)

        # top_25 = self.user_stats.nlargest(int(len(self.user_stats) * 0.25), 'total_user_conversation_length')
        # top_25 = top_25.loc[:, ['user_id', 'total_user_conversation_length', 'median_user_response_length']]\
        #     .rename(columns={'total_user_conversation_length': 'Conversation Length', 'median_user_response_length': 'Median Length'})
        # col1.write("Top 25% Students (Longest Conversations)")
        # col1.dataframe(top_25, height=250, hide_index=True)

        # # Bottom 25% students by message length
        # bottom_25 = self.user_stats.nsmallest(int(len(self.user_stats) * 0.25), 'total_user_conversation_length')
        # bottom_25 = bottom_25.loc[:, ['user_id', 'total_user_conversation_length', 'median_user_response_length']]\
        #     .rename(columns={'total_user_conversation_length': 'Conversation Length', 'median_user_response_length': 'Median Length'})
        # col2.write("Bottom 25% Students (Shortest Conversations)")
        # col2.dataframe(bottom_25, height=250, hide_index=True)


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
        st.write("### Conversation Quadrant Chart")
        # Calculate average conversation length and number of turns
        avg_conversation_length = self.user_stats['total_user_conversation_length'].mean()
        avg_turns = self.user_stats['user_turns'].mean()

        # Create a new column to classify students into quadrants
        self.user_stats['quadrant'] = self.user_stats.apply(
            lambda row: (
            'Above Avg Length & Turns' if row['total_user_conversation_length'] > avg_conversation_length and row['user_turns'] > avg_turns else
            'Above Avg Length & Below Avg Turns' if row['total_user_conversation_length'] > avg_conversation_length and row['user_turns'] <= avg_turns else
            'Below Avg Length & Above Avg Turns' if row['total_user_conversation_length'] <= avg_conversation_length and row['user_turns'] > avg_turns else
            'Below Avg Length & Turns'
            ), axis=1
        )

        # Scatter plot of students in quadrants
        scatter_plot = alt.Chart(self.user_stats).mark_circle(size=60).encode(
            x=alt.X('total_user_conversation_length', title='Total Conversation Length'),
            y=alt.Y('user_turns', title='Number of Turns'),
            color=alt.Color('quadrant', title='Quadrant'),
            tooltip=['user_id', 'total_user_conversation_length', 'user_turns']
        ).properties(
            width=600,
            height=400
        )

        st.altair_chart(scatter_plot, use_container_width=True)

    def get_activity_graph(self):
        """
        Create an interactive graph visualization of the interactions of students with activities
        """
        # Group by activity_id and user_id to create the hierarchical structure
        grouped = self.df.groupby(['activity_id', 'user_id'])
        elements = { "nodes": [],
                     "edges": [] }
        
        for (activity_id, user_id), group in grouped:
            if group[group['role'] == 'user'].shape[0] > 3:
                activity_node = {"data": {"id": f"A{activity_id}", "label": "Activity", "name": f"{activity_id}"}}
                user_node = {"data": {"id": f"U{user_id}", "label": "User", "name": f"{user_id}"}}
                edge = {"data": {"id": f"{activity_id}-{user_id}", "source": f"U{user_id}", "target": f"A{activity_id}"}, "label": "INTERACTS"}

                elements["nodes"].append(activity_node)
                elements["nodes"].append(user_node)
                elements["edges"].append(edge)

        # Style node & edge groups
        node_styles = [
            NodeStyle("User", "#FF7F3E", "name", "person"),
            NodeStyle("Activity", "#2A629A", "content", "description"),
        ]

        edge_styles = [
            EdgeStyle("INTERACTS", caption='label', directed=False),
        ]

        # Render the component
        st.markdown("### Student-Activity Interaction Graph")
        st.write("This graph shows the interactions between students and activities (#interactions > 3).")
        st_link_analysis(elements, "fcose", node_styles, edge_styles)
                                   

    def get_conversation_tree(self):
        st.write("### Conversations Overview")

        # Create a hierarchical data structure for the tree chart
        data = {
            "name": f"Course ",
            "children": []
        }

        # add activities as children
        activities = []
        for activity_id, group in self.df.groupby('activity_id'):
            activities.append(activity_id)

            activity_data = self.df[self.df['activity_id'] == activity_id]
            activity_node = {"name": f"Activity {activity_id}",
                            "children": [],
                            "collapsed": False,
                            "symbolSize": 10}
                            # "symbolSize": len(activity_data) / 10}
            
            # group by user_id
            grouped = activity_data.groupby('user_id')
            for user_id, user_group in grouped:
                user_node = {"name": f"User {user_id}",
                            "children": [],
                            "collapsed": True,
                            "symbolSize": len(user_group) / 10}

                # sort by timestamp
                user_group = user_group.sort_values('timestamp')
                for i, row in user_group.iterrows():
                    # set different colors for user and model messages
                    if row['role'] == 'user':
                        symbol = "circle"
                        itemStyle = {"color": "#228B22", "borderColor": "#228B22"}
                    else:
                        symbol = "rect"
                        itemStyle = {"color": "#FF6347", "borderColor": "#FF6347"}

                    message_node = {"name": "", #f"Message {row['message_num']}", 
                                    "value": len(row['content']),
                                    "children": [],
                                    "symbol": symbol,
                                    "symbolSize": 5, #len(row['content']) / 100,
                                    "itemStyle": itemStyle,
                                    "collapsed": False}
                    user_node["children"].append(message_node)
                
                activity_node["children"].append(user_node)

            data["children"].append(activity_node)

        opts = {
            "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
            "series": [
                {
                    "type": "tree",
                    "data": [data],
                    "top": "1%",
                    "left": "7%",
                    "bottom": "1%",
                    "right": "20%",
                    "symbolSize": 7,
                    "label": {
                        "position": "left",
                        "verticalAlign": "middle",
                        "align": "right",
                        "fontSize": 9,
                    },
                    "leaves": {
                        "label": {
                            "position": "right",
                            "verticalAlign": "middle",
                            "align": "left",
                        }
                    },
                    "expandAndCollapse": True,
                    "animationDuration": 550,
                    "animationDurationUpdate": 750,
                }
            ],
        }

        st_echarts(opts, height=800)
