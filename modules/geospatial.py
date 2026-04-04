import matplotlib.pyplot as plt
def plot_locations(df):
    plt.figure()
    plt.scatter(df["long"], df["lat"], alpha=0.7)
    plt.title("Ubicación de muestras geológicas")
    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
    plt.grid()
    plt.show()