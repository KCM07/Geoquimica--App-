# ================================
# PROYECTO GEOQUÍMICO - PYTHON
# ================================

# IMPORTS
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


def main():

    # =========================
    # 1. CARGAR DATOS
    # =========================
    path = r"D:\2026_KEM\CODEA 2026\Proyecto 2_ CODEa UNI\data\2_Geology_dataset.csv"
    df = load_data(path)

    # =========================
    # 2. LIMPIEZA
    # =========================
    df = clean_data(df)

    # =========================
    # 3. EXTRA GEOQUÍMICO 🔥
    # =========================
    df["alkalis"] = df["Na2On"] + df["K2On"]

    # =========================
    # 4. ANÁLISIS
    # =========================
    descriptive_stats(df)
    corr = correlation_analysis(df)

    # =========================
    # 5. VISUALIZACIÓN
    # =========================
    scatter_plot(df)
    bar_plot(df)
    box_plot(df)
    correlation_heatmap(corr)

    # =========================
    # 6. GEOESPACIAL 🌍
    # =========================
    plot_locations(df)


# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    main()