from django.conf.urls.defaults import patterns

import views

urlpatterns = patterns('',
    ( r"^admin/ensure_recipe_options_defaults/?$", views.ensure_recipe_options_defaults ),
    ( r"^random_recipe/?$", views.random_recipe ),
)

