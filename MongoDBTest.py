import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

print(myclient.list_database_names())

mydb = myclient["mydatabase"]
mycol = mydb["mycol"]

mydict = {"myvar": "myval"}
x = mycol.insert_one(mydict)

print(mydb.list_collection_names())
