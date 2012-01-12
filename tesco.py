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
import urllib

# python 2.6
try:
    from django.utils import simplejson as json
except ImportError:
    import json

try:
    from google.appengine.api import urlfetch
    
    def fetch_url (url):
        return (urlfetch.fetch(url.encode('utf-8'), deadline=10).content)
except:
    import urllib
    
    def fetch_url (url):
        return (urllib.urlopen(url.encode('utf-8')).read())


class TescoApi(object):
    QUERY_ROOT = "https://secure.techfortesco.com/groceryapi_b1/restservice.aspx"
    
    def __init__(self, email, password, dev_key, app_key):
        '''Tesco Direct email and password, Tesco API dev and app keys'''
        self.session_key = None
        login_response = self.get_json("LOGIN", {'email':email,
                                                 'password':password,
                                                 'developerkey':dev_key,
                                                 'applicationkey':app_key})
        if login_response:
            self.session_key = login_response.get('SessionKey')
    
    def get_json(self, command, query_dict):
        '''Get the parsed json response from the server'''
        query_dict['command'] = command
        if self.session_key:
            query_dict['sessionkey'] = self.session_key
        query = "%s?%s" % (TescoApi.QUERY_ROOT, urllib.urlencode(query_dict))
        logging.info(query)
        response = fetch_url(query)
        logging.info(response)
        return json.loads(response)
    
    def product_search(self, search_for, extended=False):
        '''Get the parsed json of the product search result'''
        query_dict = {'searchtext':urllib.quote_plus(search_for),
                      'page':1}
        if extended:
            query_dict['extendedinfo'] = 'Y'
        return self.get_json('PRODUCTSEARCH', query_dict)
