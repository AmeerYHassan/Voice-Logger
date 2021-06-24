import pymongo
import json
from pymongo import MongoClient

secrets = json.load(open('secrets.json'))
cluster = pymongo.MongoClient(secrets["MONGO_CLUSTER"])
db = cluster["VoiceLogger"]
collection = db["test"]

def check_in_db(guild_id):
    return(bool(collection.count_documents({"_id":guild_id})))

def create_guild_document(guild_id, guild_name):
    collection.insert_one({
        "_id": guild_id, # Server ID
        "verbosity": False,
        "guild_name": guild_name,
        "text_channel_id": -1,
        "user_history": {},
        "voicechat_history": []
    })

def get_text_channel_id(guild_id):
    return(collection.find_one({"_id": guild_id})["text_channel_id"])

def set_text_channel_id(guild_id, text_channel_id):
    collection.update_one({ "_id": guild_id }, { "$set": {"text_channel_id": text_channel_id } })

def get_verbosity(guild_id):
    return(collection.find_one({"_id": guild_id})["verbosity"])

def set_verbosity(guild_id, verbosity):
    collection.update_one({ "_id": guild_id }, { "$set": {"verbosity": verbosity } })

def get_vc_history(guild_id):
    return(collection.find_one({"_id": guild_id})["voicechat_history"])

def update_vc_history(guild_id, curr_vc):
    collection.update_one({ "_id": guild_id }, { "$push": {"voicechat_history": curr_vc } })

def update_user_time(guild_id, username, time):
    collection.update_one({ "_id": guild_id }, { "$inc": {f"user_history.{username}": time}})

def get_top_users(guild_id):
    pass