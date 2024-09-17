import os
import argparse
# python ./Segmentation/delete_file.py --process_folder folder1 --delete_file file
def delete_files_with_name(root_folder, file_name):
    for root, dirs, files in os.walk(root_folder, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            if file == file_name:
                print(f"deleting: {file_path}")
                try:
                    os.remove(file_path)
                    print(f"deleted: {file_path}")
                except OSError as e:
                    print(f"can not delete: {file_path},error: {e}")

def main(process_folder, delete_file):
    delete_files_with_name(process_folder, delete_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="delete files with the same name in the root folder")
    parser.add_argument("--process_folder", required=True, help="root folder to process")
    parser.add_argument("--delete_file", required=True, help="file name to delete")
    args = parser.parse_args()
    
    main(args.process_folder, args.delete_file)
