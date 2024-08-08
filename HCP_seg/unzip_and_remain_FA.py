import os
import tarfile
import argparse
import shutil
# python /home/haolin/Research/HCP_seg/unzip_and_remain_FA.py --zipfolder --outfolder --referfolder 

def extract_and_cleanup(zipfolder, outfolder, referfolder):
    # 创建输出文件夹，如果不存在的话
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    
    for zip_file in os.listdir(zipfolder):
        if zip_file.endswith(".tar.gz"):
            sub_id = zip_file.split('.')[0]
            refer_subfolder = f"sub-{sub_id}"
            # 检查是否存在对应的参考文件夹
            if refer_subfolder in os.listdir(referfolder):
                tar_path = os.path.join(zipfolder, zip_file)
                extract_path = os.path.join(outfolder, refer_subfolder)
                
                # 解压.tar.gz文件
                with tarfile.open(tar_path, "r:gz") as tar:
                    tar.extractall(path=extract_path)
                
                # 重命名解压后的Processed文件夹
                processed_path = os.path.join(extract_path, "Processed")
                new_path = os.path.join(extract_path, refer_subfolder)
                os.rename(processed_path, new_path)
                
                # 移动必要的文件并删除其余文件
                required_file = f"{sub_id}-dwi_b3000_fa.nrrd"
                required_file_path = os.path.join(new_path, "3T_Diffusion_preproc", sub_id, "T1w", "Diffusion", required_file)
                shutil.move(required_file_path, os.path.join(extract_path, required_file))
                
                # 删除多余的文件和文件夹
                for root, dirs, files in os.walk(new_path, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(new_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract .tar.gz files and clean up.")
    parser.add_argument("--zipfolder", required=True, help="Folder containing .tar.gz files")
    parser.add_argument("--outfolder", required=True, help="Output folder for extracted and cleaned files")
    parser.add_argument("--referfolder", required=True, help="Reference folder to check for corresponding sub-folders")
    
    args = parser.parse_args()
    
    extract_and_cleanup(args.zipfolder, args.outfolder, args.referfolder)
