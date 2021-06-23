import pymongo
import json
from pymongo import MongoClient

secrets = json.load(open('secrets.json'))
cluster = pymongo.MongoClient(secrets["MONGO_CLUSTER"])
db = cluster["VoiceLogger"]
collection = db["test"]

# collection.insert_one({
#     "_id": 4564565314564, # Server ID
#     "channel_ids": {
#         "text_channel_id": 4765432531,
#         "voice_channel_id": 774541654
#     },
#     "user_history": {
#         "sadboi#9757": 200,
#         "boris#4131": 599,
#     },
#     "voicechat_history": [
#         {
#             "start_date": "date_here",
#             "end_date": "date_here",
#             "vc_events": [
#                 "xxx", "yyy", "zzz"
#             ]
#         }
#     ]
# })

def check_in_db(guild_id):
    return(bool(collection.count_documents({"_id":guild_id})))

def create_guild_document(guild_id):
    collection.insert_one({
        "_id": guild_id, # Server ID
        "text_channel_id": -1,
        "user_history": {},
        "voicechat_history": []
    })

def update_vc_history(guild_id):
    pass

def update_user_time(guild_id, username):
    pass

def get_top_users(guild_id):
    pass

print(check_in_db(4564565314564))