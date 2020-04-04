from pymongo.mongo_client import MongoClient
from .Exceptions import TableNotFoundError
from pymongo.errors import BulkWriteError

class Table(object):
    
    class Scan(object):
        
        def __init__(self,table,FilterExpression={},Projection=[]):
            self.FilterExpression =FilterExpression
            self.Projection = Projection
            self.table = table
            if len(Projection)==0:
                self.results = self.table.find(FilterExpression)
            
            else: 
                pr = {}
                for i in Projection:
                    pr[i] = 1
                self.results = self.table.find(FilterExpression,pr)
            
        def values(self):
            count = 0
            items = []
       
            for item in self.results:
                items.append(item)
                count+=1
                
            return {
                "Count" : count,
                "Items" : items,
            }
            
        def limit(self,value):
            count = 0
            items = []
       
            for item in self.results.limit(value):
                items.append(item)
                count+=1
                
            return {
                "Count" : count,
                "Items" : items,
            }
                
        def sort(self,field):
            order = -1 if field[0] == '-' else 1
            label = field[1:] if field[0] == '-' else field
            count = 0
            items = []
       
            for item in self.results.sort(field,order):
                items.append(item)
                count+=1
                
            return {
                "Count" : count,
                "Items" : items,
            }    
    
    def __init__(self,tablename,):
        db = MongoClient().doca
        collist = db.list_collection_names()
        if tablename in collist:
            self.table = db[tablename]
        else:
            raise TableNotFoundError
            
    def update(self,FilterExpression={},UpdateExpression={}):
        self.table.update_many(FilterExpression,{"$set":UpdateExpression})

    def delete(self,FilterExpression={}):
        self.table.delete_many(FilterExpression)
    
    def scan(self,FilterExpression={},Projection=[]):
        return self.Scan(self.table,FilterExpression,Projection)
        
    def insertValues(self,values=[]):
        try:
            self.table.insert_many(values)
        
        except BulkWriteError as bwe:
            print(bwe.details)
            
        