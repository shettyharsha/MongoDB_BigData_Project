import pandas as pd
from pymongo import MongoClient

df = pd.read_csv("sales.csv")

data = df.to_dict("records")

client = MongoClient("mongodb://localhost:27017/")

db = client["bigdata_db"]
collection = db["sales"]

if data:
    result = collection.insert_many(data)
    print("Data imported successfully!")
    print("Documents inserted:", len(result.inserted_ids))
else:
    print("CSV file is empty.")