import os
import argparse
import csv
from collections import Counter
# python ./Segmentation/count_bvals.py --inputfolder folder --outputcsv csv

def process_bval_files(input_folder, output_csv):
    bval_counter = Counter()

    for root, dirs, files in os.walk(input_folder):
        for file_name in files:
            if file_name.lower().endswith('.bval'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r') as bval_file:
                    bval_values = bval_file.read().split()
                    bval_counter.update(bval_values)

    with open(output_csv, 'w', newline='') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerow(["bvals", "counts"])
        for value in sorted(bval_counter.keys(), key=int):
            csv_writer.writerow([value, bval_counter[value]])

    print(f"Values and counts saved to {output_csv}")
    for value in sorted(bval_counter.keys(), key=int):
        print(f"{value}: {bval_counter[value]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process bval files in a folder and save unique values.")
    parser.add_argument("--inputfolder", required=True, help="Input folder containing bval files.")
    parser.add_argument("--outputcsv", required=True, help="Output CSV file to store unique bval values and counts.")

    args = parser.parse_args()

    input_folder = args.inputfolder
    output_csv = args.outputcsv

    process_bval_files(input_folder, output_csv)



