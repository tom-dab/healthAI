"""
HealthAI Coach — ETL Load
Étape 3/3 : Chargement des données nettoyées dans PostgreSQL

Sources :
  - data/clean_bdd/daily_food_nutrition_bdd.csv  → table nutrition_items
  - data/clean_bdd/gym_members_exercise_bdd.csv  → tables users + user_metrics
"""
import os
import uuid
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger

# ── Connexion BDD ───────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://healthai_user:password@postgres:5432/healthai_db"
)
BDD_DIR = os.getenv("BDD_DIR", "/app/data/clean_bdd")

engine = create_engine(DATABASE_URL, future=True)


def load_nutrition_items():
    """
    Charge daily_food_nutrition_bdd.csv dans la table nutrition_items.
    Ignore les doublons sur le nom (ON CONFLICT DO NOTHING).
    """
    path = os.path.join(BDD_DIR, "daily_food_nutrition_bdd.csv")
    if not os.path.exists(path):
        logger.warning(f"⚠️  Fichier introuvable : {path}")
        return 0

    df = pd.read_csv(path)
    logger.info(f"   📄 {len(df)} lignes à charger dans nutrition_items")

    # Mapping colonnes CSV → colonnes BDD
    # On garde uniquement les colonnes qui existent dans notre schéma
    column_map = {
        "food_item":      "name",
        "food":           "name",
        "meal_type":      "meal_type",
        "category":       "category",
        "calories_kcal":  "calories",
        "calories":       "calories",
        "protein_g":      "proteins_g",
        "proteins_g":     "proteins_g",
        "carbohydrates_g":"carbs_g",
        "carbs_g":        "carbs_g",
        "fat_g":          "fats_g",
        "fats_g":         "fats_g",
        "fiber_g":        "fiber_g",
        "sugar_g":        "sugar_g",
        "sodium_mg":      "sodium_mg",
        "cholesterol_mg": "cholesterol_mg",
        "water_ml":       "water_ml",
    }

    df = df.rename(columns=column_map)

    # S'assurer qu'une colonne "name" existe
    if "name" not in df.columns:
        logger.error("❌ Colonne 'name' introuvable dans le CSV nutrition")
        return 0

    # Colonnes cibles de la table
    target_cols = [
        "name", "category", "meal_type",
        "calories", "proteins_g", "carbs_g", "fats_g", "fiber_g",
        "sugar_g", "sodium_mg", "cholesterol_mg", "water_ml",
    ]

    # Garder uniquement les colonnes disponibles
    available = [c for c in target_cols if c in df.columns]
    df = df[available].copy()
    df["source"] = "Kaggle - Daily Food & Nutrition Dataset"
    df = df.dropna(subset=["name"])
    df = df.drop_duplicates(subset=["name"])

    loaded = 0
    with engine.connect() as conn:
        for _, row in df.iterrows():
            try:
                # Valider meal_type avec énumération
                _meal_raw = str(row.get("meal_type", "")).strip().lower() if pd.notna(row.get("meal_type")) else None
                _valid_meals = ["breakfast", "lunch", "dinner", "snack"]

                conn.execute(text("""
                    INSERT INTO nutrition_items (id, name, category, meal_type,
                        calories, proteins_g, carbs_g, fats_g, fiber_g,
                        sugar_g, sodium_mg, cholesterol_mg, water_ml, source)
                    VALUES (:id, :name, :category, :meal_type,
                        :calories, :proteins_g, :carbs_g, :fats_g, :fiber_g,
                        :sugar_g, :sodium_mg, :cholesterol_mg, :water_ml, :source)
                    ON CONFLICT DO NOTHING
                """), {
                    "id":            str(uuid.uuid4()),
                    "name":          str(row.get("name", ""))[:255],
                    "category":      str(row.get("category", ""))[:100] if pd.notna(row.get("category")) else None,
                    "meal_type":     _meal_raw if _meal_raw in _valid_meals else None,
                    "calories":      float(row["calories"])      if "calories"      in row and pd.notna(row["calories"])      else 0,
                    "proteins_g":    float(row["proteins_g"])    if "proteins_g"    in row and pd.notna(row["proteins_g"])    else 0,
                    "carbs_g":       float(row["carbs_g"])       if "carbs_g"       in row and pd.notna(row["carbs_g"])       else 0,
                    "fats_g":        float(row["fats_g"])        if "fats_g"        in row and pd.notna(row["fats_g"])        else 0,
                    "fiber_g":       float(row["fiber_g"])       if "fiber_g"       in row and pd.notna(row["fiber_g"])       else 0,
                    "sugar_g":       float(row["sugar_g"])       if "sugar_g"       in row and pd.notna(row["sugar_g"])       else 0,
                    "sodium_mg":     float(row["sodium_mg"])     if "sodium_mg"     in row and pd.notna(row["sodium_mg"])     else 0,
                    "cholesterol_mg":float(row["cholesterol_mg"])if "cholesterol_mg"in row and pd.notna(row["cholesterol_mg"])else 0,
                    "water_ml":      float(row["water_ml"])      if "water_ml"      in row and pd.notna(row["water_ml"])      else 0,
                    "source":        "Kaggle - Daily Food & Nutrition Dataset",
                })
                loaded += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Ligne ignorée : {e}")
        conn.commit()

    logger.success(f"   ✅ {loaded} aliments chargés dans nutrition_items")
    return loaded


def load_users_and_metrics():
    """
    Charge gym_members_exercise_bdd.csv dans les tables users + user_metrics.
    Crée des utilisateurs fictifs avec des emails générés automatiquement.
    """
    path = os.path.join(BDD_DIR, "gym_members_exercise_bdd.csv")
    if not os.path.exists(path):
        logger.warning(f"⚠️  Fichier introuvable : {path}")
        return 0

    df = pd.read_csv(path)
    logger.info(f"   📄 {len(df)} lignes à charger dans users + user_metrics")

    # Mapping niveau d'expérience → fitness_level
    level_map = {1: "beginner", 2: "intermediate", 3: "advanced"}

    loaded = 0
    with engine.connect() as conn:
        for i, row in df.iterrows():
            user_id = str(uuid.uuid4())
            try:
                # Déterminer le genre
                gender_raw = str(row.get("gender", "")).strip().lower()
                gender = "male" if gender_raw in ["male", "m", "homme"] else \
                         "female" if gender_raw in ["female", "f", "femme"] else "other"

                # Niveau fitness
                exp = row.get("experience_level", 1)
                fitness_level = level_map.get(int(exp) if pd.notna(exp) else 1, "beginner")

                # Insérer user fictif
                conn.execute(text("""
                    INSERT INTO users (
                        id, email, username, password_hash,
                        age, gender, height_cm, weight_kg,
                        fitness_level, water_intake_liters, workout_frequency,
                        goal, plan, role
                    ) VALUES (
                        :id, :email, :username, :password_hash,
                        :age, :gender, :height_cm, :weight_kg,
                        :fitness_level, :water_intake_liters, :workout_frequency,
                        :goal, :plan, :role
                    ) ON CONFLICT DO NOTHING
                """), {
                    "id":                   user_id,
                    "email":                f"user_{i}_{user_id[:8]}@healthai.local",
                    "username":             f"user_{i}",
                    "password_hash":        "etl_import_no_login",
                    "age":                  int(row["age"])        if "age"        in row and pd.notna(row["age"])        else None,
                    "gender":               gender,
                    "height_cm":            float(row["height_m"]) * 100 if "height_m" in row and pd.notna(row["height_m"]) else None,
                    "weight_kg":            float(row["weight_kg"]) if "weight_kg" in row and pd.notna(row["weight_kg"]) else None,
                    "fitness_level":        fitness_level,
                    "water_intake_liters":  float(row["water_intake_liters"]) if "water_intake_liters" in row and pd.notna(row.get("water_intake_liters")) else None,
                    "workout_frequency":    int(row["workout_frequency_days/week"]) if "workout_frequency_days/week" in row and pd.notna(row.get("workout_frequency_days/week")) else None,
                    "goal":                 "general_health",
                    "plan":                 "free",
                    "role":                 "user",
                })

                # Insérer métriques biométriques
                conn.execute(text("""
                    INSERT INTO user_metrics (
                        id, user_id,
                        weight_kg, bmi, body_fat_pct,
                        heart_rate_avg, heart_rate_max, heart_rate_rest,
                        calories_burned
                    ) VALUES (
                        :id, :user_id,
                        :weight_kg, :bmi, :body_fat_pct,
                        :heart_rate_avg, :heart_rate_max, :heart_rate_rest,
                        :calories_burned
                    )
                """), {
                    "id":              str(uuid.uuid4()),
                    "user_id":         user_id,
                    "weight_kg":       float(row["weight_kg"])       if "weight_kg"       in row and pd.notna(row["weight_kg"])       else None,
                    "bmi":             float(row["bmi"])              if "bmi"              in row and pd.notna(row["bmi"])              else None,
                    "body_fat_pct":    float(row["fat_percentage"])   if "fat_percentage"   in row and pd.notna(row["fat_percentage"])   else None,
                    "heart_rate_avg":  int(row["avg_bpm"])            if "avg_bpm"          in row and pd.notna(row["avg_bpm"])          else None,
                    "heart_rate_max":  int(row["max_bpm"])            if "max_bpm"          in row and pd.notna(row["max_bpm"])          else None,
                    "heart_rate_rest": int(row["resting_bpm"])        if "resting_bpm"      in row and pd.notna(row["resting_bpm"])      else None,
                    "calories_burned": float(row["calories_burned"])  if "calories_burned"  in row and pd.notna(row["calories_burned"])  else None,
                })

                loaded += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Ligne {i} ignorée : {e}")

        conn.commit()

    logger.success(f"   ✅ {loaded} utilisateurs + métriques chargés")
    return loaded


if __name__ == "__main__":
    logger.info("🗄️  Démarrage du chargement BDD...")
    n1 = load_nutrition_items()
    n2 = load_users_and_metrics()
    logger.success(f"✅ Load terminé — {n1} aliments, {n2} utilisateurs insérés")
