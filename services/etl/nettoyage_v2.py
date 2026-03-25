import pandas as pd

import os
from datetime import datetime
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ── Configuration ─────────────────────────────────────────
DATA_DIR    = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\data\raw"
BDD_DIR     = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\data\clean_bdd"
ML_DIR      = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\data\clean_ml"
RAPPORT_DIR = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\rapport"

os.makedirs(BDD_DIR,     exist_ok=True)
os.makedirs(ML_DIR,      exist_ok=True)
os.makedirs(RAPPORT_DIR, exist_ok=True)

# ── Chargement ─────────────────────────────────────────────
print("📥 Chargement des données brutes...\n")
food = pd.read_csv(os.path.join(DATA_DIR, "daily_food_nutrition_dataset.csv"), on_bad_lines='skip')
diet = pd.read_csv(os.path.join(DATA_DIR, "diet_recommendations_dataset.csv"))
gym  = pd.read_csv(os.path.join(DATA_DIR, "gym_members_exercise_tracking.csv"))
synt = pd.read_csv(os.path.join(DATA_DIR, "gym_members_exercise_tracking_synthetic_data.csv"))

# ══════════════════════════════════════════════════════════
# NETTOYAGE BDD — léger, garde les NULL
# ══════════════════════════════════════════════════════════
print("=" * 50)
print("📦 NETTOYAGE POUR LA BDD")
print("=" * 50)

# ── BDD Dataset 1 — food ──────────────────────────────────
print("\n🧹 [BDD] daily_food_nutrition...")
food_bdd = food.drop_duplicates()
food_bdd.columns = food_bdd.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
food_bdd.to_csv(os.path.join(BDD_DIR, "daily_food_nutrition_bdd.csv"), index=False)
print(f"   ✅ {len(food_bdd)} lignes — doublons supprimés, NULL conservés")

# ── BDD Dataset 2 — diet ──────────────────────────────────
print("🧹 [BDD] diet_recommendations...")
diet_bdd = diet.copy()
diet_bdd.columns = diet_bdd.columns.str.strip().str.lower().str.replace(" ", "_")
diet_bdd.to_csv(os.path.join(BDD_DIR, "diet_recommendations_bdd.csv"), index=False)
print(f"   ✅ {len(diet_bdd)} lignes — NULL conservés")

# ── BDD Dataset 3 — gym ───────────────────────────────────
print("🧹 [BDD] gym_members_exercise...")
gym_bdd = gym.copy()
gym_bdd.columns = gym_bdd.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
gym_bdd.to_csv(os.path.join(BDD_DIR, "gym_members_exercise_bdd.csv"), index=False)
print(f"   ✅ {len(gym_bdd)} lignes — colonnes normalisées")

# ── BDD Dataset 4 — synt ─────────────────────────────────
print("🧹 [BDD] gym_members_synthetic...")
synt_bdd = synt.copy()
synt_bdd["Max_BPM"] = pd.to_numeric(synt_bdd["Max_BPM"], errors='coerce')
synt_bdd.columns = synt_bdd.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
synt_bdd.to_csv(os.path.join(BDD_DIR, "gym_members_synthetic_bdd.csv"), index=False)
print(f"   ✅ {len(synt_bdd)} lignes — NULL conservés, Max_BPM corrigé")

# ══════════════════════════════════════════════════════════
# NETTOYAGE ML — complet + normalisation
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 50)
print("🤖 NETTOYAGE POUR LE MACHINE LEARNING")
print("=" * 50)

# ── ML Dataset 1 — food ───────────────────────────────────
print("\n🧹 [ML] daily_food_nutrition...")
food_ml = food.drop_duplicates().copy()
food_ml.columns = food_ml.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
food_ml = food_ml.dropna()

# Encodage des colonnes texte
for col in food_ml.select_dtypes(include='object').columns:
    le = LabelEncoder()
    food_ml[col] = le.fit_transform(food_ml[col].astype(str))

# Normalisation des colonnes numériques
cols_num = food_ml.select_dtypes(include=['int64', 'float64']).columns
scaler = StandardScaler()
food_ml[cols_num] = scaler.fit_transform(food_ml[cols_num])

food_ml.to_csv(os.path.join(ML_DIR, "daily_food_nutrition_ml.csv"), index=False)
print(f"   ✅ {len(food_ml)} lignes — encodage + normalisation StandardScaler")

# ── ML Dataset 2 — diet ───────────────────────────────────
print("🧹 [ML] diet_recommendations...")
diet_ml = diet.copy()
diet_ml.columns = diet_ml.columns.str.strip().str.lower().str.replace(" ", "_")
diet_ml["disease_type"]         = diet_ml["disease_type"].fillna("Non renseigné")
diet_ml["dietary_restrictions"] = diet_ml["dietary_restrictions"].fillna("Non renseigné")
diet_ml["allergies"]            = diet_ml["allergies"].fillna("Non renseigné")
diet_ml = diet_ml.dropna()

# Encodage des colonnes texte
for col in diet_ml.select_dtypes(include='object').columns:
    le = LabelEncoder()
    diet_ml[col] = le.fit_transform(diet_ml[col].astype(str))

# Normalisation des colonnes numériques
cols_num = diet_ml.select_dtypes(include=['int64', 'float64']).columns
scaler = StandardScaler()
diet_ml[cols_num] = scaler.fit_transform(diet_ml[cols_num])

diet_ml.to_csv(os.path.join(ML_DIR, "diet_recommendations_ml.csv"), index=False)
print(f"   ✅ {len(diet_ml)} lignes — encodage + normalisation StandardScaler")

# ── ML Dataset 3 — gym ────────────────────────────────────
print("🧹 [ML] gym_members_exercise...")
gym_ml = gym.copy()
gym_ml.columns = gym_ml.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
gym_ml = gym_ml.dropna()

# Encodage des colonnes texte
for col in gym_ml.select_dtypes(include='object').columns:
    le = LabelEncoder()
    gym_ml[col] = le.fit_transform(gym_ml[col].astype(str))

# Normalisation des colonnes numériques
cols_num = gym_ml.select_dtypes(include=['int64', 'float64']).columns
scaler = StandardScaler()
gym_ml[cols_num] = scaler.fit_transform(gym_ml[cols_num])

gym_ml.to_csv(os.path.join(ML_DIR, "gym_members_exercise_ml.csv"), index=False)
print(f"   ✅ {len(gym_ml)} lignes — encodage + normalisation StandardScaler")

# ── ML Dataset 4 — synt ──────────────────────────────────
print("🧹 [ML] gym_members_synthetic...")
synt_ml = synt.copy()
synt_ml["Max_BPM"] = pd.to_numeric(synt_ml["Max_BPM"], errors='coerce')
synt_ml = synt_ml.dropna()
synt_ml.columns = synt_ml.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")

# Encodage des colonnes texte
for col in synt_ml.select_dtypes(include='object').columns:
    le = LabelEncoder()
    synt_ml[col] = le.fit_transform(synt_ml[col].astype(str))

# Normalisation des colonnes numériques
cols_num = synt_ml.select_dtypes(include=['int64', 'float64']).columns
scaler = StandardScaler()
synt_ml[cols_num] = scaler.fit_transform(synt_ml[cols_num])

synt_ml.to_csv(os.path.join(ML_DIR, "gym_members_synthetic_ml.csv"), index=False)
print(f"   ✅ {len(synt_ml)} lignes — encodage + normalisation StandardScaler")

# ══════════════════════════════════════════════════════════
# RAPPORT
# ══════════════════════════════════════════════════════════
rapport_path = os.path.join(RAPPORT_DIR, "rapport_nettoyage_v2.md")

with open(rapport_path, "w", encoding="utf-8") as f:
    f.write("# Rapport de nettoyage des données\n\n")
    f.write(f"**Projet** : HealthAI Coach — Backend Métier  \n")
    f.write(f"**Généré le** : {datetime.now().strftime('%d/%m/%Y à %H:%M')}  \n\n")
    f.write("---\n\n")

    f.write("## Stratégie de nettoyage\n\n")
    f.write("| Destination | Stratégie |\n|-------------|----------|\n")
    f.write("| BDD | Suppression doublons, correction types, NULL conservés |\n")
    f.write("| Machine Learning | Suppression NULL, encodage texte, normalisation StandardScaler |\n\n")
    f.write("---\n\n")

    f.write("## Bilan BDD\n\n")
    f.write("| Dataset | Lignes | Actions |\n|---------|--------|--------|\n")
    f.write(f"| daily_food_nutrition | {len(food_bdd)} | Doublons supprimés, NULL conservés |\n")
    f.write(f"| diet_recommendations | {len(diet_bdd)} | NULL conservés |\n")
    f.write(f"| gym_members_exercise | {len(gym_bdd)} | Colonnes normalisées |\n")
    f.write(f"| gym_members_synthetic | {len(synt_bdd)} | Max_BPM corrigé, NULL conservés |\n\n")
    f.write("---\n\n")

    f.write("## Bilan Machine Learning\n\n")
    f.write("| Dataset | Lignes avant | Lignes après | Actions |\n|---------|-------------|--------------|--------|\n")
    f.write(f"| daily_food_nutrition | 645 | {len(food_ml)} | Doublons + NULL supprimés, encodage, normalisation |\n")
    f.write(f"| diet_recommendations | 1000 | {len(diet_ml)} | NULL remplis + supprimés, encodage, normalisation |\n")
    f.write(f"| gym_members_exercise | 973 | {len(gym_ml)} | NULL supprimés, encodage, normalisation |\n")
    f.write(f"| gym_members_synthetic | 1800 | {len(synt_ml)} | NULL supprimés, encodage, normalisation |\n")

print("\n📄 Rapport généré : rapport_nettoyage_v2.md")
print("\n" + "=" * 50)
print("✅ NETTOYAGE V2 TERMINÉ")
print("=" * 50)