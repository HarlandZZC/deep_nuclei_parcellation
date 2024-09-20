# Pipeline of Deep Nuclei Parcellation

This is a pipeline that uses deep learning techniques to parcel brain nuclei based on tractography. It includes the entire process from dataset construction to nuclei parcellation and performance evaluation. In theory, it can be used to parcel any nuclear structures in the brain. 

Our paper [A Novel Deep Clustering Framework for Fine-Scale Parcellation of Amygdala Using DMRI Tractography](https://ieeexplore.ieee.org/document/10635363) has already been published in **ISBI2024**, demonstrating the effectiveness of this pipeline in amygdala parcellation.

The steps for using this pipeline are as follows:

1. Organize the data

    Before processing the data, it needs to be structured into a specific format. An example of the data organization format we have defined is as follows:
    
    ```bash
    site_folder_example
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

2. Nuclei Segmentation
    
    We use **segmentation** to refer to delineating the entire nuclei and **parcellation** to refer to identifying its subdivisions. 

    In this step, we used the **DDParcel**(as known as **DDSurfer**) technique to parcellate different brain regions based on each subject's DWI data. For more details on this technique, please refer to our previous work, [DDParcel: Deep Learning Anatomical Brain Parcellation From Diffusion MRI](https://ieeexplore.ieee.org/document/10314563).

    To set the environment:

    ```bash
    git clone https://github.com/HarlandZZC/deep_nuclei_parcellation.git
    cd deep_nuclei_parcellation
    git clone https://github.com/zhangfanmark/DDParcel.git
    ```

    Next, you need to follow the instructions in the [DDParcel](https://github.com/zhangfanmark/DDParcel) README to configure the DDSurfer environment, and download the [100HCP-population-mean-T2-1mm.nii.gz](https://github.com/zhangfanmark/DDSurfer/releases), placing it under `./DDParcel`.

    After that, you need to modify the four parameters: `DWIToDTIEstimation`, `DiffusionTensorScalarMeasurements`, `BRAINSFit`, and `ResampleScalarVectorDWIVolume` in `./HCP_seg/process_command.sh` based on the configuration of Slicer on your computer. Please note, we do not have to use `./DDParcel/process.sh` later.
    
    To apply DDParcel, please run:
    ```bash
    conda activate DDSurfer
    python ./HCP_seg/process_site.py --folder site_folder --flip 1
    ```

    Note: Depending on how the brain mask is created, `--flip` option may need to be adjusted to make the mask and the DTI maps in the same space after loading the nifti files as numpy arrays. For most cases, `--flip 0` is used. For the HCP data with the provided brain mask, `--flip 1` is needed. To check this, visualize the `XXX-dti-FractionalAnisotropy-Reg-NormMasked.nii.gz` file in the output folder using Slicer or other software; if there is any orientation issue, change the setting of `--flip`.



