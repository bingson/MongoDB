# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 19:12:22 2015

@author: Bing
"""
 
import json
from pymongo import MongoClient
import pprint
    
    
def get_db(db_name): 
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db


def riviera_pipe():
    pipeline = [
        {"$group": { "_id" : "$name",
                   "count" : { "$sum" : 1}}},
        {"$sort": {"count" : -1}},
        {'$match' : {'_id' : "Riviera"}}, 
        {"$limit" : 20}
        ]
    return pipeline
    
    
def top_amenities_pipe():
    pipeline = [
        {"$group": { "_id" : "$amenity",
                   "count" : { "$sum" : 1}}},
        {"$sort": {"count" : -1}},
        {'$match' : {'_id' : {'$ne' : None}}}, 
        {"$limit" : 20}
        ]
    return pipeline
    
    
def popular_cuisine_pipe():
    pipeline = [
        {"$group": { "_id" : "$cuisine",
                   "count" : { "$sum" : 1}}},
        {"$sort": {"count" : -1}},
        {'$match' : {'_id' : {'$ne' : None}}}, 
        {"$limit" : 10}
        ]
    return pipeline
       
       
def top_contributing_user_pipe():
    pipeline = [
        {"$group" : {"_id" : "$created.user",
                   "count" : { "$sum" : 1}}},
        {"$match" : {"_id" : {"$ne" : None}}}, 
        {"$sort": {"count" : -1}},
        {"$limit" : 1}
        ]
    return pipeline
    
    
def unique_users_pipe():
    pipeline = [
        {"$group": { "_id" : "$created.user"}},
        {"$group": { "_id" : 1,
                   "count" : { "$sum" : 1}}}
        ]
    return pipeline


def num_one_time_users_pipe():
    pipeline = [
        {"$group": { "_id" : "$created.user", 
                   "count" : {"$sum":1}}}, 
        {"$group": { "_id" : "$count", 
               "num_users" : {"$sum":1}}}, 
        {"$sort" : { "_id" : 1}}, 
        {"$limit": 1 }
        ]
    return pipeline
  
  
def mongo_query(db, pipeline ):
    result = db.vegas.aggregate(pipeline)
    return result 
 
 
if __name__ == '__main__': 

    db = get_db('openmap')
    result = mongo_query(db, popular_cuisine_pipe())
#    result = mongo_query(db, top_contributing_user_pipe())
#    result = db.vegas.aggregate(top_contributing_user_pipe())
#    result = mongo_query(db, top_amenities_pipe())
#    result = mongo_query(db, unique_users_pipe())
#    result = mongo_query(db, num_one_time_users_pipe())
#    result = db.vegas.distinct("created.user")
#    print len(db.vegas.distinct("created.user"))
#    print db.vegas.distinct({"$created.user"})
#    print "Unique users: %s" %(mongo_query(db, unique_users_pipe()))
#    
#    print "Number of docs: %s" %(db.vegas.find().count()) 
#    print "Number of nodes: %s" %(db.vegas.find({"type" : "node"}).count()) 
#    print "Number of ways: %s" %(db.vegas.find({"type" : "way"}).count())
    
    
#    print "Top user: %s" %(db.vegas.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, sort:{"count": ­1 }}, {"$limit":1}]))
#    print  db.vegas.distinct({"created.user"}).length # function was created for this
#    
#    
##    count = 0
    for i in result:
        if count < 1000:
            pprint.pprint(i)
            count += 1
