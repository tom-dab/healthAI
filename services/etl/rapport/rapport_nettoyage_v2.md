# Rapport de nettoyage des données

**Projet** : HealthAI Coach — Backend Métier  
**Généré le** : 22/03/2026 à 17:23  

---

## Stratégie de nettoyage

| Destination | Stratégie |
|-------------|----------|
| BDD | Suppression doublons, correction types, NULL conservés |
| Machine Learning | Suppression NULL, encodage texte, normalisation StandardScaler |

---

## Bilan BDD

| Dataset | Lignes | Actions |
|---------|--------|--------|
| daily_food_nutrition | 591 | Doublons supprimés, NULL conservés |
| diet_recommendations | 1000 | NULL conservés |
| gym_members_exercise | 973 | Colonnes normalisées |
| gym_members_synthetic | 1800 | Max_BPM corrigé, NULL conservés |

---

## Bilan Machine Learning

| Dataset | Lignes avant | Lignes après | Actions |
|---------|-------------|--------------|--------|
| daily_food_nutrition | 645 | 591 | Doublons + NULL supprimés, encodage, normalisation |
| diet_recommendations | 1000 | 1000 | NULL remplis + supprimés, encodage, normalisation |
| gym_members_exercise | 973 | 973 | NULL supprimés, encodage, normalisation |
| gym_members_synthetic | 1800 | 1352 | NULL supprimés, encodage, normalisation |
