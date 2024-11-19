import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt

def run_clustering(_user_features:pd.DataFrame,
            n_clusters:int=3,
            model_features:List[str]=None):
    """
    Cluster the students based on their conversation features

    Parameters
    ----------
    _user_features : pd.DataFrame
        The conversation features of the students
    _n_clusters : int, optional
        The number of clusters to create, by default 3

    Returns
    -------
    pd.DataFrame
        The input dataframe with an additional column 'cluster' containing the cluster labels
    """
    # Normalize the features
    scaler = StandardScaler()
    normalized_features = scaler.fit_transform(_user_features.loc[:,model_features])

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(normalized_features)

    # return the cluster labels
    _user_features['cluster'] = cluster_labels

    return _user_features

def get_boxplot(_df_features:pd.DataFrame, feature:str):
    import plotly.express as px

    fig = px.box(_df_features, x='cluster', y=feature, title=f'{feature} by Cluster')
    fig.update_layout(xaxis_title='Cluster', yaxis_title=feature)
    return fig

def get_radar_plot(_df_features:pd.DataFrame, n_clusters:int=3, model_features:List[str]=None):

    # Define the cluster labels and their corresponding values
    cluster_labels_names = [f'Cluster {i+1}' for i in range(n_clusters)]

    scaler = StandardScaler()
    normalized_features = scaler.fit_transform(_df_features.loc[:,model_features])

    # cluster_values = clustered_features.values.T
    cluster_values = normalized_features.T

    # Calculate the number of clusters and the number of features
    num_clusters = len(cluster_labels_names)
    num_features = cluster_values.shape[0]

    # Create a figure and axis for the radar plot
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw={'projection': 'polar'})

    # Set the angle and the width of each axis
    angles = np.linspace(0, 2 * np.pi, num_features, endpoint=False).tolist()
    angles += angles[:1]
    width = 2 * np.pi / num_features

    # Plot each cluster's values as a polygon
    for i in range(num_clusters):
        values = cluster_values[:, i].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=cluster_labels_names[i])

    # Set the labels for each axis
    ax.set_xticklabels(model_features, fontsize=3)
    ax.set_yticklabels([])

    # Set the title and legend
    ax.legend(fontsize=5, loc='upper right', bbox_to_anchor=(1.3, 1.1))

    fig.tight_layout()
    return fig