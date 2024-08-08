import os
import glob
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
# python /home/haolin/Research/HCP_seg/copy_mni_vtk_forSeqDilation_site.py --SiteFolder folder1 --OutFolder folder2 --num_workers 1

# 解析命令行参数s
parser = argparse.ArgumentParser()
parser.add_argument('--SiteFolder', required=True, help='要处理的文件夹路径')
parser.add_argument('--OutFolder', required=True, help='复制到的文件夹路径')
parser.add_argument('--num_workers', default=4, type=int, help='Number of workers')  
args = parser.parse_args()

# 获取文件夹的路径
SiteFolder = args.SiteFolder
OutFolder = args.OutFolder
num_workers = args.num_workers

# 定义处理函数
def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path)  # 获取子文件夹名称
    print(f"----- copy mni vtk file (for SeqDilation) for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        DS_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/selected_pass_fibers/')
        sb_DS_folders = [f for f in os.listdir(DS_folder) if f.startswith(f'{subfolder_name}_ses-1_run-1')]

        for sb_DS_folder in sb_DS_folders:
            tract_file = sb_DS_folder + '_pass_fibers-SeqDilation-mni.vtk'
            tract_path = os.path.join(DS_folder, sb_DS_folder, tract_file)

            # 生成命令行
            command = [
                "cp",
                tract_path,
                f"{OutFolder}/"
            ]

            # Execute the command
            print(f"Copying {sb_DS_folder} ...")
            subprocess.call(command)

os.makedirs(OutFolder)
with ThreadPool(processes=num_workers) as pool:
    subfolders = [os.path.join(SiteFolder, f) for f in os.listdir(SiteFolder) if os.path.isdir(os.path.join(SiteFolder, f))]
    pool.map(process_subfolder, subfolders)
  