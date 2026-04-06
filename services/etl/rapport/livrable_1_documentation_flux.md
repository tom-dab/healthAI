# Livrable 1 — Documentation des données et flux

**Projet** : HealthAI Coach — Backend Métier  
**Équipe** : ETL & Data Visualization  
**Date** : 06/04/2026  
**Version** : 1.0  

---

# PARTIE 1 — Rapport d'inventaire des sources de données

## Contexte

HealthAI Coach centralise des données provenant de sources hétérogènes
pour alimenter sa plateforme de santé connectée. Dans le cadre de ce
projet, quatre datasets open data issus de Kaggle ont été sélectionnés
pour couvrir les deux domaines principaux de la plateforme : la nutrition
et l'activité physique.

## Stratégie d'acquisition

Quatre datasets ont été intégrés dans le pipeline ETL, au-delà du minimum
de deux requis par le cahier des charges. Ce choix répond à une logique
d'anticipation : l'ensemble des datasets est nettoyé et chargé en base de
données dès maintenant, de sorte que si l'équipe data science ou produit
a besoin de toutes les données dans un futur proche, aucune migration
supplémentaire ne sera nécessaire.

Le pipeline produit deux versions des données nettoyées :
- **clean_bdd/** : données nettoyées pour alimenter la base PostgreSQL,
  livrable principal de cette mission.
- **clean_ml/** : données encodées et normalisées, produite de manière
  optionnelle pour anticiper les futurs travaux de machine learning.
  Cette couche ne fait pas partie du périmètre demandé dans le cahier
  des charges mais constitue une valeur ajoutée pour les équipes data
  science à venir.

Le pipeline est extensible : l'ajout d'une nouvelle source ne nécessite
qu'une ligne supplémentaire dans le dictionnaire DATASETS de ingestion.py.

---

## Source 1 — Daily Food & Nutrition Dataset

| Propriété | Valeur |
|-----------|--------|
| Fichier | `daily_food_nutrition_dataset.csv` |
| Source | Kaggle — adilshamim8 |
| URL | https://www.kaggle.com/datasets/adilshamim8/daily-food-and-nutrition-dataset |
| Format | CSV |
| Lignes | 645 |
| Colonnes | 12 |
| Doublons détectés | 54 — supprimés |
| Valeurs manquantes | Aucune |
| Fréquence de mise à jour | Statique — rechargement manuel si nouvelle version |

**Colonnes disponibles :**

| Colonne | Type | Description |
|---------|------|-------------|
| Food_Item | str | Nom de l'aliment |
| Category | str | Catégorie alimentaire |
| Calories (kcal) | int64 | Apport calorique |
| Protein (g) | float64 | Teneur en protéines |
| Carbohydrates (g) | float64 | Teneur en glucides |
| Fat (g) | float64 | Teneur en lipides |
| Fiber (g) | float64 | Teneur en fibres |
| Sugars (g) | float64 | Teneur en sucres |
| Sodium (mg) | int64 | Teneur en sodium |
| Cholesterol (mg) | int64 | Teneur en cholestérol |
| Meal_Type | str | Type de repas |
| Water_Intake (ml) | int64 | Consommation d'eau |

**Justification du choix** : Ce dataset fournit des apports nutritionnels
quotidiens détaillés. Il constitue la base de la fonctionnalité de suivi
alimentaire de HealthAI Coach et alimentera les futures recommandations
nutritionnelles par IA.

**Règles de qualité appliquées :**
- 54 doublons supprimés (645 → 591 lignes propres)
- Normalisation des noms de colonnes (minuscules, underscores,
  parenthèses supprimées)
- Valeurs NULL conservées pour la BDD
- Encodage LabelEncoder + normalisation StandardScaler pour le ML (optionnel)

---

## Source 2 — Diet Recommendations Dataset

| Propriété | Valeur |
|-----------|--------|
| Fichier | `diet_recommendations_dataset.csv` |
| Source | Kaggle — ziya07 |
| URL | https://www.kaggle.com/datasets/ziya07/diet-recommendations-dataset |
| Format | CSV |
| Lignes | 1000 |
| Colonnes | 20 |
| Doublons détectés | 0 |
| Valeurs manquantes | 861 sur 3 colonnes |
| Fréquence de mise à jour | Statique — rechargement manuel si nouvelle version |

**Colonnes disponibles :**

| Colonne | Type | Description |
|---------|------|-------------|
| Patient_ID | str | Identifiant patient |
| Age | int64 | Âge |
| Gender | str | Genre |
| Weight_kg | float64 | Poids en kg |
| Height_cm | int64 | Taille en cm |
| BMI | float64 | Indice de masse corporelle |
| Disease_Type | str | Type de maladie |
| Severity | str | Sévérité |
| Physical_Activity_Level | str | Niveau d'activité physique |
| Daily_Caloric_Intake | int64 | Apport calorique journalier |
| Cholesterol_mg/dL | float64 | Taux de cholestérol |
| Blood_Pressure_mmHg | int64 | Tension artérielle |
| Glucose_mg/dL | float64 | Taux de glucose |
| Dietary_Restrictions | str | Restrictions alimentaires |
| Allergies | str | Allergies |
| Preferred_Cuisine | str | Cuisine préférée |
| Weekly_Exercise_Hours | float64 | Heures d'exercice hebdomadaires |
| Adherence_to_Diet_Plan | float64 | Adhérence au plan diététique |
| Dietary_Nutrient_Imbalance_Score | float64 | Score déséquilibre nutritionnel |
| Diet_Recommendation | str | Recommandation diététique |

**Valeurs manquantes détectées :**

| Colonne | Valeurs manquantes | Taux | Traitement |
|---------|-------------------|------|------------|
| Disease_Type | 204 | 20,4% | Remplacé par "Non renseigné" |
| Dietary_Restrictions | 334 | 33,4% | Remplacé par "Non renseigné" |
| Allergies | 323 | 32,3% | Remplacé par "Non renseigné" |

**Justification du choix** : Enrichit la dimension nutrition avec des
profils de santé (maladies, allergies, restrictions alimentaires).
Directement aligné avec l'offre Premium de HealthAI Coach qui propose
des plans nutritionnels personnalisés.

**Règles de qualité appliquées :**
- Valeurs manquantes critiques remplacées par "Non renseigné"
- Normalisation des noms de colonnes
- NULL résiduels conservés pour la BDD
- Encodage LabelEncoder + normalisation StandardScaler pour le ML (optionnel)

---

## Source 3 — Gym Members Exercise Dataset

| Propriété | Valeur |
|-----------|--------|
| Fichier | `gym_members_exercise_tracking.csv` |
| Source | Kaggle — valakhorasani |
| URL | https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset |
| Format | CSV |
| Lignes | 973 |
| Colonnes | 15 |
| Doublons détectés | 0 |
| Valeurs manquantes | Aucune |
| Fréquence de mise à jour | Statique — rechargement manuel si nouvelle version |

**Colonnes disponibles :**

| Colonne | Type | Description |
|---------|------|-------------|
| Age | int64 | Âge du membre |
| Gender | str | Genre |
| Weight (kg) | float64 | Poids en kg |
| Height (m) | float64 | Taille en m |
| Max_BPM | int64 | Fréquence cardiaque maximale |
| Avg_BPM | int64 | Fréquence cardiaque moyenne |
| Resting_BPM | int64 | Fréquence cardiaque au repos |
| Session_Duration (hours) | float64 | Durée de séance en heures |
| Calories_Burned | float64 | Calories brûlées |
| Workout_Type | str | Type d'entraînement |
| Fat_Percentage | float64 | Pourcentage de graisse corporelle |
| Water_Intake (liters) | float64 | Consommation d'eau en litres |
| Workout_Frequency (days/week) | int64 | Fréquence d'entraînement |
| Experience_Level | int64 | Niveau d'expérience (1-3) |
| BMI | float64 | Indice de masse corporelle |

**Justification du choix** : Dataset le plus complet pour le suivi
d'activité physique. Aucune valeur manquante, données directement
exploitables. Correspond exactement aux métriques de performance
attendues dans le cahier des charges (BPM, calories, BMI, fréquence
d'entraînement).

**Règles de qualité appliquées :**
- Normalisation des noms de colonnes
- Aucun traitement supplémentaire nécessaire
- Encodage LabelEncoder + normalisation StandardScaler pour le ML (optionnel)

---

## Source 4 — Gym Members Exercise Synthetic Dataset

| Propriété | Valeur |
|-----------|--------|
| Fichier | `gym_members_exercise_tracking_synthetic_data.csv` |
| Source | Dataset synthétique complémentaire |
| Format | CSV |
| Lignes | 1800 |
| Colonnes | 15 |
| Doublons détectés | 0 |
| Valeurs manquantes | 481 sur 15 colonnes |
| Fréquence de mise à jour | Statique — rechargement manuel si nouvelle version |

**Valeurs manquantes détectées :**

| Colonne | Valeurs manquantes | Traitement BDD |
|---------|-------------------|----------------|
| Age | 10 | NULL conservé |
| Gender | 71 | NULL conservé |
| Weight (kg) | 22 | NULL conservé |
| Height (m) | 26 | NULL conservé |
| Max_BPM | 21 | Correction type + NULL conservé |
| Avg_BPM | 30 | NULL conservé |
| Resting_BPM | 19 | NULL conservé |
| Session_Duration (hours) | 23 | NULL conservé |
| Calories_Burned | 23 | NULL conservé |
| Workout_Type | 61 | NULL conservé |
| Fat_Percentage | 16 | NULL conservé |
| Water_Intake (liters) | 24 | NULL conservé |
| Workout_Frequency (days/week) | 58 | NULL conservé |
| Experience_Level | 57 | NULL conservé |
| BMI | 30 | NULL conservé |

**Anomalie détectée** : Colonne Max_BPM de type str au lieu de float64.
Corrigée automatiquement par le pipeline via pd.to_numeric(errors='coerce').

**Justification du choix** : Ajouté pour augmenter le volume de données
disponibles et tester la robustesse du pipeline sur des données imparfaites.
Permet de simuler une croissance de la base utilisateurs, cohérente avec
les ambitions de scaling de HealthAI Coach.

**Règles de qualité appliquées :**
- Correction du type Max_BPM (str → float64)
- Normalisation des noms de colonnes
- NULL conservés pour la BDD
- Suppression NULL + encodage + normalisation StandardScaler pour le ML (optionnel)

---

## Bilan global

| Dataset | Lignes brutes | Lignes clean_bdd | Lignes clean_ml | Doublons | Manquants |
|---------|--------------|-----------------|----------------|----------|-----------|
| daily_food_nutrition | 645 | 591 | 591 | 54 | 0 |
| diet_recommendations | 1000 | 1000 | 1000 | 0 | 861 |
| gym_members_exercise | 973 | 973 | 973 | 0 | 0 |
| gym_members_synthetic | 1800 | 1800 | 1352 | 0 | 481 |
| **TOTAL** | **4418** | **4364** | **3916** | **54** | **1342** |

---

# PARTIE 2 — Diagramme des flux de données

## Flux complet ETL

┌──────────────────────────────────────────────────────┐
│                  SOURCES BRUTES (data/raw/)           │
│                                                      │
│  daily_food_nutrition_dataset.csv       ~645 lignes  │
│  diet_recommendations_dataset.csv      ~1000 lignes  │
│  gym_members_exercise_tracking.csv      ~973 lignes  │
│  gym_members_exercise_synthetic.csv    ~1800 lignes  │
└───────────────────────────┬──────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────┐
│              ÉTAPE 1 — EXTRACT                       │
│              ingestion.py                            │
│                                                      │
│  - Chargement des 4 CSV bruts                        │
│  - Analyse structure (lignes, colonnes, types)       │
│  - Détection et comptage des doublons                │
│  - Détection des valeurs manquantes par colonne      │
│  - Génération automatique rapport_inventaire.md      │
└───────────────────────────┬──────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────┐
│              ÉTAPE 2 — TRANSFORM                     │
│              nettoyage_v2.py                         │
│                                                      │
│  - Normalisation noms de colonnes                    │
│  - Correction des types (Max_BPM)                    │
│  - Suppression des doublons                          │
│  - Traitement des valeurs manquantes                 │
│  - Encodage LabelEncoder (ML uniquement)             │
│  - Normalisation StandardScaler (ML uniquement)      │
│  - Génération rapport_nettoyage_v2.md                │
└──────────────┬────────────────────────┬──────────────┘
│                        │
▼                        ▼
┌─────────────────────┐    ┌───────────────────────────┐
│   data/clean_bdd/   │    │      data/clean_ml/        │
│                     │    │                           │
│  4 CSV nettoyés     │    │  4 CSV encodés            │
│  NULL conservés     │    │  NULL supprimés           │
│  Types corrigés     │    │  Normalisés StandardScaler│
└────────┬────────────┘    └──────────────┬────────────┘
│                                
▼                               
┌─────────────────────┐    
│  ÉTAPE 3 — LOAD     │    
└────────┬────────────┘    
│                     │  
│  Migration BDD MySQL          
│  (équipe backend)   │    
│                     │    
│
▼
