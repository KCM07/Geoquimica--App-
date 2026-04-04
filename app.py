import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from modules.loader import load_data
from modules.cleaning import clean_data

st.set_page_config(page_title="Análisis Geoquímico", layout="wide")

st.title("⛏️ Análisis Geoquímico de Rocas Ígneas")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    df = clean_data(df)

    if "Na2On" in df.columns and "K2On" in df.columns:
        df["alkalis"] = df["Na2On"] + df["K2On"]

    # =========================
    # VISTA INTERACTIVA
    # =========================
    st.subheader("📋 Vista previa de los datos")
    st.write(f"Filas totales: {df.shape[0]} | Columnas: {df.shape[1]}")

    modo = st.radio(
        "Selecciona cómo quieres visualizar los datos:",
        ["Vista previa (50 filas)", "Elegir rango", "Ver todo"]
    )

    if modo == "Vista previa (50 filas)":
        st.dataframe(df.head(50))

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
            st.dataframe(df.iloc[inicio:fin])
        else:
            st.warning("⚠️ La fila inicial debe ser menor que la final")

    elif modo == "Ver todo":
        st.dataframe(df)

    # =========================
    # ESTADÍSTICAS
    # =========================
    st.subheader("📊 Estadísticas descriptivas")
    st.dataframe(df.describe())

    # =========================
    # CORRELACIÓN
    # =========================
    st.subheader("🔗 Matriz de correlación")
    corr = df.corr(numeric_only=True)
    st.dataframe(corr)

    # =========================
    # GRÁFICOS
    # =========================
    st.subheader("📈 Gráfico de dispersión: SiO2 vs TiO2")
    fig1, ax1 = plt.subplots()
    sns.scatterplot(data=df, x="SiO2n", y="TiO2n", hue="rock_name", ax=ax1)
    ax1.set_title("SiO2 vs TiO2")
    st.pyplot(fig1)

    st.subheader("📊 Promedio de compuestos por tipo de roca")
    fig2, ax2 = plt.subplots()
    df.groupby("rock_name").mean(numeric_only=True)[
        ["SiO2n", "TiO2n", "Al2O3n"]
    ].plot(kind="bar", ax=ax2)
    ax2.set_title("Promedio por roca")
    ax2.set_ylabel("Concentración (%)")
    st.pyplot(fig2)

    st.subheader("📦 Boxplot de compuestos")
    fig3, ax3 = plt.subplots()
    sns.boxplot(data=df[["SiO2n", "MgOn", "FeO*n"]], ax=ax3)
    ax3.set_title("Distribución de compuestos")
    st.pyplot(fig3)

    st.subheader("🔥 Heatmap de correlación")
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax4)
    ax4.set_title("Matriz de correlación")
    st.pyplot(fig4)

    # =========================
    # GEOESPACIAL
    # =========================
    if "long" in df.columns and "lat" in df.columns:
        st.subheader("🌍 Ubicación de muestras geológicas")
        fig5, ax5 = plt.subplots()
        ax5.scatter(df["long"], df["lat"])
        ax5.set_xlabel("Longitud")
        ax5.set_ylabel("Latitud")
        ax5.set_title("Ubicación geográfica")
        st.pyplot(fig5)