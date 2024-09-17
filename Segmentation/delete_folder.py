import os
import argparse
import shutil
# python ./Segmentation/delete_folder.py --process_folder folder1 --delete_folder folder2

def delete_folders_with_name(root_folder, folder_name):
    for root, dirs, files in os.walk(root_folder, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if folder == folder_name:
                print(f"deleting: {folder_path}")
                try:
                    shutil.rmtree(folder_path)
                    print(f"deleted: {folder_path}")
                except OSError as e:
                    print(f"can not delete: {folder_path}, error: {e}")

def main(process_folder, delete_folder):
    delete_folders_with_name(process_folder, delete_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="delete folders with the same name in the root folder")
    parser.add_argument("--process_folder", required=True, help="root folder to process")
    parser.add_argument("--delete_folder", required=True, help="folder name to delete")
    args = parser.parse_args()
    
    main(args.process_folder, args.delete_folder)

