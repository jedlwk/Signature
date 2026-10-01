import pandas as pd


def corr(df):
    # corr on log returns, raw prices trend together and inflate it
    return df.pct_change().corr()
