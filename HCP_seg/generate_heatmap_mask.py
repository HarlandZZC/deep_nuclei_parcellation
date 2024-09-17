import nibabel as nib
import numpy as np
import os
import argparse
#  python ./HCP_seg/generate_heatmap_mask.py --infolder --outfolder --threshold 

def generate_heatmap_mask(infolder, outfolder, threshold):
    nifti_files = [f for f in os.listdir(infolder) if f.endswith('.nii.gz')]

    for nifti_file in nifti_files:
        infile = os.path.join(infolder, nifti_file)
        img = nib.load(infile)
        data = img.get_fdata()

        mask = np.where(data >= threshold, 1, 0)
        mask_img = nib.Nifti1Image(mask, img.affine, img.header)

        outfile = os.path.join(outfolder, nifti_file)
        nib.save(mask_img, outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate heatmap masks from NIfTI files.')
    parser.add_argument('--infolder', type=str, required=True, help='Input folder containing NIfTI files.')
    parser.add_argument('--outfolder', type=str, required=True, help='Output folder for the mask files.')
    parser.add_argument('--threshold', type=float, required=True, help='Threshold for generating the mask.')

    args = parser.parse_args()

    generate_heatmap_mask(args.infolder, args.outfolder, args.threshold)
