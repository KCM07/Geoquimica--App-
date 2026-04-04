# análisis
def descriptive_stats(df):
    print("\n📊 Estadísticas:")
    print(df.describe())


def correlation_analysis(df):
    corr = df.corr(numeric_only=True)
    print("\n🔗 Correlaciones:")
    print(corr)
    return corr