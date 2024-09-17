import os
import nibabel as nib
import numpy as np
import argparse
#  python ./HCP_seg/find_regions.py --infile  --outfile --region 15 11 19 13 236 17 186 22 16 21

# 228 237 235

def find_regions(infile, outfile, target_regions):
    img = nib.load(infile)
    data = img.get_fdata().astype(int)
    
    # Create a mask for the target regions
    mask = np.isin(data, target_regions)
    
    # Extract voxels in the target regions
    result_data = np.zeros_like(data)
    result_data[mask] = data[mask]
    print("Unique values in result_data:", np.unique(result_data))
    
    # Convert the result data to integer before creating a new NIfTI image
    result_data = result_data.astype(int)
    
    # Create a new NIfTI image with the result data
    result_img = nib.Nifti1Image(result_data, img.affine, img.header)
    
    # Save the result to the output file
    nib.save(result_img, outfile)
    print(f"Voxels in the specified regions extracted and saved to {outfile}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and extract voxels in specified regions from a NIfTI file.")
    parser.add_argument("--infile", required=True, help="Input NIfTI file.")
    parser.add_argument("--outfile", required=True, help="Output NIfTI file.")
    parser.add_argument("--region", nargs="+", type=int, required=True, help="List of target regions.")
    args = parser.parse_args()

    find_regions(args.infile, args.outfile, args.region)