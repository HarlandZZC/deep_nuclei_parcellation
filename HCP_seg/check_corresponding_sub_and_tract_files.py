import os
import argparse
# python ./HCP_seg/check_corresponding_sub_and_tract_files.py --subject_folder folder1 --tract_folder folder2


def list_subject_folders(folder):
    return [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f)) and f.startswith("sub-")]

def list_tract_files(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def main():
    parser = argparse.ArgumentParser(description="Check corresponding files and folders.")
    parser.add_argument("--subject_folder", required=True, help="Path to the subject folder.")
    parser.add_argument("--tract_folder", required=True, help="Path to the tract folder.")
    args = parser.parse_args()

    subject_subfolders = list_subject_folders(args.subject_folder)
    tract_files = list_tract_files(args.tract_folder)

    missing_in_subject = [subfolder for subfolder in subject_subfolders if not any(file.startswith(subfolder[4:]) for file in tract_files)]
    missing_in_tract = [file for file in tract_files if not any(file.startswith(subfolder[4:]) for subfolder in subject_subfolders)]

    if missing_in_subject:
        print("Subfolders in subject_folder with no corresponding files in tract_folder:")
        for item in missing_in_subject:
            print(f"  {item}")

    if missing_in_tract:
        print("Files/folders in tract_folder with no corresponding subfolder in subject_folder:")
        for item in missing_in_tract:
            print(f"  {item}")

    if not missing_in_subject and not missing_in_tract:
        print("All subfolders in subject_folder have corresponding files in tract_folder, and vice versa.")

if __name__ == "__main__":
    main()
