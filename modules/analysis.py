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
    return df.describe().round(2)


def correlation_analysis(df):
    return df.corr(numeric_only=True).round(2)