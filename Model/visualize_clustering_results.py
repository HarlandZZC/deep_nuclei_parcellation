import os
import pandas as pd
import nibabel as nib
import numpy as np
import random
import torch
# python /data02/DWIsegmentation/Models/DCN_whole_amygdala/visualize_clustering_results.py --csv_file csv --subject_folder folder1 --outfolder folder2

def setup_seed(seed):
     torch.manual_seed(seed)
     torch.cuda.manual_seed_all(seed)
     np.random.seed(seed)
     random.seed(seed)
     torch.backends.cudnn.deterministic = True

setup_seed(42)

def main(csv_file, subject_folder, outfolder):
    df = pd.read_csv(csv_file)
    
    unique_subjects = df['subject_id'].unique()
    
    for subject_id in unique_subjects:
        print(f"Processing subject: {subject_id}")
        
        subject_outfolder = os.path.join(outfolder, subject_id)
        os.makedirs(subject_outfolder, exist_ok=True)
        
        input_path_wmparc = os.path.join(subject_folder, subject_id, 'ses-1', 'dwi', 'DDSurfer', f'{subject_id}_ses-1_run-1', f'{subject_id}_ses-1_run-1-DDSurfer-wmparc-mni.nii.gz')
        output_path_wmparc = os.path.join(subject_outfolder, f'{subject_id}_ses-1_run-1-DDSurfer-wmparc-mni.nii.gz')
        output_path_clustered = os.path.join(subject_outfolder, f'{subject_id}_ses-1_run-1-DDSurfer-wmparc-mni-clustered.nii.gz')
        
        print(f"Copying original file from {input_path_wmparc} to {output_path_wmparc}")
        os.system(f'cp {input_path_wmparc} {output_path_wmparc}')
        
        img = nib.load(output_path_wmparc)
        data = np.zeros_like(img.get_fdata())
        
        subject_data = df[df['subject_id'] == subject_id]
        for index, row in subject_data.iterrows():
            voxel_coordinates = eval(row['voxel_coordinate'])
            cluster_id = row['cluster_id']
            
            data[voxel_coordinates] = cluster_id
        
        clustered_img = nib.Nifti1Image(data, img.affine)
        nib.save(clustered_img, output_path_clustered)
        print(f"Saved clustered file to {output_path_clustered}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize clustering results")
    parser.add_argument("--csv_file", type=str, help="Path to the CSV file", default = "./Model/output/test_results.csv")
    parser.add_argument("--subject_folder", type=str, help="Path to the subject folder", default = "./site_folder_example")
    parser.add_argument("--outfolder", type=str, help="Output folder path", default= "./Model/output")
    
    args = parser.parse_args()
    
    main(args.csv_file, args.subject_folder, args.outfolder)

