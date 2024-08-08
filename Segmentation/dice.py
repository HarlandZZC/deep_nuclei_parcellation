import os
import numpy as np
import nibabel as nib
import argparse
import csv
# python /home/haolin/Research/Segmentation/dice.py --folder folder --n_clusters c

def compute_dice_coefficient(mask1, mask2):
    intersection = np.sum(mask1 * mask2)
    denominator = np.sum(mask1) + np.sum(mask2)
    
    if intersection == 0 or denominator == 0:
        return 0.0
    else:
        return 2. * intersection / denominator

parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True)
parser.add_argument('--n_clusters', type=int, required=True, help='Number of clusters')
args = parser.parse_args()

folder = args.folder
sub_folders = [f for f in os.listdir(folder) if f.startswith('sub-')]

valid_clusters = range(1, args.n_clusters + 1)

dice_scores = {cluster: [] for cluster in valid_clusters}

for i, sub_folder_i in enumerate(sub_folders):
    file_path_i = os.path.join(folder, sub_folder_i, sub_folder_i + '_ses-1_run-1-DDSurfer-wmparc-mni-clustered.nii.gz')
    img_i = nib.load(file_path_i)
    data_i = img_i.get_fdata()

    for j, sub_folder_j in enumerate(sub_folders):
        if i >= j:
            continue

        file_path_j = os.path.join(folder, sub_folder_j, sub_folder_j + '_ses-1_run-1-DDSurfer-wmparc-mni-clustered.nii.gz')
        img_j = nib.load(file_path_j)
        data_j = img_j.get_fdata()

        for cluster in valid_clusters:
            mask_i = (data_i == cluster)
            mask_j = (data_j == cluster)
            dice_score= compute_dice_coefficient(mask_i, mask_j)
            dice_scores[cluster].append(dice_score)

average_dice_scores = {cluster: np.mean(scores) for cluster, scores in dice_scores.items()}

print('Average Dice scores:')
for cluster, score in average_dice_scores.items():
    print(f'Class {cluster}: {score}')

overall_average_dice_score = np.mean(list(average_dice_scores.values()))

with open(os.path.join(folder, 'dice.csv'), 'w', newline='') as csvfile:
    fieldnames = ['Class', 'Average Dice Score']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for cluster, score in average_dice_scores.items():
        writer.writerow({'Class': cluster, 'Average Dice Score': score})
    writer.writerow({'Class': 'Overall', 'Average Dice Score': overall_average_dice_score})

print('Average Dice scores have been written to dice.csv.')
