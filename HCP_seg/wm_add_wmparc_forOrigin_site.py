import os
import glob
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
# conda activate DDSurfer 
# python ./HCP_seg/wm_add_wmparc_forOrigin_site.py --SiteFolder folder1 --TractFolder folder2 --num_workers 1


parser = argparse.ArgumentParser()
parser.add_argument('--SiteFolder', required=True, help='要处理的文件夹路径')
parser.add_argument('--TractFolder', required=True, help='包含Tractography的文件夹路径')
parser.add_argument('--num_workers', default=4, type=int, help='Number of workers')  
args = parser.parse_args()


SiteFolder = args.SiteFolder
TractFolder = args.TractFolder
num_workers = args.num_workers


def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path)  
    print(f"----- WM add wmparc (for Origin) for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        DS_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/DDSurfer/')
        sb_DS_folders = [f for f in os.listdir(DS_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-')]

        for sb_DS_folder in sb_DS_folders:
            wmparcniigz_file = sb_DS_folder + '-DDSurfer-wmparc.nii.gz'
            tract_file = subfolder_name[len("sub-"):] + '-ukftrack_b3000_fsmask_421a7ad_minGA0.06_minFA0.08_seedFALimit0.1.vtk'

            wmparcniigz_path = os.path.join(DS_folder, sb_DS_folder, wmparcniigz_file)
            tract_path = os.path.join(TractFolder, tract_file)
            output_path = os.path.join(subfolder_path, f'{ses_folder}/dwi/WMadded/{sb_DS_folder}/{sb_DS_folder}-WMadded.vtk')
            
      
            command = [
                "python",
                "/home/haolin/Research/Segmentation/wm_add_wmparc.py",
                tract_path,
                wmparcniigz_path,
                output_path
            ]

            # Execute the command
            print(f"Processing {sb_DS_folder} ...")
            subprocess.call(command)


with ThreadPool(processes=num_workers) as pool:
    subfolders = [os.path.join(SiteFolder, f) for f in os.listdir(SiteFolder) if os.path.isdir(os.path.join(SiteFolder, f))]
    pool.map(process_subfolder, subfolders)
  