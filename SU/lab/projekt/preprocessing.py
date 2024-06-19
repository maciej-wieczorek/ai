import pandas as pd
from pathlib import Path

jobs_df = pd.DataFrame()
for file in Path('job_offers').iterdir():
    year_month = file.name.split('_')[0]
    year, month = year_month[:-2], year_month[-2:]
    df = pd.read_csv(file)
    df['year'] = year
    df['month'] = month
    jobs_df = pd.concat([jobs_df, df], ignore_index=True)

jobs_df = jobs_df.drop('id', axis=1)
jobs_df.to_csv('data.csv', index=False)
