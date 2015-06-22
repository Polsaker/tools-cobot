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
import thread


class Script(object):
    def __init__(self, config):
        self.mediawiki = _tools.MediaWikiAPI(config['mwuser'], config['mwpass'])
    
    def execute(self, app, request):
        self.logger = app.cosoEventLogger("trasladar.py", request.form['description'])
        self.mediawiki.login()
        thread.start_new_thread(self.trasladar, (request.form['pfrom'], request.form['to']))
        return render_template('taskProgress.html', taskId=self.logger.logentry.id)
    
    def render(self, app, request):
        form = SubstForm()
        if form.validate_on_submit():
            return self.execute(app, request)
            
        return render_template('trasladar.html', form=form)

    def trasladar(self, pfrom, to):
        lista = self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=query&list=backlinks&bllimit=1000&format=json&bltitle=" + quote_plus(pfrom.encode('utf-8')))
        lista = json.loads(lista)

        reg = re.compile(u"(?i)\[\[\s*" + re.escape(pfrom))
        
        percentadv = 100 / float(len(lista['query']['backlinks']))
        currper = 0

        for page in lista['query']['backlinks']:
            currper += percentadv
            self.logger.setProgress(currper)

            pagina = json.loads(self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=query&prop=revisions&titles={0}&rvprop=content&format=json&redirects".format(quote_plus(page['title'].encode('utf-8')))))['query']['pages']
            pagina = pagina[next(iter(pagina))]['revisions'][0]['*']
            
            pagina = reg.sub("[[" + to, pagina)
            
            params = {"minor": '', "bot": '', "pageid": page['pageid'], "text": pagina, "token": self.mediawiki.gettoken(), "summary": "Bot: Moviendo enlaces."}
            rec = self.mediawiki.request("https://es.wikipedia.org/w/api.php?action=edit&format=json", params)
        self.logger.finished()

        
class SubstForm(Form):
    pfrom = StringField(u'Página a trasladar', validators=[DataRequired()])
    to = StringField(u'Destino', validators=[DataRequired()])
    description = StringField(u'Razón para lanzar el script', validators=[DataRequired()])

    #def validate_category(form, field):
    #    if not field.data.startswith("Categoría:"):
    #        raise ValidationError("Eso no es una categoría!")
