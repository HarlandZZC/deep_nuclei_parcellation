import os
import argparse
import vtkmodules.all as vtk
# conda activate DDSurfer
# python ./Segmentation/combine_vtk.py --infolder folder --outfile file

def combine_vtk_files(input_folder, output_file):
    
    combined_data = vtk.vtkPolyData()

    
    vtk_files = [f for f in os.listdir(input_folder) if f.endswith(".vtk")]

    
    append_filter = vtk.vtkAppendPolyData()

   
    for vtk_file in vtk_files:
        vtk_reader = vtk.vtkPolyDataReader()
        vtk_reader.SetFileName(os.path.join(input_folder, vtk_file))
        vtk_reader.Update()
        append_filter.AddInputData(vtk_reader.GetOutput())

    
    append_filter.Update()
    combined_data.ShallowCopy(append_filter.GetOutput())

    
    vtk_writer = vtk.vtkPolyDataWriter()
    vtk_writer.SetFileName(output_file)
    vtk_writer.SetInputData(combined_data)
    vtk_writer.Write()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Combine VTK files in a folder into a single file.")
    parser.add_argument("--infolder", required=True, help="Input folder containing VTK files.")
    parser.add_argument("--outfile", required=True, help="Output file for the combined VTK data.")
    

    args = parser.parse_args()


    combine_vtk_files(args.infolder, args.outfile)
