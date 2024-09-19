# Pipeline of Deep Nuclei Parcellation

This is a pipeline that uses deep learning techniques to parcel brain nuclei based on tractography. It includes the entire process from dataset construction to nuclei parcellation and performance evaluation. In theory, it can be used to parcel any nuclear structures in the brain. 

Our paper [A Novel Deep Clustering Framework for Fine-Scale Parcellation of Amygdala Using DMRI Tractography](https://ieeexplore.ieee.org/document/10635363) has already been published in **ISBI2024**, demonstrating the effectiveness of this pipeline in amygdala parcellation.

The steps for using this pipeline are as follows:

1. Organize the data. 

    Before processing the data, it needs to be structured into a specific format. An example of the data organization format we have defined is as follows:
    
    ```bash
    site_example
        ├── sub-100307
        │   └── ses-1
        │       ├── anat
        │       │   └── sub-100307_ses-1_T1w.nii.gz
        │       └── dwi
        │           ├── corrected_masked
        │           │   ├── sub-100307_ses-1_run-1_dwi_BrainMask.nii.gz
        │           │   ├── sub-100307_ses-1_run-1_dwi_extracted.bval
        │           │   ├── sub-100307_ses-1_run-1_dwi_extracted-Bvalue5-0.bval
        │           │   ├── sub-100307_ses-1_run-1_dwi_extracted-Bvalue5-0.bvec
        │           │   ├── sub-100307_ses-1_run-1_dwi_extracted.bvec
        │           │   ├── sub-100307_ses-1_run-1_dwi_extracted.nii.gz
        │           │   ├── sub-100307_ses-1_run-1_QCed_bse-multi_BrainMask.nhdr
        │           │   └── sub-100307_ses-1_run-1_QCed.nhdr
        │           ├── sub-100307_ses-1_run-1_dwi.bval
        │           ├── sub-100307_ses-1_run-1_dwi.bvec
        │           └── sub-100307_ses-1_run-1_dwi.nii.gz
        └── sub-100408
            └── ses-1
                ├── anat
                │   └── sub-100408_ses-1_T1w.nii.gz
                └── dwi
                    ├── corrected_masked
                    │   ├── sub-100408_ses-1_run-1_dwi_BrainMask.nii.gz
                    │   ├── sub-100408_ses-1_run-1_dwi_extracted.bval
                    │   ├── sub-100408_ses-1_run-1_dwi_extracted-Bvalue5-0.bval
                    │   ├── sub-100408_ses-1_run-1_dwi_extracted-Bvalue5-0.bvec
                    │   ├── sub-100408_ses-1_run-1_dwi_extracted.bvec
                    │   ├── sub-100408_ses-1_run-1_dwi_extracted.nii.gz
                    │   ├── sub-100408_ses-1_run-1_QCed_bse-multi_BrainMask.nhdr
                    │   └── sub-100408_ses-1_run-1_QCed.nhdr
                    ├── sub-100408_ses-1_run-1_dwi.bval
                    ├── sub-100408_ses-1_run-1_dwi.bvec
                    └── sub-100408_ses-1_run-1_dwi.nii.gz
    ```