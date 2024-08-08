import os
import argparse
import subprocess
# source /data01/software/bashrc
# python /home/haolin/Research/Segmentation/regrid_and_replace_all_nifti_files_for_FA.py --folder folder

def regrid_nifti(input_path, output_path):
    command = f"mrgrid {input_path} regrid {output_path} -voxel 2,2,2 -interp nearest -force"
    subprocess.run(command, shell=True)

def regrid_and_replace(input_path):
    output_path = os.path.join(os.path.dirname(input_path), "regrid_" + os.path.basename(input_path))
    regrid_nifti(input_path, output_path)
    os.remove(input_path)
    os.rename(output_path, input_path)

def find_subdirectories(folder):
    target_folder_name = f"FA"
    subdirectories = []

    for root, dirs, files in os.walk(folder):
        if target_folder_name in dirs:
            subdirectories.append(os.path.join(root, target_folder_name))

    return subdirectories

def regrid_specific_folders(folders):
    for folder in folders:
        print(f"Regridding Nifti files in {folder} and its subfolders...")
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".nii.gz"):
                    input_path = os.path.join(root, file)
                    print(f"Processing: {input_path}")
                    regrid_and_replace(input_path)
                    print(f"Done: {input_path}")

def main():
    parser = argparse.ArgumentParser(description='Regrid specific Nifti files in subdirectories.')
    parser.add_argument('--folder', required=True, help='Path to the main folder containing subdirectories')
    args = parser.parse_args()

    subdirectories = find_subdirectories(args.folder)
    regrid_specific_folders(subdirectories)

if __name__ == "__main__":
    main()

