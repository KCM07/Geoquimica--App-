import matplotlib.pyplot as plt
import seaborn as sns


def plot_locations(df, size=(8, 5), point_size=35):
    if "long" not in df.columns or "lat" not in df.columns:
        return None

    df_plot = df.copy()

    fig, ax = plt.subplots(figsize=size)

    if "rock_group" in df_plot.columns:
        sns.scatterplot(
            data=df_plot,
            x="long",
            y="lat",
            hue="rock_group",
            palette="Set2",
            s=point_size,
            alpha=0.75,
            edgecolor="white",
            linewidth=0.3,
            ax=ax
        )
        ax.legend(title="rock_group", fontsize=7, title_fontsize=8, loc="best", frameon=True)
    else:
        ax.scatter(
            df_plot["long"],
            df_plot["lat"],
            s=point_size,
            alpha=0.75,
            edgecolors="white",
            linewidths=0.3
        )

    ax.set_title("Ubicación de muestras geológicas")
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.grid(True, linestyle="--", alpha=0.3)

    plt.tight_layout()
    return fig