import streamlit as st
import pandas as pd

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

st.set_page_config(page_title="Análisis Geoquímico", layout="wide")

col1, col2 = st.columns([2, 10])

with col1:
    st.markdown(
        """
        <img src="assets/Logo_.png" width="900">
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        "<h1 style='margin:0;'>⛏️ Análisis Geoquímico de Rocas Ígneas</h1>",
        unsafe_allow_html=True
    )

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])


def build_qc_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    qc_table = dataframe.copy()

    oxide_columns = [
        "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
        "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"
    ]

    for column in oxide_columns:
        if column not in qc_table.columns:
            qc_table[column] = pd.NA

    qc_table["QC_flag"] = ""

    present_oxides = [column for column in oxide_columns if column in qc_table.columns]
    qc_table["total_oxidos"] = qc_table[present_oxides].sum(axis=1, skipna=True)

    qc_table.loc[
        (qc_table["total_oxidos"] < 95) | (qc_table["total_oxidos"] > 105),
        "QC_flag"
    ] += "Balance de óxidos fuera de rango; "

    if "SiO2n" in qc_table.columns:
        qc_table.loc[
            (qc_table["SiO2n"] < 30) | (qc_table["SiO2n"] > 80),
            "QC_flag"
        ] += "SiO2 fuera de rango; "

    if "TiO2n" in qc_table.columns:
        qc_table.loc[
            (qc_table["TiO2n"] < 0) | (qc_table["TiO2n"] > 6),
            "QC_flag"
        ] += "TiO2 fuera de rango; "

    if "Al2O3n" in qc_table.columns:
        qc_table.loc[
            (qc_table["Al2O3n"] < 0) | (qc_table["Al2O3n"] > 30),
            "QC_flag"
        ] += "Al2O3 fuera de rango; "

    if "MgOn" in qc_table.columns:
        qc_table.loc[
            (qc_table["MgOn"] < 0) | (qc_table["MgOn"] > 25),
            "QC_flag"
        ] += "MgO fuera de rango; "

    key_columns = ["rock_name", "SiO2n", "Al2O3n", "FeO*n", "MgOn"]
    existing_key_columns = [column for column in key_columns if column in qc_table.columns]

    if existing_key_columns:
        null_mask = qc_table[existing_key_columns].isnull().any(axis=1)
        qc_table.loc[null_mask, "QC_flag"] += "Valores nulos en campos clave; "

    return qc_table

def highlight_qc(row):
    if "QC_flag" in row and isinstance(row["QC_flag"], str) and row["QC_flag"].strip() != "":
        return ["background-color: #ffdddd"] * len(row)
    return [""] * len(row)


def resumen_columna(dataframe: pd.DataFrame, col: str) -> pd.DataFrame:
    conteo = dataframe[col].value_counts().reset_index()
    conteo.columns = [col, "frecuencia"]
    conteo["porcentaje (%)"] = (conteo["frecuencia"] / len(dataframe) * 100).round(2)
    return conteo

if uploaded_file:
    df = load_data(uploaded_file)

    if df is not None:
        # =========================
        # 1. CARGA Y PROCESAMIENTO
        # =========================
        df = clean_data(df)
        df = add_geochemical_variables(df)
        df = process_rock_names(df)

        # =========================
        # 2. CONFIGURACIÓN DE GRÁFICOS
        # =========================
        st.sidebar.subheader("⚙️ Configuración de gráficos")

        ancho = st.sidebar.slider("Ancho del gráfico", 5, 20, 10)
        alto = st.sidebar.slider("Alto del gráfico", 3, 10, 5)
        tam_punto = st.sidebar.slider("Tamaño de puntos", 10, 100, 35)

        fig_size = (ancho, alto)

        # =========================
        # 3. FILTROS
        # =========================
        st.subheader("🎛️ Filtros")

        df_filtrado = df.copy()

        if "rock_group" in df.columns:
            grupos = sorted(df["rock_group"].dropna().unique().tolist())
            grupos_sel = st.multiselect(
                "Filtrar por rock_group",
                grupos,
                default=grupos
            )
            df_filtrado = df_filtrado[df_filtrado["rock_group"].isin(grupos_sel)]

        st.write(f"Filas después de filtros: {df_filtrado.shape[0]}")

        # =========================
        # 4. VISUALIZACIÓN DE DATOS
        # =========================
        st.subheader("📋 Visualización de los datos")
        st.write(f"Filas totales cargadas: {df.shape[0]} | Columnas: {df.shape[1]}")
        st.write(f"Filas visibles después del filtro: {df_filtrado.shape[0]}")

        modo = st.radio(
            "Selecciona cómo quieres visualizar los datos:",
            ["Vista previa (50 filas)", "Elegir rango", "Ver todo"],
            index=0
        )

        if modo == "Vista previa (50 filas)":
            st.dataframe(df_filtrado.head(50), use_container_width=True, height=500)

        elif modo == "Elegir rango":
            if len(df_filtrado) == 0:
                st.warning("No hay datos después del filtro.")
            else:
                col1, col2 = st.columns(2)

                with col1:
                    inicio = st.number_input(
                        "Fila inicial",
                        min_value=0,
                        max_value=len(df_filtrado) - 1,
                        value=0
                    )

                with col2:
                    fin = st.number_input(
                        "Fila final",
                        min_value=1,
                        max_value=len(df_filtrado),
                        value=min(50, len(df_filtrado))
                    )

                if inicio < fin:
                    st.dataframe(df_filtrado.iloc[inicio:fin], use_container_width=True, height=500)
                else:
                    st.warning("⚠️ La fila inicial debe ser menor que la final")

        elif modo == "Ver todo":
            st.dataframe(df_filtrado, use_container_width=True, height=500)

        # =========================
        # 5. ESTRUCTURA DE VARIABLES
        # =========================
        st.subheader("📊 Estructura de variables")

        oxidos = [
            "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
            "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"
        ]

        calculadas = [
            col for col in ["alkalis", "Fe_Mg_ratio", "A_CNK", "tipo_alumina"]
            if col in df_filtrado.columns
        ]

        c1, c2 = st.columns(2)

        with c1:
            st.write("**🧪 Variables originales (óxidos)**")
            st.write(oxidos)

        with c2:
            st.write("**⚙️ Variables calculadas**")
            st.write(calculadas)

        # =========================
        # 6. FÓRMULAS Y CONCEPTOS
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
        # 7. QA/QC
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
        # 8. REAGRUPACIÓN LITOLÓGICA
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

        cols_existentes = [col for col in cols_litologia if col in df_filtrado.columns]

        if cols_existentes:
            st.dataframe(df_filtrado[cols_existentes], use_container_width=True, height=400)
        else:
            st.warning("No se encontraron columnas de reagrupación litológica.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Roca base**")
            if "rock_base" in df_filtrado.columns:
                st.dataframe(
                    resumen_columna(df_filtrado, "rock_base"),
                    use_container_width=True,
                    height=350
                )
            else:
                st.info("Columna rock_base no disponible")

        with col2:
            st.write("**Contexto litológico**")
            if "rock_context" in df_filtrado.columns:
                st.dataframe(
                    resumen_columna(df_filtrado, "rock_context"),
                    use_container_width=True,
                    height=350
                )
            else:
                st.info("Columna rock_context no disponible")

        with col3:
            st.write("**Grupo litológico**")
            if "rock_group" in df_filtrado.columns:
                st.dataframe(
                    resumen_columna(df_filtrado, "rock_group"),
                    use_container_width=True,
                    height=350
                )
            else:
                st.info("Columna rock_group no disponible")

        st.subheader("📊 Distribución de grupos litológicos")
        fig_group_dist = bar_plot_rock_group(df_filtrado, size=fig_size)
        if fig_group_dist is not None:
            st.pyplot(fig_group_dist)

        # =========================
        # 9. ESTADÍSTICAS
        # =========================
        st.subheader("📊 Estadísticas descriptivas")
        st.dataframe(descriptive_stats(df_filtrado), use_container_width=True)

        # =========================
        # 10. CORRELACIÓN
        # =========================
        st.subheader("🔗 Matriz de correlación")
        corr = correlation_analysis(df_filtrado)
        st.dataframe(corr, use_container_width=True)

        st.subheader("🔥 Correlaciones fuertes")
        st.dataframe(strong_correlations(corr), use_container_width=True)

        # =========================
        # 11. GRÁFICOS SELECCIONABLES
        # =========================
        st.subheader("📈 Exploración gráfica")

        opciones_graficos = [
            "Scatter SiO2 vs TiO2",
            "Diagrama TAS",
            "Series magmáticas",
            "Harker",
            "Heatmap de correlación",
            "Barras de correlaciones fuertes",
            "Distribución por grupo litológico",
            "Promedios por grupo litológico",
            "Boxplot por grupo",
            "Histograma",
            "Frecuencia acumulada",
            "QQ aproximado",
            "Histograma balance de óxidos"
        ]

        graficos_sel = st.multiselect(
            "Selecciona los gráficos a mostrar:",
            opciones_graficos,
            default=["Scatter SiO2 vs TiO2", "Diagrama TAS", "Heatmap de correlación"]
        )

        if "Scatter SiO2 vs TiO2" in graficos_sel:
            fig = scatter_plot(
                df_filtrado,
                x_col="SiO2n",
                y_col="TiO2n",
                color_col="rock_group",
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)

        if "Diagrama TAS" in graficos_sel:
            fig = tas_plot(
                df_filtrado,
                color_col="rock_group",
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)

        if "Series magmáticas" in graficos_sel:
            fig = magmatic_series_plot(
                df_filtrado,
                color_col="rock_group",
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)

        if "Harker" in graficos_sel:
            y_options = ["TiO2n", "MgOn", "FeO*n", "CaOn", "Al2O3n", "Na2On", "K2On", "P2O5n"]
            y_options = [c for c in y_options if c in df_filtrado.columns]

            if y_options:
                elem = st.selectbox("Selecciona variable Harker:", y_options)
                fig = harker_plot(
                    df_filtrado,
                    elem,
                    color_col="rock_group",
                    size=fig_size,
                    point_size=tam_punto
                )
                if fig is not None:
                    st.pyplot(fig)

        if "Heatmap de correlación" in graficos_sel:
            fig = correlation_heatmap(corr, size=fig_size)
            if fig is not None:
                st.pyplot(fig)

        if "Barras de correlaciones fuertes" in graficos_sel:
            fig = strong_corr_barplot(corr, top_n=10, size=fig_size)
            if fig is not None:
                st.pyplot(fig)

        if "Distribución por grupo litológico" in graficos_sel:
            fig = bar_plot_rock_group(df_filtrado, size=fig_size)
            if fig is not None:
                st.pyplot(fig)

        if "Promedios por grupo litológico" in graficos_sel:
            fig = group_mean_plot(df_filtrado, size=fig_size)
            if fig is not None:
                st.pyplot(fig)

        if "Boxplot por grupo" in graficos_sel:
            vars_box = ["SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"]
            vars_box = [c for c in vars_box if c in df_filtrado.columns]

            if vars_box:
                var_box = st.selectbox("Variable para boxplot:", vars_box)
                fig = box_plot_by_group(df_filtrado, y_col=var_box, size=fig_size)
                if fig is not None:
                    st.pyplot(fig)

        if "Histograma" in graficos_sel:
            vars_hist = ["SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"]
            vars_hist = [c for c in vars_hist if c in df_filtrado.columns]

            if vars_hist:
                var_hist = st.selectbox("Variable para histograma:", vars_hist)
                fig = histogram_plot(df_filtrado, var_hist, size=fig_size)
                if fig is not None:
                    st.pyplot(fig)

        if "Frecuencia acumulada" in graficos_sel:
            vars_cum = ["SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"]
            vars_cum = [c for c in vars_cum if c in df_filtrado.columns]

            if vars_cum:
                var_cum = st.selectbox("Variable para frecuencia acumulada:", vars_cum)
                fig = cumulative_frequency_plot(df_filtrado, var_cum, size=fig_size)
                if fig is not None:
                    st.pyplot(fig)

        if "QQ aproximado" in graficos_sel:
            vars_qq = ["SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"]
            vars_qq = [c for c in vars_qq if c in df_filtrado.columns]

            if vars_qq:
                var_qq = st.selectbox("Variable para QQ:", vars_qq)
                fig = qq_style_plot(df_filtrado, var_qq, size=fig_size, point_size=tam_punto)
                if fig is not None:
                    st.pyplot(fig)

        if "Histograma balance de óxidos" in graficos_sel:
            if "total_oxidos" in df_qc.columns:
                fig = oxide_balance_histogram(df_qc, size=fig_size)
                if fig is not None:
                    st.pyplot(fig)

        # =========================
        # 12. GEOESPACIAL
        # =========================
        if "long" in df_filtrado.columns and "lat" in df_filtrado.columns:
            st.subheader("🌍 Ubicación de muestras")
            st.pyplot(plot_locations(df_filtrado, size=fig_size, point_size=tam_punto))

        # =========================
        # 13. VARIABLES EXTRA
        # =========================
        if "tipo_alumina" in df_filtrado.columns:
            st.subheader("🧪 Saturación de alúmina")
            st.dataframe(
                df_filtrado["tipo_alumina"].value_counts().reset_index(),
                use_container_width=True
            )