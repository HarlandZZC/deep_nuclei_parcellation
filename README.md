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

    To help you practice the entire process, we have provided a minimal `site_folder_example` containing two subjects in the release.

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
    python ./HCP_seg/wm_select_pass_fibers_forSeqDilation_site.py --SiteFolder site_folder_example --TractFolder tractography_folder_example --num_workers a_number
    ```

    This will create the folder `sub-xxxxxx/ses-x/dwi/selected_pass_fibers/sub-xxxxxx_ses-x_run-x/`. Inside the folder there are: `sub-xxxxxx_ses-x_run-x_pass_fibers-SeqDilation.vtk`.

5. Register the pass streamlines to MNI space

    Next, you need to register the identified pass streamlines to the standardized MNI space. This facilitates the unification of your subsequent analyses and allows you to compare your parcellation results with the standard atlases available online. To do this, you can run:

    ```bash
    python ./HCP_seg/transform_vtk_file_forSeqDilation_site.py --SiteFolder site_folder_example --XfmFolder xfm_folder_example --num_workers a_number
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
    python ./HCP_seg/transform_wmparc_file_forOrigin_site.py --folder site_folder_example  --num_workers a_number
    ```

    This will create `sub-xxxxxx_ses-x_run-x-DDSurfer-wmparc-mni.nii.gz`.

7. Generate the atlas of pass streamlines

    Next, you need to gather the pass streamlines from all subjects, construct an atlas, and at the same time, divide each subject's pass streamlines into several streamline clusters.

    First, you need to collect each subject's pass streamlines together and place them in a specified folder for easier subsequent operations:

    ```bash
    python ./Segmentation/copy_file_with_extension.py --source_dir site_folder_example --target_dir streamlines_for_atlas_folder_example --extension pass_fibers-SeqDilation-mni.vtk
    ```

    This will copy all of the pass streamlines files into `streamlines_folder_example`. 

    Then, you can create the atlas by:

    ```bash
    python ./Segmentation/create_atlas.py --infolder streamlines_folder_example --outfolder atlas_folder_example --num_fibers f --num_clusters k --num_workers a_number
    ```

    `f` represents how many streamlines are taken from each subject to construct the atlas, and `k` represents how many streamline clusters the final atlas will contain. This will call the built-in `wm_cluster_atlas.py` in 3D Slicer, and eventually generate a folder named `atlas_f{f}_k{k}` in `atlas_folder_example`, which contains the fiber clusters obtained from different iterations. For more information of wm_cluster_atlas.py`, please refer to [Slicer's repo](https://github.com/SlicerDMRI/whitematteranalysis/blob/master/bin/wm_cluster_from_atlas.py).

8. Choose an atlas to split

    Now, you need to select an atlas folder and split the components of each steamline cluster within this atlas that belong to each subject:

    ```bash
    python ./Segmentation/split_atlas.py --infolder atlas_folder --outfolder split_atlas_folder
    ```

    The format of the `atlas_folder` is approximately as follows:

    ```bash
    atlas_folder
    ├── atlas.p
    ├── atlas.vtp
    ├── cluster_00001.vtp
    ├── cluster_00002.vtp
    ├── cluster_00003.vtp
    ├── ...
    ```

    The format of `split_atlas_folder` is approximately as follows:

    ```bash
    split_atlas_folder
    ├── Subject_idx_0
    ├── Subject_idx_1
    ├── ...
    ├── Subjects.txt
    ```
9. Map the split results back to the site folder

    You have obtained the streamline clusters for each subject. For standardized processing, you need to map these streamline clusters back to the previous `site_folder_example`:

    ```bash
    python ./Segmentation/map_split_atlas_back_to_subjects.py  --atlas_folder split_atlas_folder --subject_folder site_folder_example --f f --k k --iteration iter
    ```
    This will map the streamline clusters of the corresponding,`f`, `k`, `iteration` back to the site folder, creating `site_folder_example/sub-xxxxxx/ses-x/dwi/atlas_split/sub-xxxxxx_ses-x_run-x/atlas_f{f}_k{k}_iteration{iter}`.

10. Transform tractography to volume
    
    Next, you need to construct a set of NIFTI files for each subject, with the same size as their original DWI. In each NIfTI file, the value stored in each voxel represents the number of times this voxel is traversed by streamlines from a specific cluster. To do this, you need to run:

    ```bash
    python ./HCP_seg/wm_tract_to_volume_site.py --folder site_folder_example --f f --k k --iteration iter --num_workers a_number
    ```

    This will create `site_folder_example/sub-xxxxxx/ses-x/dwi/WMtract2vol/sub-xxxxxx_ses-x_run-x/atlas_f{f}_k{k}_iteration{iter}`:

    ```bash
    atlas_f{f}_k{k}_iteration{iter}
    ├── cluster_00001.nii.gz
    ├── cluster_00002.nii.gz
    ├── cluster_00003.nii.gz
    ├── ...
    ```

11. Generate CSV files for each subject

    Next, by combining `sub-xxxxxx_ses-x_run-x-DDSurfer-wmparc-mni.nii.gz` and `site_folder_example/sub-xxxxxx/ses-x/dwi/WMtract2vol`, you can now calculate the traversal of each specific nucleus (the ones you previously selected for dilation) by each streamline cluster for each subject. Generate a subject-specific CSV file to record these traversal instances:

    ```bash
    python ./HCP_seg/generate_csv_for_site.py --folder ite_folder_example --f f --k k --iteration iter --labels label1 label2 ...
    ```

    This will create `/data02/DWIsegmentation/Data/HCP100_image_amygdala/sub-xxxxxx/ses-x/dwi/csv_for_segmentation/sub-xxxxxx_ses-x_run-x/atlas_f{f}_k{k}_iteration{iter}/`:

    ```bash
    atlas_f{f}_k{k}_iteration{iter}
    ├── label{label1}.csv
    ├── label{label2}.csv
    ├── ...
    ```
12. Combine the CSV files of multiple subjects into one

    For each nucleus, you need to combine the CSV files from all subjects related to it into a single CSV file:

    ```bash
    python .HCP_seg/append_csv_for_segmentation.py --infolder site_folder_example --outfolder outfolder --f f --k k --iteration iter --labels label1 label2 ...
    ```

    This will create `outfolder/f{f}_k{k}_iteration{iter}_label{label1}_append.csv`, `outfolder/f{f}_k{k}_iteration{iter}_label{label2}_append.csv`, `...`. 
    
13. Merge and tune CSV of different labels

    In the DDSurfer labeling scheme, the left and right parts of the same nucleus are assigned different labels. For instance, the left and right amygdala labels are 18 and 54, respectively. So, assuming you have obtained `f{f}_k{k}_iteration{iter}_label{18}_append.csv` and `f{f}_k{k}_iteration{iter}_label{54}_append.csv`, you may also choose to merge these two CSV files into one. You can run: 

    ```bash
    python ./Segmentation/merge_and_tune_csv_of_different_labels.py --infolder infolder --outfolder outfolder --f f --k k --iteration iter --labels label1 label2 ... --binarization 1
    ```
    Two variables need to be highlighted. The first is `--infolder`, which should be the `--outfolder` from step 12. The second variable is `--binarization`. As mentioned earlier, each voxel stores the number of times it is traversed by a cluster, with this value ranging from 0 to infinity. If `--binarization 1` is selected, the program will binarize this value to 0 or 1 during merging, recording only whether the voxel has been traversed by a cluster. This enhances data generalizability, and we recommend this approach.

    This will create `outfolder/f{f}_k{k}_iteration{iter}_label{label1}_{label2}_{...}_append_binary.csv`(if you choose `--binarization 1`) or `outfolder/f{f}_k{k}_iteration{iter}_label{label1}_{label2}_{...}_append.csv`(if you choose`--binarization 0`).

14. Gaussian smoothing

    Next, you may choose to use Gaussian smoothing techniques to refine the CSV data. For detailed technical information, please refer to our paper. To do this, please run:

    ```bash
    python ./Segmentation/smooth_the_dataset.py --in_csv in.csv --out_csv out.csv --num_workers a_number
    ```

    You can choose `outfolder/f{f}_k{k}_iteration{iter}_label{label1}_{label2}_{...}_append_binary.csv` in step 13 as `--in_csv`. Increasing the value of `--num_workers` will accelerate the smoothing process. In the code, the default settings are `mean = 1` and `std_dev = 1`, which enables both the cluster dilation and smoothing functions described in the paper. You can also choose to customize these settings.

15. Training the model and visualize the parcellation

    Now, you can finally start training the model! First, you need to adjust the hyperparameters in `Model/HCP.py` (lines 117-170). The key parameters to focus on are `--infolder` and `--csv`. If you have successfully completed all the previous steps, your `--infolder` should be the `outfolder` from step 14, and `--csv` should be `f{f}_k{k}_iteration{iter}_label{label1}_{label2}_{...}_append_binary.csv`.

    Next, you need to configure the environment:

    ```bash
    conda env create -f dwi_seg.yaml
    conda activate dwi_seg
    ```

    Then, you can start to train the model:

    ```bash
    python ./Model/HCP.py
    ```

    According to the default settings, the output parcellation results should be stored in `./Model/output`. After training, you can visualize the result of your parcellation by running:

    ```bash
    python ./Model/visualize_clustering_results.py ----subject_folder site_folder_example
    ```

    This code will generate NIFTI files containing the visualized parcellation results for each subject, based on the original images in your `site_folder_example` and the parcellation results in `./Model/output/test_results.csv`. Each voxel in these NIFTI files will store the parcel number to which it belongs.
