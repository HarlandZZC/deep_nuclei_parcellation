import argparse
import os
import shutil
# python /home/haolin/Research/Segmentation/filter.py --input folder1 --output folder2

def is_valid_file(filename):
    return filename.endswith('.vtk')

def extract_info_from_filename(filename):
    parts = filename.split('_')
    A, B = parts[-1].split('-')[:2]
    B = B.split('.')[0]  # Remove the file extension
    return int(A), int(B)

def main(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if is_valid_file(filename):
            A, B = extract_info_from_filename(filename)
            if (A == 18 and 1000 <= B <= 1035) or (A == 54 and 2000 <= B <= 2035):
                source_path = os.path.join(input_folder, filename)
                destination_path = os.path.join(output_folder, f'{A}-{B}.vtk')
                shutil.copyfile(source_path, destination_path)
                print(f"Copying {filename} to {destination_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter and copy .vtk files based on conditions')
    parser.add_argument('--input', required=True, help='Input folder containing .vtk files')
    parser.add_argument('--output', required=True, help='Output folder to copy selected .vtk files')
    args = parser.parse_args()

    input_folder = args.input
    output_folder = args.output

    main(input_folder, output_folder)
