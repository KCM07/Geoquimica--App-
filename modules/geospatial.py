import matplotlib.pyplot as plt
import seaborn as sns


def plot_locations(df):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    if "rock_group" in df.columns:
        sns.scatterplot(
            data=df,
            x="long",
            y="lat",
            hue="rock_group",
            palette="Set2",
            s=25,
            alpha=0.75,
            ax=ax
        )
    else:
        ax.scatter(df["long"], df["lat"], alpha=0.7, s=15)

    ax.set_title("Ubicación de muestras geológicas")
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig