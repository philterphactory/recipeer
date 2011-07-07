import datetime

from django.db import models


class Config(models.Model):
    email = models.CharField(max_length=127)
    password = models.CharField(max_length=127)
    developer_key = models.CharField(max_length=127)
    application_key = models.CharField(max_length=127)
    

def get_config():
    configs = Config.objects.order_by('-id')
    return configs[0]

class MealDetails(models.Model):
    """Keep track of each meal's approximate calories and cost..."""
    weavr_token= models.ForeignKey('webapp.AccessToken',
                                   related_name='day_calories_weavr')
    when = models.DatetimeField(default=datetime.datetime.now())
    calories = models.IntegerField(default=0)
    cost = models.FloatField(default=0.0)
