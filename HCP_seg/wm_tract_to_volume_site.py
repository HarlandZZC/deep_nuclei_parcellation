import os
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
# conda activate DDSurfer 
# python /home/haolin/Research/HCP_seg/wm_tract_to_volume_site.py --folder folder --f f --k k --iteration iter --num_workers 1

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, help='要处理的文件夹路径')
parser.add_argument('--num_workers', default=4, type=int, help='Number of threads')  
parser.add_argument("--f", required=True, type=int, help="Value of 'f'")
parser.add_argument("--k", required=True, type=int, help="Value of 'k'")
parser.add_argument("--iteration", required=True, type=int, help="Value of 'iteration'")
args = parser.parse_args()

# 获取文件夹的路径
folder = args.folder
num_workers = args.num_workers
f_value = args.f
k_value = args.k
iteration_value = args.iteration

# 定义处理函数
def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path)  # 获取子文件夹名称
    print(f"----- WM tract to volume for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        DS_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/DDSurfer/')
        sb_DS_folders = [f for f in os.listdir(DS_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-')]

        for sb_DS_folder in sb_DS_folders:
            refvolume_file = sb_DS_folder + '-DDSurfer-wmparc-mni.nii.gz'
            refvolume_path = os.path.join(DS_folder, sb_DS_folder, refvolume_file)
            inputVTK_folder_path = os.path.join(subfolder_path, f'{ses_folder}/dwi/atlas_split/', sb_DS_folder, f"atlas_f{f_value}_k{k_value}_iteration{iteration_value}")
            outputVol_folder_path = os.path.join(subfolder_path, f'{ses_folder}/dwi/WMtract2vol/', sb_DS_folder, f"atlas_f{f_value}_k{k_value}_iteration{iteration_value}")
            if not os.path.exists(outputVol_folder_path):
                os.makedirs(outputVol_folder_path)
            
            for filename in os.listdir(inputVTK_folder_path):
                # 检查文件是否以.vtp结尾
                if filename.endswith(".vtp"):
                    out_filename = os.path.splitext(filename)[0] + ".nii.gz"
                    # 构建命令
                    command = [
                        "python",
                        "/home/haolin/Research/Segmentation/wm_tract_to_volume.py",
                        os.path.join(inputVTK_folder_path, filename),
                        refvolume_path,
                        os.path.join(outputVol_folder_path, out_filename)
                    ]

                # Execute the command
                subprocess.call(command)


with ThreadPool(processes=num_workers) as pool:
    subfolders = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
    pool.map(process_subfolder, subfolders)
  