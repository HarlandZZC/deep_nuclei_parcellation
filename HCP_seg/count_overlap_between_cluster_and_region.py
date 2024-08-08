import os
import argparse
import nibabel as nib
import numpy as np
import pandas as pd
# python /home/haolin/Research/HCP_seg/count_overlap_between_cluster_and_region.py --cluster_folder --region_folder --outcsv

def calculate_overlap(cluster_folder, region_folder):
    overlap_dict = {}
    for cluster_file in os.listdir(cluster_folder):
        if cluster_file.endswith('.nii.gz'):
            cluster_img = nib.load(os.path.join(cluster_folder, cluster_file))
            cluster_data = cluster_img.get_fdata()
            cluster_voxels = np.sum(cluster_data)
            cluster_id = cluster_file.split('_')[1].split('.')[0]
            overlap_dict[cluster_id] = {}
            for region_file in os.listdir(region_folder):
                if region_file.endswith('.nii.gz'):
                    region_img = nib.load(os.path.join(region_folder, region_file))
                    region_data = region_img.get_fdata()
                    overlap_voxels = np.sum(cluster_data * region_data)
                    region_id = region_file.split('_')[1].split('.')[0]
                    overlap_dict[cluster_id][region_id] = overlap_voxels / cluster_voxels
    return overlap_dict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cluster_folder', required=True)
    parser.add_argument('--region_folder', required=True)
    parser.add_argument('--outcsv', required=True)
    args = parser.parse_args()

    overlap_dict = calculate_overlap(args.cluster_folder, args.region_folder)
    df = pd.DataFrame(overlap_dict).T
    df.index = df.index.astype(int)
    df.columns = df.columns.astype(int)
    df = df.sort_index(axis=0).sort_index(axis=1)
    df['max_region'] = df.idxmax(axis=1)
    df.to_csv(args.outcsv)

if __name__ == "__main__":
    main()

