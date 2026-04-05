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
    bar_plot,
    box_plot,
    correlation_heatmap,
    bar_plot_rock_group
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
    path = "data/2_Geology_dataset.csv"
    df = load_data(path)

    if df is None:
        return

    df = qa_qc_report(df)
    df = clean_data(df)
    df = add_geochemical_variables(df)

    if "rock_name" in df.columns:
        df = process_rock_names(df)

    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DESCRIPTIVAS")
    print("=" * 60)
    print(descriptive_stats(df))

    print("\n" + "=" * 60)
    print("MATRIZ DE CORRELACIÓN")
    print("=" * 60)
    corr = correlation_analysis(df)
    print(corr)

    print("\n" + "=" * 60)
    print("CORRELACIONES FUERTES")
    print("=" * 60)
    print(strong_correlations(corr))

    scatter_plot(df)
    bar_plot(df)
    box_plot(df)
    correlation_heatmap(corr)
    bar_plot_rock_group(df)

    if "long" in df.columns and "lat" in df.columns:
        plot_locations(df)

    if "tipo_alumina" in df.columns:
        print("\nClasificación de saturación de alúmina:")
        print(df["tipo_alumina"].value_counts())

    if "rock_name" in df.columns:
        print("\nConteo por tipo de roca original:")
        print(df["rock_name"].value_counts().head(20))

    print_lithology_summary(df)


if __name__ == "__main__":
    main()