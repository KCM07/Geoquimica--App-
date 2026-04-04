import streamlit as st
import pandas as pd

from modules.loader import load_data
from modules.cleaning import clean_data
from modules.analysis import (
    descriptive_stats,
    correlation_analysis,
    add_geochemical_variables
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

st.set_page_config(page_title="Análisis Geoquímico", layout="wide")

st.title("⛏️ Análisis Geoquímico de Rocas Ígneas")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])


def build_qc_table(df: pd.DataFrame) -> pd.DataFrame:
    df_qc = df.copy()

    oxidos = [
        "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
        "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"
    ]

    for col in oxidos:
        if col not in df_qc.columns:
            df_qc[col] = pd.NA

    df_qc["QC_flag"] = ""

    # Balance de óxidos
    oxidos_presentes = [col for col in oxidos if col in df_qc.columns]
    df_qc["total_oxidos"] = df_qc[oxidos_presentes].sum(axis=1, skipna=True)

    df_qc.loc[
        (df_qc["total_oxidos"] < 95) | (df_qc["total_oxidos"] > 105),
        "QC_flag"
    ] += "Balance de óxidos fuera de rango; "

    # Rangos geoquímicos básicos
    if "SiO2n" in df_qc.columns:
        df_qc.loc[
            (df_qc["SiO2n"] < 30) | (df_qc["SiO2n"] > 80),
            "QC_flag"
        ] += "SiO2 fuera de rango; "

    if "TiO2n" in df_qc.columns:
        df_qc.loc[
            (df_qc["TiO2n"] < 0) | (df_qc["TiO2n"] > 6),
            "QC_flag"
        ] += "TiO2 fuera de rango; "

    if "Al2O3n" in df_qc.columns:
        df_qc.loc[
            (df_qc["Al2O3n"] < 0) | (df_qc["Al2O3n"] > 30),
            "QC_flag"
        ] += "Al2O3 fuera de rango; "

    if "MgOn" in df_qc.columns:
        df_qc.loc[
            (df_qc["MgOn"] < 0) | (df_qc["MgOn"] > 25),
            "QC_flag"
        ] += "MgO fuera de rango; "

    # Nulos en columnas principales
    principales = ["rock_name", "SiO2n", "Al2O3n", "FeO*n", "MgOn"]
    existentes = [c for c in principales if c in df_qc.columns]
    if existentes:
        mask_nulos = df_qc[existentes].isnull().any(axis=1)
        df_qc.loc[mask_nulos, "QC_flag"] += "Valores nulos en campos clave; "

    return df_qc


def highlight_qc(row):
    if "QC_flag" in row and isinstance(row["QC_flag"], str) and row["QC_flag"].strip() != "":
        return ["background-color: #ffdddd"] * len(row)
    return [""] * len(row)


if uploaded_file:
    # =========================
    # 1. CARGA Y LIMPIEZA
    # =========================
    df = load_data(uploaded_file)

    if df is not None:
        df = clean_data(df)
        df = add_geochemical_variables(df)
        df = process_rock_names(df)

        # =========================
        # 2. VISTA INTERACTIVA
        # =========================
        st.subheader("📋 Visualización de los datos")
        st.write(f"Filas totales: {df.shape[0]} | Columnas: {df.shape[1]}")

        modo = st.radio(
            "Selecciona cómo quieres visualizar los datos:",
            ["Vista previa (50 filas)", "Elegir rango", "Ver todo"],
            index=0
        )

        if modo == "Vista previa (50 filas)":
            st.dataframe(df.head(50), use_container_width=True, height=500)

        elif modo == "Elegir rango":
            col1, col2 = st.columns(2)

            with col1:
                inicio = st.number_input(
                    "Fila inicial",
                    min_value=0,
                    max_value=len(df) - 1,
                    value=0
                )

            with col2:
                fin = st.number_input(
                    "Fila final",
                    min_value=1,
                    max_value=len(df),
                    value=min(50, len(df))
                )

            if inicio < fin:
                st.dataframe(df.iloc[inicio:fin], use_container_width=True, height=500)
            else:
                st.warning("⚠️ La fila inicial debe ser menor que la final")

        elif modo == "Ver todo":
            st.dataframe(df, use_container_width=True, height=500)

        # =========================
        # 3. ESTRUCTURA DE DATOS
        # =========================
        st.subheader("📊 Estructura de variables")

        oxidos = [
            "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
            "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"
        ]

        calculadas = [col for col in ["alkalis", "Fe_Mg_ratio", "A_CNK", "tipo_alumina"] if col in df.columns]

        c1, c2 = st.columns(2)

        with c1:
            st.write("**🧪 Variables originales (óxidos)**")
            st.write(oxidos)

        with c2:
            st.write("**⚙️ Variables calculadas**")
            st.write(calculadas)

        # =========================
        # 4. FÓRMULAS Y CONCEPTOS
        # =========================
        st.subheader("📐 Fórmulas y conceptos clave")

        st.markdown("""
**Alcalinidad total (Alkalis)**  
**Fórmula:** `Na₂O + K₂O`  
**Concepto:** se usa para explorar enriquecimiento en álcalis y es clave para diagramas TAS.

**Relación Fe/Mg**  
**Fórmula:** `FeO* / MgO`  
**Concepto:** ayuda a observar tendencias de diferenciación magmática.

**Índice A/CNK**  
**Fórmula:** `Al₂O₃ / (CaO + Na₂O + K₂O)`  
**Concepto:** permite clasificar muestras en metaluminosas, transicionales o peraluminosas.

**Balance de óxidos**  
**Fórmula:** suma de óxidos mayores  
**Concepto:** idealmente debe aproximarse a 100%; sirve para QA/QC.
        """)

        # =========================
        # 5. QA/QC Y RESALTADO
        # =========================
        st.subheader("🚨 Control de calidad (QA/QC)")

        df_qc = build_qc_table(df)
        df_error = df_qc[df_qc["QC_flag"].astype(str).str.strip() != ""]

        st.write(f"**Filas con inconsistencia:** {len(df_error)}")

        if len(df_error) > 0:
            st.write("**Resumen rápido de inconsistencias**")
            st.dataframe(
                df_error["QC_flag"].value_counts().reset_index(),
                use_container_width=True
            )
        else:
            st.success("✔ No se detectaron inconsistencias principales")

        st.write("**Tabla QA/QC con resaltado**")
        st.dataframe(
            df_qc.style.apply(highlight_qc, axis=1),
            use_container_width=True,
            height=500
        )

        if st.button("Aplicar corrección automática (quitar filas con inconsistencia)"):
            df_clean_qc = df_qc[df_qc["QC_flag"].astype(str).str.strip() == ""].copy()
            st.success(f"✔ Filas conservadas después de QA/QC: {len(df_clean_qc)}")
            st.dataframe(df_clean_qc, use_container_width=True, height=500)

        # =========================
        # 6. REAGRUPACIÓN LITOLÓGICA
        # =========================
        st.subheader("🪨 Reagrupación litológica")

        cols_litologia = [
            "rock_name",
            "rock_name_clean",
            "rock_base",
            "rock_context",
            "rock_observation",
            "rock_group"
        ]

        cols_existentes = [col for col in cols_litologia if col in df.columns]

        if cols_existentes:
            st.dataframe(
                df[cols_existentes],
                use_container_width=True,
                height=400
            )
        else:
            st.warning("No se encontraron columnas de reagrupación litológica.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Roca base**")
            st.dataframe(
                df["rock_base"].value_counts().reset_index(),
                use_container_width=True,
                height=350
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Roca base**")
            if "rock_base" in df.columns:
                st.dataframe(
                    df["rock_base"].value_counts().reset_index(),
                    use_container_width=True,
                    height=350
                )
            else:
                st.info("Columna rock_base no disponible")

        with col2:
            st.write("**Contexto litológico**")
            if "rock_context" in df.columns:
                st.dataframe(
                    df["rock_context"].value_counts().reset_index(),
                    use_container_width=True,
                    height=350
                )
            else:
                st.info("Columna rock_context no disponible")

        with col3:
            st.write("**Grupo litológico**")
            if "rock_group" in df.columns:
                st.dataframe(
                    df["rock_group"].value_counts().reset_index(),
                    use_container_width=True,
                    height=350
                )
            else:
                st.info("Columna rock_group no disponible")

        # =========================
        # 7. ESTADÍSTICAS
        # =========================
        st.subheader("📊 Estadísticas descriptivas")
        st.dataframe(descriptive_stats(df), use_container_width=True)

        # =========================
        # 8. CORRELACIÓN
        # =========================
        st.subheader("🔗 Matriz de correlación")
        corr = correlation_analysis(df)
        st.dataframe(corr, use_container_width=True)

        # =========================
        # 9. GRÁFICOS
        # =========================
        st.subheader("📈 Gráficos geoquímicos")
        st.pyplot(scatter_plot(df))
        st.pyplot(bar_plot(df))
        st.pyplot(box_plot(df))
        st.pyplot(correlation_heatmap(corr))

        st.subheader("🪨 Distribución por grupo litológico")
        st.pyplot(bar_plot_rock_group(df))

        # =========================
        # 10. GEOESPACIAL
        # =========================
        if "long" in df.columns and "lat" in df.columns:
            st.subheader("🌍 Ubicación de muestras")
            st.pyplot(plot_locations(df))

        # =========================
        # 11. VARIABLES GEOQUÍMICAS EXTRA
        # =========================
        if "tipo_alumina" in df.columns:
            st.subheader("🧪 Saturación de alúmina")
            st.dataframe(
                df["tipo_alumina"].value_counts().reset_index(),
                use_container_width=True
            )