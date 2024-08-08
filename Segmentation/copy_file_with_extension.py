import argparse
import os
import shutil
# python /home/haolin/Research/Segmentation/copy_file_with_extension.py --source_dir folder1 --target_dir folder2 --extension 

def copy_files_with_extension(source_dir, target_dir, extension):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(extension):
                source_path = os.path.join(root, file)
                target_path = os.path.join(target_dir, file)
                shutil.copy2(source_path, target_path)
                print(f"Copied {file} to {target_dir}")

def main():
    parser = argparse.ArgumentParser(description="Copy files with a specific extension from source to target directory.")
    parser.add_argument("--source_dir", type=str, required=True, help="Path to the source directory.")
    parser.add_argument("--target_dir", type=str, required=True, help="Path to the target directory.")
    parser.add_argument("--extension", type=str, required=True, help="File extension to search for and copy.")
    args = parser.parse_args()

    copy_files_with_extension(args.source_dir, args.target_dir, args.extension)

if __name__ == "__main__":
    main()

