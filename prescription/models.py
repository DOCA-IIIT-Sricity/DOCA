from django.db import models

# Create your models here.
class prescription(models.Model):
    symptoms = models.TextField()
    Notes = models.TextField()
    Tabs = models.TextField()