import os
import tarfile
import argparse
import shutil
# python ./HCP_seg/unzip_and_remain_FA.py --zipfolder --outfolder --referfolder 

def extract_and_cleanup(zipfolder, outfolder, referfolder):
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    
    for zip_file in os.listdir(zipfolder):
        if zip_file.endswith(".tar.gz"):
            sub_id = zip_file.split('.')[0]
            refer_subfolder = f"sub-{sub_id}"

            if refer_subfolder in os.listdir(referfolder):
                tar_path = os.path.join(zipfolder, zip_file)
                extract_path = os.path.join(outfolder, refer_subfolder)
                

                with tarfile.open(tar_path, "r:gz") as tar:
                    tar.extractall(path=extract_path)
                
    
                processed_path = os.path.join(extract_path, "Processed")
                new_path = os.path.join(extract_path, refer_subfolder)
                os.rename(processed_path, new_path)
                
    
                required_file = f"{sub_id}-dwi_b3000_fa.nrrd"
                required_file_path = os.path.join(new_path, "3T_Diffusion_preproc", sub_id, "T1w", "Diffusion", required_file)
                shutil.move(required_file_path, os.path.join(extract_path, required_file))
                

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
