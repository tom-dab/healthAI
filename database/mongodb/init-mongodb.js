// ════════════════════════════════════════════════════════════════
// HealthAI Coach — MongoDB Initialization Script
// Schema: NoSQL design from Subscription Payment PDF
// Collections: users, training_plans, biometrics, subscriptions, 
//              recommendations, user_preferences, training_engine_logs,
//              meal_logs, sessions
// ════════════════════════════════════════════════════════════════

// Switch to HealthAI database
db = db.getSiblingDB('healthai');

// ─────────────────────────────────────────────────────────────────
// COLLECTION 1: users
// ─────────────────────────────────────────────────────────────────
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "email", "subscription_tier", "created_at"],
      properties: {
        _id: { bsonType: "objectId" },
        name: { bsonType: "string", description: "User full name" },
        email: { bsonType: "string", description: "User email" },
        subscription_tier: { 
          enum: ["free", "premium", "premium_plus"],
          description: "Subscription level"
        },
        fitness_level: { 
          enum: ["beginner", "intermediate", "advanced"],
          description: "User fitness level"
        },
        created_at: { bsonType: "date", description: "Account creation date" }
      }
    }
  }
});

db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ subscription_tier: 1 });
db.users.createIndex({ created_at: -1 });

// ─────────────────────────────────────────────────────────────────
// COLLECTION 2: training_plans
// ─────────────────────────────────────────────────────────────────
db.createCollection("training_plans", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "objective", "created_at"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId", description: "Reference to users" },
        objective: { bsonType: "string", description: "Training objective" },
        constraints: { bsonType: "string", description: "Constraints/limitations" },
        programme: { bsonType: "string", description: "Program description" },
        progression: { bsonType: "string", description: "Progression strategy" },
        variation_strategy: { bsonType: "string", description: "Exercise variation" },
        last_exercises_used: { bsonType: "array", description: "Previous exercises" },
        active: { bsonType: "bool", description: "Plan status" },
        created_at: { bsonType: "date" }
      }
    }
  }
});

db.training_plans.createIndex({ user_id: 1 });
db.training_plans.createIndex({ active: 1 });
db.training_plans.createIndex({ created_at: -1 });

// ─────────────────────────────────────────────────────────────────
// COLLECTION 3: biometrics
// ─────────────────────────────────────────────────────────────────
db.createCollection("biometrics", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "recorded_at"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId", description: "Reference to users" },
        weight_kg: { bsonType: "double", description: "Weight in kilograms" },
        height_cm: { bsonType: "double", description: "Height in centimeters" },
        bmi: { bsonType: "double", description: "Body Mass Index" },
        heart_rate_bpm: { bsonType: "int", description: "Heart rate BPM" },
        sleep_hours: { bsonType: "double", description: "Daily sleep hours" },
        source: { bsonType: "string", description: "Data source" },
        recorded_at: { bsonType: "date", description: "Measurement timestamp" }
      }
    }
  }
});

db.biometrics.createIndex({ user_id: 1, recorded_at: -1 });
db.biometrics.createIndex({ recorded_at: -1 });

// ─────────────────────────────────────────────────────────────────
// COLLECTION 4: subscriptions
// ─────────────────────────────────────────────────────────────────
db.createCollection("subscriptions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "tier", "start_date"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId", description: "Reference to users" },
        tier: { 
          enum: ["free", "premium", "premium_plus"],
          description: "Subscription tier"
        },
        price_eur: { bsonType: "double", description: "Price in EUR" },
        start_date: { bsonType: "date", description: "Subscription start" },
        end_date: { bsonType: "date", description: "Subscription end" },
        status: { 
          enum: ["active", "cancelled", "paused", "expired"],
          description: "Subscription status"
        },
        payment_method: { bsonType: "string", description: "Payment method used" }
      }
    }
  }
});

db.subscriptions.createIndex({ user_id: 1 });
db.subscriptions.createIndex({ status: 1 });
db.subscriptions.createIndex({ end_date: 1 });

// ─────────────────────────────────────────────────────────────────
// COLLECTION 5: recommendations
// ─────────────────────────────────────────────────────────────────
db.createCollection("recommendations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "type", "created_at"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId", description: "Reference to users" },
        type: { bsonType: "string", description: "Recommendation type" },
        model_used: { bsonType: "string", description: "ML model used" },
        confidence_score: { bsonType: "double", description: "Confidence 0-1" },
        input_data: { bsonType: "string", description: "Input parameters" },
        output_data: { bsonType: "string", description: "Recommendation output" },
        created_at: { bsonType: "date" }
      }
    }
  }
});

db.recommendations.createIndex({ user_id: 1, created_at: -1 });
db.recommendations.createIndex({ type: 1 });

// ─────────────────────────────────────────────────────────────────
// COLLECTION 6: user_preferences
// ─────────────────────────────────────────────────────────────────
db.createCollection("user_preferences", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId", description: "Reference to users" },
        liked_activities: { bsonType: "string" },
        disliked_activities: { bsonType: "string" },
        preferred_duration: { bsonType: "int", description: "Minutes" },
        availability: { bsonType: "string", description: "Available times" }
      }
    }
  }
});

db.user_preferences.createIndex({ user_id: 1 }, { unique: true });

// ─────────────────────────────────────────────────────────────────
// COLLECTION 7: training_engine_logs
// ─────────────────────────────────────────────────────────────────
db.createCollection("training_engine_logs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "created_at"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId", description: "Reference to users" },
        input_data: { bsonType: "string" },
        output_data: { bsonType: "string" },
        reasoning: { bsonType: "string", description: "Engine reasoning" },
        created_at: { bsonType: "date" }
      }
    }
  }
});

db.training_engine_logs.createIndex({ user_id: 1, created_at: -1 });

// ─────────────────────────────────────────────────────────────────
// COLLECTION 8: meal_logs
// ─────────────────────────────────────────────────────────────────
db.createCollection("meal_logs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "logged_at"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId", description: "Reference to users" },
        recommendation_id: { bsonType: "objectId", description: "Reference to recommendations" },
        photo_url: { bsonType: "string", description: "Meal photo" },
        detected_foods: { bsonType: "string", description: "Identified foods" },
        calories_total: { bsonType: "double" },
        macros: { bsonType: "string", description: "Macronutrient breakdown" },
        imbalances: { bsonType: "string", description: "Nutritional issues" },
        suggestions: { bsonType: "string", description: "Recommendations" },
        meal_type: { 
          enum: ["breakfast", "lunch", "dinner", "snack"],
          description: "Type of meal"
        },
        logged_at: { bsonType: "date" }
      }
    }
  }
});

db.meal_logs.createIndex({ user_id: 1, logged_at: -1 });
db.meal_logs.createIndex({ logged_at: -1 });

// ─────────────────────────────────────────────────────────────────
// COLLECTION 9: sessions
// ─────────────────────────────────────────────────────────────────
db.createCollection("sessions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "plan_id", "session_date"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId", description: "Reference to users" },
        plan_id: { bsonType: "objectId", description: "Reference to training_plans" },
        exercises: { bsonType: "string", description: "Exercises performed" },
        duration_min: { bsonType: "int", description: "Session duration" },
        performance_score: { bsonType: "double", description: "Performance rating" },
        feedback: { bsonType: "string", description: "User feedback" },
        calories_burned: { bsonType: "double" },
        difficulty_perceived: { bsonType: "int", description: "1-10 scale" },
        completion_rate: { bsonType: "double", description: "% completed" },
        session_date: { bsonType: "date" }
      }
    }
  }
});

db.sessions.createIndex({ user_id: 1, session_date: -1 });
db.sessions.createIndex({ plan_id: 1 });

// ─────────────────────────────────────────────────────────────────
// Create indexes for performance
// ─────────────────────────────────────────────────────────────────
print("✓ MongoDB schema initialized with 9 collections");
print("✓ Schema validation enabled for all collections");
print("✓ Performance indexes created");
