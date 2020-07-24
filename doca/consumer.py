import asyncio
import json
from django.conf import Settings
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class Cities(AsyncConsumer):
    async def websocket_connect(self,event,):
        print("connected",event)
        await self.send({
            "type":"websocket.accept"
        })
    
    async def websocket_receive(self,event):
        print("receive",event)
    
    async def websocket_disconnect(self,event):
        print("disconnected",event)
        
        
def findCities(City):
    table = Table('Cities')
    cities = table.scan().values()
    res = []
    for city in cities:
        if city['city'].contains(City):
            res.append({
                "city": city['city'],
                "state":city['state']
            })
        
        