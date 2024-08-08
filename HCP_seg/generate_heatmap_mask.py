import nibabel as nib
import numpy as np
import os
import argparse
#  python /home/haolin/Research/HCP_seg/generate_heatmap_mask.py --infolder --outfolder --threshold 

def generate_heatmap_mask(infolder, outfolder, threshold):
    # 获取infolder中的所有nifti文件
    nifti_files = [f for f in os.listdir(infolder) if f.endswith('.nii.gz')]

    for nifti_file in nifti_files:
        # 读取NIfTI文件
        infile = os.path.join(infolder, nifti_file)
        img = nib.load(infile)
        data = img.get_fdata()

        # 生成heatmap mask
        mask = np.where(data >= threshold, 1, 0)
        mask_img = nib.Nifti1Image(mask, img.affine, img.header)

        # 输出mask文件
        outfile = os.path.join(outfolder, nifti_file)
        nib.save(mask_img, outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate heatmap masks from NIfTI files.')
    parser.add_argument('--infolder', type=str, required=True, help='Input folder containing NIfTI files.')
    parser.add_argument('--outfolder', type=str, required=True, help='Output folder for the mask files.')
    parser.add_argument('--threshold', type=float, required=True, help='Threshold for generating the mask.')

    args = parser.parse_args()

    generate_heatmap_mask(args.infolder, args.outfolder, args.threshold)
