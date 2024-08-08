import os
import nibabel as nib
import numpy as np
import argparse
# python /home/haolin/Research/Segmentation/compute_RSD.py --sitefolder folder1 --outfolder folder2 


def calculate_RSD(FA_values):
    # 计算RSD
    mean_FA = np.mean(FA_values)
    std_FA = np.std(FA_values)
    RSD = (std_FA / mean_FA)
    return RSD

def process_subject(sitefolder, outfolder, subject):
    FA_file_path = os.path.join(sitefolder, subject, f'ses-1/dwi/FA/{subject}_ses-1_run-1/{subject}_ses-1_run-1-dti-FractionalAnisotropy-mni.nii.gz')
    clustered_file_path = os.path.join(outfolder, subject, f'{subject}_ses-1_run-1-DDSurfer-wmparc-mni-clustered.nii.gz')

    if os.path.exists(FA_file_path) and os.path.exists(clustered_file_path):
        FA_data = nib.load(FA_file_path).get_fdata()
        clustered_data = nib.load(clustered_file_path).get_fdata()

        unique_clusters = np.unique(clustered_data)
        cluster_RSDs = []

        for cluster in unique_clusters:
            cluster_FA_values = FA_data[clustered_data == cluster]
            cluster_RSD = calculate_RSD(cluster_FA_values)
            cluster_RSDs.append(cluster_RSD)

        single_sub_aver_RSD = np.mean(cluster_RSDs)
        return single_sub_aver_RSD
    else:
        return None

def main(sitefolder, outfolder):
    all_sub_aver_RSD = []

    with open(os.path.join(outfolder, 'RSD.csv'), 'w') as f:
        f.write('subject,single_sub_aver_RSD\n')

        for subject in os.listdir(outfolder):
            if os.path.isdir(os.path.join(outfolder, subject)):
                single_sub_aver_RSD = process_subject(sitefolder, outfolder, subject)
                if single_sub_aver_RSD is not None:
                    all_sub_aver_RSD.append(single_sub_aver_RSD)
                    f.write(f'{subject},{single_sub_aver_RSD}\n')

        all_sub_aver_RSD_value = np.mean(all_sub_aver_RSD)
        print(f"all_sub_aver_RSD: {all_sub_aver_RSD_value}")
        f.write(f'all_sub_aver_RSD,{all_sub_aver_RSD_value}\n')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Compute RSD")
    parser.add_argument("--sitefolder", help="Path to site folder", required=True)
    parser.add_argument("--outfolder", help="Path to output folder", required=True)
    args = parser.parse_args()

    main(args.sitefolder, args.outfolder)



