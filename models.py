import datetime
import logging
import string

from django.db import models
from google.appengine.api import memcache


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
    when = models.DateTimeField(default=datetime.datetime.now())
    calories = models.IntegerField(default=0)
    cost = models.FloatField(default=0.0)


class RecipeOptions(models.Model):
    VALID_OPTIONS = (
        ('meal', 'Meal'),
        ('desire', 'Desire'),
        ('amount', 'Amount'),
        ('fruit', 'Fruit'),
        ('vegetable', 'Vegetable'),
        ('meat', 'Meat'),
        ('dairy', 'Dairy'),
        ('format', 'Format'),
        ('side', 'Side'),
        ('drink', 'Drink'),
        ('tag', 'Tag')
    )
    VALID_OPTION_NAMES = tuple([x[0] for x in VALID_OPTIONS])
    cache_key = 'recipeer__RecipeOptions__get_option_%s'
    name = models.CharField(max_length=128, primary_key=True) #, choices=VALID_OPTIONS)
    updated = models.DateTimeField(auto_now=True)
    option_list = models.TextField(help_text=u"Newline-seperated list of option values")

    def save(self, **kwargs):
        options = set([x.strip() for x in string.split(self.option_list, '\n') if x.strip() != ''])
        self.option_list = '\n'.join(options)
        models.Model.save(self, **kwargs)
        memcache.delete(self.cache_key)

    @classmethod
    def get_option(cls, name):
        if not name in cls.VALID_OPTION_NAMES:
            raise ValueError(u"%s is not a valid option" % name)
        cache_key = cls.cache_key % name
        cache_result = memcache.get(cache_key)
        if cache_result:
            return cache_result
        all = list(cls.objects.filter(name=name).order_by('-updated'))
        if not all:
            import data
            result = list(getattr(data, '%s_options' % name, []))
        else:
            result = string.split(all[0].option_list, '\n')
        memcache.set(cls.cache_key, result)
        return result

    @classmethod
    def ensure_defaults(cls):
        import data
        for k in cls.VALID_OPTION_NAMES:
            result = list(getattr(data, '%s_options' % k))
            logging.debug("%s defaults is: %r" % (k, result))
            v = '\n'.join([x.strip() for x in result])
            cls.objects.get_or_create(name=k, defaults={'option_list':v})
