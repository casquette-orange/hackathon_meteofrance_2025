#!/bin/sh

chemin=
file=
chemin_out=
output_file=

#Quelques exemples de commande cdo :

cdo timmean ${chemin}/${file} ${chemin_out}/${output_file} #moyenne sur tous les pas de temps

cdo seasmean ${chemin}/${file} ${chemin_out}/${output_file} #moyenne saisonnière

cdo yseasmean ${chemin}/${file} ${chemin_out}/${output_file} #moyenne saisonnière multi-annuelle

cdo monmean ${chemin}/${file} ${chemin_out}/${output_file} #moyenne mensuelle

cdo ymonmean ${chemin}/${file} ${chemin_out}/${output_file} #moyenne mensuelle multi-annuelle

cdo monsum ${chemin}/${file} ${chemin_out}/${output_file} #somme mensuelle sur chaque année

cdo selyear,1990/2000 ${chemin}/${file} ${chemin_out}/${output_file} #sélection des années 1990-2000

cdo selmon,05 ${chemin}/${file} ${chemin_out}/${output_file} #sélection des mois 05

cdo monmean ${chemin}/${file} ${chemin_out}/${output_file} #moyenne mensuelle sur chaque année

cdo timpctl,99 ${chemin}/${file} -timmin ${chemin}/${file} -timmax ${chemin}/${file} ${chemin_out}/${output_file} #percentile 99 sur toute la période

cdo daymean ${chemin}/${file} ${chemin_out}/${output_file} #moyenne journalière

cdo dhourmean ${chemin}/${file} ${chemin_out}/${output_file} #moyenne horaire sur tous les jours
