import nibabel as nib
import numpy as np
import os
import argparse
# python /home/haolin/Research/HCP_seg/generate_region_mask.py --infile --outfolder

def generate_region_mask(infile, outfolder):
    # 读取NIfTI文件
    img = nib.load(infile)
    data = img.get_fdata()

    # 获取所有的region
    regions = np.unique(data)

    # 对每个region生成mask
    for region in regions:
        if region == 0:  # 跳过空白区域
            continue
        mask = np.where(data == region, 1, 0)
        mask_img = nib.Nifti1Image(mask, img.affine, img.header)

        # 输出mask文件
        outfile = os.path.join(outfolder, f'region_{int(region)}.nii.gz')
        nib.save(mask_img, outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate region masks from a NIfTI file.')
    parser.add_argument('--infile', type=str, required=True, help='Input NIfTI file.')
    parser.add_argument('--outfolder', type=str, required=True, help='Output folder for the mask files.')

    args = parser.parse_args()

    generate_region_mask(args.infile, args.outfolder)