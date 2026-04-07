# ================================
# PROYECTO GEOQUÍMICO - PYTHON
# ================================

from modules.loader import load_data
from modules.cleaning import clean_data
from modules.analysis import (
    descriptive_stats,
    correlation_analysis,
    add_geochemical_variables,
    strong_correlations
)
from modules.visualization import (
    scatter_plot,
    tas_plot,
    harker_plot,
    correlation_heatmap,
    strong_corr_barplot,
    box_plot_by_group,
    histogram_plot,
    cumulative_frequency_plot,
    qq_style_plot,
    magmatic_series_plot,
    bar_plot_rock_group,
    group_mean_plot,
    oxide_balance_histogram
)
from modules.geospatial import plot_locations
from modules.rock_name_processing import process_rock_names

import pandas as pd


# =========================
# TAS CLASS (NUEVO 🔥)
# =========================
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

    if "alkalis" not in df.columns and "Na2On" in df.columns and "K2On" in df.columns:
        df["alkalis"] = df["Na2On"] + df["K2On"]

    if "SiO2n" in df.columns and "alkalis" in df.columns:
        df["tas_class"] = df.apply(
            lambda row: classify_tas_simple(row["SiO2n"], row["alkalis"]),
            axis=1
        )
    else:
        df["tas_class"] = "unknown"

    return df


# =========================
# QA/QC
# =========================
def qa_qc_report(df):

    print("\n" + "=" * 60)
    print("QA/QC - REPORTE DE CALIDAD DE DATOS")
    print("=" * 60)

    print(f"\nNúmero de filas: {df.shape[0]}")
    print(f"Número de columnas: {df.shape[1]}")

    print("\nValores nulos por columna:")
    print(df.isnull().sum())

    print("\nNúmero de duplicados:")
    print(df.duplicated().sum())

    oxidos = [
        "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
        "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"
    ]

    if all(col in df.columns for col in oxidos):
        df["total_oxidos"] = df[oxidos].sum(axis=1)

        print("\nBalance de óxidos:")
        print(df["total_oxidos"].describe())

    print("\nValidación de rangos:")

    if "SiO2n" in df.columns:
        print("SiO2 fuera de rango:", df[(df["SiO2n"] < 30) | (df["SiO2n"] > 80)].shape[0])

    if "TiO2n" in df.columns:
        print("TiO2 fuera de rango:", df[(df["TiO2n"] < 0) | (df["TiO2n"] > 6)].shape[0])

    if "Al2O3n" in df.columns:
        print("Al2O3 fuera de rango:", df[(df["Al2O3n"] < 0) | (df["Al2O3n"] > 30)].shape[0])

    if "MgOn" in df.columns:
        print("MgO fuera de rango:", df[(df["MgOn"] < 0) | (df["MgOn"] > 25)].shape[0])

    return df


# =========================
# RESUMEN LITOLÓGICO
# =========================
def print_lithology_summary(df):

    print("\n" + "=" * 60)
    print("RESUMEN LITOLÓGICO")
    print("=" * 60)

    if "rock_base" in df.columns:
        print("\nRoca base:")
        print(df["rock_base"].value_counts())

    if "rock_context" in df.columns:
        print("\nContexto:")
        print(df["rock_context"].value_counts())

    if "rock_group" in df.columns:
        print("\nGrupo:")
        print(df["rock_group"].value_counts())

    if "rock_observation" in df.columns:
        print("\nObservaciones:")
        print(df["rock_observation"].value_counts())


# =========================
# MAIN
# =========================
def main():

    path = "data/2_Geology_dataset.csv"
    df = load_data(path)

    if df is None:
        print("No se pudo cargar el archivo.")
        return

    # 1 QA/QC
    df = qa_qc_report(df)

    # 2 limpieza
    df = clean_data(df)

    # 3 variables geoquímicas
    df = add_geochemical_variables(df)

    # 🔥 NUEVO TAS
    df = add_tas_class(df)

    # 4 reagrupación
    if "rock_name" in df.columns:
        df = process_rock_names(df)

    # 5 estadísticas
    print("\nESTADÍSTICAS")
    print(descriptive_stats(df))

    # 6 correlación
    corr = correlation_analysis(df)
    print("\nCORRELACIÓN")
    print(corr)

    print("\nCORRELACIONES FUERTES")
    print(strong_correlations(corr))

    # 7 litología
    print_lithology_summary(df)

    # 8 alumina
    if "tipo_alumina" in df.columns:
        print("\nSATURACIÓN DE ALÚMINA")
        print(df["tipo_alumina"].value_counts())

    # =========================
    # GRÁFICOS
    # =========================
    print("\nGenerando gráficos...")

    scatter_plot(df)

    # 🔥 TAS CORREGIDO
    tas_plot(df, color_col="tas_class")

    for elem in ["TiO2n", "MgOn", "FeO*n", "CaOn", "Al2O3n", "Na2On", "K2On", "P2O5n"]:
        if elem in df.columns:
            harker_plot(df, elem)

    correlation_heatmap(corr)
    strong_corr_barplot(corr)

    if "rock_group" in df.columns:
        bar_plot_rock_group(df)
        group_mean_plot(df)

    if "rock_group" in df.columns and "SiO2n" in df.columns:
        box_plot_by_group(df, y_col="SiO2n")

    for elem in ["SiO2n", "TiO2n", "Al2O3n", "MgOn"]:
        if elem in df.columns:
            histogram_plot(df, elem)
            cumulative_frequency_plot(df, elem)
            qq_style_plot(df, elem)

    if "Fe_Mg_ratio" in df.columns:
        magmatic_series_plot(df)

    if "total_oxidos" in df.columns:
        oxide_balance_histogram(df)

    if "long" in df.columns and "lat" in df.columns:
        plot_locations(df)

    print("✔ Proceso finalizado correctamente.")


if __name__ == "__main__":
    main()