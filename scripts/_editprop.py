#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _tools
import json

# Obtener la proporción de ediciones del usuario por namespace
class Editprop(object): 
    def __init__(self, config):
        self.wikis = json.load(open("wikis.json"))
        self.mediawiki = _tools.MediaWikiAPI(config['mwuser'], config['mwpass'])

           
    def getProp(self, user):
        wiki = self.getWiki(user)
        self.listita = {}
        self.total = 0
        self.getcontrib(user, wiki)
        final = {}
        for i in self.listita:
            final[i] = {'perc': (self.listita[i] / float(self.total)) * 100, 'total': self.listita[i]}
        return final
        
    def getcontrib(self, user, wiki, ucc=""):
        global listita
        res = json.loads(self.mediawiki.request("https://" + wiki + "/w/api.php?action=query&list=usercontribs&ucuser={0}&ucprop=title&format=json&uclimit=5000&rawcontinue=".format(user.encode('utf-8')) + ucc))
        
        for page in res['query']['usercontribs']:
            try:
                self.listita[page['ns']] += 1
            except:
                self.listita[page['ns']] = 1
            self.total += 1
        try:
            self.getcontrib(user, wiki, "&uccontinue=" + res['query-continue']['usercontribs']['uccontinue'])
        except:
            pass
    
    def getWiki(self, artname):
        # Por defecto
        lang = "es"
        wiki = "wikipedia" 
        artname = artname.replace("%3A", ":")
        q = artname.split(":")
        for i, l in enumerate(q):
            for p in self.wikis:
                if p == l:
                    try:
                        wiki = self.wikis[p]['aliasof']
                    except:
                        wiki = p
                    break
        
        if self.wikis[wiki]['langs'] == []:
            return self.wikis[wiki]['url']
            
        for i, l in enumerate(q):
            for p in self.wikis[wiki]['langs']:
                if p == l:
                    lang = p
        return "{0}.{1}".format(lang, self.wikis[wiki]['url'])

