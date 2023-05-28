import os
from IResult import IResult
from pymongo import MongoClient
from bson.objectid import ObjectId
print(os.environ['DB_URL'])
client = MongoClient(os.environ['DB_URL'], 
                     username='root', 
                     password='admin',
                    authSource="admin")
results = client.LCT.results

def Save(result):
    if 'id' in result:
        result['_id'] = result['id']
        result.pop('id')
    result_id = results.insert_one(result).inserted_id
    return str(result_id)

def Delete(id):
    result_id = results.delete_one({'_id': ObjectId(id)})
    return str(result_id)

def Get(id):
    result = results.find_one({'_id': ObjectId(id)})
    if result is None:
        return False
    result['id'] = str(result['_id'])
    result.pop('_id')
    return result

def Getall():
    result = results.find()

    return result
