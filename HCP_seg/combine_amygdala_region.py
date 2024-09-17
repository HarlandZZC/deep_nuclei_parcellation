import nibabel as nib
import numpy as np
import argparse
#  python ./HCP_seg/combine_amygdala_region.py --infile --outfile 

def combine_amygdala_region(infile, outfile):
    img = nib.load(infile)
    data = img.get_fdata().astype(int)  # 转换为整数

    #LB
    data[data == 15] = 1
    data[data == 11] = 1
    data[data == 19] = 1
    data[data == 13] = 1

    #SF
    data[data == 236] = 2
    data[data == 17] = 2
    data[data == 186] = 2
    data[data == 22] = 2

    # data[data == 228] = 3
    # data[data == 237] = 3
    # data[data == 235] = 3

    #CM
    data[data == 16] = 3
    data[data == 21] = 3

    result_img = nib.Nifti1Image(data, img.affine, img.header)

    nib.save(result_img, outfile)
    print(f"Voxel values modified and saved to {outfile}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modify voxel values in a NIfTI file.")
    parser.add_argument("--infile", required=True, help="Input NIfTI file.")
    parser.add_argument("--outfile", required=True, help="Output NIfTI file.")
    args = parser.parse_args()

    combine_amygdala_region(args.infile, args.outfile)
