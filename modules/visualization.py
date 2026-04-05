import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

plt.rcParams.update({
    "figure.figsize": (7, 4.5),
    "font.size": 8,
    "axes.titlesize": 10,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7
})


def scatter_plot(df, x_col="SiO2n", y_col="TiO2n", color_col="rock_group"):
    if x_col not in df.columns or y_col not in df.columns:
        return None

    df_plot = df.copy()

    if color_col not in df_plot.columns:
        color_col = None

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.scatterplot(
        data=df_plot,
        x=x_col,
        y=y_col,
        hue=color_col,
        style=color_col if color_col else None,
        palette="Set2" if color_col else None,
        s=35,
        alpha=0.75,
        edgecolor="white",
        linewidth=0.3,
        ax=ax
    )

    ax.set_title(f"{x_col} vs {y_col}")
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.grid(True, linestyle="--", alpha=0.3)

    if color_col:
        ax.legend(title=color_col, fontsize=7, title_fontsize=8, loc="best", frameon=True)

    plt.tight_layout()
    return fig


def tas_plot(df, color_col="rock_group"):
    if "SiO2n" not in df.columns or "alkalis" not in df.columns:
        return None

    df_plot = df.copy()

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.scatterplot(
        data=df_plot,
        x="SiO2n",
        y="alkalis",
        hue=color_col if color_col in df_plot.columns else None,
        style=color_col if color_col in df_plot.columns else None,
        palette="Set2" if color_col in df_plot.columns else None,
        s=35,
        alpha=0.75,
        edgecolor="white",
        linewidth=0.3,
        ax=ax
    )

    # Límites TAS simplificados
    ax.axvline(45, color="gray", linestyle="--", linewidth=0.8)
    ax.axvline(52, color="gray", linestyle="--", linewidth=0.8)
    ax.axvline(57, color="gray", linestyle="--", linewidth=0.8)
    ax.axvline(63, color="gray", linestyle="--", linewidth=0.8)
    ax.axvline(69, color="gray", linestyle="--", linewidth=0.8)

    ax.text(41, 1, "Basalt", fontsize=7)
    ax.text(49, 2, "Basaltic\nandesite", fontsize=7, ha="center")
    ax.text(54.5, 3, "Andesite", fontsize=7, ha="center")
    ax.text(60, 4, "Dacite", fontsize=7, ha="center")
    ax.text(72, 5, "Rhyolite", fontsize=7, ha="center")

    ax.set_title("Diagrama TAS")
    ax.set_xlabel("SiO2 (%)")
    ax.set_ylabel("Na2O + K2O (%)")
    ax.grid(True, linestyle="--", alpha=0.3)

    if color_col in df_plot.columns:
        ax.legend(title=color_col, fontsize=7, title_fontsize=8, loc="best", frameon=True)

    plt.tight_layout()
    return fig


def harker_plot(df, y_col, color_col="rock_group"):
    if "SiO2n" not in df.columns or y_col not in df.columns:
        return None

    fig, ax = plt.subplots(figsize=(7, 4.5))

    sns.scatterplot(
        data=df,
        x="SiO2n",
        y=y_col,
        hue=color_col if color_col in df.columns else None,
        palette="Set2" if color_col in df.columns else None,
        s=30,
        alpha=0.7,
        edgecolor="white",
        linewidth=0.3,
        ax=ax
    )

    sns.regplot(
        data=df,
        x="SiO2n",
        y=y_col,
        scatter=False,
        ci=None,
        line_kws={"color": "black", "linewidth": 1},
        ax=ax
    )

    ax.set_title(f"Harker: SiO2 vs {y_col}")
    ax.set_xlabel("SiO2 (%)")
    ax.set_ylabel(y_col)
    ax.grid(True, linestyle="--", alpha=0.3)

    if color_col in df.columns:
        ax.legend(title=color_col, fontsize=6, title_fontsize=7, loc="best", frameon=True)

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

    ax.set_title("Correlación entre óxidos mayores")
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.yticks(fontsize=7)
    plt.tight_layout()
    return fig


def strong_corr_barplot(corr, top_n=10):
    pairs = []

    cols = list(corr.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append((f"{cols[i]} vs {cols[j]}", corr.iloc[i, j]))

    pairs = sorted(pairs, key=lambda x: abs(x[1]), reverse=True)[:top_n]

    if not pairs:
        return None

    names = [p[0] for p in pairs]
    values = [p[1] for p in pairs]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(names, values)
    ax.set_title("Correlaciones más fuertes")
    ax.set_ylabel("r")
    plt.xticks(rotation=45, ha="right")
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


def histogram_plot(df, col):
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

    ax.set_title(f"Distribución de {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Frecuencia")
    plt.tight_layout()
    return fig


def cumulative_frequency_plot(df, col):
    if col not in df.columns:
        return None

    values = df[col].dropna().sort_values().reset_index(drop=True)
    if len(values) == 0:
        return None

    cumfreq = np.arange(1, len(values) + 1) / len(values) * 100

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(values, cumfreq, marker=".", linestyle="-")
    ax.set_title(f"Frecuencia acumulada de {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Frecuencia acumulada (%)")
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    return fig


def qq_style_plot(df, col):
    if col not in df.columns:
        return None

    values = df[col].dropna().sort_values().reset_index(drop=True)
    if len(values) == 0:
        return None

    probs = (np.arange(1, len(values) + 1) - 0.5) / len(values)
    theoretical = np.quantile(np.random.normal(size=5000), probs)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.scatter(theoretical, values, s=10, alpha=0.7)
    ax.set_title(f"QQ aproximado - {col}")
    ax.set_xlabel("Cuantiles teóricos")
    ax.set_ylabel("Cuantiles observados")
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    return fig


def magmatic_series_plot(df, color_col="rock_group"):
    if "SiO2n" not in df.columns or "Fe_Mg_ratio" not in df.columns:
        return None

    fig, ax = plt.subplots(figsize=(7, 4.5))

    sns.scatterplot(
        data=df,
        x="SiO2n",
        y="Fe_Mg_ratio",
        hue=color_col if color_col in df.columns else None,
        palette="Set2" if color_col in df.columns else None,
        s=30,
        alpha=0.75,
        edgecolor="white",
        linewidth=0.3,
        ax=ax
    )

    sns.regplot(
        data=df,
        x="SiO2n",
        y="Fe_Mg_ratio",
        scatter=False,
        ci=None,
        line_kws={"color": "black", "linewidth": 1},
        ax=ax
    )

    ax.set_title("Tendencia magmática aproximada (Fe/Mg vs SiO2)")
    ax.set_xlabel("SiO2 (%)")
    ax.set_ylabel("FeO* / MgO")
    ax.grid(True, linestyle="--", alpha=0.3)

    if color_col in df.columns:
        ax.legend(title=color_col, fontsize=7, title_fontsize=8, loc="best", frameon=True)

    plt.tight_layout()
    return fig


def bar_plot_rock_group(df):
    if "rock_group" not in df.columns:
        return None

    fig, ax = plt.subplots(figsize=(6, 4))
    df["rock_group"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Distribución por grupo litológico")
    ax.set_ylabel("Frecuencia")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    return fig


def group_mean_plot(df):
    if "rock_group" not in df.columns:
        return None

    cols = ["SiO2n", "TiO2n", "Al2O3n", "MgOn"]
    cols = [c for c in cols if c in df.columns]

    if not cols:
        return None

    tabla = df.groupby("rock_group")[cols].mean(numeric_only=True)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    tabla.plot(kind="bar", ax=ax)
    ax.set_title("Promedios por grupo litológico")
    ax.set_ylabel("Concentración (%)")
    plt.xticks(rotation=20, ha="right")
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
