import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

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
    df_plot = df.copy()

    color_col = "rock_group" if "rock_group" in df_plot.columns else "rock_name"

    if "rock_group" in df_plot.columns:
        df_plot = df_plot[~df_plot["rock_group"].isin(["other", "ambiguous_intrusion"])]

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.scatterplot(
        data=df_plot,
        x="SiO2n",
        y="TiO2n",
        hue=color_col,
        style=color_col,
        palette="Set2",
        s=35,
        alpha=0.7,
        edgecolor="white",
        linewidth=0.3,
        ax=ax
    )

    ax.set_title("SiO₂ vs TiO₂ (Clasificación litológica)", fontsize=11)
    ax.set_xlabel("SiO₂ (%)")
    ax.set_ylabel("TiO₂ (%)")
    ax.grid(True, linestyle="--", alpha=0.3)

    ax.legend(
        title="Grupo",
        fontsize=7,
        title_fontsize=8,
        loc="upper right",
        frameon=True
    )

    plt.tight_layout()
    return fig


def tas_plot(df):
    if "alkalis" not in df.columns:
        return None

    df_plot = df.copy()
    color_col = "rock_group" if "rock_group" in df_plot.columns else "rock_name"

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.scatterplot(
        data=df_plot,
        x="SiO2n",
        y="alkalis",
        hue=color_col,
        style=color_col,
        palette="Set2",
        s=35,
        alpha=0.75,
        edgecolor="white",
        linewidth=0.3,
        ax=ax
    )

    ax.set_title("Diagrama TAS (SiO₂ vs Na₂O + K₂O)", fontsize=11)
    ax.set_xlabel("SiO₂ (%)")
    ax.set_ylabel("Na₂O + K₂O (%)")
    ax.grid(True, linestyle="--", alpha=0.3)

    ax.legend(
        title="Grupo",
        fontsize=7,
        title_fontsize=8,
        loc="upper left",
        frameon=True
    )

    plt.tight_layout()
    return fig


def harker_plot(df, y_col):
    if y_col not in df.columns or "SiO2n" not in df.columns:
        return None

    df_plot = df.copy()
    color_col = "rock_group" if "rock_group" in df_plot.columns else "rock_name"

    fig, ax = plt.subplots(figsize=(7, 4.5))

    sns.scatterplot(
        data=df_plot,
        x="SiO2n",
        y=y_col,
        hue=color_col,
        palette="Set2",
        s=30,
        alpha=0.7,
        edgecolor="white",
        linewidth=0.3,
        ax=ax
    )

    ax.set_title(f"Diagrama de Harker: SiO₂ vs {y_col}", fontsize=10)
    ax.set_xlabel("SiO₂ (%)")
    ax.set_ylabel(y_col)
    ax.grid(True, linestyle="--", alpha=0.3)

    ax.legend(
        title="Grupo",
        fontsize=6,
        title_fontsize=7,
        loc="best",
        frameon=True
    )

    plt.tight_layout()
    return fig


def bar_plot(df):
    fig, ax = plt.subplots(figsize=(7, 4))

    if "rock_base" in df.columns:
        tabla = df.groupby("rock_base").mean(numeric_only=True)[
            ["SiO2n", "TiO2n", "Al2O3n"]
        ].head(10)
    else:
        tabla = df.groupby("rock_name").mean(numeric_only=True)[
            ["SiO2n", "TiO2n", "Al2O3n"]
        ].head(10)

    tabla.plot(kind="bar", ax=ax)

    ax.set_title("Promedio por roca base")
    ax.set_ylabel("Concentración (%)")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    return fig


def bar_plot_rock_group(df):
    fig, ax = plt.subplots(figsize=(6, 4))

    if "rock_group" in df.columns:
        df["rock_group"].value_counts().plot(kind="bar", ax=ax)
        ax.set_title("Distribución por grupo litológico")
        ax.set_ylabel("Frecuencia")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
    else:
        ax.text(0.5, 0.5, "rock_group no disponible", ha="center", va="center")
        ax.axis("off")

    return fig


def group_mean_plot(df):
    if "rock_group" not in df.columns:
        return None

    fig, ax = plt.subplots(figsize=(8, 4.5))

    tabla = df.groupby("rock_group").mean(numeric_only=True)[
        ["SiO2n", "TiO2n", "Al2O3n", "MgOn"]
    ]

    tabla.plot(kind="bar", ax=ax)
    ax.set_title("Promedio geoquímico por grupo litológico")
    ax.set_ylabel("Concentración (%)")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    return fig


def box_plot(df):
    fig, ax = plt.subplots(figsize=(7, 5))

    cols = ["SiO2n", "MgOn", "FeO*n"]
    cols = [c for c in cols if c in df.columns]

    df_melt = df[cols].melt(var_name="Óxido", value_name="Valor")

    sns.boxplot(
        data=df_melt,
        x="Óxido",
        y="Valor",
        palette="Set3",
        ax=ax
    )

    ax.set_title("Distribución geoquímica")
    plt.tight_layout()
    return fig


def box_plot_by_group(df, y_col="SiO2n"):
    if "rock_group" not in df.columns or y_col not in df.columns:
        return None

    fig, ax = plt.subplots(figsize=(8, 4.5))

    sns.boxplot(
        data=df,
        x="rock_group",
        y=y_col,
        palette="Set2",
        ax=ax
    )

    ax.set_title(f"{y_col} por grupo litológico")
    ax.set_xlabel("Grupo litológico")
    ax.set_ylabel(y_col)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    return fig


def histogram_plot(df, col="SiO2n"):
    if col not in df.columns:
        return None

    fig, ax = plt.subplots(figsize=(7, 4))

    sns.histplot(
        data=df,
        x=col,
        bins=25,
        kde=True,
        color="steelblue",
        ax=ax
    )

    ax.set_title(f"Histograma de {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Frecuencia")
    plt.tight_layout()
    return fig


def oxide_balance_histogram(df):
    if "total_oxidos" not in df.columns:
        return None

    fig, ax = plt.subplots(figsize=(7, 4))

    sns.histplot(
        data=df,
        x="total_oxidos",
        bins=30,
        kde=True,
        color="darkorange",
        ax=ax
    )

    ax.axvline(95, color="red", linestyle="--", linewidth=1)
    ax.axvline(105, color="red", linestyle="--", linewidth=1)

    ax.set_title("Balance de óxidos")
    ax.set_xlabel("Suma de óxidos (%)")
    ax.set_ylabel("Frecuencia")
    plt.tight_layout()
    return fig


def correlation_heatmap(corr):
    fig, ax = plt.subplots(figsize=(7, 5))

    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
        annot_kws={"size": 7},
        cbar_kws={"shrink": 0.8},
        ax=ax
    )

    ax.set_title("Correlación entre óxidos mayores", fontsize=11)

    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.yticks(fontsize=7)
    plt.tight_layout()
    return fig