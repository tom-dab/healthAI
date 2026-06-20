# MongoDB Setup — HealthAI Coach

## 📋 Overview

This directory contains the MongoDB NoSQL database setup for the HealthAI Coach application, based on the schema diagram from `Subscription Payment-2026-04-30-081053.pdf`.

**Architecture:**
- 9 MongoDB collections with schema validation
- Data sourced from raw CSV files (gym metrics, nutrition data)
- Integration with FastAPI backend
- Docker Compose orchestration

---

## 🗂️ Collections Schema

### 1. **users**
Primary collection for user account data.

```javascript
{
  _id: ObjectId,
  name: String,
  email: String (unique),
  subscription_tier: Enum["free", "premium", "premium_plus"],
  fitness_level: Enum["beginner", "intermediate", "advanced"],
  created_at: Date
}
```

**Indexes:**
- `email` (unique)
- `subscription_tier`
- `created_at` (descending)

---

### 2. **biometrics**
User health metrics recorded over time.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (FK → users),
  weight_kg: Double,
  height_cm: Double,
  bmi: Double,
  heart_rate_bpm: Integer,
  sleep_hours: Double,
  source: String,
  recorded_at: Date
}
```

**Indexes:**
- `user_id, recorded_at` (compound, descending)
- `recorded_at` (descending)

**Data Source:** `gym_members_exercise_tracking.csv`

---

### 3. **training_plans**
Personalized workout programs for users.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (FK → users),
  objective: String,
  constraints: String,
  programme: String,
  progression: String,
  variation_strategy: String,
  last_exercises_used: Array,
  active: Boolean,
  created_at: Date
}
```

**Indexes:**
- `user_id`
- `active`
- `created_at` (descending)

---

### 4. **subscriptions**
Subscription and payment information.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (FK → users),
  tier: Enum["free", "premium", "premium_plus"],
  price_eur: Double,
  start_date: Date,
  end_date: Date,
  status: Enum["active", "cancelled", "paused", "expired"],
  payment_method: String
}
```

**Indexes:**
- `user_id`
- `status`
- `end_date`

---

### 5. **recommendations**
AI-generated recommendations for users.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (FK → users),
  type: String,
  model_used: String,
  confidence_score: Double (0-1),
  input_data: String,
  output_data: String,
  created_at: Date
}
```

**Indexes:**
- `user_id, created_at` (compound, descending)
- `type`

---

### 6. **user_preferences**
Personal preferences and activity preferences.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (FK → users, unique),
  liked_activities: String,
  disliked_activities: String,
  preferred_duration: Integer (minutes),
  availability: String
}
```

**Indexes:**
- `user_id` (unique)

---

### 7. **training_engine_logs**
Logs from the AI training engine.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (FK → users),
  input_data: String,
  output_data: String,
  reasoning: String,
  created_at: Date
}
```

**Indexes:**
- `user_id, created_at` (compound, descending)

---

### 8. **meal_logs**
Food intake records with nutritional analysis.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (FK → users),
  recommendation_id: ObjectId (FK → recommendations),
  photo_url: String,
  detected_foods: String,
  calories_total: Double,
  macros: String,
  imbalances: String,
  suggestions: String,
  meal_type: Enum["breakfast", "lunch", "dinner", "snack"],
  logged_at: Date
}
```

**Indexes:**
- `user_id, logged_at` (compound, descending)
- `logged_at` (descending)

**Data Source:** `daily_food_nutrition_dataset.csv`

---

### 9. **sessions**
Workout session records with performance metrics.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (FK → users),
  plan_id: ObjectId (FK → training_plans),
  exercises: String,
  duration_min: Integer,
  performance_score: Double,
  feedback: String,
  calories_burned: Double,
  difficulty_perceived: Integer (1-10),
  completion_rate: Double (0-1),
  session_date: Date
}
```

**Indexes:**
- `user_id, session_date` (compound, descending)
- `plan_id`

---

## 🚀 Quick Start

### With Docker Compose

```bash
# From project root
docker compose up mongodb -d

# Wait for MongoDB to start
docker compose logs -f mongodb

# Initialize schema and load data
docker compose exec mongodb mongosh --file /docker-entrypoint-initdb.d/01-init-schema.js

# Load CSV data (from project root)
python services/etl/load_data.py
```

### Standalone (Local MongoDB)

```bash
# Ensure MongoDB is running locally (port 27017)
mongosh

# Switch to healthai database and run init script
use healthai
load('database/mongodb/init-mongodb.js')

# Load data from Python
python database/mongodb/load_data.py
```

---

## 📊 Data Loading Pipeline

### Files Involved

| File | Purpose |
|------|---------|
| `init-mongodb.js` | Schema initialization + indexes |
| `load_data.py` | CSV-to-MongoDB data loader |
| `Dockerfile` | MongoDB container with tools |
| `requirements.txt` | Python dependencies |

### Data Sources

| CSV File | Collection | Records |
|----------|-----------|---------|
| `gym_members_exercise_tracking.csv` | users, biometrics | ~20 users, ~20 biometric records |
| `daily_food_nutrition_dataset.csv` | meal_logs | ~50 meal records |

### Loading Process

```
CSV Files
    ↓
[load_data.py]
    ↓
MongoDB Collections
    ↓
[Indexes Created]
    ↓
Ready for API
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# MongoDB Credentials
MONGO_USER=admin
MONGO_PASSWORD=healthai_secure_password
MONGO_DB=healthai
MONGO_URI=mongodb://admin:password@localhost:27017/healthai?authSource=admin

# Application
MONGO_LOG_LEVEL=INFO
```

### Connection String (from FastAPI)

```python
from motor.motor_asyncio import AsyncClient

client = AsyncClient("mongodb://user:pass@mongodb:27017/healthai?authSource=admin")
db = client.healthai
```

---

## 🛠️ Manual Operations

### Connect to MongoDB

```bash
# Local
mongosh "mongodb://localhost:27017" -u admin -p

# Docker container
docker exec -it healthai_mongodb mongosh -u admin -p

# From FastAPI container
docker exec -it healthai_api python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://mongodb:27017')
print(client.healthai.users.count_documents({}))
"
```

### Query Examples

```javascript
// Count documents in each collection
db.users.countDocuments()
db.biometrics.countDocuments()
db.training_plans.countDocuments()

// Find user by email
db.users.findOne({ email: "user1@healthai.com" })

// Get user's biometrics (recent first)
db.biometrics.find({ user_id: ObjectId("...") }).sort({ recorded_at: -1 }).limit(5)

// List all active subscriptions
db.subscriptions.find({ status: "active" })

// Get meal logs for a user
db.meal_logs.find({ user_id: ObjectId("...") }).sort({ logged_at: -1 })
```

### Export Data

```bash
# Export users collection to JSON
mongoexport --uri "mongodb://admin:password@localhost:27017/healthai" \
  --collection users --out users.json

# Export with authentication
mongoexport --uri "mongodb://admin:password@localhost:27017/healthai?authSource=admin" \
  --collection users --out users.json
```

---

## 📈 Performance Optimization

### Index Strategy

- **Compound indexes** on frequently filtered + sorted fields
- **Unique indexes** on `users.email` and `user_preferences.user_id`
- **Descending date indexes** for time-series data (biometrics, meal_logs, sessions)

### Query Optimization

```javascript
// ✅ Good: Uses index on user_id + recorded_at
db.biometrics.find({ user_id: userId }).sort({ recorded_at: -1 }).limit(10)

// ❌ Bad: No index on arbitrary fields
db.meal_logs.find({ imbalances: "high_sugar" })
```

---

## 🔐 Security

### In Production

1. **Always use authentication:**
   ```javascript
   db.createUser({
     user: "app_user",
     pwd: "strong_password_here",
     roles: [{ role: "readWrite", db: "healthai" }]
   })
   ```

2. **Enable encryption at rest**
3. **Use network policies** (e.g., only allow from API container)
4. **Rotate credentials** regularly
5. **Monitor access** with MongoDB audit logs

### In Development

- Default credentials: `admin` / `healthai_secure_password`
- Network open to all containers in `healthai_network`

---

## 🐛 Troubleshooting

### MongoDB won't start

```bash
# Check logs
docker logs healthai_mongodb

# Rebuild image
docker compose build --no-cache mongodb

# Reset data
docker volume rm healthai_mongo_data
```

### Authentication failed

```bash
# Verify credentials in .env
echo $MONGO_USER
echo $MONGO_PASSWORD

# Test connection
docker exec healthai_mongodb mongosh -u $MONGO_USER -p $MONGO_PASSWORD --authenticationDatabase admin
```

### Data not loading

```bash
# Check CSV files exist
ls -la services/etl/data/raw/

# Run loader with verbose output
python -u database/mongodb/load_data.py

# Check collection counts
docker exec healthai_mongodb mongosh -c "use healthai; show collections"
```

---

## 📚 References

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Guide](https://pymongo.readthedocs.io/)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)
- HealthAI Schema: `Subscription Payment-2026-04-30-081053.pdf`

---

## 📝 Version History

- **v1.0** (2026-04-30): Initial MongoDB setup from PDF schema
  - 9 collections with validation
  - Schema indexes
  - Data loading from CSV
  - Docker integration
