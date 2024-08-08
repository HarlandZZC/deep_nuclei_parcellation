import os
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
# 使用前在代码中修改region
# conda activate DDSurfer 
# python /home/haolin/Research/HCP_seg/sequential_region_dilation_site.py --folder folder --num_workers 1

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
    print(f"----- Region dilation for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        DS_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/DDSurfer/')
        sb_DS_folders = [f for f in os.listdir(DS_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-')]

        for sb_DS_folder in sb_DS_folders:
            wmparcniigz_file = sb_DS_folder + '-DDSurfer-wmparc.nii.gz'

            wmparcniigz_path = os.path.join(DS_folder, sb_DS_folder, wmparcniigz_file)
            output_path = os.path.join(DS_folder, sb_DS_folder, sb_DS_folder + '-DDSurfer-wmparc-SeqDilation.nii.gz')
            
            # 生成 label_numbers 列表
            label_numbers = [10, 49]  # 添加单独的数字

            # # 添加范围 1000-1035 的数字
            # for num in range(1000, 1036):
            #     label_numbers.append(num)

            # # 添加范围 2000-2035 的数字
            # for num in range(2000, 2036): 
            #     label_numbers.append(num)

            # 将列表中的数字添加到 --labels 参数中
            labels_param = "--labels " + " ".join(map(str, label_numbers))

            # 构建命令
            command = [
                "python",
                "/home/haolin/Research/Segmentation/region_dilation_sequentially.py",
                "--in_file",
                wmparcniigz_path,
                "--out_file",
                output_path,
            ]
            command.extend(labels_param.split())  # 添加 --labels 参数到命令中



            # Execute the command
            subprocess.call(command)


with ThreadPool(processes=num_workers) as pool:
    subfolders = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
    pool.map(process_subfolder, subfolders)
  