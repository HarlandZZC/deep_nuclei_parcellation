import os
import glob
import argparse
import subprocess
# conda activate DDSurfer 
# python /home/haolin/Research/HCP_seg/process_site.py --folder folder --flip 1

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, help='文件夹路径')
parser.add_argument('--flip', type=int, required=True, help='Flip value (0 or 1)')
args = parser.parse_args()

# 获取文件夹的路径
folder = args.folder
flip = args.flip

# 获取文件夹中的所有子文件夹
subfolders = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]

# 定义处理函数
def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path)  # 获取子文件夹名称
    print(f"----- DDSurfer for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        dwi_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/corrected_masked/')
        dwi_files = [f for f in os.listdir(dwi_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-') and f.endswith('_dwi_extracted.nii.gz')]
        
        for dwi_file in dwi_files:
            bval_file = dwi_file.replace('.nii.gz', '-Bvalue5-0.bval')
            bvec_file = dwi_file.replace('.nii.gz', '-Bvalue5-0.bvec')
            mask_file = dwi_file.replace('_extracted.nii.gz', '_BrainMask.nii.gz')

            dwi_path = os.path.join(dwi_folder, dwi_file)
            bval_path = os.path.join(dwi_folder, bval_file)
            bvec_path = os.path.join(dwi_folder, bvec_file)
            mask_path = os.path.join(dwi_folder, mask_file)

            run_id = dwi_file.split('_run-')[1].split('_dwi_extracted.nii.gz')[0]
            subID = f"{subfolder_name}_{ses_folder}_run-{run_id}"

            DDSurfer_output_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/DDSurfer/{subID}')
            print("Target folder path:", DDSurfer_output_folder)
            
            # 生成命令行
            command = [
                "bash",
                "/home/haolin/Research/HCP_seg/process_command.sh",
                "--dwi", dwi_path,
                "--bval", bval_path,
                "--bvec", bvec_path,
                "--mask", mask_path,
                "--subID", subID,
                "--inputdir", dwi_folder,
                "--outputdir", DDSurfer_output_folder,
                "--flip", str(flip),  # Convert flip to string as it is an int
            ]

            # Execute the command
            print(f"Processing {dwi_path} ...")
            subprocess.call(command)

            for file in glob.glob(os.path.join(DDSurfer_output_folder, '*')):
                if "FractionalAnisotropy" not in file:
                    os.remove(file)


# 处理每个子文件夹
for subfolder in subfolders:
    process_subfolder(subfolder)

