import os
import argparse
import nibabel as nib
from scipy.ndimage import zoom
# 这个代码还有问题
# python /home/haolin/Research/HCP_seg/downsample_nifti.py --infolder --outfolder --ax1 182 --ax2 218 --ax3 182


def rescale_nifti(infolder, outfolder, ax1, ax2, ax3):
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    for filename in os.listdir(infolder):
        if filename.endswith(".nii.gz"):
            img = nib.load(os.path.join(infolder, filename))
            data = img.get_fdata()
            new_data = zoom(data, (ax1/data.shape[0], ax2/data.shape[1], ax3/data.shape[2]), order=0)
            new_img = nib.Nifti1Image(new_data, img.affine, img.header)
            nib.save(new_img, os.path.join(outfolder, filename))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rescale NIfTI images.')
    parser.add_argument('--infolder', required=True, help='Input folder containing NIfTI files.')
    parser.add_argument('--outfolder', required=True, help='Output folder for rescaled NIfTI files.')
    parser.add_argument('--ax1', type=int, required=True, help='Rescaling size along axis 1.')
    parser.add_argument('--ax2', type=int, required=True, help='Rescaling size along axis 2.')
    parser.add_argument('--ax3', type=int, required=True, help='Rescaling size along axis 3.')
    args = parser.parse_args()

    rescale_nifti(args.infolder, args.outfolder, args.ax1, args.ax2, args.ax3)
