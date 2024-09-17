import nibabel as nib
import numpy as np
import argparse
#  python ./HCP_seg/combine_thalamus_region.py --infile --outfile 

def combine_amygdala_region(infile, outfile):
    img = nib.load(infile)
    data = img.get_fdata().astype(int)  # 转换为整数

    # 重赋值
    #VPm
    data[data == 5] = 1
    data[data == 30] = 1

    #VPl
    data[data == 6] = 2
    data[data == 31] = 2

    #VAi
    data[data == 7] = 3
    data[data == 32] = 3

    #VAs
    data[data == 8] = 4
    data[data == 33] = 4

    #DAm
    data[data == 9] = 5
    data[data == 34] = 5

    #DAl
    data[data == 10] = 6
    data[data == 35] = 6

    # 创建一个新的 NIfTI 图像
    result_img = nib.Nifti1Image(data, img.affine, img.header)

    # 保存结果到输出文件
    nib.save(result_img, outfile)
    print(f"Voxel values modified and saved to {outfile}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modify voxel values in a NIfTI file.")
    parser.add_argument("--infile", required=True, help="Input NIfTI file.")
    parser.add_argument("--outfile", required=True, help="Output NIfTI file.")
    args = parser.parse_args()

    combine_amygdala_region(args.infile, args.outfile)
