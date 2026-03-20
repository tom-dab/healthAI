-- ════════════════════════════════════════════════
-- HealthAI Coach — Migration initiale
-- Version : V1__init_schema.sql
-- Responsable : Hanane
-- ════════════════════════════════════════════════
-- Ce script est exécuté automatiquement au premier
-- démarrage du container PostgreSQL
-- ════════════════════════════════════════════════

-- Extension pour les UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────
-- TABLE : users (profils utilisateurs)
-- ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    username      VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,

    -- Données démographiques
    age           INTEGER CHECK (age > 0 AND age < 120),
    gender        VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    height_cm     NUMERIC(5,2) CHECK (height_cm > 0),
    weight_kg     NUMERIC(5,2) CHECK (weight_kg > 0),

    -- Objectifs
    goal          VARCHAR(50) CHECK (goal IN (
                      'weight_loss', 'muscle_gain',
                      'sleep_improvement', 'maintenance', 'general_health'
                  )),

    -- Abonnement
    plan          VARCHAR(20) DEFAULT 'free' CHECK (plan IN ('free', 'premium', 'premium_plus')),

    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────
-- TABLE : nutrition_items (base nutritionnelle)
-- ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS nutrition_items (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name          VARCHAR(255) NOT NULL,
    category      VARCHAR(100),

    -- Macronutriments (pour 100g)
    calories      NUMERIC(7,2),
    proteins_g    NUMERIC(7,2),
    carbs_g       NUMERIC(7,2),
    fats_g        NUMERIC(7,2),
    fiber_g       NUMERIC(7,2),

    -- Source de la donnée
    source        VARCHAR(100),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────
-- TABLE : exercises (catalogue d'exercices)
-- ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS exercises (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name          VARCHAR(255) NOT NULL,
    type          VARCHAR(50),
    muscle_group  VARCHAR(100),
    equipment     VARCHAR(100),
    difficulty    VARCHAR(20) CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    instructions  TEXT,

    -- Source de la donnée (ExerciseDB)
    external_id   VARCHAR(100),
    source        VARCHAR(100),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────
-- TABLE : user_metrics (métriques biométriques)
-- ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_metrics (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Biométrie
    weight_kg       NUMERIC(5,2),
    body_fat_pct    NUMERIC(5,2),
    bmi             NUMERIC(5,2),

    -- Activité
    steps           INTEGER,
    active_minutes  INTEGER,
    calories_burned NUMERIC(7,2),

    -- Sommeil
    sleep_hours     NUMERIC(4,2),

    -- Cardio
    heart_rate_avg  INTEGER,
    heart_rate_max  INTEGER
);

-- ─────────────────────────────────────────────────
-- TABLE : food_logs (journaux alimentaires)
-- ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS food_logs (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nutrition_item_id UUID NOT NULL REFERENCES nutrition_items(id),
    quantity_g        NUMERIC(7,2) NOT NULL,
    meal_type         VARCHAR(20) CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    logged_at         TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────
-- TABLE : workout_logs (journaux d'entraînement)
-- ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS workout_logs (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id  UUID NOT NULL REFERENCES exercises(id),
    duration_min INTEGER,
    sets         INTEGER,
    reps         INTEGER,
    logged_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────
-- INDEX (performances de requête)
-- ─────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_user_metrics_user_id ON user_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_metrics_recorded_at ON user_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_food_logs_user_id ON food_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_food_logs_logged_at ON food_logs(logged_at);
CREATE INDEX IF NOT EXISTS idx_workout_logs_user_id ON workout_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_workout_logs_logged_at ON workout_logs(logged_at);

-- ─────────────────────────────────────────────────
-- TRIGGER : mise à jour automatique de updated_at
-- ─────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
