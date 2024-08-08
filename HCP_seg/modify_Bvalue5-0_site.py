import os
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
# python /home/haolin/Research/HCP_seg/modify_Bvalue5-0_site.py --folder folder --num_workers 1

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, help='要处理的文件夹路径')
parser.add_argument('--num_workers', default=4, type=int, help='Number of threads')  
args = parser.parse_args()

# 获取文件夹的路径
folder = args.folder
num_workers = args.num_workers

# 定义处理函数
def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path)  # 获取子文件夹名称
    print(f"----- modify Bvalue 5-0 for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]

    
    for ses_folder in ses_folders:
        dwi_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/corrected_masked')
        dwi_files = [f for f in os.listdir(dwi_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-') and f.endswith('_dwi_extracted.nii.gz')]
        

        for dwi_file in dwi_files:
            run_id = dwi_file.split('_run-')[1].split('_dwi_extracted.nii.gz')[0]
            
            bval_path = os.path.join(dwi_folder, f"{subfolder_name}_{ses_folder}_run-{run_id}_dwi_extracted.bval")
            bvec_path = os.path.join(dwi_folder, f"{subfolder_name}_{ses_folder}_run-{run_id}_dwi_extracted.bvec")
            
            out_bval_path = os.path.join(dwi_folder, f"{subfolder_name}_{ses_folder}_run-{run_id}_dwi_extracted-Bvalue5-0.bval")
            out_bvec_path = os.path.join(dwi_folder, f"{subfolder_name}_{ses_folder}_run-{run_id}_dwi_extracted-Bvalue5-0.bvec")
            
            # 生成命令行
            command = [
                "python", 
                "/home/haolin/Research/Segmentation/modify_Bvalue5-0.py",
                "--inbval", 
                bval_path,
                "--inbvec", 
                bvec_path,
                "--outbval", 
                out_bval_path,
                "--outbvec",
                out_bvec_path
            ]

            subprocess.call(command)


with ThreadPool(processes=num_workers) as pool:
    subfolders = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
    pool.map(process_subfolder, subfolders)
  