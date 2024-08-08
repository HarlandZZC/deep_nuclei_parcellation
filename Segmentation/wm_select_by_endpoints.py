def line_regions(inpd, p_list, l_name, operator):

    inpoints = inpd.GetPoints()
    inpointdata = inpd.GetPointData()

    mask = numpy.zeros(inpd.GetNumberOfLines())
    
    ROI_arrary = inpointdata.GetArray(l_name)

    inpd.GetLines().InitTraversal()
    for lidx in range(0, inpd.GetNumberOfLines()):

        if lidx % 1000 == 0:
            print("Fiber: ", lidx)

        ptids = vtk.vtkIdList()
        inpd.GetLines().GetNextCell(ptids)

        line_region = []
        for pidx in [0, ptids.GetNumberOfIds()-1]:
            point = inpoints.GetPoint(ptids.GetId(pidx))
            line_region.append(ROI_arrary.GetTuple(ptids.GetId(pidx))[0])
        if lidx % 1000 == 0:
            print(line_region)

        flag = 0
        for p in p_list:
            if (line_region[0] == p or line_region[1] == p):
                flag += 1

        if operator == 'and':
            if flag == len(p_list):
                mask[lidx] = 1
        if operator == 'or': 
             if flag > 0:
                mask[lidx] = 1
    
    return mask


import argparse
import os
import nibabel as nib
import vtk
import numpy 
from nibabel.affines import apply_affine

try:
    import whitematteranalysis as wma
except:
    print("Error importing white matter analysis package\n")
    raise

#-----------------
# Parse arguments
#-----------------
parser = argparse.ArgumentParser(
    description="",
    epilog="Written by Fan Zhang")

parser.add_argument("-v", "--version",
    action="version", default=argparse.SUPPRESS,
    version='1.0',
    help="Show program's version number and exit")

parser.add_argument(
    'inputVTK',
    help='Input VTK/VTP file that is going to be converted.')
parser.add_argument(
    'outputVTK',
    help='Output VTK/VTP image, where the value of each voxel represents the number of fibers passing though the voxel.')
parser.add_argument(
    '-l',  action="store", type=str,
    help='name of the array.')
parser.add_argument( 
    '-o',  action="store", type=str,
    help='operator.')
parser.add_argument( 
    '-p',  action="store", type=int, nargs='+',
    help='pass.')

args = parser.parse_args()

inpd = wma.io.read_polydata(args.inputVTK)

mask = line_regions(inpd, args.p, args.l, args.o)

print('Total NoS: %s' % len(mask))

print('Saving kept: NoS %s' % numpy.sum(mask==1))
pd_ds = wma.filter.mask(inpd, mask==1, preserve_point_data=True, preserve_cell_data=True, verbose=False)
wma.io.write_polydata(pd_ds, args.outputVTK)

print("Save to:", args.outputVTK)
# pd_ds_not = wma.filter.mask(inpd, mask==0, preserve_point_data=True, preserve_cell_data=True, verbose=False)
# wma.io.write_polydata(pd_ds_not, args.outputVTK.replace('.vtp', 'not.vtp'))




