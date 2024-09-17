import os
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
# conda activate DDSurfer 
# python ./HCP_seg/generate_csv_for_site.py --folder folder --f f --k k --iteration iter --labels 18 54 

parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, help='要处理的文件夹路径')
parser.add_argument("--f", required=True, type=int, help="Value of 'f'")
parser.add_argument("--k", required=True, type=int, help="Value of 'k'")
parser.add_argument("--iteration", required=True, type=int, help="Value of 'iteration'")
parser.add_argument('--labels', nargs='+', type=int, required=True, help='关注的labels')
args = parser.parse_args()

folder = args.folder
f_value = args.f
k_value = args.k
iteration_value = args.iteration
label_list = args.labels

def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path)
    print(f"----- Reading csv for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        DS_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/DDSurfer/')
        sb_DS_folders = [f for f in os.listdir(DS_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-')]

        for sb_DS_folder in sb_DS_folders:
            refvolume_file = sb_DS_folder + '-DDSurfer-wmparc-mni.nii.gz'
            refvolume_path = os.path.join(DS_folder, sb_DS_folder, refvolume_file)

            atlas_nifti_folder = f"atlas_f{f_value}_k{k_value}_iteration{iteration_value}"
            atlas_nifti_path = os.path.join(subfolder_path, f'{ses_folder}/dwi/WMtract2vol/', sb_DS_folder, atlas_nifti_folder)

            for label in label_list:
                output_file = f"label{label}.csv"
                output_csv_folder_path = os.path.join(subfolder_path, f'{ses_folder}/dwi/csv_for_segmentation/', sb_DS_folder, atlas_nifti_folder)
                if not os.path.exists(output_csv_folder_path):
                    os.makedirs(output_csv_folder_path)

                output_csv_path = os.path.join(output_csv_folder_path, output_file)

                command = [
                    "python",
                    "/home/haolin/Research/Segmentation/generate_csv_per_subject.py",
                    "--refvolume",
                    refvolume_path,
                    "--atlas_nifti_folder",
                    atlas_nifti_path,
                    "--label_concerned",
                    f"{label}",
                    "--csv",
                    output_csv_path
                ]

                # Execute the command
                subprocess.call(command)

    
subfolders = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
for subfolder in subfolders:
    process_subfolder(subfolder)

  