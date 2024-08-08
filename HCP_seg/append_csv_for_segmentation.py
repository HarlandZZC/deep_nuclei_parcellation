import argparse
import pandas as pd
import os
# python /home/haolin/Research/HCP_seg/append_csv_for_segmentation.py --infolder folder1 --outfolder folder2 --f f --k k --iteration iter --labels labels

def append_csv_for_segmentation(infolder, outfolder, f_value, k_value, iteration_value, label_list):
    for label_value in label_list:
        merged_df = None
        for subfolder in os.listdir(infolder):
            if subfolder.startswith("sub-"):
                print(f"dealing with {subfolder}...")
                subject_id = subfolder
                csv_path = os.path.join(
                    infolder, subject_id, "ses-1", "dwi", "csv_for_segmentation",
                    f"{subject_id}_ses-1_run-1", f"atlas_f{f_value}_k{k_value}_iteration{iteration_value}",
                    f"label{label_value}.csv"
                )

                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    df.insert(0, 'label', label_value)
                    df.insert(0, 'subject_id', subject_id)
                    if merged_df is None:
                        merged_df = df
                    else:
                        merged_df = pd.concat([merged_df, df], ignore_index=True)

        if merged_df is not None:
            merged_csv_name = os.path.join(outfolder, f"f{f_value}_k{k_value}_iteration{iteration_value}_label{label_value}_append.csv")
            if not os.path.exists(merged_csv_name):
                merged_df.to_csv(merged_csv_name, index=False)
            else:
                # 如果文件已存在，将数据追加到现有文件中
                merged_df.to_csv(merged_csv_name, mode='a', header=False, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge CSV files for segmentation")
    parser.add_argument("--infolder", required=True, help="Input folder path")
    parser.add_argument("--outfolder", required=True, help="Output folder path")
    parser.add_argument("--f", required=True, type=int, help="f value")
    parser.add_argument("--k", required=True, type=int, help="k value")
    parser.add_argument("--iteration", required=True, help="iteration value")
    parser.add_argument("--labels", required=True, nargs='+', type=int, help="List of label values")

    args = parser.parse_args()

    append_csv_for_segmentation(args.infolder, args.outfolder, args.f, args.k, args.iteration, args.labels)
