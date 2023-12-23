# Extracts key-value pairs from the data.parquet file (Cincinnati, OH locations for UFOKN)
# Authors V1 (April 13, 2023) David Kedrowski

# usage:
# python data-kv_extraction.py data.parquet

import sys
import csv
from collections import defaultdict
import pandas as pd


def router(df, lim: int) -> None:
    total_rows = 0
    # kv_sets = defaultdict(set)
    kv_lists = defaultdict(list)
    desc_list = df['Description'].values.tolist()
    for entry in desc_list:
        desc = entry.split(':')
        # print(len(desc), ":", desc[0], desc[1], desc[2])
        # kv_sets[desc[1]].add(desc[2])
        kv_lists[desc[1]].append(desc[2])
        total_rows += 1
        if total_rows == lim:
            break

    print()
    print(total_rows, "rows processed from parquet file.")
    pairs = 0
    for k in kv_lists.keys():
        pairs += len(set(kv_lists[k]))
    print(pairs, "unique key-value pairs in processed rows.\n")

    with open('data_kv-pairs.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        for k, v in kv_lists.items():
            for value in set(kv_lists[k]):
                writer.writerow([kv_lists[k].count(value), k, value])
                # print(kv_lists[k].count(value), ":", k, ":", value)


def loadParquet(pqt_file: str) -> None:
    return pd.read_parquet(pqt_file, engine='pyarrow')


if __name__ == '__main__':
    parquet_file = sys.argv[1]
    df = loadParquet(parquet_file)
    router(df, -1)  # set limit to -1 to parse entire parquet file
