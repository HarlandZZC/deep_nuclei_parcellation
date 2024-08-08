import os
import argparse
import pandas as pd
# python /home/haolin/Research/Segmentation/mapcsv.py --folder folder --mapcsv csv
# 代码有问题

parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True)
parser.add_argument('--mapcsv', default="/home/haolin/Research/HCP_seg/map_rule.csv")
args = parser.parse_args()

mapping = pd.read_csv(args.mapcsv)
mapping.columns = ['folder_basename', 'Class_before', 'Class_after']

cluster_df = pd.read_csv(f"{args.folder}/output/cluster_statistics.csv")
dice_df = pd.read_csv(f"{args.folder}/output/dice.csv")

mapping = mapping.astype(str)
cluster_df = cluster_df.astype(str)
dice_df = dice_df.astype(str)

folder_name = args.folder.split('/')[-1]
mapping = mapping[mapping['folder_basename'] == folder_name]

for index, row in mapping.iterrows():
    old_class = row['Class_before'] + '.0'
    new_class = row['Class_after'] + '.0'

    print(f"Class {old_class} changed to Class {new_class}")

    cluster_df['Class'] = cluster_df['Class'].replace(old_class, new_class)
    print(cluster_df['Class'])
    dice_df['Class'] = dice_df['Class'].replace(old_class, new_class)

cluster_df = cluster_df.sort_values(by='Class').reset_index(drop=True)
cluster_df = cluster_df.sort_index() 

dice_df = dice_df.sort_values(by='Class').reset_index(drop=True)
dice_df = dice_df.sort_index()

cluster_df.to_csv(f"{args.folder}/output/cluster_statistics_mapped.csv", index=False)
dice_df.to_csv(f"{args.folder}/output/dice_mapped.csv", index=False)