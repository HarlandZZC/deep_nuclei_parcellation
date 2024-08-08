import os
import argparse
import vtkmodules.all as vtk
# conda activate DDSurfer
# python /home/haolin/Research/Segmentation/combine_vtk.py --infolder folder --outfile file

def combine_vtk_files(input_folder, output_file):
    # 创建一个用于合并的空数据集
    combined_data = vtk.vtkPolyData()

    # 获取输入文件夹中的所有VTK文件
    vtk_files = [f for f in os.listdir(input_folder) if f.endswith(".vtk")]

    # 创建一个合并器
    append_filter = vtk.vtkAppendPolyData()

    # 逐个读取VTK文件并合并
    for vtk_file in vtk_files:
        vtk_reader = vtk.vtkPolyDataReader()
        vtk_reader.SetFileName(os.path.join(input_folder, vtk_file))
        vtk_reader.Update()
        append_filter.AddInputData(vtk_reader.GetOutput())

    # 更新合并器并将数据复制到输出
    append_filter.Update()
    combined_data.ShallowCopy(append_filter.GetOutput())

    # 创建一个写入器并将合并后的数据写入输出文件
    vtk_writer = vtk.vtkPolyDataWriter()
    vtk_writer.SetFileName(output_file)
    vtk_writer.SetInputData(combined_data)
    vtk_writer.Write()

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="Combine VTK files in a folder into a single file.")
    parser.add_argument("--infolder", required=True, help="Input folder containing VTK files.")
    parser.add_argument("--outfile", required=True, help="Output file for the combined VTK data.")
    
    # 解析命令行参数
    args = parser.parse_args()

    # 调用合并函数
    combine_vtk_files(args.infolder, args.outfile)
