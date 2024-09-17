import os
import sys
import nibabel as nib
import nrrd
import argparse
# python ./HCP_seg/check_mapping_between_outfolder_FAfolder.py --FAfolder --outfolder

def check_dimensions(nii_file, nrrd_file):
    # Load the NIfTI file
    nii_img = nib.load(nii_file)
    # Load the NRRD file
    nrrd_data, _ = nrrd.read(nrrd_file)
    
    # Compare dimensions
    nii_dim = nii_img.shape
    nrrd_dim = nrrd_data.shape
    return nii_dim == nrrd_dim, nii_dim, nrrd_dim

def main(FAfolder, outfolder):
    # Iterate over subdirectories in outfolder
    for subdir in os.listdir(outfolder):
        if subdir.startswith("sub-") and os.path.isdir(os.path.join(outfolder, subdir)):
            nii_filename = f"{subdir}_ses-1_run-1-DDSurfer-wmparc-mni-clustered.nii.gz"
            nii_path = os.path.join(outfolder, subdir, nii_filename)
            
            if os.path.exists(nii_path):
                # Corresponding NRRD file in FAfolder
                nrrd_filename = f"{subdir.split('-')[1]}-dwi_b3000_fa.nrrd"
                nrrd_path = os.path.join(FAfolder, subdir, nrrd_filename)
                
                if os.path.exists(nrrd_path):
                    # Check dimensions
                    match, nii_dim, nrrd_dim = check_dimensions(nii_path, nrrd_path)
                    print(f"{nii_filename} and {nrrd_filename}: {'Match' if match else 'Do not match'}")
                    print(f"Dimensions - NIfTI: {nii_dim}, NRRD: {nrrd_dim}")
                else:
                    print(f"Missing NRRD file for {subdir}")
            else:
                print(f"Missing NIfTI file for {subdir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check matching dimensions between NIfTI and NRRD files.")
    parser.add_argument("--FAfolder", required=True, help="Path to the folder containing FA NRRD files.")
    parser.add_argument("--outfolder", required=True, help="Path to the folder containing output NIfTI files.")
    
    args = parser.parse_args()
    
    main(args.FAfolder, args.outfolder)
