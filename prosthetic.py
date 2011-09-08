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

import recipeer
import models


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
                recipe, details, total_price, total_calories = recipeer.random_recipe()
                logging.info("posting new recipe: %s" % recipe)
                logging.info("with details: %s" % details)
                self.post("/1/weavr/post/", {
                        "category":"article",
                        "title":recipe,
                        "body":details, 
                        "keywords":state["emotion"],
                        })
                details = models.MealDetails(weavr_token=self.token,
                                             cost=total_price,
                                             calories=total_calories)
                details.save()
                result = "posted recipe"
            else:
                result = "Not posting recipe, asleep"
        except recipeer.NoIngredientsException, e:
            result = "No ingredients could be found matching recipe."
        return result

