import os
import nibabel as nib
import numpy as np
# python ./Segmentation/generate_heatmap.py --folder folder

def process_folder(folder):
    # 创建heatmap文件夹
    heatmap_folder = os.path.join(folder, 'heatmap')
    os.makedirs(heatmap_folder, exist_ok=True)

    # 获取所有sub-xxxxxx文件夹
    sub_folders = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f)) and f.startswith('sub-')]

    # 初始化heatmap
    base_image_path = os.path.join(folder, sub_folders[0], sub_folders[0] + '_ses-1_run-1-DDSurfer-wmparc-mni-clustered.nii.gz')
    base_image = nib.load(base_image_path)
    base_data = base_image.get_fdata()
    heatmap = np.zeros((base_data.shape[0], base_data.shape[1], base_data.shape[2], int(np.max(base_data))))

    # 遍历所有sub-xxxxxx文件夹
    for sub_folder in sub_folders:
        image_path = os.path.join(folder, sub_folder, sub_folder + '_ses-1_run-1-DDSurfer-wmparc-mni-clustered.nii.gz')
        image = nib.load(image_path)
        data = image.get_fdata()

        # 更新heatmap
        for k in range(1, heatmap.shape[3] + 1):
            heatmap[:, :, :, k - 1] += (data == k)

    # 保存heatmap
    for k in range(1, heatmap.shape[3] + 1):
        new_image = nib.Nifti1Image(heatmap[:, :, :, k - 1], base_image.affine, base_image.header)
        nib.save(new_image, os.path.join(heatmap_folder, 'cluster_{}.nii.gz'.format(k)))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--folder', type=str, help='an integer for the accumulator')
    args = parser.parse_args()
    process_folder(args.folder)
