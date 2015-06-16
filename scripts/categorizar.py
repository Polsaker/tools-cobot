#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from urllib import urlencode
from urllib import quote_plus
import _tools
from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from flask import render_template

class Script(object):
    def __init__(self, config):
        self.mediawiki = _tools.MediaWikiAPI(config['mwuser'], config['mwpass'])
    
    def execute(self, app, request):
        self.logger = app.cosoEventLogger("categorizar.py")
        self.mediawiki.login()
        self.categorize(request.form['pages'], request.form['category'])
        return "OK!"
    
    def render(self, app, request):
        form = SubstForm()
        if form.validate_on_submit():
            return self.execute(app, request)
            
        return render_template('categorizar.html', form=form)

    def categorize(self, pages, category):
        pages = pages.replace("[", '').replace("]", '').replace('\r', '').split("\n")
        category = category.replace('[', '').replace(']', '').split(":")[1]
        
        reg = re.compile(u"\[\[(categoría|Categoría|Category|category):\s*" + category + u"\‎?\s*(\|.+)?\]\]")
        
        for page in pages:
            pagina2 = json.loads(self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=query&prop=revisions&titles={0}&rvprop=content&format=json".format(quote_plus(page.encode('utf8')))))['query']['pages']
            try:
                pagina = pagina2[next(iter(pagina2))]['revisions'][0]['*']
            except:
                self.logger.appendLog(page + ": Error. " + str(pagina2))
                self.logger.warning()
                continue
            
            if not reg.search(pagina):
                pagina += u"\n[[Categoría:" + category + "]]"
                params = {"minor": '', "bot": '', "pageid": list(pagina2)[0], "text": pagina, "token": self.mediawiki.gettoken(), "summary": "Bot: Añadiendo categoría."}
                rec = self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=edit&format=json", params)
                self.logger.appendLog(page + ": OK?. " + str(rec))
            else:
                self.logger.appendLog(page + ": Category exists.")
        self.logger.finished()

class SubstForm(Form):
    pages = TextAreaField('P&aacute;ginas', validators=[DataRequired()])
    category = StringField('Categor&iacute;a', validators=[DataRequired()])

    #def validate_category(form, field):
    #    if not field.data.startswith("Categoría:"):
    #        raise ValidationError("Eso no es una categoría!")
