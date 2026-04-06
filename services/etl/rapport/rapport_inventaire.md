# Rapport d'inventaire des sources de données

**Projet** : HealthAI Coach — Backend Métier  
**Généré le** : 06/04/2026 à 08:46  

---

## daily_food_nutrition

| Propriété | Valeur |
|-----------|--------|
| Fichier   | `daily_food_nutrition_dataset.csv` |
| Statut    | OK |
| Lignes    | 645 |
| Colonnes  | 12 |
| Doublons  | 54 |

✅ Aucune valeur manquante

**Types des colonnes :**

- `Food_Item` : object
- `Category` : object
- `Calories (kcal)` : int64
- `Protein (g)` : float64
- `Carbohydrates (g)` : float64
- `Fat (g)` : float64
- `Fiber (g)` : float64
- `Sugars (g)` : float64
- `Sodium (mg)` : int64
- `Cholesterol (mg)` : int64
- `Meal_Type` : object
- `Water_Intake (ml)` : int64

---

## diet_recommendations

| Propriété | Valeur |
|-----------|--------|
| Fichier   | `diet_recommendations_dataset.csv` |
| Statut    | OK |
| Lignes    | 1000 |
| Colonnes  | 20 |
| Doublons  | 0 |

**Valeurs manquantes :**

- `Disease_Type` : 204 valeurs manquantes
- `Dietary_Restrictions` : 334 valeurs manquantes
- `Allergies` : 323 valeurs manquantes

**Types des colonnes :**

- `Patient_ID` : object
- `Age` : int64
- `Gender` : object
- `Weight_kg` : float64
- `Height_cm` : int64
- `BMI` : float64
- `Disease_Type` : object
- `Severity` : object
- `Physical_Activity_Level` : object
- `Daily_Caloric_Intake` : int64
- `Cholesterol_mg/dL` : float64
- `Blood_Pressure_mmHg` : int64
- `Glucose_mg/dL` : float64
- `Dietary_Restrictions` : object
- `Allergies` : object
- `Preferred_Cuisine` : object
- `Weekly_Exercise_Hours` : float64
- `Adherence_to_Diet_Plan` : float64
- `Dietary_Nutrient_Imbalance_Score` : float64
- `Diet_Recommendation` : object

---

## gym_members_exercise

| Propriété | Valeur |
|-----------|--------|
| Fichier   | `gym_members_exercise_tracking.csv` |
| Statut    | OK |
| Lignes    | 973 |
| Colonnes  | 15 |
| Doublons  | 0 |

✅ Aucune valeur manquante

**Types des colonnes :**

- `Age` : int64
- `Gender` : object
- `Weight (kg)` : float64
- `Height (m)` : float64
- `Max_BPM` : int64
- `Avg_BPM` : int64
- `Resting_BPM` : int64
- `Session_Duration (hours)` : float64
- `Calories_Burned` : float64
- `Workout_Type` : object
- `Fat_Percentage` : float64
- `Water_Intake (liters)` : float64
- `Workout_Frequency (days/week)` : int64
- `Experience_Level` : int64
- `BMI` : float64

---

## gym_members_synthetic

| Propriété | Valeur |
|-----------|--------|
| Fichier   | `gym_members_exercise_tracking_synthetic_data.csv` |
| Statut    | OK |
| Lignes    | 1800 |
| Colonnes  | 15 |
| Doublons  | 0 |

**Valeurs manquantes :**

- `Age` : 10 valeurs manquantes
- `Gender` : 71 valeurs manquantes
- `Weight (kg)` : 22 valeurs manquantes
- `Height (m)` : 26 valeurs manquantes
- `Max_BPM` : 21 valeurs manquantes
- `Avg_BPM` : 30 valeurs manquantes
- `Resting_BPM` : 19 valeurs manquantes
- `Session_Duration (hours)` : 23 valeurs manquantes
- `Calories_Burned` : 23 valeurs manquantes
- `Workout_Type` : 61 valeurs manquantes
- `Fat_Percentage` : 16 valeurs manquantes
- `Water_Intake (liters)` : 24 valeurs manquantes
- `Workout_Frequency (days/week)` : 58 valeurs manquantes
- `Experience_Level` : 57 valeurs manquantes
- `BMI` : 30 valeurs manquantes

**Types des colonnes :**

- `Age` : float64
- `Gender` : object
- `Weight (kg)` : float64
- `Height (m)` : float64
- `Max_BPM` : object
- `Avg_BPM` : float64
- `Resting_BPM` : float64
- `Session_Duration (hours)` : float64
- `Calories_Burned` : float64
- `Workout_Type` : object
- `Fat_Percentage` : float64
- `Water_Intake (liters)` : float64
- `Workout_Frequency (days/week)` : float64
- `Experience_Level` : float64
- `BMI` : float64

---

