#LIMPIAR DATOS
import pandas as pd

def clean_data(df):

    numeric_cols = [
        "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
        "MgOn", "CaOn", "Na2On", "K2On", "P2O5n",
        "long", "lat"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    print("\nValores nulos:")
    print(df.isnull().sum())

    df = df.dropna()

    return df