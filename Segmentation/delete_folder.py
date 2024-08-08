import os
import argparse
import shutil
# python /home/haolin/Research/Segmentation/delete_folder.py --process_folder folder1 --delete_folder folder2

def delete_folders_with_name(root_folder, folder_name):
    for root, dirs, files in os.walk(root_folder, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if folder == folder_name:
                print(f"正在删除文件夹：{folder_path}")
                try:
                    shutil.rmtree(folder_path)
                    print(f"已成功删除文件夹：{folder_path}")
                except OSError as e:
                    print(f"无法删除文件夹：{folder_path}，错误：{e}")

def main(process_folder, delete_folder):
    delete_folders_with_name(process_folder, delete_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="递归删除指定文件夹内所有名字为指定名称的文件夹。")
    parser.add_argument("--process_folder", required=True, help="要处理的根文件夹路径。")
    parser.add_argument("--delete_folder", required=True, help="要删除的文件夹名称。")
    args = parser.parse_args()
    
    main(args.process_folder, args.delete_folder)

