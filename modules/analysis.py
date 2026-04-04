def add_geochemical_variables(df):
    df = df.copy()

    if "Na2On" in df.columns and "K2On" in df.columns:
        df["alkalis"] = df["Na2On"] + df["K2On"]

    if "FeO*n" in df.columns and "MgOn" in df.columns:
        df["Fe_Mg_ratio"] = df["FeO*n"] / df["MgOn"]

    if all(col in df.columns for col in ["Al2O3n", "CaOn", "Na2On", "K2On"]):
        df["A_CNK"] = df["Al2O3n"] / (df["CaOn"] + df["Na2On"] + df["K2On"])

        def classify_alumina(x):
            if x < 1:
                return "Metaluminoso"
            elif x > 1:
                return "Peraluminoso"
            return "Transicional"

        df["tipo_alumina"] = df["A_CNK"].apply(classify_alumina)

    return df


def descriptive_stats(df):

    oxidos = [
        "SiO2n", "TiO2n", "Al2O3n",
        "FeO*n", "MnOn", "MgOn",
        "CaOn", "Na2On", "K2On", "P2O5n"
    ]

    cols_validas = [col for col in oxidos if col in df.columns]

    stats = df[cols_validas].describe()

    print("\nEstadísticas descriptivas:")
    print(stats)

    return stats


def correlation_analysis(df):

    oxidos = [
        "SiO2n", "TiO2n", "Al2O3n",
        "FeO*n", "MnOn", "MgOn",
        "CaOn", "Na2On", "K2On", "P2O5n"
    ]

    cols_validas = [col for col in oxidos if col in df.columns]

    corr = df[cols_validas].corr()

    print("\nMatriz de correlación:")
    print(corr)

    return corr