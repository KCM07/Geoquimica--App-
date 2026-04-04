import streamlit as st
from modules.loader import load_data
from modules.cleaning import clean_data

st.title("Análisis Geoquímico de Rocas Ígneas")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file:

    df = load_data(uploaded_file)
    df = clean_data(df)

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
            inicio = st.number_input("Fila inicial", min_value=0, max_value=len(df)-1, value=0)

        with col2:
            fin = st.number_input("Fila final", min_value=1, max_value=len(df), value=50)

        if inicio < fin:
            st.dataframe(df.iloc[inicio:fin])
        else:
            st.warning("⚠️ La fila inicial debe ser menor que la final")

    elif modo == "Ver todo":
        st.dataframe(df)