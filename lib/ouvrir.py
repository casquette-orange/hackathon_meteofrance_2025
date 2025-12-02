import xarray as xr
import matplotlib.pyplot as plt

# Charger le fichier
file_name="Indicateurs-Absolue_Centiles-DRIAS2020-Enneigement_Moyenne-20ans_RWL20_Netcdf/SDmns_mon-01_RWL-20_TIMEavg_ANOMrd-1976-2005_GEOmassif_FR-Alpes_DRIAS-2020_MF-ADAMONT_rcp85_ENSmax.nc"
ds = xr.open_dataset(file_name)

# Afficher les variables et dimensions
# print(ds)



# Extraire les coordonnées et la variable
lats = ds['LAT'].values
lons = ds['LON'].values
values = ds['SDmns'].values[0]  # première valeur temporelle

# Afficher sur une carte simple
plt.figure(figsize=(8,6))
sc = plt.scatter(lons, lats, c=values, cmap="coolwarm", s=50)
plt.colorbar(sc, label="SDmns (enneigement moyen)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Carte des valeurs SDmns - Alpes (2035-07-02)")
plt.show()