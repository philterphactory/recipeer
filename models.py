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

class DateQuantities(models.Model):
    """Keep track of each day's approximate calories and cost..."""
    weavr_token= models.ForeignKey('webapp.AccessToken',
                                             related_name='day_calories_weavr')
    date = models.DateField()
    calories = models.IntegerField(default=0)
    cost = models.FloatField(default=0.0)

def increase_todays_quantities(token, cost, calories):
    """Increase today's approximate calorie count and total expenditure"""
    today = datetime.date.today()
    count, created = DateQuantities.objects.get_or_create(weavr_token=token,
                                                          date=today)
    count.cost += cost
    count.calories += calories
    count.save()

def increase_todays_expenditure(weavr, amount):
    """Increase today's approximate calorie count"""
    count = DayCalories.objects.get_or_create(weavr_token=weavr_token,
                                              date=datetime.date.today())
    count.calories += amount
    count.save()
