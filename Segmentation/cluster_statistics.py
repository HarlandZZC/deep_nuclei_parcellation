import os
import argparse
import nibabel as nib
import numpy as np
import csv
# python /home/haolin/Research/Segmentation/cluster_statistics.py --infolder folder

parser = argparse.ArgumentParser()
parser.add_argument('--infolder', required=True)
args = parser.parse_args()

folder = args.infolder

sub_folders = [f for f in os.listdir(folder) if f.startswith('sub-')]

class_counts = {}
total_voxels = 0

for sub_folder in sub_folders:
    file_path = os.path.join(folder, sub_folder, sub_folder + '_ses-1_run-1-DDSurfer-wmparc-mni-clustered.nii.gz')
    
    img = nib.load(file_path)
    data = img.get_fdata()

    valid_clusters = np.unique(data)[1:]
    
    for cluster in valid_clusters:
        if cluster not in class_counts:
            class_counts[cluster] = 0
            
        class_counts[cluster] += (data == cluster).sum()
    
    total_voxels += (data != 0).sum()

print('Class counts:')
counts = []
percentages = []
for c, count in class_counts.items():
    percentage = count/total_voxels
    print(f'Class {c}: {count} voxels ({percentage:.2%} of total)')
    counts.append(count)
    percentages.append(percentage)

with open(os.path.join(folder, 'cluster_statistics.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Class', 'Count', 'Percentage'])
    for c, count in class_counts.items():
        percentage = count / total_voxels
        writer.writerow([c, count, percentage])

    # 计算'Count'和'Percentage'的方差和标准差
    count_variance = np.var(counts)
    count_std = np.std(counts)
    percentage_variance = np.var(percentages)
    percentage_std = np.std(percentages)

    # 将方差和标准差添加到csv文件的最后一行
    writer.writerow(['Variance', count_variance, percentage_variance])
    writer.writerow(['Standard Deviation', count_std, percentage_std])