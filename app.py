# ============================================================
#  APLICACIÓN STREAMLIT – ANÁLISIS GEOQUÍMICO DE ROCAS ÍGNEAS
# ============================================================

import base64
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
from modules.visualization import *
from modules.geospatial import plot_locations
from modules.rock_name_processing import process_rock_names

st.set_page_config(page_title="Análisis Geoquímico", layout="wide")

# ============================================================
# LOGO
# ============================================================
def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

img_base64 = get_base64_image("assets/Logo_.png")

st.markdown(f"""
<div style="display:flex; align-items:center; gap:20px;">
<img src="data:image/png;base64,{img_base64}" width="180">
<h1>⛏️ ANÁLISIS GEOQUÍMICO DE ROCAS ÍGNEAS</h1>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

# ============================================================
# QA/QC
# ============================================================
def build_qc_table(df):
    qc = df.copy()
    oxidos = ["SiO2n","TiO2n","Al2O3n","FeO*n","MnOn","MgOn","CaOn","Na2On","K2On","P2O5n"]

    for col in oxidos:
        if col not in qc.columns:
            qc[col] = pd.NA

    qc["QC_flag"] = ""
    qc["total_oxidos"] = qc[oxidos].sum(axis=1, skipna=True)

    qc.loc[(qc["total_oxidos"]<95)|(qc["total_oxidos"]>105),"QC_flag"] += "Balance; "

    return qc

def highlight_qc(row):
    return ["background-color: #ffdddd"]*len(row) if row["QC_flag"] else [""]*len(row)

# ============================================================
# FLUJO PRINCIPAL
# ============================================================
if uploaded_file:

    df_raw = load_data(uploaded_file)

    if df_raw is not None:

        # ====================================================
        # 1. DATA CRUDA
        # ====================================================
        st.header("📂 Data cruda")

        df_clean = clean_data(df_raw)
        st.dataframe(df_clean.head(100))

        st.write("Valores nulos por columna")
        st.dataframe(df_clean.isnull().sum())

        # ====================================================
        # 2. QA/QC
        # ====================================================
        st.header("🚨 QA/QC – Diagnóstico")

        df_qc = build_qc_table(df_clean)

        errores = df_qc[df_qc["QC_flag"]!=""]
        st.write(f"Filas con error: {len(errores)}")

        st.dataframe(df_qc.style.apply(highlight_qc, axis=1))

        # ====================================================
        # 3. CORRECCIÓN
        # ====================================================
        st.header("🧹 Corrección de datos")

        metodo = st.selectbox("Método de limpieza", ["Eliminar errores","Reemplazar por media"])

        if metodo == "Eliminar errores":
            df_corr = df_qc[df_qc["QC_flag"]==""].copy()

        else:
            df_corr = df_qc.copy()
            df_corr.fillna(df_corr.mean(numeric_only=True), inplace=True)

        st.write("Data corregida:")
        st.dataframe(df_corr.head(50))

        # ====================================================
        # 4. REAGRUPACIÓN
        # ====================================================
        st.header("🪨 Reagrupación litológica")

        df_group = process_rock_names(df_corr)

        st.dataframe(df_group[["rock_name","rock_group"]].head(50))

        # ====================================================
        # 5. PARÁMETROS Y ESTADÍSTICA
        # ====================================================
        st.header("📊 Estadística y parámetros")

        df_calc = add_geochemical_variables(df_group)

        st.dataframe(descriptive_stats(df_calc))
        corr = correlation_analysis(df_calc)
        st.dataframe(corr)

        # ====================================================
        # 6. EDA
        # ====================================================
        st.header("📈 Exploración de datos (EDA)")

        var = st.selectbox("Variable", df_calc.select_dtypes(include="number").columns)

        st.pyplot(histogram_plot(df_calc, var))
        st.pyplot(box_plot_by_group(df_calc, var))
        st.pyplot(qq_style_plot(df_calc, var))
        st.pyplot(cumulative_frequency_plot(df_calc, var))

        # ====================================================
        # 7. DATA FINAL
        # ====================================================
        st.header("✅ Data limpia final")

        df_final = df_calc.copy()
        st.dataframe(df_final.head(100))

        # ====================================================
        # 8. INFORME GEOQUÍMICO
        # ====================================================
        st.header("🧪 Informe geoquímico")

        grupos = df_final["rock_group"].dropna().unique()
        grupos_sel = st.multiselect("Filtrar grupos", grupos, default=grupos)

        df_plot = df_final[df_final["rock_group"].isin(grupos_sel)]

        st.subheader("TAS")
        st.pyplot(tas_plot(df_plot))

        st.subheader("Harker")
        st.pyplot(harker_plot(df_plot, "MgOn"))

        st.subheader("Series magmáticas")
        st.pyplot(magmatic_series_plot(df_plot))

        st.subheader("Scatter")
        st.pyplot(scatter_plot(df_plot,"SiO2n","TiO2n"))

        if "long" in df_plot.columns:
            st.subheader("Mapa")
            st.pyplot(plot_locations(df_plot))