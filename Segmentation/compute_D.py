import os
import nibabel as nib  
from sklearn.metrics import davies_bouldin_score
import numpy as np
import multiprocessing as mp
import csv
import argparse
# python ./Segmentation/compute_D.py --infolder folder --incsv csv 

def compute_davies_bouldin_score(folder):
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
                idx18 = (sides == 18) 
                idx54 = (sides == 54)
                # print(len(labels))
                # print(len(coordinates))
                # print(len(sides))

                # print(len(labels[idx18]))
                # print(len(coordinates[idx18]))

                score18 = davies_bouldin_score(coordinates[idx18], labels[idx18])
                print(f'davies_bouldin_score for {subdir} label 18: {score18}')
                score54 = davies_bouldin_score(coordinates[idx54], labels[idx54])
                print(f'davies_bouldin_score for {subdir} label 54: {score54}')

                result1 = {'subdir': subdir, 'label': 18, 'score': score18}

                result2 = {'subdir': subdir, 'label': 54, 'score': score54}
                results.extend([result1, result2])

    # Write results to CSV file
    with open(os.path.join(args.infolder, 'D.csv'), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['subdir', 'label', 'score'])
        writer.writeheader()
        
        for result in results:
            writer.writerow(result)
           
        # Calculate summary statistics
        scores = [r['score'] for r in results]
        mean_score = np.mean(scores)
        max_score = np.max(scores)
        min_score = np.min(scores)

        # Write summary rows
        writer.writerow({'subdir': 'mean', 'label': '', 'score': mean_score})
        writer.writerow({'subdir': 'max', 'label': '', 'score': max_score})
        writer.writerow({'subdir': 'min', 'label': '', 'score': min_score})


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compute D")
    parser.add_argument("--infolder", type=str, help="infolder")
    parser.add_argument("--incsv", type=str, help="incsv", default= "/data02/AmygdalaSeg/Processing/HCP100/f9000_k150_iteration2_label18_54_append_binary.csv")

    args = parser.parse_args()

    compute_davies_bouldin_score(args.infolder)



