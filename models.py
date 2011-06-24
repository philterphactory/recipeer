from django.db import models


class Config(models.Model):
    email = models.CharField(max_length=127)
    password = models.CharField(max_length=127)
    developer_key = models.CharField(max_length=127)
    application_key = models.CharField(max_length=127)
    

def get_config():
    configs = Config.objects.order_by('-id')
    return configs[0]
