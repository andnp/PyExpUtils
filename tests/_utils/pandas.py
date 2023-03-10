import pandas as pd

def check_equal(df1: pd.DataFrame, df2: pd.DataFrame):
    pd.testing.assert_frame_equal(
        df1.reset_index(drop=True),
        df2.reset_index(drop=True),
        check_like=True,
    )
