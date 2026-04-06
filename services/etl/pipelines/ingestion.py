import pandas as pd
import os
from datetime import datetime

DATA_DIR     = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\data\raw"
RAPPORT_DIR  = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\rapport"

os.makedirs(RAPPORT_DIR, exist_ok=True)

rapport_path = os.path.join(RAPPORT_DIR, "rapport_inventaire.md")

DATASETS = {
    "daily_food_nutrition":  "daily_food_nutrition_dataset.csv",
    "diet_recommendations":  "diet_recommendations_dataset.csv",
    "gym_members_exercise":  "gym_members_exercise_tracking.csv",
    "gym_members_synthetic": "gym_members_exercise_tracking_synthetic_data.csv",
}

rapports = []

for name, file in DATASETS.items():
    path = os.path.join(DATA_DIR, file)
    try:
        # Comptage lignes brutes du fichier
        with open(path, 'r', encoding='utf-8', errors='ignore') as f_raw:
            nb_lignes_brutes = sum(1 for _ in f_raw) - 1  # -1 pour le header

        df               = pd.read_csv(path, on_bad_lines='skip')
        nb_lignes        = len(df)
        nb_colonnes      = len(df.columns)
        nb_doublons      = df.duplicated().sum()
        valeurs_manq     = df.isnull().sum()[df.isnull().sum() > 0].to_dict()
        types_colonnes   = df.dtypes.astype(str).to_dict()
        lignes_sautees   = nb_lignes_brutes - nb_lignes

        rapports.append({
            "name":           name,
            "file":           file,
            "status":         "OK",
            "lignes_brutes":  nb_lignes_brutes,
            "lignes":         nb_lignes,
            "lignes_sautees": lignes_sautees,
            "colonnes":       nb_colonnes,
            "doublons":       nb_doublons,
            "manquants":      valeurs_manq,
            "types":          types_colonnes,
        })

        print(f"✅ {name} — {nb_lignes_brutes} lignes brutes / {nb_lignes} chargées")
        if lignes_sautees > 0:
            print(f"   ⚠️  {lignes_sautees} lignes sautées (lignes corrompues)")
        print(f"   Doublons : {nb_doublons}")
        print(f"   Valeurs manquantes : {valeurs_manq if valeurs_manq else 'aucune'}\n")

    except Exception as e:
        rapports.append({
            "name":           name,
            "file":           file,
            "status":         f"ERREUR : {e}",
            "lignes_brutes":  0,
            "lignes":         0,
            "lignes_sautees": 0,
            "colonnes":       0,
            "doublons":       0,
            "manquants":      {},
            "types":          {},
        })
        print(f"❌ {name} : {e}\n")

with open(rapport_path, "w", encoding="utf-8") as f:
    f.write("# Rapport d'inventaire des sources de données\n\n")
    f.write(f"**Projet** : HealthAI Coach — Backend Métier  \n")
    f.write(f"**Généré le** : {datetime.now().strftime('%d/%m/%Y à %H:%M')}  \n\n")
    f.write("---\n\n")

    for r in rapports:
        f.write(f"## {r['name']}\n\n")
        f.write("| Propriété | Valeur |\n")
        f.write("|-----------|--------|\n")
        f.write(f"| Fichier         | `{r['file']}` |\n")
        f.write(f"| Statut          | {r['status']} |\n")
        f.write(f"| Lignes brutes   | {r['lignes_brutes']} |\n")
        f.write(f"| Lignes chargées | {r['lignes']} |\n")

        if r['lignes_sautees'] > 0:
            f.write(f"| Lignes sautées  | {r['lignes_sautees']} ⚠️ lignes corrompues |\n")
        else:
            f.write(f"| Lignes sautées  | 0 |\n")

        f.write(f"| Colonnes        | {r['colonnes']} |\n")
        f.write(f"| Doublons        | {r['doublons']} |\n")

        if r['manquants']:
            f.write("\n**Valeurs manquantes :**\n\n")
            for col, nb in r['manquants'].items():
                f.write(f"- `{col}` : {nb} valeurs manquantes\n")
        else:
            f.write("\n✅ Aucune valeur manquante\n")

        if r['types']:
            f.write("\n**Types des colonnes :**\n\n")
            for col, typ in r['types'].items():
                f.write(f"- `{col}` : {typ}\n")

        f.write("\n---\n\n")

print(f"📄 Rapport inventaire généré : {rapport_path}")