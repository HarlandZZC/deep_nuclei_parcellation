import os
import nibabel as nib
import numpy as np
import argparse
from scipy.ndimage import binary_dilation
# python ./HCP_seg/mask_dilation.py --infolder --outfolder

def dilate_masks(infolder, outfolder, struct):
    for file in os.listdir(infolder):
        if file.endswith('.nii.gz'):
            img = nib.load(os.path.join(infolder, file))
            data = img.get_fdata()
            dilated_data = binary_dilation(data, structure=struct)
            dilated_img = nib.Nifti1Image(dilated_data, img.affine, img.header)
            nib.save(dilated_img, os.path.join(outfolder, file))

def main():
    parser = argparse.ArgumentParser(description='Dilate masks in NIfTI files.')
    parser.add_argument('--infolder', required=True, help='Input folder containing NIfTI files')
    parser.add_argument('--outfolder', required=True, help='Output folder for dilated NIfTI files')
    args = parser.parse_args()

    struct = np.zeros((3,3,3))
    struct[1,1,0] = 0.5  
    struct[1,0,1] = 0.5
    struct[0,1,1] = 0.5

    dilate_masks(args.infolder, args.outfolder, struct)

if __name__ == "__main__":
    main()
