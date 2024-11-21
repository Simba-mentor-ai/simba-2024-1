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
