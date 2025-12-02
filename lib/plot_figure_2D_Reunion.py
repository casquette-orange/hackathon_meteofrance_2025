#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

import pandas as pd
import xarray as xr
import math
import configparser
import os
import matplotlib.pyplot as plt
import matplotlib
import cartopy.crs as ccrs
import geopandas
import sys
import rasterio
from rasterio.features import geometry_mask
import geopandas as gpd
import cartopy.feature as cf
import cartopy.io.shapereader as shpreader
import cartopy.io.shapereader as shpreader
from matplotlib.colors import BoundaryNorm
import cartopy.feature as cfeature
import cartopy as cart
import time

import argparse

import shapely

import shapely.vectorized
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from shapely.geometry import Polygon
from shapely.geometry import shape, MultiPolygon
from shapely.geometry import Point
from pyproj import Transformer
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import geopandas
import numpy as np
import sys
import os
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colorbar as mcbar
from matplotlib import ticker
import matplotlib.colors as mcolors


from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from osgeo import osr




#from mpl_toolkits.basemap import Basemap

# Import des fonctions necessaires a la lecture et tracer des variables



def genere_carte(bounds, title, title_size, labelsize, scale_bar_km):
    """ creation d'une carte sur un domaine predefinie a l'aide de bounds.
        bounds : extension du domaine en lat min et max et lon min et max
        title : titre de la figure
        title_size : titre de la figure
        labelsize : taille des caracteres pour le titre
        scale_bar_km : dimension de la scale bar en km"""

    fig = plt.figure(figsize=(18., 13.))
    plt_title = title
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    ax.set_global()
    lon_formatter = LongitudeFormatter(number_format='.1f', degree_symbol='', dateline_direction_label=True)
    lat_formatter = LatitudeFormatter(number_format='.1f',degree_symbol='')


    ax.set_extent(bounds)
    ax.set_title(plt_title, loc='center', size = title_size)

    ### ajout des coordonnees :

    ax.set_yticks(np.linspace(bounds[2],bounds[3],5)[1:],crs=ccrs.PlateCarree()) # set latitude indicators
    #ax.yaxis.tick_right()
    ax.set_xticks(np.linspace(bounds[0],bounds[1],5),crs=ccrs.PlateCarree()) # set longitude indicators
    lon_formatter = LongitudeFormatter(number_format='0.1f',degree_symbol='',dateline_direction_label=True) # format lons
    lat_formatter = LatitudeFormatter(number_format='0.1f',degree_symbol='') # format lats
    ax.xaxis.set_major_formatter(lon_formatter) # set lons
    ax.yaxis.set_major_formatter(lat_formatter) # set lats
    ax.xaxis.set_tick_params(labelsize=labelsize)
    ax.yaxis.set_tick_params(labelsize=labelsize)
    ax.tick_params(axis="both") # this did not work


    ### ajout de la scale bar:
    fontprops = fm.FontProperties(size=25)
    scalebar = AnchoredSizeBar(ax.transData,
                               scale_bar_km*1000, str(scale_bar_km)+' km', 'lower left',
                               pad=0.5,
                               color='black',
                               frameon=False,
                               size_vertical=1000,
                               sep=10,
                               fontproperties=fontprops, width=20)
    ax.add_artist(scalebar)

    return ax

def read_shape_file(shape_file_name):

    """Read in a shapefile and it's associated prj file to generate a GeoDataFrame"""

    directory = os.path.dirname(shape_file_name)
    file_base = os.path.splitext(os.path.basename(shape_file_name))[0]
    prj_file_name = os.path.join(directory, file_base + '.prj')

    shape_gdf = geopandas.read_file(shape_file_name)

    # read in the projection file and apply
    with open(prj_file_name, 'r') as prj_ref:
        prj = prj_ref.readline()

    srs = osr.SpatialReference()
    srs.ImportFromESRI([prj])
    proj4 = srs.ExportToProj4()

    shape_gdf.crs = proj4

    return shape_gdf



os.system('cp /cnrm/socle/COMMON/Indicateurs_WP6/UTILE/fonctions.py .')
os.system('cp /cnrm/socle/COMMON/Indicateurs_WP6/UTILE/bib_param_matplotlib_DIROI.py .')
os.system('cp /home/forstera/programmes/socle_om/UTILE/lib_fwi.py .')
os.system('cp /home/forstera/programmes/socle_om/UTILE/lib_fwiv_Arnaud.py .')
#os.system('cp /cnrm/socle/USERS/duboisc/SOCLE_OM/IFM/lib_fwiv_2025.py .')

import fonctions
import bib_param_matplotlib_DIROI as bib
#import lib_fwiv
import lib_fwi
import lib_fwiv_Arnaud
#import lib_fwiv_2025

os.system('rm fonctions.py')
os.system('rm bib_param_matplotlib_DIROI.py')
os.system('rm lib_fwi.py')
os.system('rm lib_fwiv_Arnaud.py')


communes_reunion_shp = fonctions.read_shape_file('/cnrm/socle/COMMON/Donnees-Territoires/REUNION/shapefiles/zonage_FdF_MTO.shp')
communes_reunion_shp = communes_reunion_shp.to_crs('epsg:4326')




parser = argparse.ArgumentParser(description="Filter DataFrame by date range")
parser.add_argument("date1", type=str, help="Start date in YYYY-MM-DD format")
parser.add_argument("date2", type=str, help="End date in YYYY-MM-DD format")

#######################################
## Parametres a completer
#######################################

lat_centre, lon_centre = -21.10, 55.50   #pour La Réunion (-21.08, 55.52) - a la louche
coeff_ext_spatiale = 0.4 #pour zoomer plus ou moins sur le domaine considere



#masque Reunion
reunion_shp = gpd.read_file('/cnrm/socle/COMMON/Donnees-Territoires/REUNION/shapefiles/admin-departement-reunion.shp')
f_mask = xr.open_dataset('/cnrm/socle/DATA/STATICS/OUTRE_MER/RCM/INDIEN/masque_terre_REU003_0-1.nc')
land_mask = np.squeeze(f_mask['masque']).values
#Lat=(lats.values)
#Lon=lons.values
#Lon, Lat = np.meshgrid(Lon, Lat)


don = ["AROME-OPER-8UTC","OBS-KRIGEES","OBS-KRIGEES-SHORT","AROME-OPER-8UTC-MINMAX","AROME-OPER-1DAY-MINMAX"]

#don = ["OBS-KRIGEES", "OBS-KRIGEES-SHORT", "AROME-OPER-DAILY", "AROME-OPER-6UTC", "AROME-OPER-6UTC-1DAY"]

for donnees in don: 
    if donnees == "OBS-KRIGEES":
        period = "2000-2024"
        direc = "OBS_KRIGEES"
    elif donnees == "OBS-KRIGEES-SHORT":
        period = "2020-2024"
        direc = "OBS_KRIGEES"
    elif donnees == "AROME-OPER-8UTC":
        period = "2020-2024"
        direc = "OPER"
    elif donnees == "AROME-OPER-8UTC-MINMAX":
        period = "2020-2024"
        direc = "OPER"
    elif donnees == "AROME-OPER-1DAY-MINMAX":
        period = "2020-2024"
        direc = "OPER"

#donnees= "OBS-KRIGEES"
#donnees= "AROME-OPER-DAILY"
#donnees= "AROME-OPER-6UTC"
#period = "2020-2024_20241108"

#period = "2000-2024"

#var = "icd"
#var = "ipi"
#var = "iis"
#var = "ih"
#var = "icl"
    variables = ["ifm","icd","ipi","iis","ih","icl"]

    for var in variables:

        indi = ["min", "mean", "max","q50","q80", "q90", "q95", "q97", "q99"] #, "DJF_mean", "MAM_mean", "JJA_mean", "SON_mean", "MJJAS_mean", "NDJFM_mean", "q80", "q90", "q95", "q97", "q99"]

        for ind in indi: 

        #Read RR for gridded data over la Reunion (0.03)
            file_path = f"/cnrm/socle/COMMON/Indicateurs_WP6/IFM/DATA/VALIDATION/{direc}/fire_indices_{donnees}_{period}_{ind}.nc"
            nc_file_mod = xr.open_dataset(file_path)
            data1 = xr.DataArray((nc_file_mod[var].values))
            print("data",data1)
            data = data1[0,:,:]

            Lat= xr.DataArray((nc_file_mod['lat'].values))
            Lon = xr.DataArray((nc_file_mod['lon'].values))
            Lon, Lat = np.meshgrid(Lon, Lat)


            levels = bib.levels_var[var]
            print(levels)
            cmap = bib.cmap_var[var]
            print(cmap)
            norm = bib.norm_var[var]
            titre_label = bib.titre_label_var.get(var,'') + bib.unit_var.get(var, '')
            labelsize = bib.size_titre_label_var.get(var, 12)
            tickssize = bib.size_label_var.get(var, 10)
            titre_graphique = f"{var} {ind} ({period})"

            # Define spatial extent for the map
            extend_bounds = [
            lon_centre - 1 * coeff_ext_spatiale,
            lon_centre + 1 * coeff_ext_spatiale,
            lat_centre - 1 * coeff_ext_spatiale,
            lat_centre + 1 * coeff_ext_spatiale
            ]

            print(levels[-1])

            fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
            ax = fonctions.genere_carte(extend_bounds, titre_graphique, 33, labelsize, 10)
            cmesh = ax.pcolormesh(
            Lon, Lat, data, cmap=cmap, norm=norm, transform=ccrs.PlateCarree(), zorder=0)

            cbar = plt.colorbar(cmesh, ax=ax, cmap=cmap,norm=norm,ticks=levels)
            cbar.ax.tick_params(labelsize=tickssize)
            cbar.set_label(titre_label, fontsize=labelsize)
            ax.add_geometries(
            communes_reunion_shp.geometry, crs=ccrs.PlateCarree(),
            facecolor='none', edgecolor='black', linewidth=1.5, zorder=1
            )
            for geom in reunion_shp.geometry:
                if geom.type == 'MultiPolygon':
# Itérer sur chaque polygone dans le MultiPolygon
                    paths = []
            for poly in geom.geoms:
                paths.append(Path(poly.exterior.coords))
# Créer un chemin composé à partir des polygones
    
                path = Path.make_compound_path(*paths)

# Ajouter le chemin comme un patch pour la découpe
                patch = PathPatch(path, transform=ccrs.PlateCarree(), facecolor='none', edgecolor='none')
                ax.add_patch(patch)
                cmesh.set_clip_path(patch)
#plt.show()
#sys.exit()

                plt.savefig(f"/cnrm/socle/COMMON/Indicateurs_WP6/IFM/FIGURES/{var}_{donnees}_{period}_{ind}.png", dpi=150)
                plt.close(fig)
