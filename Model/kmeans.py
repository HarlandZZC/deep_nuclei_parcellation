import numpy as np
from sklearn.cluster import KMeans
import joblib
import pandas as pd
from joblib import Parallel, delayed
import os
import math
import torch
import random

def setup_seed(seed):
     torch.manual_seed(seed)
     torch.cuda.manual_seed_all(seed)
     np.random.seed(seed)
     random.seed(seed)
     torch.backends.cudnn.deterministic = True

setup_seed(42)

def _parallel_compute_distance(X, cluster):
    n_samples = X.shape[0]
    dis_mat = np.zeros((n_samples, 1))
    for i in range(n_samples):
        dis_mat[i] += np.sqrt(np.sum((X[i] - cluster) ** 2, axis=0))
    return dis_mat

# def _parallel_compute_distance_with_itk(X, cluster, cluster_coordinate):
#     n_samples = X.shape[0]
#     dis_mat = np.zeros((n_samples, 1))
#     for i in range(n_samples):
#         dis_mat[i] += np.sqrt(np.sum((X[i] - cluster) ** 2, axis=0)) + 0.001 * np.sqrt(np.sum((X[i] - cluster_coordinate) ** 2, axis=0))
#     return dis_mat

class batch_KMeans(object):

    def __init__(self, args):
        self.args = args
        self.batch_size = args.batch_size
        self.n_features = args.latent_dim
        self.n_clusters = args.n_clusters
        self.csv_path = os.path.join(args.infolder, args.csv)
        self.csv_info = self.load_csv_info()
        self.clusters = np.zeros((self.n_clusters, self.n_features))
        self.count = 1000 * np.ones((self.n_clusters))  # serve as learning rate
        self.n_jobs = args.n_jobs

    def load_csv_info(self):
        try:
            df = pd.read_csv(self.csv_path)
            
            csv_info = {}
            for index, row in df.iterrows():
                csv_info[row['voxel_id']] = row['voxel_coordinate']
            
            return csv_info
        except Exception as e:
            print(f"Error loading CSV file: {str(e)}")
            return None

    def _compute_dist(self, X, voxel_ids):
        dis_mat = Parallel(n_jobs=self.n_jobs)(
            delayed(_parallel_compute_distance)(X, self.clusters[i])
            for i in range(self.n_clusters))
        dis_mat = np.hstack(dis_mat)

        return dis_mat


    def init_cluster(self, X, indices=None):
        """ Generate initial clusters using sklearn.Kmeans """
        # model = KMeans(n_clusters=self.n_clusters,
        #                n_init= int(self.n_clusters ** self.n_clusters / math.factorial(self.n_clusters)), max_iter=50)
        model = KMeans(n_clusters=self.n_clusters,
                       n_init=1000, max_iter=50, random_state=42)
                       
        # print(self.n_clusters ** self.n_clusters)
        # print(math.factorial(self.n_clusters))
        # print(int(self.n_clusters ** self.n_clusters / math.factorial(self.n_clusters)))
        model.fit(X)  
        self.clusters = model.cluster_centers_  # copy clusters


    def update_cluster(self, X, cluster_idx):
        """ Update clusters in Kmeans on a batch of data """
        n_samples = X.shape[0]
        for i in range(n_samples):
            self.count[cluster_idx] += 1
            eta = 1.0 / self.count[cluster_idx]
            updated_cluster = ((1 - eta) * self.clusters[cluster_idx] +
                               eta * X[i])
            self.clusters[cluster_idx] = updated_cluster


    def update_assign(self, X, voxel_ids):
        """ Assign samples in `X` to clusters """
        dis_mat = self._compute_dist(X, voxel_ids)

        return np.argmin(dis_mat, axis=1)
    
    def save_model(self, outfolder_path):
        if not os.path.exists(outfolder_path):
            os.makedirs(outfolder_path)
            
        joblib.dump(self, os.path.join(outfolder_path, "kmeans_model.pkl"))