import os
import argparse
# python ./Segmentation/check_subfolders_after_WMadd.py --folder folder

def check_wmadded_structure(subject_folder, session_folder):
    wmadded_folder = os.path.join(subject_folder, session_folder, "dwi", "WMadded")
    
    if not os.path.exists(wmadded_folder):
        print(f"subject: {subject_folder}, session: {session_folder} can not find WMadded folder")
        return False
    

    wmadded_subdirs = [subdir for subdir in os.listdir(wmadded_folder) if os.path.isdir(os.path.join(wmadded_folder, subdir))]
    
    if not wmadded_subdirs:
        print(f"subject: {subject_folder}, session:: {session_folder} can not find WMadded folder")
        return False
    
    all_files_exist = True 
    
 
    for subdir in wmadded_subdirs:
        subdir_path = os.path.join(wmadded_folder, subdir)
        vtk_files = [file for file in os.listdir(subdir_path) if file.endswith(".vtk")]
        
        if not vtk_files:
            print(f"in WMadded sublist: {subdir_path} can not find vtk")
            all_files_exist = False
    
    if all_files_exist:
        print(f"subjevt: {subject_folder}, session: {session_folder} all files exist")
    
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    args = parser.parse_args()
    
    main(args.folder)

