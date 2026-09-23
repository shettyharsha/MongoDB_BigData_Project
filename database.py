from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["bigdata_db"]
collection = db["sales"]

print("Connected to MongoDB successfully!")

count = collection.count_documents({})

print("Number of sales:", count)