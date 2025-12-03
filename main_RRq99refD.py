import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import re
import numpy as np
import matplotlib.patheffects as pe  


# --- CHEMIN A MODIFIER ---
DOSSIER_DONNEES = "data/"

ORDRE_SCENARIOS = {
    'Value_RWL_0': 0.0,
    'Value_RWL_20': 2.0,
    'Value_RWL_27': 2.7,
    'Value_RWL_40': 4.0
}
LABELS_SCENARIOS = {
    'Value_RWL_0': 'Historique (Ref)',
    'Value_RWL_20': '+2.0°C',
    'Value_RWL_27': '+2.7°C',
    'Value_RWL_40': '+4.0°C (Extrême)'
}

sns.set_theme(style="whitegrid", context="paper")
plt.rcParams['figure.dpi'] = 200



def setup_directories(base_path):
    """Crée l'arborescence de sortie."""
    root_out = os.path.join(base_path, "Resultats_Analyse_Meteo")
    dirs = {
        "csv": os.path.join(root_out, "DATA"),
        "plots": os.path.join(root_out, "PLOTS"),
        "report": os.path.join(root_out, "RAPPORTS")
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    return dirs

def convertir_duree(val):
    """Convertit les durées en jours (float)."""
    try:
        if pd.isna(val) or str(val).strip().lower() in ['nan', 'nat', '']: return np.nan
        return pd.to_timedelta(val).total_seconds() / 86400.0
    except: return np.nan

def run_etl(source_dir, output_dir_csv):
    """Extrait, transforme et charge les données."""
    print("--- 1. Chargement des données ---")
    fichiers = glob.glob(os.path.join(source_dir, "*.csv"))
    df_merged = None
    cles_fusion = ['Point', 'Latitude', 'Longitude']
    exclude = ["Resultats", "Consolidation", "Rapport", "Stats", "Graphique"]

    cols_valeurs = []

    for fichier in fichiers:
        if any(x in os.path.basename(fichier) for x in exclude): continue
        try:
            df = pd.read_csv(fichier, sep=';', comment='#')
            for c in cles_fusion: df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=cles_fusion).drop_duplicates(subset=cles_fusion)
            df['Point'] = df['Point'].astype(int)

            match = re.search(r"RWL-(\d+)", os.path.basename(fichier))
            if match: suffixe = f"RWL_{match.group(1)}"
            elif "historical" in fichier.lower() or "ref" in fichier.lower(): suffixe = "RWL_0"
            else: continue

            col_name = f"Value_{suffixe}"
            if 'Value' in df.columns:
                df[col_name] = df['Value'].apply(convertir_duree)
                df_subset = df[cles_fusion + [col_name]]
                df_merged = df_subset if df_merged is None else pd.merge(df_merged, df_subset, on=cles_fusion, how='outer')
                print(f"   -> Chargé : {col_name}")
        except Exception as e: print(f"   [Erreur] {os.path.basename(fichier)} : {e}")

    if df_merged is None or df_merged.empty:
        return None, []

    cols_valeurs = [c for c in ORDRE_SCENARIOS.keys() if c in df_merged.columns]
    df_merged[cols_valeurs] = df_merged[cols_valeurs].fillna(0.0)

    df_merged.to_csv(os.path.join(output_dir_csv, "Master_Data_Meteo.csv"), sep=';', index=False)
    return df_merged, cols_valeurs


def run_visualizations(df, cols_valeurs, plot_dir):
    """Génère l'ensemble des graphiques."""
    print("\n--- 2. Génération des Graphiques ---")
    
    df_long = df.melt(id_vars=['Point', 'Latitude', 'Longitude'], value_vars=cols_valeurs, 
                      var_name='Scenario_Code', value_name='Jours')
    df_long['Scenario'] = df_long['Scenario_Code'].map(LABELS_SCENARIOS)

    vmin_g, vmax_g = df_long['Jours'].min(), df_long['Jours'].max()
    if len(cols_valeurs) > 1:
        print(f"   A. Comparaison Spatiale...")
        g = sns.FacetGrid(df_long, col="Scenario", col_wrap=2, height=5, aspect=1.3)
        g.map_dataframe(sns.scatterplot, x="Longitude", y="Latitude", hue="Jours",
                        palette="YlOrRd", s=12, linewidth=0, alpha=0.9, hue_norm=(vmin_g, vmax_g))
        g.add_legend(title="Jours / an")
        plt.subplots_adjust(top=0.9)
        g.fig.suptitle("Comparaison de l'Exposition (Rouge = Risque Élevé)", fontweight='bold')
        plt.savefig(os.path.join(plot_dir, "1_Cartes_Comparatives.png"), dpi=300)
        plt.close()

    if 'Value_RWL_40' in df.columns and 'Value_RWL_0' in df.columns:
        print("   B. Carte Hotspots Extrêmes (Top 20)...")
        df['Delta_Abs'] = df['Value_RWL_40'] - df['Value_RWL_0']
        
        plt.figure(figsize=(12, 10))
        sc = plt.scatter(df['Longitude'], df['Latitude'], c=df['Delta_Abs'], 
                         cmap='YlOrRd', s=15, alpha=0.8, vmin=0, vmax=df['Delta_Abs'].max())
        cb = plt.colorbar(sc)
        cb.set_label("Augmentation (Jours supplémentaires)")
        
        top_20 = df.nlargest(20, 'Delta_Abs')
        for rank, (idx, row) in enumerate(top_20.iterrows(), 1):
            plt.scatter(row['Longitude'], row['Latitude'], s=80, facecolors='none', edgecolors='black', linewidth=0.8, alpha=0.7)
            if rank <= 10:
                txt = plt.text(row['Longitude'], row['Latitude'], f"#{rank} (+{row['Delta_Abs']:.1f}j)", 
                               fontsize=9, fontweight='bold', color='black')
                txt.set_path_effects([pe.withStroke(linewidth=2.5, foreground='white')])

        plt.title(f"TOP 20 DES HOTSPOTS (+4°C vs Actuel)", fontweight='bold', fontsize=14)
        plt.axis('equal')
        plt.savefig(os.path.join(plot_dir, "2_Carte_Hotspots_Top20.png"), dpi=300, bbox_inches='tight')
        plt.close()

    print("   C. ECDF...")
    plt.figure(figsize=(10, 6))
    sns.ecdfplot(data=df_long, x="Jours", hue="Scenario", palette="YlOrRd", linewidth=2)
    plt.axvline(x=10, color='black', linestyle='--', alpha=0.5, label='Seuil 10j')
    plt.title("Probabilité cumulée d'exposition")
    plt.savefig(os.path.join(plot_dir, "3_ECDF.png"), dpi=300)
    plt.close()

    if 'Value_RWL_40' in df.columns:
        print("   D. Carte % Change...")
        df['Pct_Change'] = np.where(df['Value_RWL_0'] > 0.1, 
                                   ((df['Value_RWL_40'] - df['Value_RWL_0']) / df['Value_RWL_0']) * 100, 0)
        plt.figure(figsize=(10, 8))
        sc = plt.scatter(df['Longitude'], df['Latitude'], c=df['Pct_Change'], 
                         cmap='RdYlGn_r', s=10, alpha=0.9, vmin=0, vmax=200)
        plt.colorbar(sc, label="Augmentation (%) - Max 200%")
        plt.title("Augmentation Relative en %", fontweight='bold')
        plt.axis('equal')
        plt.savefig(os.path.join(plot_dir, "4_Carte_Pct_Change.png"), dpi=300)
        plt.close()

    print("   E. Stats & Gradient...")
    plt.figure(figsize=(10, 6))
    df_long['Lat_Bin'] = df_long['Latitude'].round(1)
    sns.lineplot(data=df_long, x="Lat_Bin", y="Jours", hue="Scenario", palette="YlOrRd", errorbar=None)
    plt.title("Gradient Latitudinal")
    plt.savefig(os.path.join(plot_dir, "5_Gradient_Latitudinal.png"), dpi=300)
    plt.close()

    cols_delta = []
    for col in cols_valeurs:
        if col == 'Value_RWL_0': continue
        d_col = f"Delta_{col}"
        df[d_col] = df[col] - df['Value_RWL_0']
        cols_delta.append(d_col)
    
    if cols_delta:
        df_d = df.melt(id_vars=['Point'], value_vars=cols_delta, var_name='Scen', value_name='Delta')
        plt.figure(figsize=(8, 6))
        sns.boxplot(x='Scen', y='Delta', data=df_d, palette="YlOrRd", showfliers=False)
        plt.title("Dispersion des augmentations")
        plt.savefig(os.path.join(plot_dir, "6_Boxplot_Deltas.png"), dpi=300)
        plt.close()


def export_kpi(df, report_dir):
    """Exporte les zones critiques."""
    if 'Delta_Abs' in df.columns:
        top_50 = df.sort_values(by='Delta_Abs', ascending=False).head(50)
        cols_exp = ['Point', 'Latitude', 'Longitude', 'Value_RWL_0', 'Value_RWL_40', 'Delta_Abs']
        if 'Pct_Change' in df.columns: cols_exp.append('Pct_Change')
        
        f_out = os.path.join(report_dir, "TOP50_Zones_Critiques.csv")
        top_50[cols_exp].to_csv(f_out, sep=';', index=False, float_format="%.2f")
        print(f"\n[OK] Top 50 exporté : {f_out}")


def main():
    print("========================================")
    print("  ANALYSE CLIMATIQUE - RUN START")
    print("========================================")
    
    # 1. Setup
    dirs = setup_directories(DOSSIER_DONNEES)
    
    # 2. ETL
    df, cols = run_etl(DOSSIER_DONNEES, dirs["csv"])
    if df is None:
        print("Arrêt : Aucune donnée trouvée.")
        return

    # 3. Visualisation
    run_visualizations(df, cols, dirs["plots"])
    
    # 4. Export Report
    export_kpi(df, dirs["report"])

    print(f"\nTraitement terminé avec succès.")
    print(f"Graphiques : {dirs['plots']}")
    print("========================================")

if __name__ == "__main__":

    main()
