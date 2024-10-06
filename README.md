# Pipeline of Deep Nuclei Parcellation

This is a pipeline that uses deep learning techniques to parcel brain nuclei based on tractography. It includes the entire process from dataset construction to nuclei parcellation and performance evaluation. In theory, it can be used to parcel any nuclear structures in the brain. 

Our paper [A Novel Deep Clustering Framework for Fine-Scale Parcellation of Amygdala Using DMRI Tractography](https://ieeexplore.ieee.org/document/10635363) has already been published in **ISBI2024**, demonstrating the effectiveness of this pipeline in amygdala parcellation.

The steps for using this pipeline are as follows:

1. Organize the data

    Before processing the data, it needs to be structured into a specific format. An example of the data organization format we have defined is as follows:
    
    ```bash
    site_folder_example/
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

2. Nuclei segmentation
    
    We use **segmentation** to refer to delineating the entire nuclei and **parcellation** to refer to identifying its subdivisions. 

    In this step, we used the **DDParcel** (as known as **DDSurfer**) technique to parcellate different brain regions based on each subject's DWI data. For more details on this technique, please refer to our previous work, [DDParcel: Deep Learning Anatomical Brain Parcellation From Diffusion MRI](https://ieeexplore.ieee.org/document/10314563).

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
    conda env create -f DDSurfer.yaml
    conda activate DDSurfer
    python ./HCP_seg/process_site.py --folder site_folder --flip 1
    ```

    Note: Depending on how the brain mask is created, `--flip` option may need to be adjusted to make the mask and the DTI maps in the same space after loading the nifti files as numpy arrays. For most cases, `--flip 0` is used. For the HCP data with the provided brain mask, `--flip 1` is needed. To check this, visualize the `XXX-dti-FractionalAnisotropy-Reg-NormMasked.nii.gz` file in the output folder using Slicer or other software; if there is any orientation issue, change the setting of `--flip`.

    Next, you can check `site_folder/sub-xxxxxx/ses-x/dwi/DDSurfer/sub-xxxxxx_ses-x_run-x/sub-xxxxxx_ses-x_run-x-DDSurfer-wmparc.nii.gz`. Its format is the same as the original DWI, but each voxel is labeled with the region number of the brain area it belongs to.

3. Dilation of nuclei

    First, you need to find the region number corresponding to the nuclei you want to parcellate. We strongly recommend loading `sub-xxxxxx_ses-x_run-x-DDSurfer-wmparc.nii.gz` into Slicer to locate this information. You might find two labels, corresponding to the left and right brain parts of the nuclei you are interested in. Let's assume they are labeled as `label1` and `label2`.

    Then, you can run the nuclei dilation code:

    ```bash
    python ./HCP_seg/sequential_region_dilation_site.py --folder site_folder_example --num_workers a_number 
    ```

    This will create `sub-xxxxxx_ses-x_run-x-DDSurfer-wmparc-SeqDilation.nii.gz` beside every `sub-xxxxxx_ses-x_run-x-DDSurfer-wmparc.nii.gz`. If your server has multiple CPU cores and supports multiprocessing, you can choose to set `num_workers` to a value greater than 1.

4. Find the streamlines passing through the nuclei

    Next, you need to find all the fibers (also called streamlines) that pass through the nuclei. First, you should create a tractography folder to store the tractography data for all subjects. An example structure of a tractography_folder is as follows:

    ```bash
    tractography_folder_example/
    ├── 100307-ukftrack_b3000_fsmask_421a7ad_minGA0.06_minFA0.08_seedFALimit0.1.vtk
    └── 100408-ukftrack_b3000_fsmask_421a7ad_minGA0.06_minFA0.08_seedFALimit0.1.vtk
    ```

    To find the passing streamlines, please run:
    
    ```bash
    ./HCP_seg/wm_select_pass_fibers_forSeqDilation_site.py --SiteFolder site_folder_example --TractFolder tractography_folder_example --num_workers a_number
    ```

    This will create the folder `sub-xxxxxx/ses-x/dwi/selected_pass_fibers/sub-xxxxxx_ses-x_run-x/`. Inside the folder there are: `sub-xxxxxx_ses-x_run-x_pass_fibers-SeqDilation.vtk`.

5. Register the pass streamlines to MNI space

    Next, you need to register the identified pass streamlines to the standardized MNI space. This facilitates the unification of your subsequent analyses and allows you to compare your parcellation results with the standard atlases available online. To do this, you can run:

    ```bash
    ./HCP_seg/transform_vtk_file_forSeqDilation_site.py --SiteFolder site_folder_example --XfmFolder xfm_folder_example --num_workers a_number
    ```

    An example structure of a xfm_folder is as follows:

    ```bash
    xfm_folder_example/
    ├── 100307_acpc_dc2standard_itk.nii.gz
    └── 100408_acpc_dc2standard_itk.nii.gz
    ```
    This will create `sub-xxxxxx/ses-x/dwi/selected_pass_fibers/sub-xxxxxx_ses-x_run-x/sub-xxxxxx_ses-x_run-x_pass_fibers-SeqDilation-mni.vtk`. 

6. Register the `wmparc` files to MNI space

    Similarly, you need to register each previously generated `sub-xxxxxx_ses-x_run-x-DDSurfer-wmparc.nii.gz` image to the MNI space. Please run:

    ```bash
    ./HCP_seg/transform_wmparc_file_forOrigin_site.py --folder site_folder_example  --num_workers a_number
    ```

    This will create `sub-xxxxxx_ses-x_run-x-DDSurfer-wmparc-mni.nii.gz`.

7. Generated the atlas of pass streamlines

    Next, you need to gather the pass streamlines from all subjects, construct an atlas, and at the same time, divide each subject's pass streamlines into several streamline clusters.

    First, you need to collect each subject's pass streamlines together and place them in a specified folder for easier subsequent operations:

    ```bash
    .Segmentation/copy_file_with_extension.py --source_dir site_folder_example --target_dir streamlines_for_atlas_folder_example --extension pass_fibers-SeqDilation-mni.vtk
    ```

    This will copy all of the pass streamlines files into `streamlines_folder_example`. 

    Then, you can create the atlas by:

    ```bash
    python ./Segmentation/create_atlas.py --infolder streamlines_folder_example --outfolder atlas_folder_example --num_fibers f --num_clusters k --num_workers a_number
    ```

    `f` represents how many streamlines are taken from each subject to construct the atlas, and `k` represents how many streamline clusters the final atlas will contain. This will call the built-in `wm_cluster_atlas.py` in 3D Slicer, and eventually generate a folder named `atlas_f{f}_k{k}` in `atlas_folder_example`, which contains the fiber clusters obtained from different iterations. For more information of wm_cluster_atlas.py`, please refer to [Slicer's repo](https://github.com/SlicerDMRI/whitematteranalysis/blob/master/bin/wm_cluster_from_atlas.py).



