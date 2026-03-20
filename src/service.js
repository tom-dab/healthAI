const fs   = require("fs");
const csv  = require("csv-parser");
const pool = require("./db");

// ═══════════════════════════════════════════════════════════════
// UTILITAIRE — Lire un fichier CSV et retourner les lignes
// ═══════════════════════════════════════════════════════════════
function lireCSV(ruta) {
    return new Promise((resolve, reject) => {
        const resultados = [];
        fs.createReadStream(ruta)
            .pipe(csv())
            .on("data", (data) => resultados.push(data))
            .on("end",  () => resolve(resultados))
            .on("error", reject);
    });
}



// ═══════════════════════════════════════════════════════════════
// 1. INSERTION — Table foods
//    Source : daily_food_nutrition_clean.csv
//    Colonnes : Food_Item, Category, Calories (kcal), Protein (g),
//               Carbohydrates (g), Fat (g), Fiber (g), Sugars (g),
//               Sodium (mg), Cholesterol (mg), Meal_Type, Water_Intake (ml)
// ═══════════════════════════════════════════════════════════════
async function insertarFoods(ruta) {
    console.log("📂 Lecture :", ruta);
    const filas = await lireCSV(ruta);

    await pool.query("DELETE FROM nutrition_logs");
    await pool.query("DELETE FROM foods");

    let ok = 0, err = 0;

    for (let f of filas) {
        try {
            await pool.query(
                `INSERT INTO foods 
                (nom, calories_kcal, proteines_g, glucides_g, lipides_g, 
                 fibres_g, sucres_g, sodium_mg, cholesterol_mg, type_repas, source_donnee)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [
                    f["Food_Item"]         || null,
                    parseFloat(f["Calories (kcal)"])   || 0,
                    parseFloat(f["Protein (g)"])        || 0,
                    parseFloat(f["Carbohydrates (g)"])  || 0,
                    parseFloat(f["Fat (g)"])            || 0,
                    parseFloat(f["Fiber (g)"])          || 0,
                    parseFloat(f["Sugars (g)"])         || 0,
                    parseFloat(f["Sodium (mg)"])        || 0,
                    parseFloat(f["Cholesterol (mg)"])   || 0,
                    ({"Breakfast":"petit_dejeuner","Lunch":"dejeuner","Dinner":"diner","Snack":"collation"}[f["Meal_Type"]] || "collation"),
                    "kaggle_daily_food"
                ]
            );
            ok++;
        } catch (e) {
            console.warn("   ⚠️  Ligne ignorée (foods):", f["Food_Item"], "→", e.message);
            err++;
        }
    }
    console.log(`✅ foods : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// 2. INSERTION — Table users + biometrics
//    Source : gym_members_exercise_clean.csv  (973 lignes)
//             gym_members_synthetic_clean.csv (1352 lignes)
//    Colonnes : age, gender, weight_kg, height_m, max_bpm, avg_bpm,
//               resting_bpm, session_duration_hours, calories_burned,
//               workout_type, fat_percentage, bmi, experience_level
// ═══════════════════════════════════════════════════════════════
async function insertarUsers(rutaExercise, rutaSynthetic) {
    // Vider dans le bon ordre (FK)
    await pool.query("DELETE FROM activity_logs");
    await pool.query("DELETE FROM biometrics");
    await pool.query("DELETE FROM user_goals");
    await pool.query("DELETE FROM users");

    // Combiner les deux sources
    const sources = [];
    if (rutaExercise) {
        console.log("📂 Lecture :", rutaExercise);
        const filas = await lireCSV(rutaExercise);
        sources.push(...filas);
    }
    if (rutaSynthetic) {
        console.log("📂 Lecture :", rutaSynthetic);
        const filas = await lireCSV(rutaSynthetic);
        sources.push(...filas);
    }

    let ok = 0, err = 0;

    for (let i = 0; i < sources.length; i++) {
        const f     = sources[i];
        const email = `user${i + 1}@healthai.com`;

        // Mapping niveau fitness
        const exp    = parseFloat(f["experience_level"] || f["Experience_Level"] || 1);
        const niveau = exp <= 1 ? "debutant" : exp <= 2 ? "intermediaire" : "avance";

        // Mapping genre
        const genreRaw = (f["gender"] || f["Gender"] || "").trim();
        const genre    = genreRaw === "Male" ? "M" : genreRaw === "Female" ? "F" : "autre";

        // Taille : height_m → cm
        const hauteurM = parseFloat(f["height_m"] || f["Height (m)"] || 0);
        const tailleCm = hauteurM > 0 ? Math.round(hauteurM * 100) : null;
        const poids    = parseFloat(f["weight_kg"] || f["Weight (kg)"] || 0) || null;
        const age      = parseInt(f["age"]         || f["Age"]         || 0) || null;

        try {
            await pool.query(
                `INSERT INTO users (email, age, genre, poids_kg, taille_cm, niveau_fitness)
                 VALUES (?, ?, ?, ?, ?, ?)`,
                [email, age, genre, poids, tailleCm, niveau]
            );

            await pool.query(
                `INSERT INTO biometrics (user_id, date_mesure, poids_kg, bpm_moyen, bpm_max, bmi, body_fat_pct)
                 VALUES ((SELECT id FROM users WHERE email = ? LIMIT 1), CURDATE(), ?, ?, ?, ?, ?)`,
                [
                    email,
                    poids,
                    parseFloat(f["avg_bpm"]        || f["Avg BPM"]        || 0) || null,
                    parseFloat(f["max_bpm"]        || f["Max BPM"]        || 0) || null,
                    parseFloat(f["bmi"]            || f["BMI"]            || 0) || null,
                    parseFloat(f["fat_percentage"] || f["Fat Percentage"] || 0) || null,
                ]
            );

            ok++;
        } catch (e) {
            console.warn("   ⚠️  User ignoré:", email, "→", e.message);
            err++;
        }
    }
    console.log(`✅ users + biometrics : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// 3. INSERTION — Table user_goals
//    Source : diet_recommendations_clean.csv
//    Colonnes : Patient_ID, Age, Gender, Weight_kg, Height_cm,
//               BMI, Disease_Type, Severity, Daily_Caloric_Intake,
//               Diet_Recommendation
// ═══════════════════════════════════════════════════════════════
async function insertarUserGoals(ruta) {
    console.log("📂 Lecture :", ruta);
    const filas = await lireCSV(ruta);

    // Nombre total d'users insérés
    const [[{ total }]] = await pool.query("SELECT COUNT(*) AS total FROM users");

    let ok = 0, err = 0;

    for (let i = 0; i < Math.min(filas.length, total); i++) {
        const f     = filas[i];
        const email = `user${i + 1}@healthai.com`;

        // Mapping objectif depuis Disease_Type et Diet_Recommendation
        const disease = (f["Disease_Type"]       || "").toLowerCase();
        const rec     = (f["Diet_Recommendation"] || "").toLowerCase();
        let objectif  = "maintien";
        if (disease.includes("obes") || rec.includes("loss"))    objectif = "perte_poids";
        else if (rec.includes("muscle") || rec.includes("gain")) objectif = "prise_masse";
        else if (disease.includes("sleep"))                       objectif = "sommeil";

        const calories = parseFloat(f["Daily_Caloric_Intake"] || 0) || null;

        try {
            await pool.query(
                `INSERT INTO user_goals (user_id, type_objectif, valeur_cible, date_debut, date_fin)
                 VALUES ((SELECT id FROM users WHERE email = ? LIMIT 1), ?, ?, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 90 DAY))`,
                [email, objectif, calories]
            );
            ok++;
        } catch (e) {
            console.warn("   ⚠️  Goal ignoré:", email, "→", e.message);
            err++;
        }
    }
    console.log(`✅ user_goals : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// 4. INSERTION — Table exercises + activity_logs
//    Source : gym_members_exercise_clean.csv + gym_members_synthetic_clean.csv
// ═══════════════════════════════════════════════════════════════
async function insertarActivity(rutaExercise, rutaSynthetic) {
    // Combiner les deux sources (même ordre que insertarUsers)
    const sources = [];
    if (rutaExercise) {
        const filas = await lireCSV(rutaExercise);
        sources.push(...filas);
    }
    if (rutaSynthetic) {
        const filas = await lireCSV(rutaSynthetic);
        sources.push(...filas);
    }

    // Exercices uniques
    const exercicesUniques = [...new Set(
        sources.map(f => f["workout_type"] || f["Workout_Type"]).filter(Boolean)
    )];

    for (let ex of exercicesUniques) {
        try {
            await pool.query(
                `INSERT IGNORE INTO exercises (nom, type_exercice, muscle_cible, equipement, niveau)
                 VALUES (?, 'cardio_muscu', 'multiple', 'variable', 'intermediaire')`,
                [ex]
            );
        } catch (e) {
            console.warn("   ⚠️  Exercice ignoré:", ex);
        }
    }
    console.log(`✅ exercises : ${exercicesUniques.length} types insérés`);

    // Activity logs
    let ok = 0, err = 0;
    for (let i = 0; i < sources.length; i++) {
        const f        = sources[i];
        const email    = `user${i + 1}@healthai.com`;
        const exercice = f["workout_type"] || f["Workout_Type"] || null;
        const dureeH   = parseFloat(f["session_duration_hours"] || 0);
        const dureeMin = dureeH > 0 ? Math.round(dureeH * 60) : null;
        const calories = parseFloat(f["calories_burned"] || f["Calories_Burned"] || 0) || null;

        try {
            await pool.query(
                `INSERT INTO activity_logs (user_id, exercise_id, date_seance, duree_min, calories_brulees)
                 VALUES (
                     (SELECT id FROM users     WHERE email = ? LIMIT 1),
                     (SELECT id FROM exercises WHERE nom   = ? LIMIT 1),
                     CURDATE(), ?, ?
                 )`,
                [email, exercice, dureeMin, calories]
            );
            ok++;
        } catch (e) {
            console.warn("   ⚠️  Activity ignorée:", email, "→", e.message);
            err++;
        }
    }
    console.log(`✅ activity_logs : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// 5. INSERTION — Table nutrition_logs
// ═══════════════════════════════════════════════════════════════
async function insertarNutritionLogs(ruta) {
    console.log("📂 Lecture :", ruta);
    const filas = await lireCSV(ruta);

    const repasMap = {
        "Breakfast": "petit_dejeuner",
        "Lunch":     "dejeuner",
        "Dinner":    "diner",
        "Snack":     "collation"
    };

    // Nombre total d'users
    const [[{ total }]] = await pool.query("SELECT COUNT(*) AS total FROM users");

    let ok = 0, err = 0;
    const today = new Date().toISOString().split("T")[0];

    for (let i = 0; i < filas.length; i++) {
        const f       = filas[i];
        const userNum = (i % total) + 1;
        const email   = `user${userNum}@healthai.com`;
        const nomFood = f["Food_Item"] || null;
        const repas   = repasMap[f["Meal_Type"]] || "collation";

        try {
            await pool.query(
                `INSERT INTO nutrition_logs (user_id, food_id, date_repas, repas, quantite_g)
                 VALUES (
                     (SELECT id FROM users WHERE email = ? LIMIT 1),
                     (SELECT id FROM foods WHERE nom   = ? LIMIT 1),
                     ?, ?, 150.00
                 )`,
                [email, nomFood, today, repas]
            );
            ok++;
        } catch (e) {
            console.warn("   ⚠️  Nutrition log ignoré ligne", i, "→", e.message);
            err++;
        }
    }
    console.log(`✅ nutrition_logs : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// VÉRIFICATION FINALE
// ═══════════════════════════════════════════════════════════════
async function verificationFinale() {
    const tables = ["users","biometrics","foods","user_goals","exercises","activity_logs","nutrition_logs"];
    console.log("\n── Vérification finale ──");
    for (let t of tables) {
        const [[{ nb }]] = await pool.query(`SELECT COUNT(*) AS nb FROM ${t}`);
        console.log(`   ${t.padEnd(20)} : ${nb} lignes`);
    }
}

module.exports = {
    insertarFoods,
    insertarUsers,
    insertarUserGoals,
    insertarActivity,
    insertarNutritionLogs,
    verificationFinale
};

// Traitement CSV → MariaDB — HealthAI Coach
