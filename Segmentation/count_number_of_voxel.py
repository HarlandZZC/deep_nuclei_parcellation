import os
import argparse
import nibabel as nib
import numpy as np
import pandas as pd
# conda activate DDSurfer 
# python /home/haolin/Research/Segmentation/count_number_of_voxel.py --folder folder --outcsv csv --labels 18 54

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, help='要处理的文件夹路径')
parser.add_argument('--outcsv', required=True, help='要输出的csv路径')
parser.add_argument('--labels', nargs='+', type=int)

args = parser.parse_args()

# 获取文件夹的路径
folder = args.folder
outcsv = args.outcsv
labels = args.labels

# Create an empty dictionary to store the results
results = {'subject_id': []}

# Add label columns to the results dictionary
for label in labels:
    results[f'label_{label}'] = []

subfolder_paths = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
for subfolder_path in subfolder_paths:
    subfolder_name = os.path.basename(subfolder_path)  # 获取子文件夹名称
    print(f"----- Count number of voxels for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        DS_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/DDSurfer/')
        sb_DS_folders = [f for f in os.listdir(DS_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-')]

        for sb_DS_folder in sb_DS_folders:
            wmparcniigz_file = sb_DS_folder + '-DDSurfer-wmparc.nii.gz'
            results['subject_id'].append(sb_DS_folder)
            
            # Load the wmparcniigz_file
            wmparc_file_path = os.path.join(DS_folder, sb_DS_folder, wmparcniigz_file)
            img = nib.load(wmparc_file_path)
            data = img.get_fdata()
            
            # Count voxel for each label
            for label in labels:
                voxel_count = np.sum(data == label)
                results[f'label_{label}'].append(voxel_count)
    
    # Create a DataFrame from the results dictionary
    df = pd.DataFrame(results)

    # Save the DataFrame to a CSV file
    df.to_csv(outcsv, index=False)





  