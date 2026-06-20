#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════
# HealthAI Coach — MongoDB Data Loader
# Loads CSV data from raw folder into MongoDB collections
# ════════════════════════════════════════════════════════════════

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'healthai'
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '../etl/data/raw')

class MongoDBDataLoader:
    def __init__(self, mongo_uri, db_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        logger.info(f"✓ Connected to MongoDB: {db_name}")

    def close(self):
        self.client.close()
        logger.info("✓ MongoDB connection closed")

    def load_users_from_gym_data(self):
        """Load users from gym_members_exercise_tracking.csv"""
        file_path = os.path.join(RAW_DATA_DIR, 'gym_members_exercise_tracking.csv')
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return 0
        
        try:
            df = pd.read_csv(file_path)
            users_collection = self.db['users']
            count = 0
            
            # Create sample users from unique rows in gym data
            for idx, row in df.head(20).iterrows():
                user_doc = {
                    'name': f"User_{idx+1}",
                    'email': f"user{idx+1}@healthai.com",
                    'subscription_tier': 'premium' if idx % 3 == 0 else 'free',
                    'fitness_level': self._map_experience_level(row.get('Experience_Level', 2)),
                    'created_at': datetime.now() - timedelta(days=idx*10)
                }
                
                try:
                    result = users_collection.insert_one(user_doc)
                    count += 1
                    logger.debug(f"Created user: {user_doc['email']}")
                except DuplicateKeyError:
                    logger.debug(f"User already exists: {user_doc['email']}")
            
            logger.info(f"✓ Loaded {count} users from gym_members_exercise_tracking.csv")
            return count
            
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return 0

    def load_biometrics_from_gym_data(self):
        """Load biometrics from gym_members_exercise_tracking.csv"""
        file_path = os.path.join(RAW_DATA_DIR, 'gym_members_exercise_tracking.csv')
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return 0
        
        try:
            df = pd.read_csv(file_path)
            biometrics_collection = self.db['biometrics']
            users_collection = self.db['users']
            
            count = 0
            users = list(users_collection.find().limit(20))
            
            for idx, row in df.head(20).iterrows():
                if idx < len(users):
                    user_id = users[idx]['_id']
                    
                    biometric_doc = {
                        'user_id': user_id,
                        'weight_kg': float(row.get('Weight (kg)', 70)),
                        'height_cm': float(row.get('Height (m)', 1.7)) * 100,
                        'bmi': float(row.get('BMI', 24.0)),
                        'heart_rate_bpm': int(row.get('Avg_BPM', 100)),
                        'sleep_hours': 7.5,
                        'source': 'gym_members_exercise_tracking.csv',
                        'recorded_at': datetime.now() - timedelta(days=idx)
                    }
                    
                    biometrics_collection.insert_one(biometric_doc)
                    count += 1
                    logger.debug(f"Created biometric for user {idx+1}")
            
            logger.info(f"✓ Loaded {count} biometric records")
            return count
            
        except Exception as e:
            logger.error(f"Error loading biometrics: {e}")
            return 0

    def load_meal_logs_from_nutrition_data(self):
        """Load meal logs from daily_food_nutrition_dataset.csv"""
        file_path = os.path.join(RAW_DATA_DIR, 'daily_food_nutrition_dataset.csv')
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return 0
        
        try:
            df = pd.read_csv(file_path)
            meal_logs_collection = self.db['meal_logs']
            users_collection = self.db['users']
            
            count = 0
            users = list(users_collection.find())
            
            for idx, row in df.head(50).iterrows():
                user_idx = idx % len(users)
                user_id = users[user_idx]['_id']
                
                meal_doc = {
                    'user_id': user_id,
                    'detected_foods': str(row.get('Food_Item', 'Unknown')),
                    'calories_total': float(row.get('Calories (kcal)', 0)),
                    'macros': f"P:{row.get('Protein (g)', 0)}g | C:{row.get('Carbohydrates (g)', 0)}g | F:{row.get('Fat (g)', 0)}g",
                    'imbalances': 'None',
                    'suggestions': 'Good nutritional balance',
                    'meal_type': str(row.get('Meal_Type', 'snack')).lower(),
                    'logged_at': datetime.now() - timedelta(hours=idx)
                }
                
                meal_logs_collection.insert_one(meal_doc)
                count += 1
                logger.debug(f"Created meal log: {row.get('Food_Item', 'Unknown')}")
            
            logger.info(f"✓ Loaded {count} meal log records")
            return count
            
        except Exception as e:
            logger.error(f"Error loading meal logs: {e}")
            return 0

    def load_training_plans(self):
        """Create sample training plans for users"""
        try:
            training_plans_collection = self.db['training_plans']
            users_collection = self.db['users']
            
            count = 0
            users = list(users_collection.find())
            
            for idx, user in enumerate(users):
                plan_doc = {
                    'user_id': user['_id'],
                    'objective': ['weight_loss', 'muscle_gain', 'maintenance', 'endurance'][idx % 4],
                    'constraints': 'Limited equipment available',
                    'programme': f'8-week progressive training program for {user.get("fitness_level", "intermediate")}',
                    'progression': 'Increase weight by 5% weekly',
                    'variation_strategy': 'Rotate exercises every 4 weeks',
                    'last_exercises_used': ['push-ups', 'squats', 'deadlifts'],
                    'active': True,
                    'created_at': user['created_at']
                }
                
                training_plans_collection.insert_one(plan_doc)
                count += 1
            
            logger.info(f"✓ Loaded {count} training plans")
            return count
            
        except Exception as e:
            logger.error(f"Error loading training plans: {e}")
            return 0

    def load_subscriptions(self):
        """Create subscriptions for users"""
        try:
            subscriptions_collection = self.db['subscriptions']
            users_collection = self.db['users']
            
            count = 0
            users = list(users_collection.find())
            
            for idx, user in enumerate(users):
                tier = user['subscription_tier']
                price_map = {'free': 0.0, 'premium': 9.99, 'premium_plus': 19.99}
                
                sub_doc = {
                    'user_id': user['_id'],
                    'tier': tier,
                    'price_eur': price_map.get(tier, 0.0),
                    'start_date': user['created_at'],
                    'end_date': user['created_at'] + timedelta(days=365),
                    'status': 'active',
                    'payment_method': 'credit_card' if tier != 'free' else None
                }
                
                subscriptions_collection.insert_one(sub_doc)
                count += 1
            
            logger.info(f"✓ Loaded {count} subscriptions")
            return count
            
        except Exception as e:
            logger.error(f"Error loading subscriptions: {e}")
            return 0

    def load_user_preferences(self):
        """Create user preferences"""
        try:
            preferences_collection = self.db['user_preferences']
            users_collection = self.db['users']
            
            count = 0
            users = list(users_collection.find())
            
            activities = ['running', 'cycling', 'swimming', 'yoga', 'weightlifting']
            
            for idx, user in enumerate(users):
                pref_doc = {
                    'user_id': user['_id'],
                    'liked_activities': activities[idx % len(activities)],
                    'disliked_activities': activities[(idx + 1) % len(activities)],
                    'preferred_duration': 45 + (idx % 3) * 15,
                    'availability': 'Evening (6PM-9PM)'
                }
                
                preferences_collection.insert_one(pref_doc)
                count += 1
            
            logger.info(f"✓ Loaded {count} user preferences")
            return count
            
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
            return 0

    def load_recommendations(self):
        """Create AI recommendations"""
        try:
            recommendations_collection = self.db['recommendations']
            users_collection = self.db['users']
            
            count = 0
            users = list(users_collection.find())
            
            for idx, user in enumerate(users):
                rec_doc = {
                    'user_id': user['_id'],
                    'type': ['nutrition', 'training', 'recovery'][idx % 3],
                    'model_used': 'HealthAI_v1.0',
                    'confidence_score': 0.85 + (idx % 10) * 0.01,
                    'input_data': 'User biometrics and preferences',
                    'output_data': 'Personalized recommendation generated',
                    'created_at': datetime.now() - timedelta(days=idx)
                }
                
                recommendations_collection.insert_one(rec_doc)
                count += 1
            
            logger.info(f"✓ Loaded {count} recommendations")
            return count
            
        except Exception as e:
            logger.error(f"Error loading recommendations: {e}")
            return 0

    def load_sessions(self):
        """Create workout sessions"""
        try:
            sessions_collection = self.db['sessions']
            users_collection = self.db['users']
            training_plans_collection = self.db['training_plans']
            
            count = 0
            users = list(users_collection.find())
            plans = list(training_plans_collection.find())
            
            for idx, user in enumerate(users):
                if idx < len(plans):
                    plan = plans[idx]
                    
                    session_doc = {
                        'user_id': user['_id'],
                        'plan_id': plan['_id'],
                        'exercises': 'Push-ups, Squats, Deadlifts',
                        'duration_min': 45,
                        'performance_score': 8.2,
                        'feedback': 'Good session, need to increase intensity',
                        'calories_burned': 450.0,
                        'difficulty_perceived': 7,
                        'completion_rate': 0.95,
                        'session_date': datetime.now() - timedelta(days=idx)
                    }
                    
                    sessions_collection.insert_one(session_doc)
                    count += 1
            
            logger.info(f"✓ Loaded {count} workout sessions")
            return count
            
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            return 0

    def _map_experience_level(self, level):
        """Map numeric experience level to string"""
        mapping = {1: 'beginner', 2: 'intermediate', 3: 'advanced'}
        return mapping.get(int(level), 'intermediate')

    def run(self):
        """Execute complete data loading pipeline"""
        logger.info("="*60)
        logger.info("Starting MongoDB Data Loading Pipeline")
        logger.info("="*60)
        
        total_loaded = 0
        
        # Load core data from CSV files
        total_loaded += self.load_users_from_gym_data()
        total_loaded += self.load_biometrics_from_gym_data()
        total_loaded += self.load_meal_logs_from_nutrition_data()
        
        # Generate related data
        total_loaded += self.load_training_plans()
        total_loaded += self.load_subscriptions()
        total_loaded += self.load_user_preferences()
        total_loaded += self.load_recommendations()
        total_loaded += self.load_sessions()
        
        logger.info("="*60)
        logger.info(f"✓ Data Loading Complete: {total_loaded} total records loaded")
        logger.info("="*60)
        
        # Print collection statistics
        print("\n📊 Collection Statistics:")
        print("-" * 60)
        for collection_name in self.db.list_collection_names():
            count = self.db[collection_name].count_documents({})
            print(f"  {collection_name:25} : {count:5} documents")
        print("-" * 60)


if __name__ == '__main__':
    loader = MongoDBDataLoader(MONGO_URI, DB_NAME)
    try:
        loader.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        loader.close()
