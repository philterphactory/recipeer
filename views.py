from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from models import RecipeOptions

#noinspection PyUnusedLocal
@login_required
def ensure_recipe_options_defaults(request):
    RecipeOptions.ensure_defaults()
    return HttpResponse(u"done")
