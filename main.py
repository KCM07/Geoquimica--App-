# ================================
# PROYECTO GEOQUÍMICO - PYTHON
# ================================

# ================================
# IMPORTACIÓN DE MÓDULOS
# Cada módulo contiene una etapa del flujo geoquímico:
# - loader: lectura de datos
# - cleaning: limpieza y estandarización
# - analysis: cálculos geoquímicos y estadísticos
# - visualization: generación de gráficos
# - geospatial: análisis espacial
# - rock_name_processing: normalización litológica
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


def qa_qc_report(df):

    """
     REPORTE QA/QC (Calidad de datos geoquímicos)

    Esta función realiza una revisión inicial del dataset:
    - Dimensiones del conjunto de datos
    - Valores nulos por columna
    - Filas duplicadas
    - Balance de óxidos mayores
    - Validación de rangos geoquímicos razonables

    No modifica los datos, solo genera diagnóstico.
    """

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
        #  Cálculo del balance total de óxidos mayores
        # En análisis geoquímico, la suma ideal debe aproximarse a 100 %

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

    if "Al2O3n" in df.columns:
        fuera_rango_al = df[(df["Al2O3n"] < 0) | (df["Al2O3n"] > 30)].shape[0]
        print(f"Al2O3 fuera de rango: {fuera_rango_al}")

    if "MgOn" in df.columns:
        fuera_rango_mg = df[(df["MgOn"] < 0) | (df["MgOn"] > 25)].shape[0]
        print(f"MgO fuera de rango: {fuera_rango_mg}")

    return df


def print_lithology_summary(df):
    """
       RESUMEN LITOLÓGICO

       Genera conteos de:
       - roca base
       - contexto litológico
       - grupo litológico
       - observaciones

       Permite validar la reagrupación litológica
       y evaluar representatividad de muestras.
       """

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

    if "rock_observation" in df.columns:
        print("\nObservaciones litológicas:")
        print(df["rock_observation"].value_counts())


def main():
    # =========================
    # 1. CARGAR DATOS
    # Se lee el archivo CSV principal del proyecto
    # =========================
    path = "data/2_Geology_dataset.csv"
    df = load_data(path)

    if df is None:
        print("No se pudo cargar el archivo.")
        return

    # =========================
    # 2. QA/QC INICIAL
    # Diagnóstico de calidad antes de limpiar datos
    # =========================
    df = qa_qc_report(df)

    # =========================
    # 3. LIMPIEZA
    # Normaliza formatos, elimina errores y prepara el dataset
    # =========================
    df = clean_data(df)

    # =========================
    # 4. VARIABLES GEOQUÍMICAS
    # Se calculan índices usados en interpretación magmática
    # =========================
    df = add_geochemical_variables(df)

    # =========================
    # 5. REAGRUPACIÓN LITOLÓGICA
    # Estandariza nombres de roca y agrupa por categoría
    # =========================
    if "rock_name" in df.columns:
        df = process_rock_names(df)

    # =========================
    # 6. ESTADÍSTICAS
    # Media, mediana, desviación, min, max
    # =========================
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DESCRIPTIVAS")
    print("=" * 60)
    print(descriptive_stats(df))

    # =========================
    # 7. CORRELACIÓN
    # Relaciones geoquímicas entre óxidos
    # =========================
    print("\n" + "=" * 60)
    print("MATRIZ DE CORRELACIÓN")
    print("=" * 60)
    corr = correlation_analysis(df)
    print(corr)

    print("\n" + "=" * 60)
    print("CORRELACIONES FUERTES")
    print("=" * 60)
    print(strong_correlations(corr))

    # =========================
    # 8. RESUMEN LITOLÓGICO
    # =========================
    print_lithology_summary(df)

    # =========================
    # 9. VARIABLES EXTRA
    # =========================
    if "tipo_alumina" in df.columns:
        print("\n" + "=" * 60)
        print("SATURACIÓN DE ALÚMINA")
        print("=" * 60)
        print(df["tipo_alumina"].value_counts())

    # =========================
    # 10. GENERAR GRÁFICOS
    # Visualización geoquímica clásica

    #  Diagrama TAS: clasificación química de rocas ígneas
    #  Diagramas de Harker: tendencias magmáticas
    #  Heatmap: relaciones multivariantes
    #  Series magmáticas: evolución composicional
    #  Histogramas y QQ: distribución de datos

    # =========================
    print("\nGenerando gráficos...")

    # Scatter principal
    scatter_plot(df)

    # TAS
    tas_plot(df)

    # Harker principales
    for elem in ["TiO2n", "MgOn", "FeO*n", "CaOn", "Al2O3n", "Na2On", "K2On", "P2O5n"]:
        if elem in df.columns:
            harker_plot(df, elem)

    # Heatmap
    correlation_heatmap(corr)

    # Barras de correlaciones fuertes
    strong_corr_barplot(corr)

    # Distribución por grupo litológico
    if "rock_group" in df.columns:
        bar_plot_rock_group(df)
        group_mean_plot(df)

    # Boxplot por grupo
    if "rock_group" in df.columns and "SiO2n" in df.columns:
        box_plot_by_group(df, y_col="SiO2n")

    # Histogramas
    for elem in ["SiO2n", "TiO2n", "Al2O3n", "MgOn"]:
        if elem in df.columns:
            histogram_plot(df, elem)
            cumulative_frequency_plot(df, elem)
            qq_style_plot(df, elem)

    # Serie magmática
    if "Fe_Mg_ratio" in df.columns:
        magmatic_series_plot(df)

    # Balance de óxidos
    if "total_oxidos" in df.columns:
        oxide_balance_histogram(df)

    # =========================
    # GEOESPACIAL
    # Visualiza distribución espacial de muestras
    # =========================

    if "long" in df.columns and "lat" in df.columns:
        plot_locations(df)

    print("✔ Proceso finalizado correctamente.")


# Punto de entrada del programa
# Garantiza ejecución controlada del flujo principal

if __name__ == "__main__":
    main()