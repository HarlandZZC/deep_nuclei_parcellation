import os
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
# source /data01/software/bashrc
# conda activate DDSurfer 
# python ./HCP_seg/transform_FA_file_site.py --folder folder  --num_workers 1

parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, help='要处理的文件夹路径')
parser.add_argument('--num_workers', default=4, type=int, help='Number of workers')  
args = parser.parse_args()

folder = args.folder
num_workers = args.num_workers


def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path) 
    print(f"----- Transform FA for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        DS_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/FA/')
        sb_DS_folders = [f for f in os.listdir(DS_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-')]

        for sb_DS_folder in sb_DS_folders:
            FA_file = sb_DS_folder + '-dti-FractionalAnisotropy.nii.gz'
            xfm_file = subfolder_name[len("sub-"):] + '_acpc_dc2standard_itk.nii.gz'

            atlas_T2 = "/home/haolin/Research/Segmentation/DDSurfer-main/100HCP-population-mean-T2-1mm.nii.gz"
            
            xfm_path = os.path.join("/data02/DWIsegmentation/Data/HCPall_xfms/", xfm_file)
            FA_path = os.path.join(DS_folder, sb_DS_folder, FA_file)
            output_path = os.path.join(DS_folder, sb_DS_folder, sb_DS_folder + '-dti-FractionalAnisotropy-mni.nii.gz')

            command = [
                "antsApplyTransforms",
                "-d",
                "3",
                "-i",
                FA_path,
                "-r",
                atlas_T2,
                "-t",
                xfm_path,
                "-o",
                output_path,
                "-n",
                "NearestNeighbor"
            ]

            # Execute the command
            subprocess.call(command)


with ThreadPool(processes=num_workers) as pool:
    subfolders = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
    pool.map(process_subfolder, subfolders)
  