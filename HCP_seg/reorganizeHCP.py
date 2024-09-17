import os
import shutil
import argparse
# python ./HCP_seg/reorganizeHCP.py  --folder folder

def process_folder(folder_path):
    for subject_folder in os.listdir(folder_path):
        subject_path = os.path.join(folder_path, subject_folder)
        print(f"processing {subject_folder}...")
        
        if os.path.isdir(subject_path) and subject_folder.isdigit() and len(subject_folder) == 6:
            diffusion_path = os.path.join(subject_path, 'T1w', 'Diffusion')
            new_diffusion_path = os.path.join(subject_path, 'Diffusion')
            os.rename(diffusion_path, new_diffusion_path)
            
            corrected_masked_path = os.path.join(new_diffusion_path, 'corrected_masked')
            os.makedirs(corrected_masked_path)
            
            os.rename(os.path.join(new_diffusion_path, 'bvals'), os.path.join(new_diffusion_path, 'sub-{}_ses-1_run-1_dwi.bval'.format(subject_folder)))
            os.rename(os.path.join(new_diffusion_path, 'bvecs'), os.path.join(new_diffusion_path, 'sub-{}_ses-1_run-1_dwi.bvec'.format(subject_folder)))
            os.rename(os.path.join(new_diffusion_path, 'data.nii.gz'), os.path.join(new_diffusion_path, 'sub-{}_ses-1_run-1_dwi.nii.gz'.format(subject_folder)))
            os.rename(os.path.join(new_diffusion_path, 'grad_dev.nii.gz'), os.path.join(new_diffusion_path, 'sub-{}_ses-1_run-1_grad_dev.nii.gz'.format(subject_folder)))
            shutil.move(os.path.join(new_diffusion_path, 'eddylogs'), os.path.join(corrected_masked_path, 'eddylogs'))
            os.rename(os.path.join(new_diffusion_path, 'nodif_brain_mask.nii.gz'), os.path.join(new_diffusion_path, 'sub-{}_ses-1_run-1_dwi_BrainMask.nii.gz'.format(subject_folder)))
            shutil.move(os.path.join(new_diffusion_path, 'sub-{}_ses-1_run-1_dwi_BrainMask.nii.gz'.format(subject_folder)), os.path.join(corrected_masked_path, 'sub-{}_ses-1_run-1_dwi_BrainMask.nii.gz'.format(subject_folder)))
            shutil.copy2(os.path.join(new_diffusion_path, 'sub-{}_ses-1_run-1_dwi.nii.gz'.format(subject_folder)),
                         os.path.join(corrected_masked_path, 'sub-{}_ses-1_run-1_dwi.nii.gz'.format(subject_folder)))


            os.rename(os.path.join(subject_path, 'Diffusion'), os.path.join(subject_path, 'dwi'))
            os.rename(os.path.join(subject_path, 'T1w'), os.path.join(subject_path, 'anat'))
            
            os.rename(os.path.join(subject_path, 'anat', 'T1w_acpc_dc_restore_1.25.nii.gz'), os.path.join(subject_path, 'anat', 'sub-{}_ses-1_T1w.nii.gz'.format(subject_folder)))
            
            ses_path = os.path.join(subject_path, 'ses-1')
            os.makedirs(ses_path)
            shutil.move(os.path.join(subject_path, 'anat'), ses_path)
            shutil.move(os.path.join(subject_path, 'dwi'), ses_path)
            shutil.move(os.path.join(subject_path, 'release-notes'), ses_path)
            os.rename(subject_path, os.path.join(folder_path, f"sub-{subject_folder}"))
            print(f"{subject_folder} has been reorganized")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process subject folders")
    parser.add_argument("--folder", required=True, help="Path to the parent folder containing subject folders")
    args = parser.parse_args()

    parent_folder_path = args.folder
    process_folder(parent_folder_path)
