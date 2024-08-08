import os
# python /home/haolin/Research/HCP_seg/rename_file.py

def rename_brainmask_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith("BrainMask.nii.gz"):
                new_name = file.replace("BrainMask.nii.gz", "dwi_BrainMask.nii.gz")
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")

folder_path = ""  # 替换为你的文件夹路径
rename_brainmask_files(folder_path)
