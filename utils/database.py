from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from config import Config
import certifi
import urllib.parse
"""MongoDB utility class for handling database operations"""
class MongoDB:
    def __init__(self):
        try:
            # Properly encode username and password if they contain special characters
            self.client = MongoClient(Config.MONGO_URI, tlsCAFile=certifi.where())
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully!")
            
            self.db = self.client[Config.DB_NAME]
            
            # Collections
            self.users = self.db['users']
            self.medicines = self.db['medicines']
            self.history = self.db['history']
            
            # Create indexes
            self.create_indexes()
            
        except OperationFailure as e:
            print(f"❌ Authentication failed: {e}")
            print("\nPlease check your MongoDB Atlas credentials:")
            print("1. Go to MongoDB Atlas -> Database Access")
            print("2. Ensure username/password is correct")
            print("3. If using special characters in password, they need to be URL encoded")
            print("4. Make sure your IP is whitelisted in Network Access")
            raise e
        except ConnectionFailure as e:
            print(f"❌ Connection failed: {e}")
            print("\nPlease check:")
            print("1. Your internet connection")
            print("2. MongoDB Atlas cluster is running")
            print("3. Network Access IP whitelist includes your current IP")
            raise e
    
    def create_indexes(self):
        """Create indexes for better performance"""
        try:
            self.users.create_index('email', unique=True)
            self.medicines.create_index([('user_id', 1), ('medicine_name', 1)])
            self.history.create_index([('user_id', 1), ('date', -1)])
            print("✅ Indexes created successfully")
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
    
    # ... rest of the methods remain the same
    def get_user_by_id(self, user_id):
        return self.users.find_one({'_id': user_id})
    
    def get_user_by_email(self, email):
        return self.users.find_one({'email': email})
    
    def create_user(self, user_data):
        return self.users.insert_one(user_data)
    
    def get_user_medicines(self, user_id):
        return list(self.medicines.find({'user_id': user_id}))
    
    def add_medicine(self, medicine_data):
        return self.medicines.insert_one(medicine_data)
    
    def update_medicine(self, medicine_id, update_data):
        return self.medicines.update_one(
            {'_id': medicine_id}, 
            {'$set': update_data}
        )
    
    def delete_medicine(self, medicine_id):
        return self.medicines.delete_one({'_id': medicine_id})
    
    def create_history_entry(self, history_data):
        return self.history.insert_one(history_data)
    
    def update_history_entry(self, history_id, update_data):
        return self.history.update_one(
            {'_id': history_id},
            {'$set': update_data}
        )
    def update_medicine(self, medicine_id, update_data):
        """Update medicine information"""
        return self.medicines.update_one(
            {'_id': medicine_id},
            {'$set': update_data}
        )
    def get_today_reminders(self):
        from datetime import datetime
        current_day = datetime.now().strftime('%a').lower()
        
        # Find medicines scheduled for today
        medicines_today = self.medicines.find({
            f'days.{current_day}': {'$exists': True}
        })
        
        return list(medicines_today)