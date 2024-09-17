import os
import vtk
import numpy
import argparse
# conda activate DDSurfer
# python ./Segmentation/split_atlas.py --infolder folder1 --outfolder folder2

parser = argparse.ArgumentParser()
parser.add_argument('--infolder', required=True)
parser.add_argument('--outfolder', required=True)
args = parser.parse_args()

infolder = args.infolder 
outfolder = args.outfolder


def mask(inpd, fiber_mask, color=None, preserve_point_data=False, preserve_cell_data=True, verbose=True):

    inpoints = inpd.GetPoints()
    inpointdata = inpd.GetPointData()
    incelldata = inpd.GetCellData()
    
    # output and temporary objects
    ptids = vtk.vtkIdList()
    outpd = vtk.vtkPolyData()
    outlines = vtk.vtkCellArray()
    outpoints = vtk.vtkPoints()
    outcolors = None
    outpointdata = outpd.GetPointData()
    outcelldata = outpd.GetCellData()
    tensor_names = []

    if color is not None:
        # if input is RGB
        if len(color.shape) == 2:
            if color.shape[1] == 3:
                outcolors = vtk.vtkUnsignedCharArray()
                outcolors.SetNumberOfComponents(3)

        # otherwise output floats as colors
        if outcolors == None:
            outcolors = vtk.vtkFloatArray()

    # check for cell data arrays to keep
    if preserve_cell_data:
        if incelldata.GetNumberOfArrays() > 0:
            cell_data_array_indices = list(range(incelldata.GetNumberOfArrays()))            
            for idx in cell_data_array_indices:
                array = incelldata.GetArray(idx)
                dtype = array.GetDataType()
                if dtype == 10:
                    out_array = vtk.vtkFloatArray()
                elif dtype == 6:
                    out_array = vtk.vtkIntArray()
                elif dtype == 3:
                    out_array = vtk.vtkUnsignedCharArray()
                else:
                    out_array = vtk.vtkFloatArray()
                out_array.SetNumberOfComponents(array.GetNumberOfComponents())
                out_array.SetName(array.GetName())
                if verbose:
                    print("Cell data array found:", array.GetName(), array.GetNumberOfComponents())
                outcelldata.AddArray(out_array)
                # make sure some scalars are active so rendering works
                #outpd.GetCellData().SetActiveScalars(array.GetName())
                
            #if inpd.GetCellData().GetArray('ClusterNumber'):
            #    # this will be active unless we have embedding colors
            #    outpd.GetCellData().SetActiveScalars('ClusterNumber')
            #if inpd.GetCellData().GetArray('EmbeddingColor'):
            #    # Note Slicer can't display these cell scalars (all is red)
            #    outpd.GetCellData().SetActiveScalars('EmbeddingColor')

        else:
            preserve_cell_data = False

    # check for point data arrays to keep
    if preserve_point_data:
        if inpointdata.GetNumberOfArrays() > 0:
            point_data_array_indices = list(range(inpointdata.GetNumberOfArrays()))            
            for idx in point_data_array_indices:
                array = inpointdata.GetArray(idx)
                out_array = vtk.vtkFloatArray()
                out_array.SetNumberOfComponents(array.GetNumberOfComponents())
                out_array.SetName(array.GetName())
                if verbose:
                    print("Point data array found:", array.GetName(), array.GetNumberOfComponents())
                outpointdata.AddArray(out_array)
                # make sure some scalars are active so rendering works
                #outpd.GetPointData().SetActiveScalars(array.GetName())
                # keep track of tensors to choose which is active
                if array.GetNumberOfComponents() == 9:
                    tensor_names.append(array.GetName())
        else:
            preserve_point_data = False

    # Set up scalars and tensors attributes for correct visualization in Slicer.
    # Slicer works with point data and does not handle cell data well.
    # This set of changes breaks old internal wma default visualization of cell scalars. 
    # Changes must be propagated through wma so that render is called with the name of the field to visualize.
    # the new way in wma is like this line, below.
    #ren = wma.render.render(output_polydata_s, 1000, data_mode="Cell", data_name='EmbeddingColor')

    # For Slicer: First set one of the expected tensor arrays as default for vis
    tensors_labeled = False
    for name in tensor_names:
        if name == "tensors":
            outpd.GetPointData().SetTensors(outpd.GetPointData().GetArray("tensors"))
            tensors_labeled = True
        if name == "Tensors":
            outpd.GetPointData().SetTensors(outpd.GetPointData().GetArray("Tensors"))
            tensors_labeled = True
        if name == "tensor1":
            outpd.GetPointData().SetTensors(outpd.GetPointData().GetArray("tensor1"))
            tensors_labeled = True
        if name == "Tensor1":
            outpd.GetPointData().SetTensors(outpd.GetPointData().GetArray("Tensor1"))
            tensors_labeled = True
    if not tensors_labeled:
        if len(tensor_names) > 0:
            print("Data has unexpected tensor name(s). Unable to set active for visualization:", tensor_names)
    # now set cell data visualization inactive.
    outpd.GetCellData().SetActiveScalars(None)
                
    # loop over lines
    inpd.GetLines().InitTraversal()
    outlines.InitTraversal()

    for lidx in range(0, inpd.GetNumberOfLines()):
        inpd.GetLines().GetNextCell(ptids)

        if fiber_mask[lidx]:

            if verbose:
                if lidx % 100 == 0:
                    print("Line:", lidx, "/", inpd.GetNumberOfLines())

            # get points for each ptid and add to output polydata
            cellptids = vtk.vtkIdList()

            for pidx in range(0, ptids.GetNumberOfIds()):
                point = inpoints.GetPoint(ptids.GetId(pidx))
                idx = outpoints.InsertNextPoint(point)
                cellptids.InsertNextId(idx)
                if preserve_point_data:
                    for idx in point_data_array_indices:
                        array = inpointdata.GetArray(idx)
                        out_array = outpointdata.GetArray(idx)
                        out_array.InsertNextTuple(array.GetTuple(ptids.GetId(pidx)))

            outlines.InsertNextCell(cellptids)                    

            if color is not None:
                # this code works with either 3 or 1 component only
                if outcolors.GetNumberOfComponents() == 3:
                    outcolors.InsertNextTuple3(color[lidx,0], color[lidx,1], color[lidx,2])
                else:
                    outcolors.InsertNextTuple1(color[lidx])

            if preserve_cell_data:
                for idx in cell_data_array_indices:
                    array = incelldata.GetArray(idx)
                    out_array = outcelldata.GetArray(idx)
                    out_array.InsertNextTuple(array.GetTuple(lidx))

    # put data into output polydata
    outpd.SetLines(outlines)
    outpd.SetPoints(outpoints)

    # if we had an input color requested during masking, set that to be the default scalar for vis
    if color is not None:
        outpd.GetCellData().SetScalars(outcolors)

    if verbose:
        print("Fibers sampled:", outpd.GetNumberOfLines(), "/", inpd.GetNumberOfLines())

    return outpd


with open(f"{infolder}/input_subjects.txt", "r") as file:
    subject_ids = []

    first_line = True 
    for line in file:
        if first_line:
            first_line = False  
            continue  

        columns = line.strip().split('\t')
        if len(columns) > 0:
            subject_id = columns[0] 
            subject_ids.append(subject_id)


subject_ids = [int(id) - 1 for id in subject_ids]

print(f"Subject_ID: {subject_ids}")



for fname in os.listdir(infolder):
    if fname.startswith('cluster_') and fname.endswith('.vtp'):
        inpd_path = os.path.join(infolder, fname)

        
        inpd_reader = vtk.vtkXMLPolyDataReader()

        
        inpd_file_path = os.path.join(infolder, fname)
        inpd_reader.SetFileName(inpd_file_path)

       
        inpd_reader.Update()

 
        inpd = inpd_reader.GetOutput()


        fiber_mask = numpy.zeros(inpd.GetNumberOfLines(), dtype=int)
        point_data_array = inpd.GetPointData().GetArray("Subject_ID")


        num_lines = inpd.GetNumberOfLines()


        cell_data_array = numpy.zeros(num_lines, dtype=int)
        inpd.GetLines().InitTraversal()



        for line_id in range(num_lines):
            line = inpd.GetCell(line_id)
            point_id = line.GetPointId(0)
            # print(f"point_id:{point_id}")
            subject_id = inpd.GetPointData().GetArray("Subject_ID").GetValue(point_id)
            
            all_subject_ids_match = True
            for i in range(line.GetNumberOfPoints()):
                point_id = line.GetPointId(i)
                current_subject_id = inpd.GetPointData().GetArray("Subject_ID").GetValue(point_id)
                # print(f"current_subject_id:{current_subject_id}")
                if current_subject_id != subject_id:
                    all_subject_ids_match = False
                    break
            

            if all_subject_ids_match:
                cell_data_array[line_id] = subject_id
            else:
                raise Exception("Subject_ID not thr same。line ID:" + str(line_id))
        

        for subject_id in subject_ids:

            fiber_mask = numpy.zeros(inpd.GetNumberOfLines(), dtype=int)

            for lidx in range(0, inpd.GetNumberOfLines()):
                if cell_data_array is not None:
                    line_subject_id = cell_data_array[lidx]
                    # print(f"line:{line_subject_id}")
                    # print(f"sub:{subject_id}")
                    if int(line_subject_id) == int(subject_id):
                        fiber_mask[lidx] = 1
            # print(f"fiber mask for {subject_id}:{fiber_mask} ")

            output= mask(inpd, fiber_mask)

            if not os.path.exists(os.path.join(outfolder, f"Subject_idx_{subject_id}")):
                os.makedirs(os.path.join(outfolder, f"Subject_idx_{subject_id}"))
            out_fname = os.path.join(outfolder, f"Subject_idx_{subject_id}", fname)
            writer = vtk.vtkXMLPolyDataWriter()
            writer.SetFileName(out_fname)
            writer.SetInputData(output)
            writer.Write()


input_file_path = f"{infolder}/input_subjects.txt"
output_file_path = f"{outfolder}/Subjects.txt"

with open(input_file_path, "r") as infile, open(output_file_path, "w") as outfile:
    header = infile.readline().strip().split('\t')
    
    outfile.write(f"{header[0]}\t{header[1]}\n")

    for line in infile:
        parts = line.strip().split('\t')
        

        if len(parts) >= 3:
            subject_idx = str(int(parts[0]) - 1)
            
            # subject_id_parts = parts[1].split('_')
            # subject_id = subject_id_parts[0]
            subject_id = parts[1]
            
            outfile.write(f"{subject_idx}\t{subject_id}\n")

print("DONE!")
