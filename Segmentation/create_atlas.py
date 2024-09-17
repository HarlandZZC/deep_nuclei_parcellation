import os
import glob
import argparse
import subprocess
from multiprocessing.pool import ThreadPool
from itertools import product
# conda activate DDSurfer
# python ./Segmentation/create_atlas.py --infolder folder1 --outfolder folder2 --num_fibers 9000 --num_clusters 100 200 300 400 --num_workers 4

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
    

    print(f"processing {infolder} with num_fibers={num_fibers} and num_clusters={num_clusters} ...")
    subprocess.call(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--infolder', required=True)
    parser.add_argument('--outfolder', required=True)
    parser.add_argument('--num_fibers', nargs='+', type=int, required=True)
    parser.add_argument('--num_clusters', nargs='+', type=int, required=True)
    parser.add_argument('--num_workers', type=int, default=1)
    args = parser.parse_args()

    infolder = args.infolder
    outfolder = args.outfolder

    num_fibers_list = args.num_fibers
    num_clusters_list = args.num_clusters

    pool = ThreadPool(args.num_workers)


    combinations = product(num_fibers_list, num_clusters_list)
    pool.starmap(process_cluster, [(num_fibers, num_clusters, infolder, outfolder) for num_fibers, num_clusters in combinations])


    pool.close()
    pool.join()

