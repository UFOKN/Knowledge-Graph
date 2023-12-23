import pandas as pd

pd.set_option('display.max_columns', None)

df1 = pd.read_parquet('data.parquet', engine='pyarrow')
df2 = df1[df1.duplicated('UFOKN_ID', keep=False) == True]
df2.to_csv('data-duplicates.csv')

print(df2)
