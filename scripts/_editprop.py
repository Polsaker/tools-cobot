#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _tools
import json

# Obtener la proporción de ediciones del usuario por namespace
class Editprop(object): 
    def __init__(self, config):
        self.mediawiki = _tools.MediaWikiAPI(config['mwuser'], config['mwpass'])
        self.mediawiki.login()

           
    def getProp(self, user):
        self.listita = {}
        self.total = 0
        self.getcontrib(user)
        final = {}
        for i in self.listita:
            final[i] = (self.listita[i] / float(self.total)) * 100
        return final
        
    def getcontrib(self, user, ucc=""):
        global listita
        res = json.loads(self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=query&list=usercontribs&ucuser={0}&ucprop=title&format=json&uclimit=5000".format(user) + ucc))
        
        for page in res['query']['usercontribs']:
            try:
                self.listita[page['ns']] += 1
            except:
                self.listita[page['ns']] = 1
            self.total += 1
        try:
            self.getcontrib(user, "&uccontinue=" + res['query-continue']['usercontribs']['uccontinue'])
        except:
            pass
