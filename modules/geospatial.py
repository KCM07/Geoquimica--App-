import matplotlib.pyplot as plt


def plot_locations(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(df["long"], df["lat"], alpha=0.7, s=15)
    ax.set_title("Ubicación de muestras geológicas")
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig