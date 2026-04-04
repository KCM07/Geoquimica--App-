import pandas as pd


def clean_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    numeric_cols = [
        "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
        "MgOn", "CaOn", "Na2On", "K2On", "P2O5n",
        "long", "lat"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def qa_qc_report(df):
    report = {}

    report["filas"] = df.shape[0]
    report["columnas"] = df.shape[1]
    report["nulos_por_columna"] = df.isnull().sum()
    report["duplicados"] = int(df.duplicated().sum())

    oxidos = [
        "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
        "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"
    ]

    if all(col in df.columns for col in oxidos):
        df["total_oxidos"] = df[oxidos].sum(axis=1)
        report["balance_oxidos"] = df["total_oxidos"].describe()

    rangos = {}
    if "SiO2n" in df.columns:
        rangos["SiO2_fuera_rango"] = int(df[(df["SiO2n"] < 30) | (df["SiO2n"] > 80)].shape[0])
    if "TiO2n" in df.columns:
        rangos["TiO2_fuera_rango"] = int(df[(df["TiO2n"] < 0) | (df["TiO2n"] > 6)].shape[0])

    report["rangos"] = rangos

    return df, report


def drop_missing_data(df):
    return df.dropna()