import os
import argparse
import pandas as pd
import re
import numpy as np
# python /home/haolin/Research/Segmentation/merge_and_tune_csv_of_different_labels.py --infolder folder1 --outfolder folder2 --f f --k k --iteration iter --labels labels --binarization 1

def merge_and_tune_csv(infolder, outfolder, f_value, k_value, iteration_value, labels, binarization):
    data_frames = []
    new_voxel_id = 0
    
    # Create a combined label for the output file name
    combined_label = "_".join(labels)
    
    # Determine the output file name pattern based on binarization
    if binarization == 1:
        output_file_pattern = f"f{f_value}_k{k_value}_iteration{iteration_value}_label{combined_label}_append_binary.csv"
    else:
        output_file_pattern = f"f{f_value}_k{k_value}_iteration{iteration_value}_label{combined_label}_append.csv"
    
    for label_value in labels:
        # Determine the file pattern based on binarization

        file_pattern = f"f{f_value}_k{k_value}_iteration{iteration_value}_label{label_value}_append.csv"
        
        file_path = os.path.join(infolder, file_pattern)
        
        if os.path.exists(file_path):
            data = pd.read_csv(file_path)
            
            # Assign new voxel_id values starting from 0
            data['voxel_id'] = range(new_voxel_id, new_voxel_id + len(data))
            new_voxel_id += len(data)
            
            # Round the "cluster" columns to integers
            cluster_columns = [col for col in data.columns if re.match(r'cluster_\d+', col)]

            # # 打印包含非有限值的行
            # rows_with_inf = data[data[cluster_columns].isin([np.inf, -np.inf, np.nan]).any(axis=1)]
            # print("Rows with non-finite values:")
            # print(rows_with_inf)

            # # 打印包含非有限值和 NaN 的行
            # rows_with_inf_nan = data[data[cluster_columns].isin([np.inf, -np.inf, np.nan]).any(axis=1)]
            # print("Rows with non-finite values or NaN:")
            # print(rows_with_inf_nan)

            data[cluster_columns] = data[cluster_columns].round().astype(int)

            # Binarize the data[cluster_columns] if binarization is 1
            if binarization == 1:
                data[cluster_columns] = data[cluster_columns].applymap(lambda x: 1 if x != 0 else 0)
            
            # Append data to the list of data frames
            data_frames.append(data)
        else:
            print(f"Warning: File not found for label {label_value}: {file_pattern}")
    
    if data_frames:
        # Concatenate all data frames into a single data frame
        merged_data = pd.concat(data_frames, ignore_index=True)
        
        # Save the merged and tuned data to a new CSV file with the determined label
        merged_file_path = os.path.join(outfolder, output_file_pattern)
        merged_data.to_csv(merged_file_path, index=False)
        print(f"Merged and tuned data saved to {merged_file_path}")
    else:
        print("No data found to merge.")

def main():
    parser = argparse.ArgumentParser(description="Merge and tune CSV files with different labels.")
    parser.add_argument("--infolder", required=True, help="Input folder containing CSV files.")
    parser.add_argument("--outfolder", required=True, help="Output folder to save the merged CSV file.")
    parser.add_argument("--f", required=True, type=int, help="f_value.")
    parser.add_argument("--k", required=True, type=int, help="k_value.")
    parser.add_argument("--iteration", required=True, type=int, help="iteration_value.")
    parser.add_argument("--labels", nargs='+', required=True, help="List of label values.")
    parser.add_argument("--binarization", type=int, default=0, help="Binarization option (0 or 1).")
    
    args = parser.parse_args()
    
    merge_and_tune_csv(args.infolder, args.outfolder, args.f, args.k, args.iteration, args.labels, args.binarization)

if __name__ == "__main__":
    main()

