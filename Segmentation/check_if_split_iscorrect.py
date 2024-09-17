import os
import argparse
import vtk
from collections import defaultdict
# conda activate DDSurfer
# python ./Segmentation/check_if_split_iscorrect.py --original_atlas folder1 --split_atlas folder2 --num_clusters 200


def count_fibers_in_vtp(file_path):
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_path)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata.GetNumberOfLines()


# def check_if_split_is_correct(original_atlas, split_atlas, num_fibers, num_clusters):
def check_if_split_is_correct(original_atlas, split_atlas, num_clusters):
    original_files = os.listdir(original_atlas)
    split_subject_folders = [f for f in os.listdir(split_atlas) if os.path.isdir(os.path.join(split_atlas, f))]
    
    subject_fiber_counts = defaultdict(int)
    
    for subject_folder in split_subject_folders:
        subject_id_x = subject_folder.split('_')[-1]
        subject_folder_path = os.path.join(split_atlas, subject_folder)
        
        subject_files = os.listdir(subject_folder_path)
        
        # Check if the number of files is equal to num_clusters
        if len(subject_files) != num_clusters:
            print(f"Error: {subject_folder} does not have {num_clusters} cluster files.")
            continue

        # Check if all Subject_ID values are the same and equal to subject_id_x
        subject_id_set = set()
        for subject_file in subject_files:
            file_path = os.path.join(subject_folder_path, subject_file)
            reader = vtk.vtkXMLPolyDataReader()
            reader.SetFileName(file_path)
            reader.Update()
            point_data = reader.GetOutput().GetPointData()
            subject_id_array = point_data.GetArray("Subject_ID")
            
            if subject_id_array:
                subject_id_count = subject_id_array.GetNumberOfTuples()
                subject_id_values = set()
                for i in range(subject_id_count):
                    subject_id = subject_id_array.GetValue(i)
                    subject_id_values.add(subject_id)
                
                if len(subject_id_values) != 1 or subject_id_values.pop() != subject_id_x:
                    print(f"Error: {subject_file} in {subject_folder} has inconsistent or incorrect Subject_ID values.")

        
        # Calculate total fiber count for the subject
        subject_fiber_count = sum(count_fibers_in_vtp(os.path.join(subject_folder_path, f)) for f in subject_files)
        subject_fiber_counts[subject_id_x] = subject_fiber_count
        

    for subject_folder in split_subject_folders:
        subject_id_x = subject_folder.split('_')[-1]
        # if subject_fiber_counts[subject_id_x] == num_fibers:
        #     print(f"Total fiber count for subject {subject_id_x}: {subject_fiber_counts[subject_id_x]}")
        # else:
        #     print(f"Total fiber count for subject {subject_id_x}: {subject_fiber_counts[subject_id_x]} does not match num_fibers: {num_fibers}")

        print(f"Total fiber count for subject {subject_id_x}: {subject_fiber_counts[subject_id_x]}")

    for original_file in original_files:
        if original_file.startswith("cluster_") and original_file.endswith(".vtp"):
            original_file_path = os.path.join(original_atlas, original_file)
            original_fiber_count = count_fibers_in_vtp(original_file_path)
            total_subject_fiber_count = sum(count_fibers_in_vtp(os.path.join(split_atlas, subject_folder, original_file)) for subject_folder in split_subject_folders)

            if original_fiber_count != total_subject_fiber_count:
                 print(f"Error: Total fiber count for {original_file} does not match in split_atlas. Original count: {original_fiber_count}, Total count in split_atlas: {total_subject_fiber_count}")

            else:
                print(f"Total fiber count for {original_file} matches in split_atlas. Original count: {original_fiber_count}, Total count in split_atlas: {total_subject_fiber_count}")
    
    print("Validation completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if split atlas is correct.")
    parser.add_argument("--original_atlas", required=True, help="Path to the original atlas folder.")
    parser.add_argument("--split_atlas", required=True, help="Path to the split atlas folder.")
    # parser.add_argument("--num_fibers", type=int, required=True, help="Expected number of fibers per subject.")
    parser.add_argument("--num_clusters", type=int, required=True, help="Expected number of clusters per subject.")
    
    args = parser.parse_args()
    
    # check_if_split_is_correct(args.original_atlas, args.split_atlas, args.num_fibers, args.num_clusters)
    check_if_split_is_correct(args.original_atlas, args.split_atlas, args.num_clusters)
