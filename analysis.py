import pandas as pd
df = pd.read_csv('loan_slim.csv')

print('\n --Missing values per column--')
print(df.isna().sum())

print('\n--loan status categories--')
print(df['loan_status'].value_counts())