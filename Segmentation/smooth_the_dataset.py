import argparse
import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean
import scipy.stats as stats
import multiprocessing
from multiprocessing import Pool, Manager
# python ./Segmentation/smooth_the_dataset.py --in_csv csv1 --out_csv csv2 --num_workers 4

def find_nearest_neighbor(voxel_coord, subject_data):
    nearest_neighbor = None
    min_distance = float('inf')

    for _, neighbor_row in subject_data.iterrows():
        neighbor_coord = eval(neighbor_row['voxel_coordinate'])
        distance = euclidean(voxel_coord, neighbor_coord)

        if distance < min_distance:
            min_distance = distance
            nearest_neighbor = neighbor_row

    return nearest_neighbor, min_distance

def process_row(args):
    index, row, df, data_columns, result_list = args
    print(f"processing index {index}...")
    voxel_coord = eval(row['voxel_coordinate'])
    processed_row = row.copy()
    for column in data_columns:
        if row[column] == 0:
            subject_data = df[(df['subject_id'] == row['subject_id']) & (df['label'] == row['label']) & (df[column] == 1)]

            if not subject_data.empty:
                nearest_neighbor, min_distance = find_nearest_neighbor(voxel_coord, subject_data)

                if nearest_neighbor is not None and min_distance > 0:
                    mean = 1
                    std_dev = 1

                    # 计算归一化的函数值
                    pdf_mean = stats.norm.pdf(mean, loc=mean, scale=std_dev)
                    # 将min_distance带入归一化函数
                    processed_row[column] = stats.norm.pdf(min_distance, loc=mean, scale=std_dev) / pdf_mean
    result_list.append(processed_row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smooth the dataset")
    parser.add_argument("--in_csv", required=True, help="Input CSV file")
    parser.add_argument("--out_csv", required=True, help="Output CSV file")
    parser.add_argument("--num_workers", type=int, default=multiprocessing.cpu_count(), help="Number of worker processes")
    args = parser.parse_args()
    in_csv = args.in_csv
    out_csv = args.out_csv
    num_workers = args.num_workers

    df = pd.read_csv(in_csv)
    data_columns = df.columns[4:]

    manager = Manager()
    result_list = manager.list()

    pool = Pool(processes=num_workers)
    args_list = [(index, row, df, data_columns, result_list) for index, row in df.iterrows()]
    pool.map(process_row, args_list)
    pool.close()
    pool.join()

    df_out = pd.DataFrame(list(result_list), columns=df.columns)

    df_out = df_out.sort_values(by='voxel_id')

    df_out.to_csv(out_csv, index=False)
