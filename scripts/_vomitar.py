#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _tools
from .. import app
from urllib import quote_plus

# Esto sirve para que sea mas fácil ejecutar desde la lína de comandos (cron, etc)

class Vomitador(object):
    def __init__(self, config, logger):
        if logger:
            self.logger = logger
        else:
            self.logger = app.EventLogger("vomitar.py", "Volcado automático", True)
            
        self.mediawiki = _tools.MediaWikiAPI(config['mwuser'], config['mwpass'])
        

    def vomitar(self, arbolito, balde):
        arbolito = res[0]
        balde = res[1]
        
        page = ""
        page2 = ""
        parent = self.mediawiki.request("http://es.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=" + quote_plus(arbolito) + "&prop=info&cmprop=title&cmlimit=5000&format=json")
        parent = json.loads(parent)
        
        percentadv = 100 / float(len(parent['query']['categorymembers']))
        currper = 0
        
        for child in parent['query']['categorymembers']:
            currper += percentadv
                
            self.logger.setProgress(currper)
            
            if child['ns'] == 14:
                page = page + "\n" + self.explorecat(child['title'], 2)
                if page[-2:] == "• ":
                    page = page[:-2]
            else:
                page2 = page2 + "[[" + child['title'] + "]] • "
                
        if page2[-2:] == "• ":
            page2 = page[:-2]
        page = page2 + page
        params = {"title": balde, "text": page, "token": self.mediawiki.gettoken(), "summary": "Bot: Volcando categorías"}
        rec = self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=edit&format=json", params)
        self.logger.finished()

    def explorecat(self, cat, level):
        if level == 6:
            return ""

        toreturn = "=" * level + "[[:" + cat + "]]" + "="*level + "\n" # titulo
        parent = json.loads(self.mediawiki.request("http://es.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=" + quote_plus(cat) + "&prop=info&cmprop=title&cmlimit=5000&format=json"))
        for child in parent['query']['categorymembers']:

            if child['ns'] == 14:
                
                if toreturn[-2:]== "• ":
                    toreturn = toreturn[:-2]
                adding = self.explorecat(child['title'], level + 1)
                if adding != "":
                    toreturn = toreturn + "\n" + adding
            else:
                toreturn = toreturn + "[[" + child['title'] + "]] • "
        
        return toreturn

if __name__ == "__main__":
    import sys
    try:
        res = " ".join(sys.argv[1:]).replace("‎", "")[2:-2].split("]] [[")
    except:
        raise Exception("Entrada invalida")
    
    config = json.load(open("../config.json"))
    
    Vomitador(config, False).vomitar(res[0], res[1])
