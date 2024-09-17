import argparse
import pandas as pd
# python ./Segmentation/statistics_for_dataset.py --in_csv csv1 --out_csv csv2

def main():
    parser = argparse.ArgumentParser(description="count the number of zero vectors in the dataset")
    parser.add_argument("--in_csv", required=True, help="input CSV file")
    parser.add_argument("--out_csv", required=True, help="output CSV file")
    args = parser.parse_args()

    df = pd.read_csv(args.in_csv, dtype={"subject_id": str})

    is_zero_vector = (df.iloc[:, 4:] == 0).all(axis=1)

    df['is_zero_vector'] = is_zero_vector

    result = df.groupby(["subject_id", "label"])["is_zero_vector"].agg(['sum', 'count']).reset_index()
    result.rename(columns={"sum": "zero_vector_count", "count": "total_vector_count"}, inplace=True)

    result.to_csv(args.out_csv, index=False)

if __name__ == "__main__":
    main()

