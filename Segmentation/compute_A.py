import os
import nibabel as nib  
from sklearn.metrics import calinski_harabasz_score
from scipy.ndimage import label, generate_binary_structure, find_objects
import numpy as np
import multiprocessing as mp
import csv
import argparse
# python ./Segmentation/compute_A.py --incsv csv --labels --infolder folder


def compute_agglomeration(coordinates, labels):
    unique_labels = np.unique(labels)

    total_voxels = len(coordinates)
    max_agglomeration = 0

    for label_value in unique_labels:
        label_indices = np.where(labels == label_value)[0]
        label_coordinates = coordinates[label_indices]

        # Create a binary mask with ones at label coordinates
        binary_mask = np.zeros(coordinates.max(axis=0) + 1, dtype=bool)
        binary_mask[tuple(label_coordinates.T)] = 1

        # Label connected components in the binary mask
        structure = generate_binary_structure(3, 1)
        labeled_array, num_features = label(binary_mask, structure=structure)

        max_agglomeration_for_label = 0

        for i in range(1, num_features + 1):
            cluster_size = np.sum(labeled_array == i)
            max_agglomeration_for_label = max(max_agglomeration_for_label, cluster_size)

        max_agglomeration += max_agglomeration_for_label

    agglomeration_ratio = max_agglomeration / total_voxels
    return agglomeration_ratio

def compute_agglomeration_ratio(folder, label_values):
    results = []

    for subdir in os.listdir(folder):
        if subdir.startswith('sub-'):
            print(f"processing {subdir}")
            file_path = os.path.join(folder, subdir, f'{subdir}_ses-1_run-1-DDSurfer-wmparc-mni-clustered.nii.gz')
            if os.path.exists(file_path):
                img = nib.load(file_path)
                data = img.get_fdata()
                
                labels = []
                coordinates = []
                sides = []
                
                data_dict = {}

                with open(args.incsv) as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        key = (row[0], row[3])
                        data_dict[key] = int(row[1])

                for i in range(data.shape[0]):
                    for j in range(data.shape[1]):
                        for k in range(data.shape[2]):
                            if data[i,j,k] != 0:
                                labels.append(data[i, j, k])
                                coordinates.append([i, j, k])
                                str_lst = "(" + ", ".join(map(str, [i, j, k])) + ")"
                                key = (subdir, str_lst)
                                if key in data_dict:
                                    sides.append(data_dict[key])
                
                sides = np.array(sides)
                coordinates = np.array(coordinates)
                labels = np.array(labels)
                
                scores = []
                for label_value in label_values:
                    idx = (sides == label_value)
                    score = compute_agglomeration(coordinates[idx], labels[idx])
                    print(f'agglomeration_ratio for {subdir} label {label_value}: {score}')
                    result = {'subdir': subdir, 'label': label_value, 'score': score}
                    results.append(result)

    with open(os.path.join(args.infolder, 'A.csv'), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['subdir', 'label', 'score'])
        writer.writeheader()
        
        for result in results:
            writer.writerow(result)
           
        scores = [r['score'] for r in results]
        mean_score = np.mean(scores)
        max_score = np.max(scores)
        min_score = np.min(scores)

        writer.writerow({'subdir': 'mean', 'label': '', 'score': mean_score})
        writer.writerow({'subdir': 'max', 'label': '', 'score': max_score})
        writer.writerow({'subdir': 'min', 'label': '', 'score': min_score})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute A")
    parser.add_argument("--infolder", type=str, help="infolder")
    parser.add_argument("--incsv", type=str, help="incsv", default="/home/haolin/Research/HCP_seg/DCN_whole_amygdala/dataset_HCP100/f9000_k150_iteration2_label18_54_append_binary_smooth_gaussian_loc1_scale1.csv")
    parser.add_argument("--labels", nargs='+', type=int, help="label values to compute agglomeration ratio", required=True)

    args = parser.parse_args()

    compute_agglomeration_ratio(args.infolder, args.labels)

