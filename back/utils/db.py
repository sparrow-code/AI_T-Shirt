from pymongo import MongoClient
from const import MONGO_DB

client = MongoClient(MONGO_DB)
db = client["AI_T_Shirt"]
