from django.db import models

# Create your models here.
from mongoengine import *

class slots(Document):
    slot_id = models.CharField(max_length=200)
    
class slots_available(Document):
    id = models.CharField(max_length=200)

class appointments(Document):
    app_id = models.CharField(max_length=200)