import os
import argparse
# python /home/haolin/Research/Segmentation/delete_file.py --process_folder folder1 --delete_file file
def delete_files_with_name(root_folder, file_name):
    for root, dirs, files in os.walk(root_folder, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            if file == file_name:
                print(f"正在删除文件：{file_path}")
                try:
                    os.remove(file_path)
                    print(f"已成功删除文件：{file_path}")
                except OSError as e:
                    print(f"无法删除文件：{file_path}，错误：{e}")

def main(process_folder, delete_file):
    delete_files_with_name(process_folder, delete_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="递归删除指定文件夹内所有名字为指定名称的文件。")
    parser.add_argument("--process_folder", required=True, help="要处理的根文件夹路径。")
    parser.add_argument("--delete_file", required=True, help="要删除的文件名称。")
    args = parser.parse_args()
    
    main(args.process_folder, args.delete_file)
