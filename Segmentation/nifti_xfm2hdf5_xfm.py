import os
import argparse
import nibabel as nib
import h5py
# python ./Segmentation/nifti_xfm2hdf5_xfm.py --infolder folder1 --outfolder folder2

def convert_nifti_to_hd5(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".nii.gz"):
            nifti_path = os.path.join(input_folder, filename)
            hd5_path = os.path.join(output_folder, filename.replace(".nii.gz", ".hd5"))

            img = nib.load(nifti_path)
            data = img.get_fdata()

            with h5py.File(hd5_path, "w") as hf:
                hf.create_dataset("data", data=data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert NIfTI displacement fields to HDF5 format")
    parser.add_argument("--infolder", required=True, help="Input folder containing NIfTI files")
    parser.add_argument("--outfolder", required=True, help="Output folder for HDF5 files")

    args = parser.parse_args()
    input_folder = args.infolder
    output_folder = args.outfolder

    convert_nifti_to_hd5(input_folder, output_folder)
