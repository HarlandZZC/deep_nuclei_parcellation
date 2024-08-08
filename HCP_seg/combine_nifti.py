import os
import nibabel as nib
import numpy as np
import argparse
# python /home/haolin/Research/HCP_seg/combine_nifti.py --infolder  --outfile


def combine_nifti(infolder, outfile):
    nifti_files = [f for f in os.listdir(infolder) if f.endswith('.nii.gz')]
    
    if not nifti_files:
        print("No NIfTI files found in the specified input folder.")
        return
    
    combined_data = None
    conflicts = False
    
    for nifti_file in nifti_files:
        file_path = os.path.join(infolder, nifti_file)
        img = nib.load(file_path)
        data = img.get_fdata()

        if combined_data is None:
            combined_data = data
        else:
            # Check for conflicts
            conflict_mask = np.logical_and(combined_data != 0, data != 0)
            if np.any(conflict_mask):
                conflicts = True
                print(f"Conflict detected in file: {nifti_file}")

            combined_data += data
    
    combined_data = combined_data.astype(int)
    combined_img = nib.Nifti1Image(combined_data, img.affine, img.header)
    nib.save(combined_img, outfile)
    
    if not conflicts:
        print("No conflicts detected during the merging process.")
    else:
        print("Conflicts detected during the merging process.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine NIfTI files in a folder.")
    parser.add_argument("--infolder", required=True, help="Input folder containing NIfTI files.")
    parser.add_argument("--outfile", required=True, help="Output NIfTI file.")
    args = parser.parse_args()

    combine_nifti(args.infolder, args.outfile)
