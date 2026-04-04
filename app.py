import streamlit as st

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

if uploaded_file:
    # =========================
    # 1. CARGA Y LIMPIEZA
    # =========================
    df = load_data(uploaded_file)
    df = clean_data(df)
    df = add_geochemical_variables(df)
    df = process_rock_names(df)

    # =========================
    # 2. VISTA INTERACTIVA
    # =========================
    st.subheader("📋 Vista previa de los datos")
    st.write(f"Filas totales: {df.shape[0]} | Columnas: {df.shape[1]}")

    modo = st.radio(
        "Selecciona cómo quieres visualizar los datos:",
        ["Vista previa (50 filas)", "Elegir rango", "Ver todo"]
    )

    if modo == "Vista previa (50 filas)":
        modo = st.radio(
            "Visualización",
            ["50 filas", "Rango", "Todo"]
        )

        if modo == "50 filas":
            st.dataframe(df.head(51))

        elif modo == "Rango":
            inicio = st.number_input("Inicio", 0, len(df) - 1, 0)
            fin = st.number_input("Fin", 1, len(df), 51)
            st.dataframe(df.iloc[inicio:fin])

        else:
            st.dataframe(df)

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
                value=min(51, len(df))
            )

        if inicio < fin:
            st.dataframe(df.iloc[inicio:fin])
        else:
            st.warning("⚠️ La fila inicial debe ser menor que la final")

    elif modo == "Ver todo":
        st.dataframe(df)

    # =========================
    # 3. QA/QC DE rock_name
    # =========================
    st.subheader("🪨 Reagrupación litológica")

    st.dataframe(
        df[[
            "rock_name",
            "rock_name_clean",
            "rock_base",
            "rock_context",
            "rock_group"
        ]].head(50)
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Roca base**")
        st.dataframe(df["rock_base"].value_counts().reset_index())

    with col2:
        st.write("**Contexto litológico**")
        st.dataframe(df["rock_context"].value_counts().reset_index())

    with col3:
        st.write("**Grupo litológico**")
        st.dataframe(df["rock_group"].value_counts().reset_index())

    # =========================
    # 4. ESTADÍSTICAS
    # =========================
    st.subheader("📊 Estadísticas descriptivas")
    st.dataframe(descriptive_stats(df))

    # =========================
    # 5. CORRELACIÓN
    # =========================
    st.subheader("🔗 Matriz de correlación")
    corr = correlation_analysis(df)
    st.dataframe(corr)

    # =========================
    # 6. GRÁFICOS
    # =========================
    st.subheader("📈 Gráficos geoquímicos")
    st.pyplot(scatter_plot(df))
    st.pyplot(bar_plot(df))
    st.pyplot(box_plot(df))
    st.pyplot(correlation_heatmap(corr))

    st.subheader("🪨 Distribución por grupo litológico")
    st.pyplot(bar_plot_rock_group(df))

    # =========================
    # 7. GEOESPACIAL
    # =========================
    if "long" in df.columns and "lat" in df.columns:
        st.subheader("🌍 Ubicación de muestras")
        st.pyplot(plot_locations(df))

    # =========================
    # 8. VARIABLES GEOQUÍMICAS EXTRA
    # =========================
    if "tipo_alumina" in df.columns:
        st.subheader("🧪 Saturación de alúmina")
        st.dataframe(df["tipo_alumina"].value_counts().reset_index())