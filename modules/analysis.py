import numpy as np
import pandas as pd


# ============================================================
# VARIABLES GEOQUÍMICAS
# ============================================================
def add_geochemical_variables(df):
    df = df.copy()

    # =========================
    # Alcalinidad total
    # =========================
    if "Na2On" in df.columns and "K2On" in df.columns:
        df["alkalis"] = df["Na2On"] + df["K2On"]

    # =========================
    # Relación Fe/Mg
    # =========================
    if "FeO*n" in df.columns and "MgOn" in df.columns:
        df["Fe_Mg_ratio"] = np.where(
            df["MgOn"] != 0,
            df["FeO*n"] / df["MgOn"],
            np.nan
        )

    # =========================
    # Índice A/CNK
    # =========================
    if all(col in df.columns for col in ["Al2O3n", "CaOn", "Na2On", "K2On"]):

        denominador = df["CaOn"] + df["Na2On"] + df["K2On"]

        df["A_CNK"] = np.where(
            denominador != 0,
            df["Al2O3n"] / denominador,
            np.nan
        )

        def classify_alumina(x):
            if pd.isna(x):
                return "Indeterminado"
            if x < 1:
                return "Metaluminoso"
            elif x > 1.1:
                return "Peraluminoso"
            else:
                return "Transicional"

        df["tipo_alumina"] = df["A_CNK"].apply(classify_alumina)

    return df


# ============================================================
# 🔥 NUEVO: TAS CLASS
# ============================================================
def classify_tas_simple(sio2, alkalis):
    if pd.isna(sio2) or pd.isna(alkalis):
        return "unknown"

    if sio2 < 45:
        return "ultrabasic"
    elif 45 <= sio2 < 52:
        return "basalt"
    elif 52 <= sio2 < 57:
        return "basaltic andesite"
    elif 57 <= sio2 < 63:
        return "andesite"
    elif 63 <= sio2 < 69:
        return "dacite"
    else:
        return "rhyolite"


def add_tas_class(df):
    df = df.copy()

    # asegurar alkalis
    if "alkalis" not in df.columns:
        if "Na2On" in df.columns and "K2On" in df.columns:
            df["alkalis"] = df["Na2On"] + df["K2On"]

    if "SiO2n" in df.columns and "alkalis" in df.columns:
        df["tas_class"] = df.apply(
            lambda row: classify_tas_simple(row["SiO2n"], row["alkalis"]),
            axis=1
        )
    else:
        df["tas_class"] = "unknown"

    return df


# ============================================================
# ESTADÍSTICAS DESCRIPTIVAS
# ============================================================
def descriptive_stats(df):
    oxidos = [
        "SiO2n", "TiO2n", "Al2O3n",
        "FeO*n", "MnOn", "MgOn",
        "CaOn", "Na2On", "K2On", "P2O5n"
    ]

    cols_validas = [col for col in oxidos if col in df.columns]
    return df[cols_validas].describe().round(2)


# ============================================================
# CORRELACIÓN
# ============================================================
def correlation_analysis(df):
    oxidos = [
        "SiO2n", "TiO2n", "Al2O3n",
        "FeO*n", "MnOn", "MgOn",
        "CaOn", "Na2On", "K2On", "P2O5n"
    ]

    cols_validas = [col for col in oxidos if col in df.columns]
    return df[cols_validas].corr().round(2)


# ============================================================
# CORRELACIONES FUERTES
# ============================================================
def strong_correlations(corr, threshold=0.7):
    pares = []

    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            val = corr.iloc[i, j]
            if abs(val) >= threshold:
                pares.append([corr.columns[i], corr.columns[j], round(val, 2)])

    if not pares:
        return pd.DataFrame(columns=["Variable 1", "Variable 2", "Correlación"])

    return pd.DataFrame(
        pares,
        columns=["Variable 1", "Variable 2", "Correlación"]
    ).sort_values(by="Correlación", ascending=False)