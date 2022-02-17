import os
from .mongodb import mongo
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class UsersRepository():

    def __init__(self):
        self.users_collection = mongo.db.users
        self.users_inputs_collection = mongo.db.usersInputs
        ttl_users_inputs = 30*60*60*24 # 30 days in seconds
        if os.environ.get("MONGODB_PROVIDER", "") == "CosmosDB":
            self.users_inputs_collection.ensure_index("_ts", expireAfterSeconds=ttl_users_inputs)
        else:
            self.users_inputs_collection.ensure_index("date", expireAfterSeconds=ttl_users_inputs)

    def insert_user_input(self, data):
        return(self.users_inputs_collection.insert_one(data))
    
    def count_user_inputs(self, agent_name):
        return self.users_inputs_collection.count({"agent_name": agent_name})

    def get_agent_inputs(self, agent_name, max_confidence, min_confidence, page_number, page_size):
        max_page_size = int(os.environ.get("MAX_PAGE_SIZE", 200))
        if page_size > max_page_size:
            page_size = max_page_size
        return(self.users_inputs_collection.find({"agent_name": agent_name, "intent.confidence": {"$lte": max_confidence, "$gte": min_confidence}}, {"agent_name": 0}).sort("timestamp", -1).sort("date", -1).skip((page_number - 1) * page_size).limit(page_size))

    def delete_users_inputs(self, agent_name):
        self.users_inputs_collection.delete_many({"agent_name": agent_name})

    def delete_user_input(self, agent_name, id):
        try:
            self.users_inputs_collection.delete_one({"agent_name": agent_name, "_id": ObjectId(id)})
            return True
        except Exception as e:
            logger.error("Can't delete user input {0}".format(e), exc_info=True)
            return(False)  

    def get_user_inputs(self, agent_name, user_id, max_confidence, min_confidence, page_number, page_size):
        max_page_size = int(os.environ.get("MAX_PAGE_SIZE", 200))
        if page_size > max_page_size:
            page_size = max_page_size
        return(self.users_inputs_collection.find({"agent_name": agent_name, "user_id": user_id, "intent.confidence": {"$lt": max_confidence, "$gt": min_confidence}}, {"agent_name": 0}).skip((page_number - 1) * page_size).limit(page_size))

    def find_all_users(self):
        return self.users_collection.find({})

    def add_user(self, user):
        return(self.users_collection.insert_one(user))

    def get_user(self, email):
        return self.users_collection.find_one({"email": email})

    def get_one_user_by_role(self, role):
        return self.users_collection.find_one({"role": role})

    def update_user_password(self, email, new_password):
        return self.users_collection.update_one(
            {"email": email}, 
            {"$set": 
                {
                    "password": new_password, 
                    "is_first_login": False
                }
            }
        )
    
    def update_user_data(self, email, first_name, last_name, role, agents):
        return self.users_collection.update_one(
            {"email": email}, 
            {"$set": 
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": role,
                    "agents": agents
                }
            }
        )

    def delete_user(self, email):
        self.users_collection.delete_one({"email": email})
