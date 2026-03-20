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
            console.log(`\n🚀 Serveur démarré sur http://localhost:${PORT}`);
            console.log(`👉 Pour charger les données : http://localhost:${PORT}/charger-donnees`);
        });
    } catch (error) {
        console.error("❌ Impossible de démarrer le serveur :", error.message);
        process.exit(1);
    }
}

// ── Endpoint racine ───────────────────────────────────────────
app.get("/", (req, res) => {
    res.send("HealthAI Coach Backend actif ✅");
});

// ── Endpoint principal : charge TOUS les CSV en BDD ──────────
app.get("/charger-donnees", async (req, res) => {
    try {
        console.log("\n========================================");
        console.log("  HealthAI Coach — Pipeline ETL démarré");
        console.log("========================================\n");

        console.log("📥 ÉTAPE 1/5 — foods");
        await insertarFoods("./data/daily_food_nutrition_clean.csv");

        console.log("\n📥 ÉTAPE 2/5 — users + biometrics");
        await insertarUsers("./data/gym_members_exercise_clean.csv");

        console.log("\n📥 ÉTAPE 3/5 — user_goals");
        await insertarUserGoals("./data/diet_recommendations_clean.csv");

        console.log("\n📥 ÉTAPE 4/5 — exercises + activity_logs");
        await insertarActivity("./data/gym_members_exercise_clean.csv");

        console.log("\n📥 ÉTAPE 5/5 — nutrition_logs");
        await insertarNutritionLogs("./data/daily_food_nutrition_clean.csv");

        await verificationFinale();

        console.log("\n✅ Pipeline ETL terminé avec succès !");

        res.json({
            status:  "success",
            message: "Toutes les données ont été insérées dans MariaDB",
            tables:  ["users", "biometrics", "foods", "user_goals", "exercises", "activity_logs", "nutrition_logs"]
        });

    } catch (error) {
        console.error("❌ Erreur ETL :", error);
        res.status(500).json({ status: "error", message: error.message });
    }
});

// ── Endpoints de consultation ─────────────────────────────────
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

app.get("/dashboard/kpis", async (req, res) => {
    const [[kpis]] = await pool.query(`
        SELECT
            (SELECT COUNT(*) FROM users)                               AS total_users,
            (SELECT COUNT(*) FROM activity_logs)                       AS total_seances,
            (SELECT ROUND(AVG(calories_brulees),0) FROM activity_logs) AS calories_moy,
            (SELECT ROUND(AVG(bmi),1) FROM biometrics)                 AS bmi_moyen,
            (SELECT COUNT(*) FROM nutrition_logs)                      AS total_repas
    `);
    res.json(kpis);
});

// ── Lancement ─────────────────────────────────────────────────
demarrer();
