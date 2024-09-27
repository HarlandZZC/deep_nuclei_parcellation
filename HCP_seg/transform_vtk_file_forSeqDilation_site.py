import os
import glob
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
# conda activate DDSurfer 
# python ./HCP_seg/transform_vtk_file_forSeqDilation_site.py --SiteFolder folder1 --XfmFolder folder2 --num_workers 1

parser = argparse.ArgumentParser()
parser.add_argument('--SiteFolder', required=True)
parser.add_argument('--XfmFolder', required=True)
parser.add_argument('--num_workers', default=4, type=int)  
args = parser.parse_args()

SiteFolder = args.SiteFolder
XfmFolder = args.XfmFolder
num_workers = args.num_workers

def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path)
    print(f"----- transform vtk file (for SeqDilation) for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        DS_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/selected_pass_fibers/')
        sb_DS_folders = [f for f in os.listdir(DS_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-')]

        for sb_DS_folder in sb_DS_folders:
            tract_file = sb_DS_folder + '_pass_fibers-SeqDilation.vtk'
            xfm_file = subfolder_name[len("sub-"):] + '_acpc_dc2standard_itk.nii.gz'

            tract_path = os.path.join(DS_folder, sb_DS_folder, tract_file)
            xfm_path = os.path.join(XfmFolder, xfm_file)

            output_path = os.path.join(DS_folder, sb_DS_folder, f'{sb_DS_folder}_pass_fibers-SeqDilation-mni.vtk')
            
            command = [
                "/data01/software/Slicer-5.2.2-linux-amd64/Slicer",
                "--no-main-window",
                "--python-script",
                "/home/haolin/Research/Segmentation/harden_transform_with_slicer_haolin.py",
                tract_path,
                xfm_path,
                "0",
                output_path,
                "--python-code",
                "slicer.app.quit()"
            ]


            # Execute the command
            print(f"Processing {sb_DS_folder} ...")
            subprocess.call(command)


with ThreadPool(processes=num_workers) as pool:
    subfolders = [os.path.join(SiteFolder, f) for f in os.listdir(SiteFolder) if os.path.isdir(os.path.join(SiteFolder, f))]
    pool.map(process_subfolder, subfolders)
  