# CARGAR DATOS
import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    print("✔ Datos cargados")
    return df
