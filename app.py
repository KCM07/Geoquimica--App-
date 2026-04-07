# ============================================================
#  APLICACIÓN STREAMLIT – ANÁLISIS GEOQUÍMICO DE ROCAS ÍGNEAS
# ============================================================

# =========================
# IMPORTACIÓN DE LIBRERÍAS
# =========================
import base64
import pandas as pd
import streamlit as st

# =========================
# IMPORTACIÓN DE MÓDULOS
# =========================
from modules.loader import load_data
from modules.cleaning import clean_data
from modules.analysis import (
    descriptive_stats,
    correlation_analysis,
    add_geochemical_variables,
    strong_correlations,
    add_tas_class,
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
    oxide_balance_histogram,
)
from modules.geospatial import plot_locations
from modules.rock_name_processing import process_rock_names

# =========================
# IMPORTS OPCIONALES
# =========================
try:
    from modules.visualization import irvine_baragar_plot
except ImportError:
    irvine_baragar_plot = None

try:
    from modules.visualization import ringwood_plot
except ImportError:
    ringwood_plot = None

try:
    from modules.visualization import lemaitre_plot
except ImportError:
    lemaitre_plot = None

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(page_title="Análisis Geoquímico", layout="wide")

# ============================================================
# LOGO / ENCABEZADO
# ============================================================
def get_base64_image(path: str) -> str:
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


img_base64 = get_base64_image("assets/Logo_.png")
st.markdown(
    f"""
    <div style="display:flex; flex-direction:column; align-items:center; gap:10px; margin-bottom:10px;">
        <img src="data:image/png;base64,{img_base64}" width="750">
        <h1 style="margin:0; text-align:center;">
            ⛏️ ANÁLISIS GEOQUÍMICO DE ROCAS ÍGNEAS              By: Kem Carbajal Moscoso
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)
uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

# ============================================================
# FUNCIONES AUXILIARES QaQc        $
# ============================================================
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

    dup_mask = qc_table.duplicated()
    qc_table.loc[dup_mask, "QC_flag"] += "Fila duplicada; "

    return qc_table


def highlight_qc(row):
    if "QC_flag" in row and isinstance(row["QC_flag"], str) and row["QC_flag"].strip() != "":
        return ["background-color: #ffdddd"] * len(row)
    return [""] * len(row)


def resumen_columna(dataframe: pd.DataFrame, col: str) -> pd.DataFrame:
    conteo = dataframe[col].value_counts(dropna=False).reset_index()
    conteo.columns = [col, "frecuencia"]
    conteo["porcentaje (%)"] = (conteo["frecuencia"] / len(dataframe) * 100).round(2)
    return conteo


def get_numeric_columns(dataframe: pd.DataFrame) -> list[str]:
    return dataframe.select_dtypes(include="number").columns.tolist()


def ensure_geochemical_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()

    if "alkalis" not in df.columns and {"Na2On", "K2On"}.issubset(df.columns):
        df["alkalis"] = df["Na2On"].fillna(0) + df["K2On"].fillna(0)

    if "Fe_Mg_ratio" not in df.columns and {"FeO*n", "MgOn"}.issubset(df.columns):
        df["Fe_Mg_ratio"] = df["FeO*n"] / df["MgOn"].replace(0, pd.NA)

    if "A_CNK" not in df.columns and {"Al2O3n", "CaOn", "Na2On", "K2On"}.issubset(df.columns):
        denominator = (df["CaOn"] + df["Na2On"] + df["K2On"]).replace(0, pd.NA)
        df["A_CNK"] = df["Al2O3n"] / denominator

    if "tipo_alumina" not in df.columns and "A_CNK" in df.columns:
        def classify_alumina(value):
            if pd.isna(value):
                return "unknown"
            if value > 1.1:
                return "peraluminosa"
            if value >= 1.0:
                return "transicional"
            return "metaluminosa"

        df["tipo_alumina"] = df["A_CNK"].apply(classify_alumina)

    return df


def summarize_missing_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    summary = pd.DataFrame({
        "columna": dataframe.columns,
        "nulos": dataframe.isnull().sum().values,
        "porcentaje_nulos": ((dataframe.isnull().sum() / len(dataframe)) * 100).round(2).values
    })
    return summary.sort_values("nulos", ascending=False).reset_index(drop=True)


def detect_outliers_iqr(dataframe: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = dataframe.copy() # $
    outlier_count = pd.Series(0, index=df.index)

    valid_cols = [c for c in columns if c in df.columns]

    for col in valid_cols:
        series = pd.to_numeric(df[col], errors="coerce")
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if pd.isna(iqr) or iqr == 0:
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (series < lower) | (series > upper)
        outlier_count += mask.fillna(False).astype(int)

    df["outlier_count"] = outlier_count
    df["outlier_flag"] = df["outlier_count"] > 0
    return df


def apply_outlier_treatment(dataframe: pd.DataFrame, columns: list[str], method: str) -> pd.DataFrame:
    df = dataframe.copy()
    valid_cols = [c for c in columns if c in df.columns]

    if method == "No corregir":
        return df

    if method == "Eliminar filas con outliers":
        df_out = detect_outliers_iqr(df, valid_cols)
        return df_out[~df_out["outlier_flag"]].drop(columns=["outlier_count", "outlier_flag"], errors="ignore").copy()

    if method == "Reemplazar outliers por mediana":
        for col in valid_cols:
            series = pd.to_numeric(df[col], errors="coerce")
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1

            if pd.isna(iqr) or iqr == 0:
                continue

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            median_val = series.median()
            mask = (series < lower) | (series > upper)
            df.loc[mask, col] = median_val

        return df

    return df


def summarize_oxidation_proxy(dataframe: pd.DataFrame) -> pd.DataFrame:
    if "Fe_Mg_ratio" not in dataframe.columns or "rock_group" not in dataframe.columns:
        return pd.DataFrame()

    summary = dataframe.groupby("rock_group", dropna=False)["Fe_Mg_ratio"].agg(
        frecuencia="count",
        media="mean",
        mediana="median",
        minimo="min",
        maximo="max"
    ).reset_index()

    def classify_ratio(value):
        if pd.isna(value):
            return "unknown"
        if value < 1:
            return "bajo"
        if value < 2:
            return "intermedio"
        return "alto"

    summary["grado_oxidacion_proxy"] = summary["media"].apply(classify_ratio)
    return summary


def get_row_filtered_df(dataframe: pd.DataFrame, mode_key: str, title: str) -> pd.DataFrame:
    st.write(title)
    mode = st.radio(
        "Modo de selección",
        ["Ver todo", "Elegir rango"],
        horizontal=True,
        key=f"mode_{mode_key}"
    )

    if mode == "Ver todo":
        return dataframe.copy()

    if len(dataframe) == 0:
        return dataframe.copy()

    col_range_1, col_range_2 = st.columns(2)

    with col_range_1:
        start = st.number_input(
            "Fila inicial",
            min_value=0,
            max_value=max(len(dataframe) - 1, 0),
            value=0,
            key=f"start_{mode_key}"
        )

    with col_range_2:
        end = st.number_input(
            "Fila final",
            min_value=1,
            max_value=max(len(dataframe), 1),
            value=min(100, len(dataframe)),
            key=f"end_{mode_key}"
        )

    if start < end:
        return dataframe.iloc[start:end].copy()

    st.warning("La fila inicial debe ser menor que la final.")
    return pd.DataFrame()


# ============================================================
# FLUJO PRINCIPAL
# ============================================================
if uploaded_file:
    raw_df = load_data(uploaded_file)     # FUNCION PRINCIPAL****************************************************

    if raw_df is not None:
        # =========================
        # CONFIGURACIÓN DE GRÁFICOS
        # =========================
        st.sidebar.subheader("⚙️ Configuración de gráficos")
        ancho = st.sidebar.slider("📐 Ancho del gráfico", 5, 20, 10)
        alto = st.sidebar.slider("📏 Alto del gráfico", 3, 10, 5)
        tam_punto = st.sidebar.slider("🔵 Tamaño de puntos", 10, 100, 35)
        fig_size = (ancho, alto)

        # =========================
        # 1. CARGA DE DATA CRUDA
        # =========================
        st.header("1. 📂 Cargado de data")

        df_raw = raw_df.copy()
        st.write(f"**Filas:** {df_raw.shape[0]} | **Columnas:** {df_raw.shape[1]}")

        vista_raw = get_row_filtered_df(df_raw, "raw_view", "Vista de la data cruda")
        if len(vista_raw) > 0:
            st.dataframe(vista_raw, use_container_width=True, height=420)

        with st.expander("Ver nombres de columnas y tipos de dato"):
            schema_df = pd.DataFrame({
                "columna": df_raw.columns,
                "tipo_dato": [str(df_raw[col].dtype) for col in df_raw.columns]
            })
            st.dataframe(schema_df, use_container_width=True)

        df_base = clean_data(df_raw) ### FUNCION PRINCIPAL ******************************************

        # =========================
        # 2. ANÁLISIS DE INCONSISTENCIAS
        # =========================
        st.header("2. 🚨 Análisis de inconsistencias, vacíos y QA/QC")

        col_metric_1, col_metric_2, col_metric_3 = st.columns(3)
        with col_metric_1:
            st.metric("Filas", df_base.shape[0])
        with col_metric_2:
            st.metric("Columnas", df_base.shape[1])
        with col_metric_3:
            st.metric("Duplicados exactos", int(df_base.duplicated().sum()))

        st.subheader("Valores nulos por columna")
        st.dataframe(summarize_missing_values(df_base), use_container_width=True, height=350)

        df_qc = build_qc_table(df_base) ### FUNCION PRINCIPAL ****************************************(*)

        df_outliers = detect_outliers_iqr(df_qc, get_numeric_columns(df_qc))

        st.subheader("Resumen QA/QC")
        qc_flags = (df_qc["QC_flag"].astype(str).str.strip() != "")
        n_qc_flags = int(pd.Series(qc_flags).sum())

        st.write(f"**Filas con flags QA/QC:** {n_qc_flags}")

        if n_qc_flags > 0:
            qc_resumen = df_qc.loc[qc_flags, "QC_flag"].value_counts().reset_index()
            qc_resumen.columns = ["tipo_inconsistencia", "frecuencia"]
            st.dataframe(qc_resumen, use_container_width=True)

        n_outliers = int(pd.Series(df_outliers["outlier_flag"]).sum())
        st.write(f"**Filas con outliers (IQR) en una o más variables:** {n_outliers}")

        st.subheader("Tabla QA/QC Incongruencias detectadas")
        st.dataframe(
            df_qc.style.apply(highlight_qc, axis=1),
            use_container_width=True,
            height=450
        )

        # =========================
        # 3. CORRECCIÓN DE DATOS
        # =========================
        st.header("3. 🧹 Corrección de datos")

        st.subheader("Tratamiento de filas con flags QA/QC")
        qc_method = st.selectbox(
            "Qué hacer con filas marcadas en QA/QC",
            [
                "Conservar todas",
                "Eliminar filas con flags QA/QC"
            ],
            index=0
        )

        st.subheader("Imputación de valores nulos numéricos")
        null_method = st.selectbox(
            "Cómo tratar nulos numéricos",
            [
                "No imputar",
                "Reemplazar por media",
                "Reemplazar por mediana"
            ],
            index=0
        )

        st.subheader("Tratamiento de valores atípicos")
        outlier_method = st.selectbox(
            "Qué hacer con outliers (método IQR)",
            [
                "No corregir",
                "Eliminar filas con outliers",
                "Reemplazar outliers por mediana"
            ],
            index=0
        )

        df_corrected = df_qc.copy() ## FUNCION PRINCIPAL ********************************************

        if qc_method == "Eliminar filas con flags QA/QC":
            df_corrected = df_corrected[df_corrected["QC_flag"].astype(str).str.strip() == ""].copy()

        numeric_cols_corr = get_numeric_columns(df_corrected)

        if null_method == "Reemplazar por media":
            df_corrected[numeric_cols_corr] = df_corrected[numeric_cols_corr].fillna(
                df_corrected[numeric_cols_corr].mean(numeric_only=True)
            )
        elif null_method == "Reemplazar por mediana":
            df_corrected[numeric_cols_corr] = df_corrected[numeric_cols_corr].fillna(
                df_corrected[numeric_cols_corr].median(numeric_only=True)
            )

        df_corrected = apply_outlier_treatment(df_corrected, numeric_cols_corr, outlier_method)

        st.write(f"**Filas después de correcciones:** {df_corrected.shape[0]}")
        st.write(f"**Columnas después de correcciones:** {df_corrected.shape[1]}")

        vista_corr = get_row_filtered_df(df_corrected, "corrected_view", "Vista de la data corregida")
        if len(vista_corr) > 0:
            st.dataframe(vista_corr, use_container_width=True, height=420)

        # =========================
        # 4. REAGRUPACIÓN / NORMALIZACIÓN LITOLÓGICA
        # =========================
        st.header("4. 🪨 Reagrupación / normalización litológica")

        df_group = process_rock_names(df_corrected) # FUNCION PRINCIPAL ***************************************

        cols_litologia = [
            "rock_name",
            "rock_name_clean",
            "rock_base",
            "rock_context",
            "rock_observation",
            "rock_group"
        ]
        cols_existentes = [col for col in cols_litologia if col in df_group.columns]

        if cols_existentes:
            st.dataframe(df_group[cols_existentes], use_container_width=True, height=400)
        else:
            st.info("No se encontraron columnas litológicas para mostrar.")

        if "rock_group" in df_group.columns:
            st.subheader("Resumen de grupos litológicos normalizados")
            col_lito_1, col_lito_2, col_lito_3 = st.columns(3)

            with col_lito_1:
                if "rock_base" in df_group.columns:
                    st.dataframe(resumen_columna(df_group, "rock_base"), use_container_width=True, height=320)

            with col_lito_2:
                if "rock_context" in df_group.columns:
                    st.dataframe(resumen_columna(df_group, "rock_context"), use_container_width=True, height=320)

            with col_lito_3:
                st.dataframe(resumen_columna(df_group, "rock_group"), use_container_width=True, height=320)

            fig_group_dist = bar_plot_rock_group(df_group, size=fig_size)
            if fig_group_dist is not None:
                st.pyplot(fig_group_dist)

        st.caption("La normalización litológica usa nombres de roca y reglas textuales. Sirve como referencia práctica, no reemplaza una clasificación modal QAPF estricta.")

        # =========================
        # 5. RESUMEN ESTADÍSTICO Y PARÁMETROS
        # =========================
        st.header("5. 📊 Resumen estadístico y cálculos de parámetros")

        df_calc = add_geochemical_variables(df_group) # FUNCION PRINCIPAL *************************************************
        df_calc = ensure_geochemical_columns(df_calc)
        df_calc = add_tas_class(df_calc)              # FUNCION PRINCIPAL *****************************

        st.subheader("Estructura de variables")
        oxidos = [
            "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
            "MgOn", "CaOn", "Na2On", "K2On", "P2O5n"
        ]
        calculadas = [
            col for col in [
                "alkalis", "Fe_Mg_ratio", "A_CNK",
                "tipo_alumina", "tas_class", "total_oxidos"
            ] if col in df_calc.columns
        ]

        col_var_1, col_var_2 = st.columns(2)
        with col_var_1:
            st.write("**Variables originales (óxidos)**")
            st.write(oxidos)
        with col_var_2:
            st.write("**Variables calculadas**")
            st.write(calculadas)

        st.subheader("Fórmulas y conceptos clave")
        st.markdown("""
**Alcalinidad total (Alkalis)**  
`Na₂O + K₂O`

**Relación Fe/Mg**  
`FeO* / MgO`

**Índice A/CNK**  
`Al₂O₃ / (CaO + Na₂O + K₂O)`

**Balance de óxidos**  
Suma de óxidos mayores, idealmente cerca de 100%.

**TAS class**  
Clasificación simplificada basada en `SiO₂` y `Na₂O + K₂O`.
        """)

        st.subheader("Estadísticas descriptivas")
        st.dataframe(descriptive_stats(df_calc), use_container_width=True)

        st.subheader("Matriz de correlación")
        corr = correlation_analysis(df_calc)
        st.dataframe(corr, use_container_width=True)

        st.subheader("Correlaciones fuertes")
        st.dataframe(strong_correlations(corr), use_container_width=True)

        # =========================
        # 6. EXPLORACIÓN DE DATOS (EDA)
        # =========================
        st.header("6. 📈 Exploración de datos (EDA)")

        numeric_vars = [
            c for c in [
                "SiO2n", "TiO2n", "Al2O3n", "FeO*n", "MnOn",
                "MgOn", "CaOn", "Na2On", "K2On", "P2O5n",
                "alkalis", "Fe_Mg_ratio", "A_CNK", "total_oxidos"
            ] if c in df_calc.columns
        ]

        if len(numeric_vars) > 0:
            var_eda = st.selectbox(
                "Selecciona la sustancia/variable para explorar",
                numeric_vars,
                index=0
            )

            df_eda = get_row_filtered_df(df_calc, "eda_view", "Selecciona el subconjunto para EDA")

            if len(df_eda) > 0:
                eda_options = st.multiselect(
                    "Selecciona gráficos EDA",
                    [
                        "Histograma",
                        "Frecuencia acumulada",
                        "QQ aproximado",
                        "Boxplot por grupo",
                        "Heatmap de correlación",
                        "Barras de correlaciones fuertes",
                        "Histograma balance de óxidos"
                    ],
                    default=["Histograma", "QQ aproximado", "Boxplot por grupo"]
                )

                if "Histograma" in eda_options:
                    fig = histogram_plot(df_eda, var_eda, size=fig_size)
                    if fig is not None:
                        st.pyplot(fig)

                if "Frecuencia acumulada" in eda_options:
                    fig = cumulative_frequency_plot(df_eda, var_eda, size=fig_size)
                    if fig is not None:
                        st.pyplot(fig)

                if "QQ aproximado" in eda_options:
                    fig = qq_style_plot(df_eda, var_eda, size=fig_size, point_size=tam_punto)
                    if fig is not None:
                        st.pyplot(fig)

                if "Boxplot por grupo" in eda_options and "rock_group" in df_eda.columns:
                    fig = box_plot_by_group(df_eda, y_col=var_eda, size=fig_size)
                    if fig is not None:
                        st.pyplot(fig)

                if "Heatmap de correlación" in eda_options:
                    fig = correlation_heatmap(correlation_analysis(df_eda), size=fig_size)
                    if fig is not None:
                        st.pyplot(fig)

                if "Barras de correlaciones fuertes" in eda_options:
                    corr_eda = correlation_analysis(df_eda)
                    fig = strong_corr_barplot(corr_eda, top_n=10, size=fig_size)
                    if fig is not None:
                        st.pyplot(fig)

                if "Histograma balance de óxidos" in eda_options and "total_oxidos" in df_eda.columns:
                    fig = oxide_balance_histogram(df_eda, size=fig_size)
                    if fig is not None:
                        st.pyplot(fig)
            else:
                st.warning("No hay datos para la selección EDA actual.")
        else:
            st.info("No hay variables numéricas disponibles para EDA.")

        # =========================
        # 7. DATA LIMPIA FINAL
        # =========================
        st.header("7. ✅ Data limpia final")

        df_final = df_calc.copy()

        st.write(f"**Filas finales:** {df_final.shape[0]} | **Columnas finales:** {df_final.shape[1]}")
        vista_final = get_row_filtered_df(df_final, "final_view", "Vista de la data final")
        if len(vista_final) > 0:
            st.dataframe(vista_final, use_container_width=True, height=420)

        csv_final = df_final.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Descargar data limpia final (CSV)",
            data=csv_final,
            file_name="data_limpia_final_geoquimica.csv",
            mime="text/csv"
        )

        # =========================
        # 8. INFORME GEOQUÍMICO
        # =========================
        st.header("8. 🧪 Informe geoquímico")

        df_geoq = df_final.copy()

        st.subheader("Selección de datos para diagramas geoquímicos")
        modo_geoq = st.radio(
            "Cómo quieres visualizar los diagramas geoquímicos",
            ["Ver todo", "Elegir rango", "Filtrar por grupos"],
            index=0,
            horizontal=True
        )

        if modo_geoq == "Elegir rango":
            df_geoq = get_row_filtered_df(df_final, "geoq_range", "Selecciona el rango para diagramas geoquímicos")
        elif modo_geoq == "Filtrar por grupos" and "rock_group" in df_final.columns:
            grupos = sorted(df_final["rock_group"].dropna().unique().tolist())
            grupos_sel = st.multiselect(
                "Selecciona grupos litológicos",
                grupos,
                default=grupos,
                key="grupos_geoq"
            )
            df_geoq = df_final[df_final["rock_group"].isin(grupos_sel)].copy()

        st.write(f"**Filas usadas en el informe geoquímico:** {df_geoq.shape[0]}")

        st.subheader("Grado de oxidación por grupo (proxy Fe/Mg)")
        oxidation_summary = summarize_oxidation_proxy(df_geoq)
        if not oxidation_summary.empty:
            st.dataframe(oxidation_summary, use_container_width=True)
        else:
            st.info("No se pudo calcular el proxy de oxidación por grupo.")

        st.subheader("Saturación de alúmina")
        if "tipo_alumina" in df_geoq.columns:
            alumina_resumen = df_geoq["tipo_alumina"].value_counts(dropna=False).reset_index()
            alumina_resumen.columns = ["tipo_alumina", "frecuencia"]
            st.dataframe(alumina_resumen, use_container_width=True)
        else:
            st.info("No está disponible la columna tipo_alumina.")

        st.subheader("Diagrama TAS")
        if {"SiO2n", "alkalis", "tas_class"}.issubset(df_geoq.columns):
            cols_show = [c for c in ["SiO2n", "alkalis", "tas_class", "rock_group"] if c in df_geoq.columns]
            st.dataframe(df_geoq[cols_show].head(50), use_container_width=True)

            fig = tas_plot(
                df_geoq,
                color_col="tas_class",
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)
        else:
            st.info("No hay columnas suficientes para construir el TAS.")

        st.subheader("Diagrama de Harker")
        harker_options = [c for c in ["TiO2n", "MgOn", "FeO*n", "CaOn", "Al2O3n", "Na2On", "K2On", "P2O5n"] if c in df_geoq.columns]
        if len(harker_options) > 0:
            elem = st.selectbox("Selecciona variable para Harker", harker_options, key="harker_elem")
            fig = harker_plot(
                df_geoq,
                elem,
                color_col="rock_group" if "rock_group" in df_geoq.columns else None,
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)
        else:
            st.info("No hay variables suficientes para Harker.")

        st.subheader("Diagrama de Irvine y Baragar")
        if callable(magmatic_series_plot):
            fig = magmatic_series_plot(
                df_geoq,
                color_col="rock_group" if "rock_group" in df_geoq.columns else None,
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)
        elif callable(irvine_baragar_plot):
            fig = irvine_baragar_plot(
                df_geoq,
                color_col="rock_group" if "rock_group" in df_geoq.columns else None,
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)
        else:
            st.info("No se encontró una función específica para Irvine y Baragar en visualization.py.")

        st.subheader("Diagrama de Ringwood")
        if callable(ringwood_plot):
            fig = ringwood_plot(
                df_geoq,
                color_col="rock_group" if "rock_group" in df_geoq.columns else None,
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)
        else:
            st.info("No se encontró la función ringwood_plot en visualization.py.")

        st.subheader("Diagrama de Le Maitre")
        if callable(lemaitre_plot):
            fig = lemaitre_plot(
                df_geoq,
                color_col="rock_group" if "rock_group" in df_geoq.columns else None,
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)
        else:
            st.info("No se encontró la función lemaitre_plot en visualization.py.")

        st.subheader("Scatter complementario SiO₂ vs TiO₂")
        if {"SiO2n", "TiO2n"}.issubset(df_geoq.columns):
            fig = scatter_plot(
                df_geoq,
                x_col="SiO2n",
                y_col="TiO2n",
                color_col="rock_group" if "rock_group" in df_geoq.columns else None,
                size=fig_size,
                point_size=tam_punto
            )
            if fig is not None:
                st.pyplot(fig)

        st.subheader("Promedios por grupo litológico")
        if "rock_group" in df_geoq.columns:
            fig = group_mean_plot(df_geoq, size=fig_size)
            if fig is not None:
                st.pyplot(fig)

        if "long" in df_geoq.columns and "lat" in df_geoq.columns:
            st.subheader("Ubicación de muestras")
            fig_map = plot_locations(df_geoq, size=fig_size, point_size=tam_punto)
            if fig_map is not None:
                st.pyplot(fig_map)