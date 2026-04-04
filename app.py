import streamlit as st
from modules.loader import load_data
from modules.cleaning import clean_data

st.title("Análisis Geoquímico de Rocas Ígneas")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file:

    df = load_data(uploaded_file)
    df = clean_data(df)

    st.subheader("Datos")
    st.write(df.head())

    st.subheader("Estadísticas")
    st.write(df.describe())