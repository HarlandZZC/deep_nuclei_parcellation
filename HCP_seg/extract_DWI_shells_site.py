import os
import argparse
import subprocess
import csv
# python /home/haolin/Research/HCP_seg/extract_DWI_shells_site.py --folder folder 

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, help='要处理的文件夹路径')
args = parser.parse_args()

# 获取文件夹的路径
folder = args.folder
subfolders = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]

command = [
    "/data01/software/MATLAB/R2022b/bin/matlab",
    "-nodisplay", "-nosplash", "-nodesktop",
    "-r"
]

run_script = "addpath(genpath('/home/haolin/Research/Segmentation/MK-Curve-master'));" 

for subfolder_path in subfolders:
    subfolder_name = os.path.basename(subfolder_path)  # 获取子文件夹名称
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]

    for ses_folder in ses_folders:
        dwi_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi')
        dwi_files = [f for f in os.listdir(dwi_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-') and f.endswith('_dwi.nii.gz')]
        
        for dwi_file in dwi_files:
            run_id = dwi_file.split('_run-')[1].split('_dwi.nii.gz')[0]
            case_id = f"{subfolder_name}_{ses_folder}_run-{run_id}"
            dwi_nifti_path = os.path.join(dwi_folder, f"{subfolder_name}_{ses_folder}_run-{run_id}_dwi.nii.gz")
            bval_path = os.path.join(dwi_folder, f"{subfolder_name}_{ses_folder}_run-{run_id}_dwi.bval")
            bvec_path = os.path.join(dwi_folder, f"{subfolder_name}_{ses_folder}_run-{run_id}_dwi.bvec")
            
            out_dwi_nifti_path = os.path.join(dwi_folder, f"corrected_masked/{subfolder_name}_{ses_folder}_run-{run_id}_dwi_extracted.nii.gz")
            out_bval_path = os.path.join(dwi_folder, f"corrected_masked/{subfolder_name}_{ses_folder}_run-{run_id}_dwi_extracted.bval")
            out_bvec_path = os.path.join(dwi_folder, f"corrected_masked/{subfolder_name}_{ses_folder}_run-{run_id}_dwi_extracted.bvec")

            removed_bvals = []

            with open('/data02/AmygdalaSeg/Processing/statistics_bval_HCP100.csv') as f:
                reader = csv.reader(f) 
                next(reader) # 跳过第一行
                for row in reader:
                    bval = int(row[0])
                    if bval < 0 or bval > 1020:  
                        removed_bvals.append(bval)
            print(f"removed_bvals for {case_id}:{removed_bvals}")
            removed_bvals_str = ",".join(map(str, removed_bvals))


            # Execute the command
            print(f"Command append for {case_id} ...")
            run_script = run_script + f"extract_DWI_shells_for_python('{dwi_nifti_path}', '{bval_path}', '{bvec_path}', '{removed_bvals_str}', '{out_dwi_nifti_path}', '{out_bval_path}','{out_bvec_path}');"

run_script = run_script + "exit"
command.append(run_script)
# 将命令列表转换为字符串
# command_str = " ".join(command)
print("start running...")
subprocess.call(command)
