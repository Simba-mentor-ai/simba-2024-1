#######################
# Import libraries
import plotly.figure_factory as ff
import streamlit as st
from streamlit_echarts import st_echarts
from openai import OpenAI

openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_conversation_tree(_df):
    # Create a hierarchical data structure for the tree chart
    class_colors = {
        'Greeting': '#FFD700',
        'Question': '#FF6347',
        'Answer': '#228B22',
        'Feedback': '#87CEFA'
    }
    data = {}
    curr_node = data

    for i, row in _df.iterrows():
        # set different colors for user and model messages
        if row['role'] == 'user':
            symbol = "circle"
            itemStyle = {"color": class_colors[row['class']],
                         "borderColor": "#228B22"}
        else:
            symbol = "rect"
            itemStyle = {"color": class_colors[row['class']], 
                         "borderColor": "#FF6347"}

        message_node = {"name": row['class'], #f"Message {row['message_num']}", 
                        "value": row['content'],
                        "children": [],
                        "symbol": symbol,
                        "symbolSize": max(10, len(row['content']) / 100),
                        "itemStyle": itemStyle,
                        "collapsed": False}
        if data == {}:
            data = message_node
        else:
            curr_node["children"].append(message_node)
        curr_node = message_node

    return data


def classify_conversation(conversation):
    PROMPT_SYSTEM = """You are a meta cognition evaluator. You are evaluating a conversation between a student and a chatbot. 
           Evaluate this conversation in terms of the quality of the questions asked, the quality of the answers provided,
           and the overall feedback given by the student.
           Classify the conversation into one of the following categories: Information Seeking, Clarification, 
        """
    response = openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": PROMPT_SYSTEM},
            {"role": "user", "content": conversation}
        ],
        stream=False,
        timeout=1500  # Set the timeout to 1500 seconds
    )
    return response.choices[0].message



def create_student_stats(df):
    # 1st Row - Filter by activity_id
    col1, col2 = st.columns(2)
    with col1:
        tab2_activity_filter = st.selectbox("Select Activity ID", df['activity_id'].unique(), key='tab2_activity_filter')
        filtered_df = df[df['activity_id'] == tab2_activity_filter]
    with col2:
        student_filter = st.selectbox("Select Student ID", df['user_id'].unique())
        filtered_df = filtered_df[filtered_df['user_id'] == student_filter]

    cols = st.columns(3)
    with cols[0]:
        # st.markdown('#### Number of messages per user')
        hist_data = [df[df['role'] == 'user']['user_id'].value_counts().values,
                     df[df['role'] == 'model']['user_id'].value_counts().values]
        fig = ff.create_distplot(
                hist_data, ['Users', 'Bot'], bin_size=[.5, .5])
        if student_filter:
            # selected_user_bin = df[df['user_id'] == student_filter]['role'].value_counts().values[0]
            pass
            # fig.add_vline(x=selected_user_bin, line_dash="dash", line_color="red", annotation_text="Selected User", annotation_position="top right")
        
        fig.update_layout(title="Number of Messages Distribution")

        st.plotly_chart(fig, use_container_width=True)

    with cols[1]:
        # st.markdown('#### Average message length per user')
        hist_data = [df[df['role'] == 'user']['content'].str.len().values,
                     df[df['role'] == 'model']['content'].str.len().values]
        fig = ff.create_distplot(
                hist_data, ['Users', 'Bot'], bin_size=[10, 10])
        # print(filtered_df)

        selected_user_bin = filtered_df['content'].str.len().values[0]
        fig.add_vline(x=selected_user_bin, line_dash="dash", line_color="red", annotation_text="Selected User", annotation_position="top right")
        fig.update_layout(title="Message Length Distribution")
        
        st.plotly_chart(fig, use_container_width=True)

    with cols[2]:
        # Sum over all messages for each student
        user_message_lengths = df[df['role'] == 'user'].groupby('user_id')['content'].apply(lambda x: x.str.len().sum()).values
        model_message_lengths = df[df['role'] == 'model'].groupby('user_id')['content'].apply(lambda x: x.str.len().sum()).values
        hist_data = [user_message_lengths, model_message_lengths]
        fig = ff.create_distplot(
                hist_data, ['Users', 'Bot'], bin_size=[200, 200])
        selected_user_bin = filtered_df.loc[filtered_df['role'] == 'user']['content'].str.len().values[0]
        fig.add_vline(x=selected_user_bin, line_dash="dash", line_color="red", annotation_text="Selected User", annotation_position="top right")
        
        fig.update_layout(title="Conversation Length Distribution")
        
        st.plotly_chart(fig, use_container_width=True)

    # user conversation
    cols = st.columns(2)
    with cols[0]:
        st.write("### User Conversation")
        with st.container(height=500):
            for index, row in filtered_df.iterrows():
                if row['role'] == 'user':
                    st.markdown(
                    f"<div style='float: right; text-align: left; background-color: #DAF7A6; border-radius: 10px; padding: 10px; margin: 5px 0; width: 75%;'><b>User:</b>{row['content']} [{row['class']}]</div>", 
                    unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                    f"<div style='float: left; background-color: #aed6f1; border-radius: 10px; padding: 10px; margin: 5px 0; width: 75%;'><b>Bot:</b> {row['content']} [{row['class']}]</div>", 
                    unsafe_allow_html=True
                    )
    with cols[1]:
        st.write("#### Message Classification")
        tree = get_conversation_tree(filtered_df)
        opts = {
            "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
            "series": [
            {
                "type": "tree",
                "data": [tree],
                "orient": "vertical",
                "top": "1%",
                "left": "7%",
                "bottom": "1%",
                "right": "20%",
                "symbolSize": 15,
                "label": {
                "position": "top",
                "verticalAlign": "middle",
                "align": "center",
                "fontSize": 9,
                },
                "leaves": {
                "label": {
                    "position": "bottom",
                    "verticalAlign": "middle",
                    "align": "center",
                }
                },
                "expandAndCollapse": True,
                "animationDuration": 550,
                "animationDurationUpdate": 750,
            }
            ],
        }

        st_echarts(opts, height=500)
        
