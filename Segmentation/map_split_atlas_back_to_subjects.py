import os
import argparse
import shutil
# python ./Segmentation/map_split_atlas_back_to_subjects.py  --atlas_folder folder1 --subject_folder folder2 --f f --k k --iteration iteration

def parse_args():
    parser = argparse.ArgumentParser(description="Map atlas folders back to subjects.")
    parser.add_argument("--atlas_folder", required=True, help="Path to the atlas folder")
    parser.add_argument("--subject_folder", required=True, help="Path to the subject folder")
    parser.add_argument("--f", required=True, type=int, help="Value of 'f'")
    parser.add_argument("--k", required=True, type=int, help="Value of 'k'")
    parser.add_argument("--iteration", required=True, type=int, help="Value of 'iteration'")
    return parser.parse_args()

def main():
    args = parse_args()

    # Load Subject.txt
    subject_txt_path = os.path.join(args.atlas_folder, "Subjects.txt")
    subject_map = {}
    with open(subject_txt_path, "r") as file:
        for line in file:
            columns = line.strip().split('\t')
            if len(columns) >= 2:
                subject_idx = columns[0]
                subject_id = columns[1]
                subject_map[subject_idx] = subject_id

    # Process each Subject_idx folder
    atlas_folder = args.atlas_folder
    subject_folder = args.subject_folder
    f_value = args.f
    k_value = args.k
    iteration_value = args.iteration

    for atlas_subfolder in os.listdir(atlas_folder):
        atlas_subfolder_path = os.path.join(atlas_folder, atlas_subfolder)
        if os.path.isdir(atlas_subfolder_path) and atlas_subfolder.startswith("Subject_idx_"):
            subject_idx = atlas_subfolder.split("_")[-1]
            if subject_idx in subject_map:
                subject_id = subject_map[subject_idx]
                
                # Split subject_id into sub_id, ses_id, and run_id
                parts = subject_id.split("_")
                sub_id = parts[0]
                ses_id = parts[1]
                run_id = parts[2]
                
                # Create destination directory
                destination_folder = os.path.join(subject_folder, sub_id, ses_id, "dwi", "atlas_split", sub_id + "_" + ses_id + "_" + run_id, f"atlas_f{f_value}_k{k_value}_iteration{iteration_value}")
                os.makedirs(destination_folder, exist_ok=True)
                
                # Copy contents from atlas folder to destination folder
                for item in os.listdir(atlas_subfolder_path):
                    source_item = os.path.join(atlas_subfolder_path, item)
                    destination_item = os.path.join(destination_folder, item)
                    if os.path.isdir(source_item):
                        shutil.copytree(source_item, destination_item)
                        print(f"copy to {destination_item} done!")
                    else:
                        shutil.copy2(source_item, destination_item)
                        print(f"copy to {destination_item} done!")

if __name__ == "__main__":
    main()
