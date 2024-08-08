import os
# python /home/haolin/Research/HCP_seg/rename_folder.py

def rename_folders(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            if dir_name == "selected_ByEndPoints":
                old_path = os.path.join(root, dir_name)
                new_name = dir_name.replace("selected_ByEndPoints", "selected_by_endpoints")
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")

folder_path = ""  # 替换为你的文件夹路径
rename_folders(folder_path)
