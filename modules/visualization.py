# Gráficos
import matplotlib.pyplot as plt
import seaborn as sns

def scatter_plot(df):
    plt.figure()
    sns.scatterplot(x="SiO2n", y="TiO2n", hue="rock_name", data=df)
    plt.title("SiO2 vs TiO2")
    plt.show()


def bar_plot(df):
    plt.figure()
    df.groupby("rock_name").mean(numeric_only=True)[
        ["SiO2n", "TiO2n", "Al2O3n"]
    ].plot(kind="bar")
    plt.title("Promedio por roca")
    plt.ylabel("Concentración (%)")
    plt.show()


def box_plot(df):
    plt.figure()
    sns.boxplot(data=df[["SiO2n", "MgOn", "FeO*n"]])
    plt.title("Distribución")
    plt.show()


def correlation_heatmap(corr):
    plt.figure()
    sns.heatmap(corr, annot=True, cmap="coolwarm")
    plt.title("Correlación")
    plt.show()