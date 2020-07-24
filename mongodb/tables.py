
from pymongo.mongo_client import MongoClient
import pymongo

tables = [
        {
            "table_name" : "users",
            "id" : "email",
            "constraints" : {
                "username" : "unique",
            }
        },
        {
            "table_name" : "SessionStore",
            'id' : 'session_key',
            "constraints" : {
                "foreign_key" : "users",
            }
        },
        {
            'table_name' : "otp",
            'id' : 'otp',
            "constraints": {
                "foreign_key" : "users",
            }
        },
        {
            'table_name' : "forgototpsignatures",
            'id' : 'signature',
        },
        {
            'table_name' : "slots",
            'id' : 'slot_id',
        },
        {
            'table_name' : 'appointement_helper',
            'id' : 'id',
        },
        {
            'table_name' : 'appointments',
            'id' : 'app_id',
        },
        {
            'table_name' : 'doctor',
            'id':'doc_id'
        },
        {
            'table_name' : 'Cities',
            'id':'city_id'
        },
        {
            'table_name' : 'Specilizations',
            'id':'spec_id'
        },
        {
            'table_name' : 'med',
            'id' : 'med_id',
        },
        {
            'table_name' : 'symp',
            'id' : 'symp_id',
        },
        {
            'table_name' : 'pres_table',
            'id' : 'app_id',
        },
        {
            'table_name' : 'transaction',
            'id' : 'order_id',
        },
    ]

def migrate():
    db = MongoClient().doca

    for table in tables:

        collist = db.list_collection_names()
        if table['table_name'] not in collist:
            print(table['table_name'])
            myTable = db[table['table_name']]
            if 'id' in table:
                myTable.create_index([(table['id'], pymongo.ASCENDING)],unique=True)
