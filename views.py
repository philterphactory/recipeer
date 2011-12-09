from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson
from models import RecipeOptions
import recipeer

#noinspection PyUnusedLocal
@login_required
def ensure_recipe_options_defaults(request):
    RecipeOptions.ensure_defaults()
    return HttpResponse(u"done")


def random_recipe(request):
    recipe, details, total_price, total_calories = recipeer.random_recipe()
    ctx = {
        'recipe': recipe,
        'details': details,
        'total_price': total_price,
        'total_calories': total_calories
    }
    content = simplejson.dumps(ctx, indent=4)
    return HttpResponse(content, content_type='application/json')
