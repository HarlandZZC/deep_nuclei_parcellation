import os
import glob
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
from itertools import product
# conda activate DDSurfer
# python /home/haolin/Research/Segmentation/create_atlas.py --infolder folder1 --outfolder folder2 --num_fibers 9000 --num_clusters 100 200 300 400 --num_workers 4

def process_cluster(num_fibers, num_clusters, infolder, outfolder):
    command = [
        "wm_cluster_atlas.py",
        "-norender",
        "-l",
        "0",
        "-f",
        f"{num_fibers}",
        "-nystrom_sample",
        "2500",
        "-k",
        f"{num_clusters}",
        "-j",
        "1",
        infolder,
        f"{outfolder}/atlas_f{num_fibers}_k{num_clusters}"
    ]
    
    # 执行命令
    print(f"processing {infolder} with num_fibers={num_fibers} and num_clusters={num_clusters} ...")
    subprocess.call(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--infolder', required=True, help='要处理的文件夹路径')
    parser.add_argument('--outfolder', required=True, help='输出的文件夹路径')
    parser.add_argument('--num_fibers', nargs='+', type=int, required=True, help='设定的fiber的数量')
    parser.add_argument('--num_clusters', nargs='+', type=int, required=True, help='设定的cluster的数量')
    parser.add_argument('--num_workers', type=int, default=1, help='线程池中的工作线程数量')
    args = parser.parse_args()

    infolder = args.infolder
    outfolder = args.outfolder

    num_fibers_list = args.num_fibers
    num_clusters_list = args.num_clusters

    # 创建线程池
    pool = ThreadPool(args.num_workers)

    # 生成所有可能的组合并使用线程池并行执行处理
    combinations = product(num_fibers_list, num_clusters_list)
    pool.starmap(process_cluster, [(num_fibers, num_clusters, infolder, outfolder) for num_fibers, num_clusters in combinations])

    # 关闭线程池
    pool.close()
    pool.join()

