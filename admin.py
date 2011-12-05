from django.contrib import admin

from models import Config, RecipeOptions

class RecipeOptionsAdmin(admin.ModelAdmin):
    list_display = ['name', 'option_list']
    list_editable = ['option_list']

admin.site.register(Config)
admin.site.register(RecipeOptions, RecipeOptionsAdmin)
