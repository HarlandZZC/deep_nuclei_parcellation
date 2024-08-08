import os
import argparse
# python /home/haolin/Research/Segmentation/delete_file_with_suffix.py --subject_folder --suffix

def delete_files_with_suffix(subject_folder, suffix):
    # 获取subject_folder中所有文件的路径
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(subject_folder) for f in filenames]
    
    # 遍历文件，删除以指定后缀结尾的文件
    deleted_files = []
    for file_path in files:
        if file_path.endswith(suffix):
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {str(e)}")

    # 打印已删除的文件
    if deleted_files:
        print(f"Deleted files with suffix '{suffix}':")
        for deleted_file in deleted_files:
            print(deleted_file)
    else:
        print(f"No files with suffix '{suffix}' found.")

if __name__ == "__main__":
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="Delete files with a specified suffix in a given folder.")
    parser.add_argument("--subject_folder", required=True, help="Path to the subject folder")
    parser.add_argument("--suffix", required=True, help="Suffix of the files to be deleted")

    # 解析命令行参数
    args = parser.parse_args()

    # 调用删除函数
    delete_files_with_suffix(args.subject_folder, args.suffix)
