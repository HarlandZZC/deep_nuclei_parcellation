import os
import glob
import argparse
import subprocess
import nibabel as nib
import numpy as np
import vtk
from multiprocessing.pool import ThreadPool
# conda activate DDSurfer 
# python /home/haolin/Research/HCP_seg/wm_select_by_endpoints_forOrigin_site.py --folder folder --num_workers 1

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, help='要处理的文件夹路径')
parser.add_argument('--num_workers', default=4, type=int, help='Number of threads')  
args = parser.parse_args()

# 获取文件夹的路径
folder = args.folder
num_workers = args.num_workers

# 清空日志文件夹
txt_path = "/home/haolin/Research/HCP_seg/missing_labels_inselect.txt"

try:
    with open(txt_path, "w") as file:
        file.truncate(0)  # 清空文件内容
    print(f"Content of {txt_path} has been cleared.")
except FileNotFoundError:
    print(f"File {txt_path} not found.")
except Exception as e:
    print(f"An error occurred: {e}")


# 定义处理函数
def process_subfolder(subfolder_path):
    subfolder_name = os.path.basename(subfolder_path)  # 获取子文件夹名称
    print(f"----- WM select by endpoints (forOrigin) for {subfolder_name} -----") 
    ses_folders = [f for f in os.listdir(subfolder_path) if f.startswith('ses-') and os.path.isdir(os.path.join(subfolder_path, f))]
    
    for ses_folder in ses_folders:
        DS_folder = os.path.join(subfolder_path, f'{ses_folder}/dwi/WMadded/')
        sb_DS_folders = [f for f in os.listdir(DS_folder) if f.startswith(f'{subfolder_name}_{ses_folder}_run-')]

        for sb_DS_folder in sb_DS_folders:
            print(f"processing {sb_DS_folder}")
            wmparcniigz_file = sb_DS_folder + '-DDSurfer-wmparc.nii.gz'
            tract_file = sb_DS_folder + '-WMadded.vtk'

            wmparcniigz_path = os.path.join(subfolder_path, f'{ses_folder}/dwi/DDSurfer/', sb_DS_folder, wmparcniigz_file)
            tract_path = os.path.join(DS_folder, sb_DS_folder, tract_file)
            output_path = os.path.join(subfolder_path, f'{ses_folder}/dwi/selected_by_endpoints/', sb_DS_folder)
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            img = nib.load(wmparcniigz_path)
            data = img.get_fdata()

            # 2. 找到里面的18和54两个label
            label_18 = 18
            label_54 = 54


            # 初始标签获取
            all_labels = find_other_labels(sb_DS_folder, data, label_18, label_54)
            new_labels = set(all_labels)

            # 添加符合条件的标签
            for label in range(1000, 1036):
                if label not in all_labels:
                    new_labels.add(label)

            for label in range(2000, 2036):
                if label not in all_labels:
                    new_labels.add(label)

            print(f"all_labels: {all_labels}")
            print(f"new_labels: {new_labels}")

            # 3. 写一个循环，遍历18与所有label中除了18和54以外的所有label，调用wm_select_by_endpoints.py进行处理。
            for label in new_labels:
                if label != label_18 and label != label_54 and label in all_labels:
                    call_wm_select_by_endpoints(label_18, label, tract_path, output_path, sb_DS_folder, 1)
                elif label != label_18 and label != label_54 and label not in all_labels:
                    call_wm_select_by_endpoints(label_18, label, tract_path, output_path, sb_DS_folder, 0)

            # 4. 写一个循环，遍历54与所有label中除了18和54以外的所有label，调用wm_select_by_endpoints.py进行处理。
            for label in new_labels:
                if label != label_18 and label != label_54 and label in all_labels:
                    call_wm_select_by_endpoints(label_54, label, tract_path, output_path, sb_DS_folder, 1) 
                elif label != label_18 and label != label_54 and label not in all_labels:
                    call_wm_select_by_endpoints(label_54, label, tract_path, output_path, sb_DS_folder, 0)


            call_wm_select_by_endpoints(label_18, label_54, tract_path, output_path, sb_DS_folder, 1) 
           

def find_other_labels(sb_DS_folder, data, target_label1, target_label2):
    all_labels = set(data.flatten())
    all_labels.remove(0)  

    try:
        all_labels.remove(target_label1)
    except KeyError:
        print(f"Target label {target_label1} not found in {sb_DS_folder}, skipping removal.")
        with open("/home/haolin/Research/HCP_seg/missing_labels_inselect.txt", "a") as file:
            file.write(f"Target label {target_label1} not found in {sb_DS_folder}\n")
    
    try:
        all_labels.remove(target_label2)
    except KeyError:
        print(f"Target label {target_label2} not found in {sb_DS_folder}, skipping removal.")
        with open("/home/haolin/Research/HCP_seg/missing_labels_inselect.txt", "a") as file:
            file.write(f"Target label {target_label2} not found in {sb_DS_folder}\n")

    # Remove labels that are not within the specified ranges
    valid_ranges = set(range(1000, 1036)).union(set(range(2000, 2036)))
    all_labels = all_labels.intersection(valid_ranges)

    return all_labels



def call_wm_select_by_endpoints(label1, label2, tract_path, output_path, sb_DS_folder, run_flag):
    label1 = int(label1)
    label2 = int(label2)

    output_file = f'{output_path}/{sb_DS_folder}_{label1}-{label2}.vtk'
    # print(run_flag)

    if run_flag == 1:
        if os.path.exists(output_file):
            print(f"Output file {output_file} already exists. Skipping subprocess call.")
        else:
            cmd = [
                "python",
                "/home/haolin/Research/Segmentation/wm_select_by_endpoints.py",
                tract_path,
                output_file,
                "-l", "ROI_label_wmparc",
                "-o", "and",
                "-p",
                f'{label1}', 
                f'{label2}'
            ] 
            subprocess.call(cmd)

    elif run_flag == 0:
        # Create an empty vtk file
        polydata = vtk.vtkPolyData()  # 创建一个空的 vtkPolyData 对象

        # 创建一个 vtkPolyDataWriter 对象来写入文件
        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(output_file)
        writer.SetInputData(polydata)

        # 写入 VTK 文件
        writer.Write()

        print(f"Created empty output file {output_file}.")



with ThreadPool(processes=num_workers) as pool:
    subfolders = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
    pool.map(process_subfolder, subfolders)