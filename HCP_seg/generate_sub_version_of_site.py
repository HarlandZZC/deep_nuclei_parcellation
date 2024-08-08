import os
import shutil
import argparse
# python /home/haolin/Research/HCP_seg/generate_sub_version_of_site.py --sitefolder  --outputfolder  --copyfoldername  --keyword


def generate_sub_version(site_folder, output_folder, copy_folder_name, keyword):
    # 遍历源文件夹
    for root, dirs, files in os.walk(site_folder):
        if copy_folder_name in dirs and keyword in root:
            source_folder = os.path.join(root, copy_folder_name)
            destination_folder = source_folder.replace(site_folder, output_folder)
            
            # 复制文件夹到目标文件夹
            shutil.copytree(source_folder, destination_folder)
            
            print(f'复制文件夹 {source_folder} 到 {destination_folder}')

def main():
    parser = argparse.ArgumentParser(description='Generate a sub-version of a site')
    parser.add_argument('--sitefolder', type=str, help='Path to the source site folder')
    parser.add_argument('--outputfolder', type=str, help='Path to the output folder')
    parser.add_argument('--copyfoldername', type=str, help='List of folder names to copy')
    parser.add_argument('--keyword', type=str, help='Keywords to check in dirs')

    args = parser.parse_args()
    
    if not all([args.sitefolder, args.outputfolder, args.copyfoldername, args.keyword]):
        parser.error('请提供正确的参数')
    
    generate_sub_version(args.sitefolder, args.outputfolder, args.copyfoldername, args.keyword)

if __name__ == '__main__':
    main()
