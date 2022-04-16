import numpy as np
import pandas as pd

def collapseRuns(df: pd.DataFrame):
    cols = list(df.columns)
    header = list(filter(lambda c: c not in ['data', 'run'], cols))

    df = df.groupby(header)['data'].apply(lambda x: np.array(list(x))).reset_index()
    return df
