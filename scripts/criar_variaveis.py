import numpy as np
import pandas as pd


def add_variaveis(df: pd.DataFrame) -> pd.DataFrame:
    df['log10_Temperature'] = np.log10(df['Temperature (K)'])
    lum = df['Luminosity(L/Lo)'].replace(0, np.nan)
    rad = df['Radius(R/Ro)'].replace(0, np.nan)
    df['Luminosity_per_Radius2'] = lum / (rad ** 2)
    df['is_Giant'] = df['Star type'].apply(lambda t: 1 if t in (3, 4, 5) else 0)
    return df
