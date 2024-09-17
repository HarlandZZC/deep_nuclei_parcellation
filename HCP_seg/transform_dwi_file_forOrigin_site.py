import os
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
# source /data01/software/bashrc
# conda activate DDSurfer 
# python ./HCP_seg/transform_dwi_file_forOrigin_site.py --folder folder  --num_workers 1

parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, help='要处理的文件夹路径')
parser.add_argument('--num_workers', default=4, type=int, help='Number of workers')  
args = parser.parse_args()

folder = args.folder
num_workers = args.num_workers


def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path) 
    print(f"----- Transform DWI(for Origin) for {subfolder_name} -----") 
  
    nifti_path = os.path.join(subfolder_path, "ses-1", "dwi", f"{subfolder_name}_ses-1_run-1_dwi.nii.gz" )

    xfm_file = subfolder_name[len("sub-"):] + '_acpc_dc2standard_itk.nii.gz'

    atlas_T2 = "/home/haolin/Research/Segmentation/DDSurfer-main/100HCP-population-mean-T2-1mm.nii.gz"
    
    xfm_path = os.path.join("/data02/AmygdalaSeg/Processing/HCPall_xfms/", xfm_file)

    output_path = os.path.join(subfolder_path, "ses-1", "dwi", f"{subfolder_name}_ses-1_run-1_dwi-mni.nii.gz" )


    command = [
        "antsApplyTransforms",
        "-d",
        "3",
        "-i",
        nifti_path,
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
  