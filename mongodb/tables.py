
from pymongo.mongo_client import MongoClient
import pymongo

def migrate():
    db = MongoClient().doca
    
    tables = [
        {
            "table_name" : "users",
            "id" : "email",
            "constraints" : [
                "username":"unique"
            ]
        },
        {
            "table_name" : "SessionStore",
            'id' : 'session_key',
        },
        {
            'table_name' : "otp",
            'id' : 'otp',
        },
        {
            'table_name' : "forgototpsignatures",
            'id' : 'signature',
        }
    ]
    
    for table in tables:
        
        collist = db.list_collection_names()
        if table['table_name'] not in collist:
            print(table['table_name'])
            myTable = db[table['table_name']]
            if 'id' in table:
                myTable.create_index([(table['id'], pymongo.ASCENDING)],unique=True)
            