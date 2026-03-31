const express = require("express");
const pool    = require("./db");
const {
    insertarFoods,
    insertarUsers,
    insertarUserGoals,
    insertarActivity,
    insertarNutritionLogs,
    verificationFinale
} = require("./service");
const initDB = require("./init_db");

const app  = express();
const PORT = 3000;

// ── Démarrage sécurisé : BDD prête avant d'accepter des requêtes ──
async function demarrer() {
    try {
        await initDB();
        app.listen(PORT, () => {
            console.log(`\n Serveur démarré sur http://localhost:${PORT}`);
            console.log(` Pour charger les données : http://localhost:${PORT}/charger-donnees`);
        });
    } catch (error) {
        console.error(" Impossible de démarrer le serveur :", error.message);
        process.exit(1);
    }
}

// ── Endpoint racine ───────────────────────────────────────────
app.get("/", (req, res) => {
    res.send("HealthAI Coach Backend actif ");
});

// ── Endpoint principal : charge TOUS les CSV en BDD ──────────
app.get("/charger-donnees", async (req, res) => {
    try {
        console.log("\n========================================");
        console.log("  HealthAI Coach — Pipeline ETL démarré");
        console.log("========================================\n");

        const CSV_FOODS    = "./data/daily_food_nutrition_bdd.csv";
        const CSV_EXERCISE = "./data/gym_members_exercise_bdd.csv";
        const CSV_SYNTH    = "./data/gym_members_synthetic_bdd.csv";
        const CSV_DIET     = "./data/diet_recommendations_bdd.csv";

        console.log(" ÉTAPE 1/5 — foods");
        await insertarFoods(CSV_FOODS);

        console.log("\n ÉTAPE 2/5 — users + biometrics (exercise + synthetic)");
        await insertarUsers(CSV_EXERCISE, CSV_SYNTH);

        console.log("\n ÉTAPE 3/5 — health_profiles + user_goals");
        await insertarUserGoals(CSV_DIET);

        console.log("\n ÉTAPE 4/5 — exercises + activity_logs");
        await insertarActivity(CSV_EXERCISE, CSV_SYNTH);

        console.log("\n ÉTAPE 5/5 — nutrition_logs");
        await insertarNutritionLogs(CSV_FOODS);

        await verificationFinale();

        console.log("\n Pipeline ETL terminé avec succès !");

        res.json({
            status:  "success",
            message: "Toutes les données ont été insérées dans MariaDB",
            tables:  ["users", "biometrics", "foods", "health_profiles", "user_goals", "exercises", "activity_logs", "nutrition_logs"]
        });

    } catch (error) {
        console.error(" Erreur ETL :", error);
        res.status(500).json({ status: "error", message: error.message });
    }
});

// ── Endpoints de consultation de base ────────────────────────
app.get("/users", async (req, res) => {
    const [rows] = await pool.query("SELECT * FROM users LIMIT 50");
    res.json(rows);
});

app.get("/foods", async (req, res) => {
    const [rows] = await pool.query("SELECT * FROM foods LIMIT 50");
    res.json(rows);
});

app.get("/biometrics", async (req, res) => {
    const [rows] = await pool.query("SELECT * FROM biometrics LIMIT 50");
    res.json(rows);
});

// ── Endpoints nouveaux ────────────────────────────────────────

// Profil complet d'un utilisateur
app.get("/users/:id/profile", async (req, res) => {
    try {
        const id = req.params.id;
        const [[user]]    = await pool.query("SELECT * FROM users WHERE id = ?", [id]);
        const [[bio]]     = await pool.query("SELECT * FROM biometrics WHERE user_id = ? ORDER BY date_mesure DESC LIMIT 1", [id]);
        const [[health]]  = await pool.query("SELECT * FROM health_profiles WHERE user_id = ? LIMIT 1", [id]);
        const [[goal]]    = await pool.query("SELECT * FROM user_goals WHERE user_id = ? ORDER BY id DESC LIMIT 1", [id]);
        if (!user) return res.status(404).json({ error: "Utilisateur non trouvé" });
        res.json({ user, biometrics: bio || null, health_profile: health || null, goal: goal || null });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Profils de santé
app.get("/health-profiles", async (req, res) => {
    const [rows] = await pool.query("SELECT * FROM health_profiles LIMIT 50");
    res.json(rows);
});

// Statistiques par maladie
app.get("/stats/diseases", async (req, res) => {
    const [rows] = await pool.query(`
        SELECT disease_type, COUNT(*) AS total,
               ROUND(AVG(cholesterol_mg_dl), 1) AS chol_moy,
               ROUND(AVG(glucose_mg_dl), 1)     AS glucose_moy,
               ROUND(AVG(adherence_to_diet_plan), 1) AS adherence_moy
        FROM health_profiles
        GROUP BY disease_type
        ORDER BY total DESC
    `);
    res.json(rows);
});

// Statistiques par recommandation alimentaire
app.get("/stats/diet-recommendations", async (req, res) => {
    const [rows] = await pool.query(`
        SELECT diet_recommendation, COUNT(*) AS total,
               ROUND(AVG(weekly_exercise_hours), 1) AS exercise_moy,
               ROUND(AVG(daily_caloric_intake), 0)  AS calories_moy
        FROM health_profiles
        JOIN user_goals ON health_profiles.user_id = user_goals.user_id
        GROUP BY diet_recommendation
        ORDER BY total DESC
    `);
    res.json(rows);
});

// Dashboard KPIs enrichis
app.get("/dashboard/kpis", async (req, res) => {
    const [[kpis]] = await pool.query(`
        SELECT
            (SELECT COUNT(*) FROM users)                                        AS total_users,
            (SELECT COUNT(*) FROM activity_logs)                                AS total_seances,
            (SELECT ROUND(AVG(calories_brulees), 0) FROM activity_logs)         AS calories_moy,
            (SELECT ROUND(AVG(bmi), 1)              FROM biometrics)            AS bmi_moyen,
            (SELECT COUNT(*) FROM nutrition_logs)                               AS total_repas,
            (SELECT COUNT(*) FROM health_profiles)                              AS total_profils_sante,
            (SELECT ROUND(AVG(cholesterol_mg_dl), 1) FROM health_profiles)      AS chol_moyen,
            (SELECT ROUND(AVG(adherence_to_diet_plan), 1) FROM health_profiles) AS adherence_moy,
            (SELECT ROUND(AVG(water_intake_liters), 2) FROM users)              AS water_intake_moy
    `);
    res.json(kpis);
});

// Top aliments par calories
app.get("/foods/top-calories", async (req, res) => {
    const [rows] = await pool.query(`
        SELECT nom, categorie, calories_kcal, type_repas
        FROM foods ORDER BY calories_kcal DESC LIMIT 20
    `);
    res.json(rows);
});

// Aliments par type de repas
app.get("/foods/by-meal/:type", async (req, res) => {
    const typeMap = {
        breakfast: "petit_dejeuner", lunch: "dejeuner",
        dinner: "diner", snack: "collation"
    };
    const repas = typeMap[req.params.type] || req.params.type;
    const [rows] = await pool.query(
        "SELECT * FROM foods WHERE type_repas = ? LIMIT 50", [repas]
    );
    res.json(rows);
});

// ── Lancement ─────────────────────────────────────────────────
demarrer();
