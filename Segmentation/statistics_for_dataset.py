import argparse
import pandas as pd
# python /home/haolin/Research/Segmentation/statistics_for_dataset.py --in_csv csv1 --out_csv csv2

def main():
    parser = argparse.ArgumentParser(description="统计每个subject的每个label中，对应数据为全0向量的voxel的数量并保存到CSV文件")
    parser.add_argument("--in_csv", required=True, help="输入CSV文件路径")
    parser.add_argument("--out_csv", required=True, help="输出CSV文件路径")
    args = parser.parse_args()

    # 读取输入CSV文件，跳过第一行（标题行），指定subject_id为字符串类型
    df = pd.read_csv(args.in_csv, dtype={"subject_id": str})

    # 计算每行数据是否为全0向量，从第五列开始
    is_zero_vector = (df.iloc[:, 4:] == 0).all(axis=1)

    # 将 is_zero_vector 列添加到 DataFrame 中
    df['is_zero_vector'] = is_zero_vector

    # 按subject_id和label进行分组，计算每组中is_zero_vector为True的数量
    result = df.groupby(["subject_id", "label"])["is_zero_vector"].agg(['sum', 'count']).reset_index()
    result.rename(columns={"sum": "zero_vector_count", "count": "total_vector_count"}, inplace=True)

    # 保存结果到输出CSV文件
    result.to_csv(args.out_csv, index=False)

if __name__ == "__main__":
    main()

