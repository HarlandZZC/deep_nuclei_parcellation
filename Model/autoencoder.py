import torch
import torch.nn as nn
import torch.nn.functional as F
import random
import os
import numpy as np

def setup_seed(seed):
     torch.manual_seed(seed)
     torch.cuda.manual_seed_all(seed)
     np.random.seed(seed)
     random.seed(seed)
     torch.backends.cudnn.deterministic = True

setup_seed(42)

class AutoEncoder(nn.Module):

    def __init__(self, args):
        super(AutoEncoder, self).__init__()
        self.args = args
        self.input_dim = args.input_dim
        self.output_dim = self.input_dim
        self.latent_dim = args.latent_dim
        self.n_clusters = args.n_clusters

        # nn.Conv2d(1, 4, kernel_size=3, stride=2, padding=1),
        # Encoder Network
        self.encoder_conv1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=6, kernel_size=5, stride=1, padding=1),
            nn.Tanh(),
            nn.BatchNorm2d(6),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.encoder_conv2 = nn.Sequential(
            nn.Conv2d(in_channels=7, out_channels=16, kernel_size=5, stride=1, padding=1),
            nn.Tanh(),
            nn.BatchNorm2d(16), 
            nn.MaxPool2d(kernel_size=2, stride=2)
        )

        if args.input_dim == 150:
            temp_linear = 31104
        elif args.input_dim == 25:
            temp_linear = 384
        elif args.input_dim == 50:
            temp_linear = 2904
        elif args.input_dim == 100:
            temp_linear = 12696
        elif args.input_dim == 200:
            temp_linear = 55296

        self.encoder_fc = nn.Sequential(
            nn.Linear(temp_linear, 4096),
            nn.BatchNorm1d(4096), 
            nn.Linear(4096, 512),
            nn.Tanh(),
            nn.BatchNorm1d(512),
            nn.Linear(512, self.latent_dim),
            nn.Tanh()
        )

        # Decoder Network
        self.decoder_fc = nn.Sequential(
            nn.Linear(self.latent_dim, 64),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(64),
            nn.Linear(64, 128),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(128),
            nn.Linear(128, self.output_dim),
            nn.LeakyReLU(0.2)
        )

    
    def cyclic_shift_and_concat(self, input_data):
        input_data = input_data.unsqueeze(1).unsqueeze(3)
        batch_size, _, k, _ = input_data.size()
        
        result = torch.empty((batch_size, 1, k, k), dtype=input_data.dtype, device=input_data.device)
        
        for i in range(k):
            shift = i % k
            shifted_data = torch.roll(input_data, shifts=shift, dims=2)
            result[:, :, :, i] = shifted_data.squeeze(dim=3)
            # print(f"result_data.size: {result.size()}")

        return result

    def forward(self, X, latent=False):
        X = self.cyclic_shift_and_concat(X)
        X_backup_after_cyc = X.clone()  

        X = self.encoder_conv1(X)
        batch_size, channels, height, width = X.size()
        X_cyctoconv1 = F.interpolate(X_backup_after_cyc, size=(height, width), mode='bilinear', align_corners=False)
        X = torch.cat((X, X_cyctoconv1), dim=1)
        X_backup_after_conv1 = X.clone()

        X = self.encoder_conv2(X)
        batch_size, channels, height, width = X.size()
        X_conv1toconv2 = F.interpolate(X_backup_after_conv1, size=(height, width), mode='bilinear', align_corners=False)
        X_cyctocov2 = F.interpolate(X_backup_after_cyc, size=(height, width), mode='bilinear', align_corners=False)
        X = torch.cat((X, X_conv1toconv2, X_cyctocov2), dim=1)

        X = X.view(batch_size, -1)

        X = self.encoder_fc(X)
        if latent:
            return X
        return self.decoder_fc(X)
    
    # test k-means
        # if latent:
        #     return X
        # return X

    def save_model(self, outfolder_path):
        if not os.path.exists(outfolder_path):
            os.makedirs(outfolder_path)
            
        # actual_model = self.module if hasattr(self, 'module') else self

        # torch.save(actual_model.state_dict(), os.path.join(outfolder_path, "autoencoder.pth"))

        torch.save(self.state_dict(), os.path.join(outfolder_path, "autoencoder.pth"))


