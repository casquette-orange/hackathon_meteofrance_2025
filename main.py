import pandas as pd


##############################  transformer la data en df
path = "data/Indicateurs-Absolue_Centiles-Explore2-Climat_Moyenne-20ans_historical_csv"

# precipitations max
file = "Rx1D_yr_historical_TIMEavg_GEOxy_FR-Metro_EXPLORE2-2022_MF-ADAMONT_rcp85_ENSmax.csv"

# Cumul des déficits hydrique quotidien annuels
# file = "CWB-Hg0175_yr_historical_TIMEavg_GEOxy_FR-Metro_EXPLORE2-2022_MF-ADAMONT_rcp85_ENSmax.csv"

# jours avec indice feu > 40
# file="IFM40D_yr_historical_TIMEavg_GEOxy_FR-Metro_EXPLORE2-2022_MF-ADAMONT_rcp85_ENSmax.csv"

pathToFile = path + "/" + file


df = pd.read_csv(
    pathToFile,
    sep=";",
    comment="#"
)

# Supprimer les valeurs manquantes
df = df.dropna(subset=["Value"])

# Vérifier les colonnes
print(df.head())





############################## Conversion en objet spatial et affichage
import geopandas as gpd
from shapely.geometry import Point

# Créer une colonne geometry
geometry = [Point(xy) for xy in zip(df["Longitude"], df["Latitude"])]
gdf = gpd.GeoDataFrame(df, geometry=geometry)

# Définir le système de coordonnées (WGS84)
gdf.set_crs(epsg=4326, inplace=True)




############################## Affichage
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 10))
gdf.plot(column="Value", cmap="Blues", legend=True, ax=ax, markersize=5)
plt.title("Rx1D - Maximum annuel des précipitations quotidiennes")
plt.show()

# ---