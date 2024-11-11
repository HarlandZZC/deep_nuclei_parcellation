import torch
import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import visdom
import random
from DCN import DCN
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
# python /data02/DWIsegmentation/Models/DCN_whole_amygdala/HCP.py

def setup_seed(seed):
     torch.manual_seed(seed)
     torch.cuda.manual_seed_all(seed)
     np.random.seed(seed)
     random.seed(seed)
     torch.backends.cudnn.deterministic = True

setup_seed(42)

class CSVDataset(Dataset):
    def __init__(self, csv_file):
        df = pd.read_csv(csv_file)

        self.X = df.iloc[:, 4:].values.astype('float32')
        self.y = df.iloc[:, 2].values.astype('float32')
        self.subject_ids = df.iloc[:, 0].values

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
    

def create_train_test_loaders(args):
    dataset = CSVDataset(os.path.join(args.infolder, args.csv))

    unique_subject_ids = list(set(dataset.subject_ids))
    unique_subject_ids.sort()
    # print(unique_subject_ids)
    
    train_subject_ids, test_subject_ids = train_test_split(unique_subject_ids, test_size=0.2)

    train_indices = [i for i, subject_id in enumerate(dataset.subject_ids) if subject_id in train_subject_ids]
    test_indices = [i for i, subject_id in enumerate(dataset.subject_ids) if subject_id in test_subject_ids]

    train_dataset = torch.utils.data.Subset(dataset, train_indices)
    test_dataset = torch.utils.data.Subset(dataset, test_indices)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)

    train_subject_count = len(set(train_subject_ids))
    test_subject_count = len(set(test_subject_ids))
    train_voxel_count = len(train_dataset)
    test_voxel_count = len(test_dataset)
    
    print(f"Train Loader - Subject Count: {train_subject_count}, Voxel Count: {train_voxel_count}")
    print(f"Test Loader - Subject Count: {test_subject_count}, Voxel Count: {test_voxel_count}")

    return train_loader, test_loader


def trainer(args, model, train_loader):
    pretrain_rec_loss_list = model.pretrain(train_loader, args.pre_epoch) 
    rec_loss_list = []
    dist_loss_list = []
    combined_loss_list = []

    vis = visdom.Visdom(env='main')
    vis.close(env='main')

    for e in range(args.epoch):
        model.train()
        loss, rec_loss, dist_loss = model.fit(e, train_loader)
        
        combined_loss_list.append(loss)
        rec_loss_list.append(rec_loss)
        dist_loss_list.append(dist_loss)

        vis.line(X=np.array([e]), 
             Y=np.array([rec_loss]),
             win='Rec-Loss in Training',
             update='append',  
             opts=dict(title='Reconstruction Loss', xlabel='Epoch', ylabel='Loss'))

        vis.line(X=np.array([e]),
             Y=np.array([dist_loss]),
             win='Dist-Loss in Training',
             update='append',  
             opts=dict(title='Distance Loss', xlabel='Epoch', ylabel='Loss'))

        vis.line(X=np.array([e]),
             Y=np.array([loss]),
             win='Combined-Loss in Training',
             update='append',  
             opts=dict(title='Combined Loss', xlabel='Epoch', ylabel='Loss'))

    model.kmeans.save_model(args.outfolder)
    model.autoencoder.module.save_model(args.outfolder)

    return pretrain_rec_loss_list, combined_loss_list, rec_loss_list, dist_loss_list


def tester(args, model, test_loader):
    model.eval()
    model.load_models()
    results = model.test(test_loader)
    return results


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Deep Clustering Network')

    # Dataset parameters
    parser.add_argument('--infolder', default='path_to_input_folder',
                        help='input folder')
    parser.add_argument('--csv', default='path_to_csv',
                        help='csv name')
    parser.add_argument('--input_dim', type=int, default=150,
                        help='input dimension')
    parser.add_argument('--outfolder', default='./Model/output',
                    help='output folder')

    # Training parameters
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='learning rate (default: 1e-4)')
    parser.add_argument('--wd', type=float, default=5e-4,
                        help='weight decay (default: 5e-4)')
    parser.add_argument('--batch_size', type=int, default=2500,
                        help='input batch size for training')
    parser.add_argument('--epoch', type=int, default=200,
                        help='number of epochs to train')
    parser.add_argument('--pre_epoch', type=int, default=100, 
                        help='number of pre-train epochs')
    parser.add_argument('--pretrain', type=bool, default=True,
                        help='whether use pre-training')

    # Model parameters
    # before : 2000
    parser.add_argument('--lamda', type=float, default=2000,
                        help='coefficient of the reconstruction loss')
    parser.add_argument('--beta', type=float, default=1/1000,
                        help=('coefficient of the regularization term on '
                              'clustering'))
    parser.add_argument('--latent_dim', type=int, default=36,
                        help='latent space dimension')
    parser.add_argument('--n_clusters', type=int, default=9,
                        help='number of clusters in the latent space')

    # Utility parameters
    parser.add_argument('--cuda', type=bool, default=True,
                        help='whether to use GPU')
    
    # parser.add_argument('--gpu_index', type=int, default=0,
    #                 help='GPU index')
    parser.add_argument('--gpu_index', nargs='+', type=int, default=[0], help='GPU indices to use')
    
    parser.add_argument('--n_jobs', type=int, default=4,
                    help='number of jobs to run in parallel')
    
    parser.add_argument('--log_interval', type=int, default=5,
                    help=('how many batches to wait before logging the '
                            'training status'))

    args = parser.parse_args()

    # Load data
    train_loader, test_loader = create_train_test_loaders(args)
    
    # Main body
    model = DCN(args)
    
    pretrain_rec_loss_list, combined_loss_list, rec_loss_list, dist_loss_list = trainer(
        args, model, train_loader)

    results = tester(args, model, test_loader)


    if not os.path.exists(args.outfolder):
        os.makedirs(args.outfolder)

    column_names = ['subject_id', 'voxel_id', 'voxel_coordinate', 'cluster_id']

    df = pd.DataFrame(results, columns=column_names)

    df['cluster_id'] = df['cluster_id'] + 1

    csv_file = os.path.join(args.outfolder, "test_results.csv")
    if os.path.exists(csv_file):
        os.remove(csv_file)
    df.to_csv(csv_file, index=False)


def save_loss_and_plot(loss_list, loss_name, img_name, args):
    # Save loss_list data
    np.savetxt(os.path.join(args.outfolder, f'{loss_name}_data.txt'), loss_list)

    plt.plot(loss_list)
    plt.xlabel('Epoch')
    plt.ylabel(loss_name)
    # save png
    img_path = os.path.join(args.outfolder, f'{img_name}.png')
    if os.path.exists(img_path):
        os.remove(img_path)
    plt.savefig(img_path)
    print(f'Figure and {loss_name} values saved to', img_path)
    plt.close()

# Save pretrain_rec_loss_list data
save_loss_and_plot(pretrain_rec_loss_list, 'Rec-Loss_in_Pretraining', 'Rec-Loss_in_Pretraining', args)

# Save combined_loss_list data
save_loss_and_plot(combined_loss_list, 'Combined-Loss_in_Training', 'Combined-Loss_in_Training', args)

# Repeat the same process for rec_loss_list and dist_loss_list

# Save rec_loss_list data
save_loss_and_plot(rec_loss_list, 'Rec-Loss_in_Training', 'Rec-Loss_in_Training', args)

# Save dist_loss_list data
save_loss_and_plot(dist_loss_list, 'Dist-Loss_in_Training', 'Dist-Loss_in_Training', args)

