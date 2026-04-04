import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({
    "figure.figsize": (6, 4),
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7
})


def scatter_plot(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(data=df, x="SiO2n", y="TiO2n", hue="rock_name", s=25, ax=ax)
    ax.set_title("SiO2 vs TiO2")
    ax.set_xlabel("SiO2 (%)")
    ax.set_ylabel("TiO2 (%)")
    plt.tight_layout()
    return fig


def bar_plot(df):
    fig, ax = plt.subplots(figsize=(7, 4))
    df.groupby("rock_base").mean(numeric_only=True)[
        ["SiO2n", "TiO2n", "Al2O3n"]
    ].head(10).plot(kind="bar", ax=ax)
    ax.set_title("Promedio por roca base")
    ax.set_ylabel("Concentración (%)")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    return fig


def box_plot(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=df[["SiO2n", "MgOn", "FeO*n"]], ax=ax)
    ax.set_title("Distribución de compuestos")
    plt.tight_layout()
    return fig


def correlation_heatmap(corr):
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        annot_kws={"size": 6},
        ax=ax
    )
    ax.set_title("Matriz de correlación")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


def bar_plot_rock_group(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    df["rock_group"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Distribución por grupo litológico")
    ax.set_ylabel("Frecuencia")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    return fig