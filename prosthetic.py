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
import re

from base_prosthetic import Prosthetic

import recipeer
import models


class Recipeer(Prosthetic):
    '''A prosthetic that publishes innovative recipe ideas.'''

    @classmethod
    def time_between_runs(cls):
        return 3600 * 4

    def is_awake(self, state):
        logging.info("awake state is %r"%state["awake"])
        return state['awake']

    def should_post(self, state):
        return self.is_awake(state)

    def act(self, force=False):
        result = "Failed to post recipe."
        try:
            state = self.get("/1/weavr/state/")
            if not self.should_post(state):
                return "Not posting recipe, asleep"

            recipe, details, total_price, total_calories = recipeer.random_recipe()
            logging.info("posting new recipe: %s" % recipe)
            logging.info("with details: %s" % details)
            self.post("/1/weavr/post/", {
                "category":"article",
                "title":recipe,
                "body":details, 
                "keywords":state["emotion"],
            })
            details = models.MealDetails(weavr_token=self.token, cost=total_price, calories=total_calories)
            details.save()
            return "posted recipe"

        except recipeer.NoIngredientsException, e:
            return "No ingredients could be found matching recipe."

