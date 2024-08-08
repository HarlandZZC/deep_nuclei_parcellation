import os
import argparse
# python /home/haolin/Research/Segmentation/check_subfolders_after_WMadd.py --folder folder

def check_wmadded_structure(subject_folder, session_folder):
    wmadded_folder = os.path.join(subject_folder, session_folder, "dwi", "WMadded")
    
    if not os.path.exists(wmadded_folder):
        print(f"受访者：{subject_folder}，会话：{session_folder} 下找不到 WMadded 文件夹。")
        return False
    
    # 检查 WMadded 中的子目录
    wmadded_subdirs = [subdir for subdir in os.listdir(wmadded_folder) if os.path.isdir(os.path.join(wmadded_folder, subdir))]
    
    if not wmadded_subdirs:
        print(f"在受访者：{subject_folder}，会话：{session_folder} 下未找到 WMadded 的子目录。")
        return False
    
    all_files_exist = True  # 假设所有文件都存在
    
    # 检查每个子目录中是否有 vtk 文件
    for subdir in wmadded_subdirs:
        subdir_path = os.path.join(wmadded_folder, subdir)
        vtk_files = [file for file in os.listdir(subdir_path) if file.endswith(".vtk")]
        
        if not vtk_files:
            print(f"在 WMadded 子目录：{subdir_path} 中未找到 VTK 文件。")
            all_files_exist = False
    
    if all_files_exist:
        print(f"受访者：{subject_folder}，会话：{session_folder} 的所有文件都存在。")
    
    return all_files_exist

def check_sessions(root_folder):
    for subject_folder in os.listdir(root_folder):
        full_subject_folder = os.path.join(root_folder, subject_folder)
        if os.path.isdir(full_subject_folder):
            for session_folder in os.listdir(full_subject_folder):
                full_session_folder = os.path.join(full_subject_folder, session_folder)
                if os.path.isdir(full_session_folder):
                    check_wmadded_structure(full_subject_folder, session_folder)

def main(root_folder):
    check_sessions(root_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="检查受访者的 WMadded 结构。")
    parser.add_argument("--folder", required=True, help="包含受访者文件夹的根文件夹路径。")
    args = parser.parse_args()
    
    main(args.folder)

