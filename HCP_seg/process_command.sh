#DWIToDTIEstimation=/Applications/Slicer5.2.2.app/Contents/Extensions-31382/SlicerDMRI/lib/Slicer-5.2/cli-modules/DWIToDTIEstimation
#DiffusionTensorScalarMeasurements=/Applications/Slicer5.2.2.app/Contents/Extensions-31382/SlicerDMRI/lib/Slicer-5.2/cli-modules/DiffusionTensorScalarMeasurements
#BRAINSFit=/Applications/Slicer5.2.2.app/Contents/lib/Slicer-5.2/cli-modules/BRAINSFit
#ResampleScalarVectorDWIVolume=/Applications/Slicer5.2.2.app/Contents/lib/Slicer-5.2/cli-modules/ResampleScalarVectorDWIVolume

DWIToDTIEstimation="/data01/software/Slicer-5.2.2-linux-amd64/Slicer --launch /data01/software/Slicer-5.2.2-linux-amd64/NA-MIC/Extensions-31382/SlicerDMRI/lib/Slicer-5.2/cli-modules/DWIToDTIEstimation"
DiffusionTensorScalarMeasurements="/data01/software/Slicer-5.2.2-linux-amd64/Slicer --launch /data01/software/Slicer-5.2.2-linux-amd64/NA-MIC/Extensions-31382/SlicerDMRI/lib/Slicer-5.2/cli-modules/DiffusionTensorScalarMeasurements"
BRAINSFit="/data01/software/Slicer-5.2.2-linux-amd64/Slicer --launch /data01/software/Slicer-5.2.2-linux-amd64/lib/Slicer-5.2/cli-modules/BRAINSFit"
ResampleScalarVectorDWIVolume="/data01/software/Slicer-5.2.2-linux-amd64/Slicer --launch /data01/software/Slicer-5.2.2-linux-amd64/lib/Slicer-5.2/cli-modules/ResampleScalarVectorDWIVolume"

atlas_T2=/home/haolin/Research/Segmentation/DDSurfer-main/100HCP-population-mean-T2-1mm.nii.gz

# Parse command-line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dwi) dwi="$2"; shift ;;
        --bval) bval="$2"; shift ;;
        --bvec) bvec="$2"; shift ;;
        --mask) mask="$2"; shift ;;
        --subID) subID="$2"; shift ;;

        
        --inputdir) inputdir="$2"; shift ;;
        --outputdir) outputdir="$2"; shift ;;
        --flip) flip="$2"; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Check if mandatory arguments are provided
if [ -z "$dwi" ] || [ -z "$bval" ] || [ -z "$bvec" ] || [ -z "$mask" ] || [ -z "$subID" ] || [ -z "$inputdir" ]; then
    echo "Missing required arguments."
    exit 1
fi

# Your processing code goes here using the provided arguments
echo "DWI: $dwi"
echo "bval: $bval"
echo "bvec: $bvec"
echo "mask: $mask"
echo "subID: $subID"
echo "inputdir: $inputdir"
echo "outputdir: $outputdir"
echo "flip: $flip"

mkdir -p $outputdir

nrrd_dwi=$inputdir/${subID}_QCed.nhdr
nrrd_mask=$inputdir/${subID}_QCed_bse-multi_BrainMask.nhdr
if [ ! -f  $nrrd_mask ]; then
	$1 nhdr_write.py --nifti $dwi --bval $bval --bvec $bvec --nhdr $nrrd_dwi
	$1 nhdr_write.py --nifti $mask --nhdr $nrrd_mask
fi

# DTI parameter computation
nrrd_dti=$outputdir/$subID-dti.nhdr
nrrd_b0=$outputdir/$subID-b0.nhdr
if [ ! -f $nrrd_b0 ]; then
    $1 $DWIToDTIEstimation --enumeration LS $nrrd_dwi $nrrd_dti $nrrd_b0 #-m $nrrd_mask
fi

nrrd_fa=$outputdir/$subID-dti-FractionalAnisotropy.nhdr
nrrd_trace=$outputdir/$subID-dti-Trace.nhdr
nrrd_minEig=$outputdir/$subID-dti-MinEigenvalue.nhdr
nrrd_midEig=$outputdir/$subID-dti-MidEigenvalue.nhdr

nii_fa=$outputdir/$subID-dti-FractionalAnisotropy.nii.gz
nii_trace=$outputdir/$subID-dti-Trace.nii.gz
nii_minEig=$outputdir/$subID-dti-MinEigenvalue.nii.gz
nii_midEig=$outputdir/$subID-dti-MidEigenvalue.nii.gz
 
if [ ! -f $nii_midEig ]; then
    $1 $DiffusionTensorScalarMeasurements --enumeration FractionalAnisotropy $nrrd_dti $nrrd_fa
    $1 $DiffusionTensorScalarMeasurements --enumeration Trace $nrrd_dti $nrrd_trace
    $1 $DiffusionTensorScalarMeasurements --enumeration MinEigenvalue $nrrd_dti $nrrd_minEig
    $1 $DiffusionTensorScalarMeasurements --enumeration MidEigenvalue $nrrd_dti $nrrd_midEig

    $1 nifti_write.py -i $nrrd_fa     -p ${nrrd_fa//.nhdr/}
    $1 nifti_write.py -i $nrrd_trace  -p ${nrrd_trace//.nhdr/}
    $1 nifti_write.py -i $nrrd_minEig -p ${nrrd_minEig//.nhdr/}
    $1 nifti_write.py -i $nrrd_midEig -p ${nrrd_midEig//.nhdr/}
fi

# register data to MNI
tfm=$outputdir/$subID-b0ToAtlasT2.tfm 
tfminv=$outputdir/$subID-b0ToAtlasT2_Inverse.h5
if [ ! -f $tfm ]; then
	$1 $BRAINSFit --fixedVolume $atlas_T2 --movingVolume $nrrd_b0 --linearTransform $outputdir/$subID-b0ToAtlasT2.tfm --useRigid --useAffine
fi

nii_fa_reg=$outputdir/$subID-dti-FractionalAnisotropy-Reg.nii.gz
nii_trace_reg=$outputdir/$subID-dti-Trace-Reg.nii.gz
nii_minEig_reg=$outputdir/$subID-dti-MinEigenvalue-Reg.nii.gz
nii_midEig_reg=$outputdir/$subID-dti-MidEigenvalue-Reg.nii.gz
nii_mask_reg=$outputdir/$subID-mask-Reg.nii.gz
if [ ! -f $nii_mask_reg ]; then
	$1 $ResampleScalarVectorDWIVolume -i linear ${nii_fa}     --Reference ${atlas_T2}     --transformationFile $tfm $nii_fa_reg
	$1 $ResampleScalarVectorDWIVolume -i linear ${nii_trace}  --Reference ${atlas_T2}  --transformationFile $tfm $nii_trace_reg
	$1 $ResampleScalarVectorDWIVolume -i linear ${nii_minEig} --Reference ${atlas_T2} --transformationFile $tfm $nii_minEig_reg
	$1 $ResampleScalarVectorDWIVolume -i linear ${nii_midEig} --Reference ${atlas_T2} --transformationFile $tfm $nii_midEig_reg
	$1 $ResampleScalarVectorDWIVolume -i nn     ${mask}       --Reference ${atlas_T2}       --transformationFile $tfm $nii_mask_reg
fi


# normalizing 
nii_fa_reg_norm=$outputdir/$subID-dti-FractionalAnisotropy-Reg-NormMasked.nii.gz
nii_trace_reg_norm=$outputdir/$subID-dti-Trace-Reg-NormMasked.nii.gz
nii_minEig_reg_norm=$outputdir/$subID-dti-MinEigenvalue-Reg-NormMasked.nii.gz
nii_midEig_reg_norm=$outputdir/$subID-dti-MidEigenvalue-Reg-NormMasked.nii.gz

if [ ! -f $nii_midEig_reg_norm ]; then
	$1 python /home/haolin/Research/Segmentation/DDSurfer-main/normalize.py --input $nii_fa_reg --mask $nii_mask_reg --output $nii_fa_reg_norm --flip $flip
	$1 python /home/haolin/Research/Segmentation/DDSurfer-main/normalize.py --input $nii_trace_reg --mask $nii_mask_reg --output $nii_trace_reg_norm --flip $flip
	$1 python /home/haolin/Research/Segmentation/DDSurfer-main/normalize.py --input $nii_minEig_reg --mask $nii_mask_reg --output $nii_minEig_reg_norm --flip $flip
	$1 python /home/haolin/Research/Segmentation/DDSurfer-main/normalize.py --input $nii_midEig_reg --mask $nii_mask_reg --output $nii_midEig_reg_norm --flip $flip
fi

# DDSurfer
mgz_wmparc_reg=$outputdir/$subID-DDSurfer-wmparc-Reg.mgz
if [ ! -f $mgz_wmparc_reg ]; then
	$1 python /home/haolin/Research/Segmentation/DDSurfer-main/DDSurfer_Pred.py --in_dir $outputdir --out_dir $outputdir --weights_dir /home/haolin/Research/Segmentation/DDSurfer-main/weights/
fi

nii_wmparc=$outputdir/$subID-DDSurfer-wmparc.nii.gz
if [ ! -f $nii_wmparc ]; then
 $1 $ResampleScalarVectorDWIVolume --Reference $mask --transformationFile $tfminv --interpolation nn $mgz_wmparc_reg $nii_wmparc
fi








