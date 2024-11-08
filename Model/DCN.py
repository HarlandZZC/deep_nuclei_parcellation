import torch
import numbers
import numpy as np
import torch.nn as nn
import random
import os
import joblib
import pandas as pd
from kmeans import batch_KMeans
from autoencoder import AutoEncoder

def setup_seed(seed):
     torch.manual_seed(seed)
     torch.cuda.manual_seed_all(seed)
     np.random.seed(seed)
     random.seed(seed)
     torch.backends.cudnn.deterministic = True

setup_seed(42)

# class DCN(nn.Module):

#     def __init__(self, args):
#         super(DCN, self).__init__()
#         self.args = args
#         self.beta = args.beta  # coefficient of the clustering term
#         self.lamda = args.lamda  # coefficient of the reconstruction term
#         self.infolder = args.infolder
#         self.csv = args.csv
#         self.outfolder = args.outfolder
#         device_list = list(map(int,list(args.gpu_index)))
#         self.device = device_list[0]
#         # self.device = torch.device(f'cuda:{gpu_index}' if args.cuda else 'cpu')

#         # Validation check
#         if not self.beta > 0:
#             msg = 'beta should be greater than 0 but got value = {}.'
#             raise ValueError(msg.format(self.beta))

#         if not self.lamda > 0:
#             msg = 'lambda should be greater than 0 but got value = {}.'
#             raise ValueError(msg.format(self.lamda))

#         self.kmeans = batch_KMeans(args)
#         self.autoencoder = AutoEncoder(args).to(self.device)

#         self.criterion = nn.MSELoss()
#         self.optimizer = torch.optim.Adam(self.parameters(),
#                                           lr=args.lr,
#                                           weight_decay=args.wd)

class DCN(nn.Module):

    def __init__(self, args):
        super(DCN, self).__init__()
        self.args = args
        self.beta = args.beta  # coefficient of the clustering term
        self.lamda = args.lamda  # coefficient of the reconstruction term
        self.infolder = args.infolder
        self.csv = args.csv
        self.outfolder = args.outfolder
        device_list = list(map(int, list(args.gpu_index)))
        self.device = device_list[0]

        # Validation check
        if not self.beta > 0:
            msg = 'beta should be greater than 0 but got value = {}.'
            raise ValueError(msg.format(self.beta))

        if not self.lamda > 0:
            msg = 'lambda should be greater than 0 but got value = {}.'
            raise ValueError(msg.format(self.lamda))

        self.kmeans = batch_KMeans(args)

        # Wrap the autoencoder model in DataParallel
        self.autoencoder = nn.DataParallel(AutoEncoder(args).to(self.device), device_ids=device_list)

        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.parameters(),
                                          lr=args.lr,
                                          weight_decay=args.wd)

    """ Compute the Equation (5) in the original paper on a data batch """
    def _loss(self, X, cluster_id):

        batch_size = X.size()[0]
        rec_X = self.autoencoder(X)
        latent_X = self.autoencoder(X, latent=True)

        # Reconstruction error
        rec_loss = self.lamda * self.criterion(X, rec_X)

        # Regularization term on clustering
        dist_loss = torch.tensor(0.).to(self.device)
        clusters = torch.FloatTensor(self.kmeans.clusters).to(self.device)
        for i in range(batch_size):
            diff_vec = latent_X[i] - clusters[cluster_id[i]]
            sample_dist_loss = torch.matmul(diff_vec.view(1, -1),
                                            diff_vec.view(-1, 1))
            dist_loss += 0.5 * self.beta * torch.squeeze(sample_dist_loss)

        return (rec_loss + dist_loss,
                rec_loss.detach().cpu().numpy(),
                dist_loss.detach().cpu().numpy())

    # def _loss(self, X, cluster_id):

    #     batch_size = X.size()[0]
    #     rec_X = self.autoencoder(X)
    #     latent_X = self.autoencoder(X, latent=True)

    #     # Calculate dist_loss using self.beta
    #     dist_loss = torch.tensor(0.).to(self.device)
    #     clusters = torch.FloatTensor(self.kmeans.clusters).to(self.device)
    #     for i in range(batch_size):
    #         diff_vec = latent_X[i] - clusters[cluster_id[i]]
    #         sample_dist_loss = torch.matmul(diff_vec.view(1, -1),
    #                                         diff_vec.view(-1, 1))
    #         dist_loss += 0.5 * self.beta * torch.squeeze(sample_dist_loss)

    #     # Calculate lamda to balance rec_loss and dist_loss
    #     lamda = dist_loss / self.criterion(X, rec_X).detach()
    #     rec_loss = 10 * lamda * self.criterion(X, rec_X)

    #     return (rec_loss + dist_loss,
    #             rec_loss.detach().cpu().numpy(),
    #             dist_loss.detach().cpu().numpy())


    def pretrain(self, train_loader, epoch, verbose=True):

        if not self.args.pretrain:
            return

        if not isinstance(epoch, numbers.Integral):
            msg = '`epoch` should be an integer but got value = {}'
            raise ValueError(msg.format(epoch))

        if verbose:
            print('========== Start pretraining ==========')

        pretrain_rec_loss_list = []

        self.train()
        for e in range(epoch):
            for batch_idx, (data, _) in enumerate(train_loader):
                batch_size = data.size()[0]
                data = data.to(self.device).view(batch_size, -1)
                rec_X = self.autoencoder(data)
                loss = self.criterion(data, rec_X)

                if verbose and batch_idx % self.args.log_interval == 0:
                    msg = 'Epoch: {:02d} | Batch: {:03d} | Rec-Loss: {:.3f}'
                    print(msg.format(e, batch_idx,
                                     loss.detach().cpu().numpy()))
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
            pretrain_rec_loss_list.append(loss.detach().cpu().numpy())
        self.eval()

        if verbose:
            print('========== End pretraining ==========\n')

        # Initialize clusters in self.kmeans after pre-training
        batch_X = []
        for batch_idx, (data, _) in enumerate(train_loader):
            batch_size = data.size()[0]
            data = data.to(self.device).view(batch_size, -1)
            latent_X = self.autoencoder(data, latent=True)
            batch_X.append(latent_X.detach().cpu().numpy())
        batch_X = np.vstack(batch_X)
        self.kmeans.init_cluster(batch_X)

        return pretrain_rec_loss_list

    def fit(self, epoch, train_loader, verbose=True):
        loss_return = 0
        rec_loss_return = 0
        dist_loss_return = 0
        
        for batch_idx, (data, voxel_ids) in enumerate(train_loader):
            batch_size = data.size()[0]
            data = data.view(batch_size, -1).to(self.device)
            # subject_info = self.load_subject_info()

            # Get the latent features
            with torch.no_grad():
                latent_X = self.autoencoder(data, latent=True)
                latent_X = latent_X.cpu().numpy()

            # [Step-1] Update the assignment results
            cluster_id = self.kmeans.update_assign(latent_X,voxel_ids)

            elem_count = np.bincount(cluster_id,
                            minlength=self.args.n_clusters)
            
            if verbose and batch_idx % self.args.log_interval == 0:
                for k in range(self.args.n_clusters):
                    print(f'Cluster {k}: {elem_count[k]} elements')
            
            # [Step-2] Update the network parameters
            loss, rec_loss, dist_loss = self._loss(data, cluster_id)
            # test_kmeans
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            if verbose and batch_idx % self.args.log_interval == 0:
                loss_return = loss.detach().cpu().numpy()
                rec_loss_return = rec_loss
                dist_loss_return = dist_loss

                msg = 'Epoch: {:02d} | Batch: {:03d} | Loss: {:.3f} | Rec-' \
                      'Loss: {:.3f} | Dist-Loss: {:.3f}'
                print(msg.format(epoch, batch_idx,
                                 loss.detach().cpu().numpy(),
                                 rec_loss, dist_loss))    

            # [Step-3] Update clusters in bath Kmeans
            
            # if verbose and batch_idx % self.args.log_interval == 0:
            #     for k in range(self.args.n_clusters):
            #         print(f'Cluster {k}: {elem_count[k]} elements')

            # for k in range(self.args.n_clusters):
            #     # avoid empty slicing
            #     if elem_count[k] == 0:
            #         continue
            #     self.kmeans.update_cluster(latent_X[cluster_id == k], k)

            # for k in range(self.args.n_clusters):
            #     # Check if any cluster has fewer points than the threshold
            #     min_points_threshold = 1 / 100 * self.args.batch_size
            #     if elem_count[k] < min_points_threshold:
            #         print("averaging clusters...")
            #         # Find clusters with more than min_points_threshold points
            #         candidate_clusters = [j for j in range(len(self.kmeans.clusters)) if elem_count[j] >= min_points_threshold]
            #         # Calculate the average of candidate clusters
            #         if candidate_clusters:
            #             avg_cluster = np.mean([self.kmeans.clusters[j] for j in candidate_clusters], axis=0)

            #             # Update the cluster center with the average
            #             self.kmeans.clusters[k] = avg_cluster

            #     else:
            #         self.kmeans.update_cluster(latent_X[cluster_id == k], k)
                    
            elem_count = np.bincount(cluster_id,
                                     minlength=self.args.n_clusters)
            # update_flag = 1
            min_points_threshold = 1/100 * self.args.batch_size
            candidate_clusters = [j for j in range(len(self.kmeans.clusters)) if elem_count[j] > min_points_threshold]
            avg_cluster = np.mean([self.kmeans.clusters[j] for j in candidate_clusters], axis=0)

            for k in range(self.args.n_clusters):
                # Check if any cluster has fewer points than the threshold
                if elem_count[k] <= min_points_threshold:
                    print(f"averaging cluster {k}...")
                    # Calculate the average of candidate clusters
                    self.kmeans.clusters[k] = avg_cluster + np.random.uniform(0, 0.01, size=avg_cluster.shape)
                    # update_flag = 0
                # elif elem_count[k] <= min_points_threshold and update_flag == 0:
                #     print(f"averaging cluster {k}...")
                #     self.kmeans.clusters[k] = avg_cluster + np.random.uniform(0, 0.01, size=avg_cluster.shape)
                else:
                    self.kmeans.update_cluster(latent_X[cluster_id == k], k)
            
        return loss_return, rec_loss_return, dist_loss_return
        
    def load_models(self):
        # Load the trained K-means and autoencoder models
        kmeans_model_path = os.path.join(self.outfolder, "kmeans_model.pkl")
        autoencoder_model_path = os.path.join(self.outfolder, "autoencoder.pth")
        self.kmeans = joblib.load(kmeans_model_path)
        self.autoencoder.module.load_state_dict(torch.load(autoencoder_model_path, map_location=torch.device(self.device)))
        self.autoencoder.module.to(self.device)
        self.autoencoder.module.eval()


    def load_subject_info(self):
        csv_file_path = os.path.join(self.infolder, self.csv)
        df = pd.read_csv(csv_file_path)
        subject_info = []

        for i in range(len(df)):
            subject_id = df.iloc[i, 0]
            voxel_coordinates = df.iloc[i, 3] 
            subject_info.append((subject_id, voxel_coordinates))

        return subject_info

    def test(self, test_loader):
        results = []
        subject_info = self.load_subject_info()

        for batch_idx, (data, voxel_id) in enumerate(test_loader):
            data = data.to(self.device).view(data.size(0), -1)

            with torch.no_grad():
                latent_X = self.autoencoder(data, latent=True).detach().cpu().numpy()

            cluster_ids = self.kmeans.update_assign(latent_X,voxel_id)

            subject_info_batch = [subject_info[vid.int().item()] for vid in voxel_id]

            for i in range(data.size(0)):
                subject_id, voxel_coordinates = subject_info_batch[i]

                print(f"subject_id: {subject_id}, voxel_id: {voxel_id[i]}, voxel_coordinate: {voxel_coordinates}, cluster_id: {cluster_ids[i]}")

                results.append({
                    'subject_id': subject_id,
                    'voxel_id': voxel_id[i].int().item(),
                    'voxel_coordinate': str(voxel_coordinates),
                    'cluster_id': cluster_ids[i]
                })

        return results
