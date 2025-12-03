import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

csv_paths = [
    "data/RRq99/RRq99_yr_RWL-20_TIMEavg_GEOxy_FR-Metro_EXPLORE2-2022_MF-ADAMONT_rcp85_ENSmax.csv",
    "data/RRq99/RRq99_yr_RWL-40_TIMEavg_GEOxy_FR-Metro_EXPLORE2-2022_MF-ADAMONT_rcp85_ENSmax.csv"
]

# Lecture et nettoyage des fichiers
gdfs = []
for path in csv_paths:
    df = pd.read_csv(path, sep=";", comment="#")
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df["RRq99"] = pd.to_numeric(df["Value"], errors="coerce")
    df_clean = df.dropna(subset=["Latitude", "Longitude", "RRq99"])
    geometry = [Point(xy) for xy in zip(df_clean["Longitude"], df_clean["Latitude"])]
    gdf = gpd.GeoDataFrame(df_clean, geometry=geometry)
    gdfs.append(gdf)

# Fond de carte France
world = gpd.read_file("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson")
france = world[world["ADMIN"] == "France"]

# Titres synthétiques
titles = [
    "RRq99 – RWL‑20 (+2.0 °C)",
    "RRq99 – RWL‑40 (+4.0 °C)",
    "Différence (RWL‑40 – RWL‑20)"
]

# Calcul des bornes globales pour l'échelle des deux premiers plots
all_values = pd.concat([gdf["RRq99"] for gdf in gdfs])
vmin, vmax = all_values.min(), all_values.max()

# Calcul de la différence
# On suppose que les deux fichiers ont les mêmes points (Lat/Lon)
diff_df = gdfs[1][["Latitude", "Longitude", "RRq99"]].copy()
diff_df["RRq99_diff"] = gdfs[1]["RRq99"].values - gdfs[0]["RRq99"].values
geometry = [Point(xy) for xy in zip(diff_df["Longitude"], diff_df["Latitude"])]
diff_gdf = gpd.GeoDataFrame(diff_df, geometry=geometry)

# Tracé côte à côte (3 cartes)
fig, axes = plt.subplots(1, 3, figsize=(30, 6), sharex=True, sharey=True)

# Scénario +2°C
france.boundary.plot(ax=axes[0], linewidth=0.5, color="black")
gdfs[0].plot(
    ax=axes[0],
    column="RRq99",
    cmap="viridis",
    markersize=40,
    legend=True,
    vmin=vmin,
    vmax=vmax
)
axes[0].set_title(titles[0], fontsize=10)
axes[0].set_xlim(-5.5, 10)
axes[0].set_ylim(41, 52)
axes[0].axis("off")

# Scénario +4°C
france.boundary.plot(ax=axes[1], linewidth=0.5, color="black")
gdfs[1].plot(
    ax=axes[1],
    column="RRq99",
    cmap="viridis",
    markersize=40,
    legend=True,
    vmin=vmin,
    vmax=vmax
)
axes[1].set_title(titles[1], fontsize=10)
axes[1].set_xlim(-5.5, 10)
axes[1].set_ylim(41, 52)
axes[1].axis("off")

# Différence
france.boundary.plot(ax=axes[2], linewidth=0.5, color="black")
diff_gdf.plot(
    ax=axes[2],
    column="RRq99_diff",
    cmap="RdBu",
    markersize=40,
    legend=True,
    vmin=diff_gdf["RRq99_diff"].min(),
    vmax=diff_gdf["RRq99_diff"].max()
)
axes[2].set_title(titles[2], fontsize=10)
axes[2].set_xlim(-5.5, 10)
axes[2].set_ylim(41, 52)
axes[2].axis("off")

plt.suptitle("RRq99 – Comparaison des scénarios (+2 °C vs +4 °C)", fontsize=14)
plt.tight_layout()
plt.show()
