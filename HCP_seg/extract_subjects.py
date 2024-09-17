import os
import shutil
import argparse
# python ./HCP_seg/extract_subjects.py --inputfolder folder --list list.txt --outfolder folder

def copy_folders(input_folder, list_file, output_folder):
    with open(list_file, 'r') as f:
        subject_ids = [line.strip() for line in f.readlines()]

    for root, dirs, files in os.walk(input_folder):
        for dir_name in dirs:
            if dir_name.startswith("sub-") and dir_name[4:] in subject_ids:
                source_dir = os.path.join(root, dir_name)
                destination_dir = os.path.join(output_folder, dir_name)
                
                shutil.copytree(source_dir, destination_dir)
                print(f"Copied {source_dir} to {destination_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy subject folders based on a list of subject IDs.")
    parser.add_argument("--inputfolder", required=True, help="Input folder containing subfolders.")
    parser.add_argument("--list", required=True, help="Text file containing subject IDs.")
    parser.add_argument("--outfolder", required=True, help="Output folder for copied subfolders.")
    
    args = parser.parse_args()
    
    input_folder = args.inputfolder
    list_file = args.list
    output_folder = args.outfolder
    
    copy_folders(input_folder, list_file, output_folder)
