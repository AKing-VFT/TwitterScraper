'''
Created on Apr 14, 2016

@author: Andrew
'''
from pymongo.mongo_client import MongoClient

client = MongoClient()
db = client.tweets
collection = db.OlympicSongs

#https://stackoverflow.com/questions/34722866/pymongo-remove-duplicates-map-reduce
cursor = collection.aggregate(
    [
        {"$group": {"_id": "$tweet id", "unique_ids": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": { "$gte": 2 }}}
    ]
)
#group the tweets by their tweet id. Add each id to a set of unique ids, then increment the count for that id by one. Look for ids with at least 2 members

response = []
for doc in cursor:
    #doc["unique_ids"] is the list of unique ids
    print "keeping {}".format(doc["unique_ids"][0])
    del doc["unique_ids"][0]
    #remove the first item from the list (this is the one that will remain)
    for id in doc["unique_ids"]:
        print "deleting {}".format(id)
        response.append(id)

print "Removing {} duplicates".format(len(response))
collection.remove({"_id": {"$in": response}})