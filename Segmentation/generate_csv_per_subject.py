import os
import argparse
import nibabel as nib
import numpy as np
import csv
import re
# python /home/haolin/Research/Segmentation/generate_csv_per_subject.py --refvolume refvolume.nii.gz --atlas_nifti_folder folder --label_concerned label --csv output.csv

def generate_csv(refvolume, atlas_nifti_folder, label_concerned, csv_file):
    # Load the reference volume (refvolume)
    ref_img = nib.load(refvolume)
    ref_data = ref_img.get_fdata()

    # Find the coordinates of the voxels with the specified label (label_concerned)
    label_coordinates = np.argwhere(ref_data == label_concerned)

    # Get the shape of the reference volume
    volume_shape = ref_data.shape

    # Initialize the CSV data dictionary
    csv_data = {}

    # Add voxel_id and voxel_coordinate columns
    csv_data['voxel_id'] = list(range(len(label_coordinates)))
    csv_data['voxel_coordinate'] = [tuple(coord) for coord in label_coordinates]

    # Initialize a list to store cluster values for each voxel
    cluster_columns = []

    # Define a regular expression to extract "cluster_数值" from filenames
    cluster_pattern = re.compile(r'cluster_(\d+)')

    # Iterate through the cluster NIfTI files in the folder
    for filename in os.listdir(atlas_nifti_folder):
        if filename.startswith("cluster_") and filename.endswith(".nii.gz"):
            print(f"dealing with {filename}...")
            # Load the cluster NIfTI file
            cluster_img = nib.load(os.path.join(atlas_nifti_folder, filename))
            cluster_data = cluster_img.get_fdata()

            # Extract cluster values for each voxel with the specified label
            cluster_values = []
            for coord in label_coordinates:
                x, y, z = coord
                cluster_value = cluster_data[x, y, z]
                cluster_values.append(cluster_value)

            # Extract "cluster_数值" from the filename
            match = cluster_pattern.search(filename)
            if match:
                cluster_number = match.group(1)
                cluster_column_name = f"cluster_{cluster_number}"
                cluster_columns.append(cluster_column_name)

                # Add cluster values to the CSV data dictionary
                csv_data[cluster_column_name] = cluster_values

    # Sort cluster columns in ascending order
    cluster_columns.sort(key=lambda x: int(x.split('_')[1]))

    # Rearrange the CSV data dictionary based on the sorted cluster columns
    sorted_csv_data = {'voxel_id': csv_data['voxel_id'], 'voxel_coordinate': csv_data['voxel_coordinate']}
    for column_name in cluster_columns:
        sorted_csv_data[column_name] = csv_data[column_name]

    # Write CSV file
    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = sorted_csv_data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(label_coordinates)):
            writer.writerow({key: sorted_csv_data[key][i] for key in fieldnames})
    
    print(f"CSV file '{csv_file}' has been successfully generated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a CSV file with cluster values for specified labels.")
    parser.add_argument("--refvolume", required=True, help="Path to the reference NIfTI volume.")
    parser.add_argument("--atlas_nifti_folder", required=True, help="Path to the folder containing cluster NIfTI files.")
    parser.add_argument("--label_concerned", type=int, required=True, help="Label to be concerned.")
    parser.add_argument("--csv", required=True, help="Path to the output CSV file.")

    args = parser.parse_args()

    generate_csv(args.refvolume, args.atlas_nifti_folder, args.label_concerned, args.csv)


