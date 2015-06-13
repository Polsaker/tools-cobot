#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from urllib import urlencode
from urllib import quote_plus
import _tools
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, ValidationError
from flask import render_template

class Script(object):
    def __init__(self, config):
        self.mediawiki = _tools.MediaWikiAPI(config['mwuser'], config['mwpass'])
        self.mediawiki.login()
    
    def execute(self, app, request):
        self.addSubst(request.form['name'])
        return "OK!"
    
    def render(self, app, request):
        form = SubstForm()
        if form.validate_on_submit():
            return self.execute(app, request)
            
        return render_template('subst.html', form=form)

    def addSubst(self, plantilla):
        COSO = plantilla
        syns = '(?:'
        try:
            synonims = json.loads(self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=query&prop=redirects&titles={0}&rdnamespace=10&rdlimit=500&format=json".format(quote_plus(COSO))))
            synonims = synonims['query']['pages'][next(iter(synonims['query']['pages']))]['redirects']
            for synomim in synonims:
                f = synomim['title'].replace("Plantilla:",'')
                syns += "(?:" + f[0].lower() + "|" + f[0].upper() + ")" + f[1:] + "|"
        except:
            pass
        f = COSO.replace("Plantilla:",'')
        syns += "(?:" + f[0].lower() + "|" + f[0].upper() + ")" + f[1:] + ")"


        linkeds = json.loads(self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=query&prop=transcludedin&titles={0}&tinamespace=1|3|5|11|15|101|103|105&tishow=!redirect&tilimit=500&format=json".format(quote_plus(COSO))))
        try:
            linkeds = linkeds['query']['pages'][next(iter(linkeds['query']['pages']))]['transcludedin']
        except:
            return
            
        for page in linkeds:
            pagina = json.loads(self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=query&prop=revisions&titles={0}&rvprop=content&format=json".format(quote_plus(page['title']))))['query']['pages'][str(page['pageid'])]['revisions'][0]['*']
            pagina = re.sub('{{(?:Plantilla\:)?' + syns + "(\||})", '{{subst:' + COSO.replace("Plantilla:",'') + r"\1", pagina)
            #pagina = pagina.replace("{{" + COSO.replace("Plantilla:",''), "{{subst:" + COSO.replace("Plantilla:",''))
            params = {"minor": '', "bot": '', "pageid": page['pageid'], "text": pagina, "token": gettoken(), "summary": "Bot: Añadiendo \"subst:\"."}
            rec = self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=edit&format=json", params)
            print(rec)
            #print(pagina)


class SubstForm(Form):
    name = StringField('Plantilla', validators=[DataRequired()])
    
    def validate_name(form, field):
        if not field.data.startswith("Plantilla:"):
            raise ValidationError("Eso no es una plantilla!")
