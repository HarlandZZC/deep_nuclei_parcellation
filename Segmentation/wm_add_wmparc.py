# python wm_compute_labels.py /home/annabelchen/PycharmProjects/SWMA/files/UKF-1T-GM-0p08-0p05-0p01-l100-r1-regionfiltered.vtp /home/annabelchen/PycharmProjects/SWMA/files/nouchine_convert_b0space.nii.gz /home/annabelchen/PycharmProjects/SWMA/files/processed_region.vtk
#!/usr/bin/env python
import glob
import os
import argparse
import multiprocessing
import numpy
import vtk
import nibabel
from nibabel.affines import apply_affine
#import cifti
import copy


try:
    import whitematteranalysis as wma
except:
    print("<wm_laterality.py> Error importing white matter analysis package\n")
    raise

try:
    from joblib import Parallel, delayed
except:
    print("<wm_laterality.py> Error importing joblib package\n")
    raise


def Incorporate_ROI_surf_Info_fan(pd_tract, refvolume):
    volume = nibabel.load(refvolume)
    print('<>', refvolume,', input volume shape: ', volume.get_fdata().shape)
    # print('<>', refvolume,', input volume shape: ', volume.get_fdata(caching='unchanged', dtype=numpy.float64).shape)
    num_fibers = pd_tract.GetNumberOfLines()
    print('fiber number:', num_fibers)
    
    pd_tract.GetLines().InitTraversal()
    line_ptids = vtk.vtkIdList()
    inpoints = pd_tract.GetPoints()
    num_points = inpoints.GetNumberOfPoints()

    label_list = numpy.zeros(num_points)
    # end_label_list = numpy.zeros(num_points)

    volume_data = volume.get_fdata()
    # volume_data = volume.get_fdata(caching='unchanged', dtype=numpy.float64)
    for lidx in range(0, num_fibers):
        pd_tract.GetLines().GetNextCell(line_ptids)
        line_length = line_ptids.GetNumberOfIds()
        number_of_endpoints = line_length

        ptidx_list = numpy.zeros(line_length)
        line_labels = numpy.zeros(line_length)
        line_end_labels=numpy.zeros(line_length)

        for pidx in range(0, line_length):
            ptidx = line_ptids.GetId(pidx)
            ptidx_list[pidx] = ptidx
            
            if pidx < number_of_endpoints or pidx > line_length - number_of_endpoints - 1:
                point = inpoints.GetPoint(ptidx) 
                point_ijk = apply_affine(numpy.linalg.inv(volume.affine), point) 
                point_ijk = numpy.rint(point_ijk).astype(numpy.int32)
                try:
                    label = volume_data[(point_ijk[0], point_ijk[1], point_ijk[2])]
                except:
                    label = 0
                    print('out point axis:', (point_ijk[0], point_ijk[1], point_ijk[2])) #print out surface
                line_labels[pidx] = round(label)


        # if endpoint touches 0 region
        if line_labels[0] < 1:
            for t_idx in range(0, number_of_endpoints):
                if line_labels[t_idx] > 0:
                    line_labels[0:t_idx] = line_labels[t_idx]
                    break

        if line_labels[-1] < 1:
            for t_idx in range(0, number_of_endpoints):
                if line_labels[-t_idx - 1] > 0:
                    line_labels[-t_idx:] = line_labels[-t_idx - 1]
                    break

        # line_end_labels[0] = line_labels[0]
        # line_end_labels[-1] = line_labels[-1]

        for pidx in range(0, line_length):
            ptidx = ptidx_list[pidx]
            label = line_labels[pidx]
            label_list[int(ptidx)] = label
            # label_end = line_end_labels[pidx]
            # end_label_list[int(ptidx)] = label_end

    vtk_array1 = vtk.vtkIntArray()
    vtk_array1.SetName('ROI_label_wmparc')
    for val in label_list:
        vtk_array1.InsertNextValue(int(val))

    # vtk_array2 = vtk.vtkDoubleArray()
    # vtk_array2.SetName('end_label')
    # for val in end_label_list:
    #     vtk_array2.InsertNextValue(int(val))

    inpointsdata = pd_tract.GetPointData()
    inpointsdata.AddArray(vtk_array1)
    # inpointsdata.AddArray(vtk_array2)
    inpointsdata.Update()
    return pd_tract
    
def main():
    #-----------------
    # Parse arguments
    #-----------------
    parser = argparse.ArgumentParser(
        description="",
        epilog="Written by Fan Zhang")
    
    parser.add_argument(
        'inputFile',
        help='Contains whole-brain tractography as vtkPolyData file(s).')

    parser.add_argument(
        'parcelFile',
        help='Contains brain region parcellation.')

    parser.add_argument(
        'outputFile',
        help='The output directory should be a specific directory in detail. It will be created if needed.')


    args = parser.parse_args()
    
    print("Input File", args.inputFile)
    print("Output File", args.outputFile)
    
    print("")
    print("=====input directory======\n", args.inputFile)
    print("=====output directory=====\n", args.outputFile)
    print("==========================")

    
    # =======================================================================
    # Above this line is argument parsing. Below this line is the pipeline.
    # =======================================================================

    wm = wma.io.read_polydata(args.inputFile)
    refvolume =args.parcelFile

    wm2 = Incorporate_ROI_surf_Info_fan(wm, refvolume)

    # outputs
    # -------------------
    fname = args.outputFile
    path=os.path.dirname(fname)
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        wma.io.write_polydata(wm2, fname)
        print("Wrote output", fname, ".")
    except:
        print("Unknown exception in IO")
        raise


if __name__ == '__main__':
    main()
