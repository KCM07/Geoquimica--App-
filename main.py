# ================================
# PROYECTO GEOQUÍMICO - PYTHON
# ================================

from modules.loader import load_data
from modules.cleaning import clean_data
from modules.analysis import descriptive_stats, correlation_analysis
from modules.visualization import (
    scatter_plot,
    bar_plot,
    box_plot,
    correlation_heatmap
)
from modules.geospatial import plot_locations
from modules.rock_name_processing import process_rock_names


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
        fuera_rango_sio2 = df[(df["SiO2n"] < 30) | (df["SiO2n"] > 80)].shape[0]
        print(f"SiO2 fuera de rango: {fuera_rango_sio2}")

    if "TiO2n" in df.columns:
        fuera_rango_tio2 = df[(df["TiO2n"] < 0) | (df["TiO2n"] > 6)].shape[0]
        print(f"TiO2 fuera de rango: {fuera_rango_tio2}")

    return df


def add_geochemical_variables(df):
    if "Na2On" in df.columns and "K2On" in df.columns:
        df["alkalis"] = df["Na2On"] + df["K2On"]

    if "FeO*n" in df.columns and "MgOn" in df.columns:
        df["Fe_Mg_ratio"] = df["FeO*n"] / df["MgOn"]

    if all(col in df.columns for col in ["Al2O3n", "CaOn", "Na2On", "K2On"]):
        df["A_CNK"] = df["Al2O3n"] / (df["CaOn"] + df["Na2On"] + df["K2On"])

        def classify_alumina(x):
            if x < 1:
                return "Metaluminoso"
            elif x > 1:
                return "Peraluminoso"
            else:
                return "Transicional"

        df["tipo_alumina"] = df["A_CNK"].apply(classify_alumina)

    return df


def print_lithology_summary(df):
    print("\n" + "=" * 60)
    print("RESUMEN LITOLÓGICO REAGRUPADO")
    print("=" * 60)

    if "rock_base" in df.columns:
        print("\nConteo por roca base:")
        print(df["rock_base"].value_counts())

    if "rock_context" in df.columns:
        print("\nConteo por contexto litológico:")
        print(df["rock_context"].value_counts())

    if "rock_group" in df.columns:
        print("\nConteo por grupo litológico:")
        print(df["rock_group"].value_counts())


def main():
    # =========================
    # 1. CARGAR DATOS
    # =========================
    path = "data/2_Geology_dataset.csv"
    df = load_data(path)

    # =========================
    # 2. QA/QC INICIAL
    # =========================
    df = qa_qc_report(df)

    # =========================
    # 3. LIMPIEZA
    # =========================
    df = clean_data(df)

    # =========================
    # 4. VARIABLES GEOQUÍMICAS
    # =========================
    df = add_geochemical_variables(df)

    # =========================
    # 5. LIMPIEZA Y REAGRUPACIÓN DE rock_name
    # =========================
    if "rock_name" in df.columns:
        df = process_rock_names(df)

    # =========================
    # 6. ESTADÍSTICAS
    # =========================
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DESCRIPTIVAS")
    print("=" * 60)
    print(descriptive_stats(df))

    # =========================
    # 7. CORRELACIÓN
    # =========================
    print("\n" + "=" * 60)
    print("MATRIZ DE CORRELACIÓN")
    print("=" * 60)
    corr = correlation_analysis(df)
    print(corr)

    # =========================
    # 8. VISUALIZACIÓN
    # =========================
    scatter_plot(df)
    bar_plot(df)
    box_plot(df)
    correlation_heatmap(corr)

    # =========================
    # 9. GEOESPACIAL
    # =========================
    plot_locations(df)

    # =========================
    # 10. RESÚMENES EXTRA
    # =========================
    if "tipo_alumina" in df.columns:
        print("\nClasificación de saturación de alúmina:")
        print(df["tipo_alumina"].value_counts())

    if "rock_name" in df.columns:
        print("\nConteo por tipo de roca original:")
        print(df["rock_name"].value_counts().head(20))

    print_lithology_summary(df)


if __name__ == "__main__":
    main()