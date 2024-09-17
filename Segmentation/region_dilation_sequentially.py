import nibabel as nib
import numpy as np
from scipy import ndimage
import argparse
# python ./Segmentation/region_dilation_successively.py --in_file /data02/ASD/test/test_301DS/sub-13166/ses-2/dwi/DDSurfer/sub-13166_ses-2_run-1/sub-13166_ses-2_run-1-DDSurfer-wmparc.nii.gz --out_file /data02/ASD/test/test_301DS/sub-13166/ses-2/dwi/DDSurfer/sub-13166_ses-2_run-1/sub-13166_ses-2_run-1-DDSurfer-wmparc-dilation.nii.gz --labels 18 54

parser = argparse.ArgumentParser()
parser.add_argument('--in_file')
parser.add_argument('--out_file')
parser.add_argument('--labels', nargs='+', type=int)

args = parser.parse_args()

img = nib.load(args.in_file)
data = img.get_fdata()

# struct = ndimage.generate_binary_structure(3, 1)
struct = np.zeros((3,3,3))
struct[1,1,0] = 0.5  
struct[1,0,1] = 0.5
struct[0,1,1] = 0.5

for label in args.labels:
    print(f"--- Processing label {label} ---") 
    mask = (data == label)
    print('Mask shape:', mask.shape)
    
    dilated_mask = ndimage.binary_dilation(mask, struct)
    print('Dilated mask shape:', dilated_mask.shape)

    orig_data = data.copy()
    # orig_labels = {label: np.count_nonzero(orig_data ==label) for label in np.unique(orig_data)}
    print('Original data type:', orig_data.dtype)
    # print('Original label counts:', orig_labels)

    dilated_data = data.copy()

    overlay_coords = np.where(dilated_mask)
    

    for overlay_x, overlay_y, overlay_z in zip(*overlay_coords):
        overlay_label = dilated_data[overlay_x, overlay_y, overlay_z]
        if (1000 <= overlay_label <= 1035) or (2000 <= overlay_label <= 2035):
            continue  
        dilated_data[overlay_x, overlay_y, overlay_z] = label
    
    print('Dilated data type:', dilated_data.dtype)
    # print('Dilated label counts:', {label: np.count_nonzero(dilated_data==label) for label in np.unique(dilated_data)})
    
    change_mask = (orig_data != dilated_data)
    change_locs = np.where(change_mask)
    labels_before = orig_data[change_locs]
    label_before, counts = np.unique(labels_before, return_counts=True)
    print("Label changes:")
    for l, c in zip(label_before, counts):
        print(f"{l}: {c} pixels")
    total_change = np.count_nonzero(change_mask)
    print(f"Total label changes: {total_change}")

    data = dilated_data

nib.Nifti1Image(dilated_data, img.affine).to_filename(args.out_file)
         
         
print('Dilated labels saved to:', args.out_file)