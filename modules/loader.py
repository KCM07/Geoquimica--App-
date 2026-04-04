# CARGAR DATOS
import pandas as pd


def load_data(path):
    try:
        df = pd.read_csv(path)

        if df.empty:
            print("⚠ Archivo cargado pero está vacío")
        else:
            print(f"✔ Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")

        return df

    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return None