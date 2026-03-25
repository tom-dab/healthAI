# Rapport de nettoyage des données

**Projet** : HealthAI Coach — Backend Métier  
**Généré le** : 22/03/2026 à 16:05  

---

## daily_food_nutrition

| Action | Détail |
|--------|--------|
| Doublons supprimés | 54 lignes |
| Lignes avant | 645 |
| Lignes après | 591 |
| Fichier produit | `daily_food_nutrition_clean.csv` |

## diet_recommendations

| Action | Détail |
|--------|--------|
| Valeurs manquantes traitées | 861 cellules → 'Non renseigné' |
| Colonnes concernées | Disease_Type, Dietary_Restrictions, Allergies |
| Lignes conservées | 1000 |
| Fichier produit | `diet_recommendations_clean.csv` |

## gym_members_exercise

| Action | Détail |
|--------|--------|
| Normalisation colonnes | Espaces, majuscules, parenthèses supprimés |
| Lignes conservées | 973 |
| Fichier produit | `gym_members_exercise_clean.csv` |



---

## Bilan global

| Dataset | Lignes avant | Lignes après | Taux de rétention |
|---------|-------------|--------------|-------------------|
| daily_food_nutrition | 645 | 591 | 91.6% |
| diet_recommendations | 1000 | 1000 | 100% |
| gym_members_exercise | 973 | 973 | 100% |
| gym_members_synthetic | 1800 | 1352 | 75.1% |
## gym_members_synthetic

| Action | Détail |
|--------|--------|
| Correction type | Max_BPM converti str → float64 |
| Lignes supprimées | 448 lignes incomplètes |
| Lignes avant | 1800 |
| Lignes après | 1352 |
| Fichier produit | `gym_members_synthetic_clean.csv` |
