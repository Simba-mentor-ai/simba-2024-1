#######################
# Import libraries
import altair as alt
import pandas as pd
import streamlit as st
from dashboard import cluster_students
from dashboard.feature_extractor import ConversationFeatureExtractor
from scipy.stats import zscore
from streamlit_echarts import st_echarts
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle


class ConversationStats():

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.user_stats = ConversationFeatureExtractor(self.df).extract_features().fillna(0)

    def create_overview(self):
        # 1st row - Overall statistics
        with st.container():
            self.get_overall_stats()

        # 2nd row - Top 25%, Bottom 25%, and suggested chart
        with st.container():
            self.get_conversation_stats()

        # 3rd row - Conversation grid and tree
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                # self.get_conversation_tree()
                self.get_activity_graph()

            with col2:
                self.get_conversation_grid()

    def get_conversation_stats(self):
        # 2nd Row - Top 25%, Bottom 25%, and suggested chart
        st.write("### Conversation Statistics")

        col1, col2, col3 = st.columns(3)

        # Top 25% students by message length
        top_25 = self.user_stats.nlargest(int(len(self.user_stats) * 0.25), 'total_user_conversation_length')
        top_25 = top_25.loc[:, ['user_id', 'total_user_conversation_length', 'median_user_response_length']]\
            .rename(columns={'total_user_conversation_length': 'Conversation Length', 'median_user_response_length': 'Median Length'})
        col1.write("Top 25% Students (Longest Conversations)")
        col1.dataframe(top_25, height=250, hide_index=True)

        # Bottom 25% students by message length
        bottom_25 = self.user_stats.nsmallest(int(len(self.user_stats) * 0.25), 'total_user_conversation_length')
        bottom_25 = bottom_25.loc[:, ['user_id', 'total_user_conversation_length', 'median_user_response_length']]\
            .rename(columns={'total_user_conversation_length': 'Conversation Length', 'median_user_response_length': 'Median Length'})
        col2.write("Bottom 25% Students (Shortest Conversations)")
        col2.dataframe(bottom_25, height=250, hide_index=True)

        # student with no messages
        no_messages = self.user_stats[self.user_stats['user_turns'] == 0]
        no_messages = no_messages.loc[:, ['user_id', 'total_user_conversation_length', 'median_user_response_length']]\
            .rename(columns={'total_user_conversation_length': 'Conversation Length', 'median_user_response_length': 'Median Length'})
        col3.write("Students with no messages")
        col3.dataframe(no_messages, height=250, hide_index=True)   

    def get_overall_stats(self):
        total_students = self.df['user_id'].nunique()
        total_activities = self.df['activity_id'].nunique()
        total_user_turns = self.df[self.df['role'] == 'user'].shape[0]
        total_model_turns = self.df[self.df['role'] == 'model'].shape[0]
        median_user_response_length = self.df[self.df['role'] == 'user']['content'].str.len().median()
        median_model_response_length = self.df[self.df['role'] == 'model']['content'].str.len().median()
        average_conversation_duration = self.df.groupby('user_id')['timestamp'].apply(lambda x: x.max() - x.min()).mean()

        # Display metrics
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        col1.metric("Total Students", total_students)
        col2.metric("Total Activities", total_activities)
        col3.metric("Total User Turns", total_user_turns)
        col4.metric("Total Model Turns", total_model_turns)
        col5.metric("Median User Response Length", median_user_response_length)
        col6.metric("Median Model Response Length", median_model_response_length)
        average_conversation_duration_hours = average_conversation_duration.total_seconds() // 3600
        average_conversation_duration_minutes = (average_conversation_duration.total_seconds() % 3600) // 60
        col7.metric("Average Conversation Duration", f"{int(average_conversation_duration_hours)}h {int(average_conversation_duration_minutes)}m")

    def get_conversation_grid(self):
        model_features = [  'total_turns','user_turns','model_turns',
                            'avg_response_time_seconds','total_conversation_duration_seconds', 
                            'avg_user_response_length','avg_model_response_length']
        
        clusters = cluster_students.run_clustering(self.user_stats, n_clusters=4, model_features=model_features)
        
    
        # scatter plot of number of messages vs conversation length
        st.write("### Conversation Length vs Number of Messages")
        # centralize data to the origin by subtracting the mean
        scatter_data = clusters.copy()
        # standardize the data
        scatter_data['norm__total_user_conversation_length'] = zscore(scatter_data['total_user_conversation_length'])
        scatter_data['norm__user_turns'] = zscore(scatter_data['user_turns'])
        # scatter_data['cluster'] = clusters['cluster']  # Add cluster information to the scatter data
        
        scatter = alt.Chart(scatter_data)\
            .mark_circle()\
            .encode(
                x=alt.X('norm__total_user_conversation_length', 
                        axis=alt.Axis(values=[0.5], grid=True)),
                y=alt.Y('norm__user_turns', 
                        axis=alt.Axis(values=[0.5], grid=True)),
                size='median_user_response_length',
                color='cluster:N',  # Color by cluster
                tooltip=['user_id', 'total_user_conversation_length', 'user_turns', 'median_user_response_length', 'cluster']
            ).properties(
                width=800,
                height=400
            ).configure_axis(
                domain=False
            ).configure_view(
                stroke=None
            )

        st.altair_chart(scatter, use_container_width=True)

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

        # # Sample Data
        # elements = {
        #     "nodes": [
        #         {"data": {"id": 1, "label": "PERSON", "name": "Streamlit"}},
        #         {"data": {"id": 2, "label": "PERSON", "name": "Hello"}},
        #         {"data": {"id": 3, "label": "PERSON", "name": "World"}},
        #         {"data": {"id": 4, "label": "POST", "content": "x"}},
        #         {"data": {"id": 5, "label": "POST", "content": "y"}},
        #     ],
        #     "edges": [
        #         {"data": {"id": 6, "label": "FOLLOWS", "source": 1, "target": 2}},
        #         {"data": {"id": 7, "label": "FOLLOWS", "source": 2, "target": 3}},
        #         {"data": {"id": 8, "label": "POSTED", "source": 3, "target": 4}},
        #         {"data": {"id": 9, "label": "POSTED", "source": 1, "target": 5}},
        #         {"data": {"id": 10, "label": "QUOTES", "source": 5, "target": 4}},
        #     ],
        # }

        # Style node & edge groups
        node_styles = [
            NodeStyle("User", "#FF7F3E", "name", "person"),
            NodeStyle("Activity", "#2A629A", "content", "description"),
        ]

        edge_styles = [
            EdgeStyle("INTERACTS", caption='label', directed=False),
            # EdgeStyle("POSTED", caption='label', directed=True),
            # EdgeStyle("QUOTES", caption='label', directed=True),
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
