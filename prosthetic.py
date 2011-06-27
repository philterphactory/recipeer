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

from base_prosthetic import Prosthetic
from django.template.loader import render_to_string
import logging
import random
import re
import time
import urllib

import models
import tesco

def tesco_api(): 
    '''Create a Tesco API object using the Datastore Config'''
    config = models.get_config()
    return tesco.TescoApi(config.email, config.password, config.developer_key,
                         config.application_key)

def tesco_ingredients_details(api, ingredients_list):
    '''Get a list of recipe ingredients details via the Tesco API'''
    results = []
    for ingredient in ingredients_list:
        # Constrain the search to food
        food_search = "%s %s" % (ingredient, "food")
        details = api.product_search(ingredient)
        if details['StatusCode'] == 0 and \
                details['TotalProductCount'] > 0:
            results.append(random.choice(details['Products']))
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
    if the_string and the_string[0] in "aeioUAEIOU":
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
    return maybe_choose_one_of(("For breakfast,",
                                "Um, for mid morning,",
                                "For lunch,",
                                "Aha! For a snack -",
                                "For dinner...",
                                "For a late snack,",
                                "If I have a late dinner,",
                                "For a midnight snack:",
                                "After the game -",
                                "Naughty, but before bed",
                                "It's been a long day -",
                                "Before the game on TV",
                                "By myself tonight -",
                                "Home alone:",
                                "If the olds come over",
                                "Next week:",
                                "Next Sunday,",
                                "Next Friday,",
                                "On Sunday morning",
                                "For Sunday lunch,",
                                "For Sunday #brunch",
                                "For tomorrow,",
                                "For tomorrow morning,",
                                "For tomorrow lunchtime,",
                                "For tomorrow night",
                                "If they arrive early,",
                                "I had this the other day:",
                                "If I have company tonight",
                                "Oo0oh, I know what I want:",
                                "Yes!",
                                "#nomnomnom",
                                "Watching #Seinfeld;",
                                "Watching #CYE;",
                                "Watching The Wire,",
                                "Peckish.",
                                "Watching #TopGear",
                                "Gotta eat now,",
                                "#woohoo",
                                "Just watched some Keith Floyd,",
                                "Just reading about Heston Blumenthal,",
                                "Just been blogging. Now",
                                "Back home,",
                                "Going home,",
                                "Going to see friends,",
                                "Back home,",
                                "Going out,"))

def desire():
    return choose_one_of(("gotta get the recipe for",
                          "can I haz",
                          "I fancy",
                          "I would like",
                          "I could do with",
                          "I'm tempted to try",
                          "I would murder",
                          "I would luv",
                          "damn, I'm in the mood for",
                          "we should all have",
                          "gotta have",
                          "serving",
                          "making",
                          "thinking of",
                          "def o wants",
                          "I love the idea of",
                          "I'd love",
                          "I want",
                          "I could guzzle",
                          "I could murder",
                          "I would love",
                          "wantz",
                          "planning a dinner party of",
                          "planning a lunch of",
                          "in search of",
                          "planning a soiree: considering",
                          "hey #lazytweet, I'm looking for the recipe to",
                          #"@Hestonfatduck inspired me! Having",
                          #"@Hestonfatduck inspired me to try",
                          #"hi @Hestonfatduck - I'm looking for the recipe to",
                          #"@Jamie_Oliver inspired me to make",
                          #"@Jamie_Oliver inspired us to cook",
                          #"@Jamie_Oliver inspired me to try",
                          #"@matkiwi inspired me to cook",
                          #"@tomaikens inspired me. Cooking",
                          #"@tomaikens inspired me to try",
                          #"@foodphilosophy I'd say #sexonaplate is",
                          #"@foodphilosophy for the next #sexonaplate could you serve",
                          ))

def amount():
    return choose_one_of(("some",
                          "a healthy portion of",
                          "an unhealthy portion of",
                          "a tub of",
                          "a plate of",
                          "a bit of",
                          "a little",
                          "loads of",
                          "a bucket of",
                          "a tiny bit of",
                          "a tidy plate of",
                          "a posh serving of",
                          "a decent",
                          "a bowl of",
                          "a slice of",
                          "a portion of",
                          "a side of",
                          "more of",
                          "a big plate of",
                          "a small plate of",
                          "a tiny plate of",
                          "a huge plate of",
                          "a huge bowl of"))

def fruit():
    # http://en.wikipedia.org/wiki/List_of_culinary_fruits
    return choose_one_of(("apple",
                          "pear",
                          "grapefruit",
                          "lemon",
                          "orange",
                          "kiwi",
                          "apple",
                          "hawthorn",
                          "loquat",
                          "pear",
                          "quince",
                          "apricot",
                          "cherry",
                          "chokeberry",
                          "greengage",
                          "peach",
                          "plum",
                          "blackberry",
                          "loganberry",
                          "raspberry",
                          "salmonberry",
                          "wineberry",
                          "bearberry",
                          "bilberry",
                          "blueberry",
                          "cranberry",
                          "huckleberry",
                          "strawberry",
                          "barberry",
                          "currant",
                          "elderberry",
                          "gooseberry",
                          "hackberry",
                          "mulberry",
                          "date",
                          "fig",
                          "grape",
                          "raisin",
                          "sultana",
                          "jujube",
                          "pomegranate",
                          "blood orange",
                          "celemetine",
                          "grapefruit",
                          "kumquat",
                          "lime",
                          "mandarin",
                          "orange",
                          "polemo",
                          "sweet lemon",
                          "tangerine",
                          "advocado",
                          "carob",
                          "guava",
                          "longan",
                          "lychee",
                          "passion fruit",
                          "avocado",
                          "banana",
                          "custard",
                          "damson",
                          "date",
                          "guarana",
                          "guava",
                          "guavaberry",
                          "hog plum",
                          "kumquat",
                          "mango",
                          "papaya",
                          "peach palm",
                          "peanut",
                          "pineapple"
                          "plantain",
                          "pummelo",
                          "pupunha",
                          "soursop",
                          "soybean",
                          "tamarind",
                          "vanilla",
                          "water apple",
                          "watermelon",
                          "mango",
                          "coconut",
                          "quince",
                          "kiwi",
                          "lychee",
                          "rhubarb",
                          "pineapple",
                          "papaya",
                          "black cherry",
                          "pawpaw",
                          "pecan",
                          "pumpkin",
                          "squash",
                          "melon",
                          "pistachio",
                          "walnut",
                          "peanut",
                          "coconut",
                          "cranberry",
                          "hazelnut",
                          "almond"))

def vegetable():
    # http://en.wikipedia.org/wiki/List_of_culinary_vegetables
    return choose_one_of(("carrot",
                          "beans",
                          "potato",
                          "turnip",
                          "leek",
                          "onion",
                          "chilli",
                          "garlic",
                          "beet greens",
                          "bok choy",
                          "broccoli",
                          "brussels sprout",
                          "cabbage",
                          "celery",
                          "ceylon spinach",
                          "chard",
                          "chaya",
                          "chickweed",
                          "chicory",
                          "chinese cabbage",
                          "cress",
                          "endive",
                          "garden rocket",
                          "kale",
                          "lettuce",
                          "sorrel",
                          "spinach",
                          "turnip greens",
                          "watercress",
                          "avocado",
                          "squash",
                          "cucumber",
                          "aubergine",
                          "bell pepper",
                          "bitter melon",
                          "courgette",
                          "cucumber",
                          "eggplant",
                          "pumpkin",
                          "sweetcorn",
                          "sweet pepper",
                          "tomato",
                          "artichoke",
                          "broccoli",
                          "cauliflower",
                          "okra",
                          "pea",
                          "peanut",
                          "runner bean",
                          "soybean",
                          "asparagus",
                          "celeriac",
                          "celery",
                          "garlic",
                          "kohlrabi",
                          "onion",
                          "lettuce",
                          "shallot",
                          "bamboo shoot",
                          "beetroot",
                          "carrot",
                          "ginger",
                          "parsnip",
                          "radish",
                          "sweet potato",
                          "wasabi",
                          "water chestnut",
                          "yam",
                          "tofu",
                          "chick pea",
                          "mash potatoes",
                          "new potatoes",
                          "sweet potatoes",
                          "gherkins",
                          "cauliflower"))

def meat():
    # http://en.wikipedia.org/wiki/List_of_meat_animals
    return choose_one_of(("beef",
                          "beef sausages",
                          "vegetarian sausages",
                          "spam",
                          "ham",
                          "pork sausages",
                          "black pudding",
                          "bacon",
                          "steak",
                          "t-bone steak",
                          "rib-eye",
                          "pork",
                          "pork trotters",
                          "pork chop",
                          "pork loin",
                          "ostrich",
                          "veal",
                          "veal sausages",
                          "duck sausages",
                          "duck",
                          "goose",
                          "dove",
                          "new world quail",
                          "ostrich",
                          "emu",
                          "guineafowl",
                          "pheasant",
                          "grouse",
                          "partridge",
                          "crow",
                          "quail",
                          "pigeon",
                          "kangaroo",
                          "lamb",
                          "goat",
                          "sea urchin",
                          "sushi",
                          "chicken wings",
                          "chicken breast",
                          "fried chicken",
                          "roast chicken",
                          "liver",
                          "kidney",
                          "chicken",
                          "sausages",
                          "turkey",
                          "salami",
                          "bratwurst",
                          "mince",
                          "fish",
                          "anchovy",
                          "bass",
                          "catfish",
                          "carp",
                          "cod",
                          "eel",
                          "flounder",
                          "fugu",
                          "grouper",
                          "haddock",
                          "halibut",
                          "herring",
                          "kingfish",
                          "mackerel",
                          "mahimahi",
                          "marlin",
                          "orange roughy",
                          "perch",
                          "pike",
                          "pollock",
                          "salmon",
                          "sardine",
                          "shark",
                          "snapper",
                          "sole",
                          "swordfish",
                          "tilapia",
                          "trout",
                          "tuna",
                          "shrimp",
                          "prawn",
                          "crab",
                          "haddock",
                          "plaice",
                          "crab paste",
                          "lobster",
                          "whitebait",
                          "black pudding",
                          "clam",
                          "mussel",
                          "oyster",
                          "scallop",
                          "snail",
                          "cuttlefish",
                          "scallops",
                          "squid",
                          "shell fish"))

def dairy():
  return choose_one_of(("custard",
                        "cream",
                        "milk",
                        "cheddar",
                        "brie",
                        "gouda",
                        "sour cream",
                        "milk",
                        "milk chocolate",
                        "white chocolate",
                        "dark chocolate",
                        "egg",
                        "soft cheese",
                        "parmesan",
                        "yogurt",
                        "creme fraiche",
                        "condensed milk",
                        "evaporated milk",
                        "ricotta cheese"))

def meal_format():
  return choose_one_of(("pie",
                        "ice cream",
                        "cake",
                        "roast dinner",
                        "crepe",
                        "sandwich",
                        "burger",
                        "cupcake",
                        "soup",
                        "noodles",
                        "flan",
                        "on biscuits",
                        "on crumpets",
                        "TV dinner",
                        "take-away",
                        "pasta",
                        "fry up",
                        "on waffles",
                        "on toast",
                        "grill",
                        "kebab",
                        "stew",
                        "porridge",
                        "fondue",
                        "dumplings",
                        "mash",
                        "salad",
                        "curry",
                        "in a roll",
                        "in a bap"))

def side_dish():
    return "with %s" % choose_one_of(("chips",
                                      "a green salad",
                                      "a tomato salad",
                                      "crisps",
                                      "pickles",
                                      "sesame seeds",
                                      "mint",
                                      "basil",
                                      "capers",
                                      "chillies",
                                      "salt and vinegar",
                                      "mayonnaise",
                                      "custard",
                                      "mustard",
                                      "gravy",
                                      "sweet and sour sauce",
                                      "curry source",
                                      "tomato ketchup",
                                      "corriander",
                                      "fennel",
                                      "garlic",
                                      "ginger",
                                      "horseradish",
                                      "lemongrass",
                                      "thyme",
                                      "spicy sauce",
                                      "soy sauce",
                                      "bacon",
                                      "bacon bits",
                                      "savory dips",
                                      "chocolate",
                                      "new potatoes",
                                      "crusty bread",
                                      "marshmallows",
                                      "rice",
                                      "a bread roll"))

def drink():
    maybe(lambda : "With %s." % choose_one_of(("a cuppa tea",
                                               "a mug of tea",
                                               "a peppermint tea",
                                               "a strong cuppa tea",
                                               "a weak cuppa tea",
                                               "an earl grey",
                                               "a black tea",
                                               "a sweet tea",
                                               "an ice tea",
                                               "a dry martini",
                                               "a dirty martini",
                                               "a bottle of Jever",
                                               "a cold beer",
                                               "a lemonade",
                                               "an orange juice",
                                               "a grape juice",
                                               "a cherry soda",
                                               "a cherry cola",
                                               "an Orangina",
                                               "a blackcurrant tango",
                                               "a 7up",
                                               "a Sprite",
                                               "an apple tango",
                                               "a red #wine",
                                               "a white #wine",
                                               "a soda",
                                               "a cola",
                                               "a #Redbull",
                                               "a vodka cola",
                                               "a coffee",
                                               "a strong coffee",
                                               "a milky coffee",
                                               "a cappuccino",
                                               "a flat white",
                                               "an espresso",
                                               "a double espresso",
                                               "a hot chocolate",
                                               "a ginger bear",
                                               "a root beer",
                                               "a root beer float",
                                               "a tequila",
                                               "a water",
                                               "an iced water and a slice of lemon",
                                               "a cranberry juice",
                                               "a gin and tonic")))

def tags():
    return maybe_choose_one_of(("#nomnomnom",
                                "#feedme",
                                "#yummy",
                                "#feedme",
                                "#plsplspls",
                                #"#140recipe",
                                "Attention #foodies",
                                "#foodie",
                                "#food",
                                ":D",
                                ";)",
                                ":)"))

def ingredients():
    return random.sample([fruit(),
                          vegetable(),
                          meat(),
                          dairy()],
                         random.randint(1, 4))

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
    details = ""
    total_price = 0.0
    #total_calories = 0.0
    for detail in ingredients_details:
        price = round(float(detail['Price']), 2)
        product_url = tesco_product_url(detail['ProductId'])
        #calories = detail['RDA_Calories_Count']
        details += '<p>&pound;%s <a href="%s">%s</a></p>' % \
            (price, product_url, detail['Name'])
        total_price += price
        #total_calories += calories
    if details:
        details += "<p>&pound;%s <b>total</b></p>" % total_price
        #details += "<p>%s Calories <b>total</b></p>" % total_calories
    for detail in ingredients_details:
        product_url = tesco_product_url(detail['ProductId'])
        image_url = detail['ImagePath']
        details += '<a href="%s"><img src="%s"></a>&nbsp;' % (product_url,
                                                              image_url)
    return details

def random_recipe():
    '''A possible (albeit often improbable) recipe title and description'''
    ingredients_list = ingredients()
    drink_item = drink()
    if drink_item:
        ingredients_list.append(drink_item)
    description = " ".join(filter(bool, [recipe_description(ingredients_list),
                                         tags()]))
    recipe = capitalize_start(description)
    details = recipe_details(ingredients_list)
    return recipe, details

class Recipeer(Prosthetic):
    '''A prosthetic that publishes innovative recipe ideas.'''

    def is_awake(self, state):
        return state['awake']

    def should_post(self, state):
        return self.is_awake(state)

    def act(self, force=False):
        result = "Failed to post recipe."
        try:
            state = self.get("/1/weavr/state/")
            if self.should_post(state):
                recipe, details = random_recipe()
                logging.info("posting new recipe: %s" % recipe)
                logging.info("with details: %s" % details)
                self.post("/1/weavr/post/", {
                        "category":"article",
                        "title":recipe,
                        "body":details, 
                        "keywords":state["emotion"],
                        })
                result = "posted recipe"
            else:
                result = "Not posting recipe, asleep"
        except Exception, e:
            logging.error("Exception in recipeer prosthetic:\n%s" % str(e))
        return result


