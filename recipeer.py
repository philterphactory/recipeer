# Copyright (C) 2011 Philter Phactory Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X
# CONSORTIUM BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of Philter Phactory Ltd. shall
# not be used in advertising or otherwise to promote the sale, use or other
# dealings in this Software without prior written authorization from Philter
# Phactory Ltd.

import logging
import random
import re

from django.utils.html import escape

import tesco
import models

class NoSuitableProduct(Exception):
    """No suitable food product could be found"""
    pass

class NoIngredientsException(Exception):
    """No matching ingredients whatsoever could be found"""
    pass

def tesco_api(): 
    '''Create a Tesco API object using the Datastore Config'''
    config = models.get_config()
    return tesco.TescoApi(config.email, config.password, config.developer_key, config.application_key)

def tesco_purchase(title, details):
    items = [detail["BaseProductId"] for detail in details]
    qty = ",".join(["1"] * len(items))
    purchase = ",".join(["PURCHASE"] * len(items))
    return "http://www.tesco.com/groceries/recipe/default.aspx?listid=%s&items=%s&qty=%s&purchase=%s" % (title, ",".join(items), qty, purchase)

def tesco_is_food(product):
    """Check whether it's cucumber, or cucumber scented product"""
    # This is not reliable. We exclude some food, e.g. Camp Coffee
    return int(product.get("NutrientsCount", "0")) != 0

def tesco_calories(extended):
    calories = int(extended['RDA_Calories_Count'])
    if (calories == 0) and (int(extended["NutrientsCount"]) > 0):
        for nutrient in extended["Nutrients"]:
            if nutrient["NutrientName"] == "Energy":
                serving = nutrient["ServingSize"]
                if serving != '-':
                    try:
                        calories = int(re.search(r"\((\d+)kcal\)", serving).group(1))
                    except Exception, e:
                        logging.info("Calorie finding failed (%s), leaving calories as zero"%str(e))
                break
    return calories

def tesco_ingredient_extended_details(api, ingredient):
    '''Get the extended details for a single item'''
    return api.product_search(ingredient['ProductId'], extended=True)

def tesco_ingredient_details(api, search):
    details = api.product_search(search)
    result = None
    if int(details['StatusCode']) == 0 and int(details['TotalProductCount']) > 0:
        products = details['Products']
        random.shuffle(products)
        for product in products:
            extended = tesco_ingredient_extended_details(api, product)
            if int(extended['StatusCode']) == 0 and int(extended['TotalProductCount']) > 0:
                extended_product = extended['Products'][0]
                if tesco_is_food(extended_product):
                    result = extended_product
                    break
    if not result:
        raise NoSuitableProduct(search)
    return result
    
def tesco_ingredients_details(api, ingredients_list):
    '''Get a list of recipe ingredients details via the Tesco API'''
    results = []
    for ingredient in ingredients_list:
        # Constrain the search to food
        food_search = "%s %s" % (ingredient, "food")
        try:
            results.append(tesco_ingredient_details(api, food_search))
        except NoSuitableProduct, e:
            logging.info("Couldn't find suitable product for %s" % ingredient)
    return results

def maybe(fun, probability=0.5, default=None):
    """Call fun with args if random(0..1) is less than probability."""
    result = default
    if random.random() < probability:
        result = fun()
    return result

def choose_one_of(choices):
    """Choose one of the parameters randomly."""
    return random.choice(choices)

def maybe_choose_one_of(choices, probability=0.5):
    """Choose one of the list or return None."""
    result = None
    if random.random() < probability:
        result = choose_one_of(choices)
    return result

def singular_for(the_string):
    singular = "a"
    if the_string and the_string[0] in "aeiouAEIOU":
        singular = "an"
    return singular

def singular_or_plural_for(the_string):
    result = "some"
    if the_string[-1] != "s":
        result = singular_for(the_string)
    return result

def nice_list(items):
    if len(items) == 1:
        result = items[0]
    elif len(items) == 2:
        result = " and ".join(items)
    else:
        result = "%s and %s " % ( ", ".join(items[:-1]), items[-1])
    return result

def meal_moment():
    return maybe_choose_one_of(models.RecipeOptions.get_option('meal'))

def desire():
    return choose_one_of(models.RecipeOptions.get_option('desire'))

def amount():
    return choose_one_of(models.RecipeOptions.get_option('amount'))

def fruit():
    return choose_one_of(models.RecipeOptions.get_option('fruit'))

def vegetable():
    return choose_one_of(models.RecipeOptions.get_option('vegetable'))

def meat():
    return choose_one_of(models.RecipeOptions.get_option('meat'))

def dairy():
  return choose_one_of(models.RecipeOptions.get_option('dairy'))

def meal_format():
  return choose_one_of(models.RecipeOptions.get_option('format'))

def side_dish():
    return "with %s" % choose_one_of(models.RecipeOptions.get_option('side'))

def drink():
    maybe(lambda : "With %s." % choose_one_of(models.RecipeOptions.get_option('drink')))

def tags():
    return maybe_choose_one_of(models.RecipeOptions.get_option('tag'))

def ingredients():
    return random.sample([fruit(), vegetable(), meat(), dairy()], random.randint(1, 4))

def recipe_description(ingredients_list):
    return " ".join(filter(bool, [meal_moment(),
                                  desire(),
                                  amount(),
                                  nice_list(ingredients_list),
                                  meal_format(),
                                  side_dish()])) + "."

def capitalize_start(string):
    words = string.split()
    words[0] = words[0].capitalize()
    return " ".join(words)

def tesco_product_url(product_id):
    '''Construct a url on the Tesco site for a product id'''
    return "http://www.tesco.com/groceries/Product/Details/?id=%s" % product_id

def recipe_details(ingredients_list):
    '''Create a body for the post using details from the Tesco API'''
    api = tesco_api()
    ingredients_details = tesco_ingredients_details(api, ingredients_list)
    if not ingredients_details:
        raise NoIngredientsException()

    details = ""
    total_price = 0.0
    total_calories = 0
    for detail in ingredients_details:
        price = round(float(detail['Price']), 2)
        total_price += price
        product_url = tesco_product_url(detail['ProductId'])
        details += '<p>&pound;%.2f <a href="%s">%s</a>' % \
            (price, product_url, detail['Name'])
        calories = tesco_calories(detail)
        if calories:
            details += ' %s Calories (approx.)' % calories
            total_calories += calories
        details += '</p>'

    if details:
        details += "<p>&pound;%.2f <b>total</b></p>" % total_price
        if total_calories:
            details += "<p>%s Calories <b>total</b> (approx)</p>" % \
                total_calories

    for detail in ingredients_details:
        product_url = tesco_product_url(detail['ProductId'])
        image_url = detail['ImagePath']
        details += '<a href="%s"><img src="%s"></a>&nbsp;'%(escape(product_url), escape(image_url))
    details += '<p><a href="%s">Click here</a> to buy these items.</p>'%escape(tesco_purchase("Weavr Recipe Ingredients", ingredients_details))
    return details, total_price, total_calories

def random_recipe():
    '''A possible (albeit often improbable) recipe title and description'''
    ingredients_list = ingredients()
    drink_item = drink()
    if drink_item:
        ingredients_list.append(drink_item)
    description = " ".join(filter(bool, [recipe_description(ingredients_list),
                                         tags()]))
    recipe = capitalize_start(description)
    details, total_price, total_calories = recipe_details(ingredients_list)
    return recipe, details, total_price, total_calories
