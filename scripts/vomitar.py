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

import _vomitar


class Script(object):
    def __init__(self, config):
        self.config = config
    
    def execute(self, app, request):
        self.logger = app.cosoEventLogger("vomitar.py", request.form['description'])
        thread.start_new_thread(_vomitar.Vomitador(self.config, self.logger).vomitar, (request.form['arbolito'].encode('utf-8'), request.form['balde'].encode('utf-8')))
        return render_template('taskProgress.html', taskId=self.logger.logentry.id)
    
    def render(self, app, request):
        form = SubstForm()
        if form.validate_on_submit():
            return self.execute(app, request)
            
        return render_template('vomitar.html', form=form)


class SubstForm(Form):
    arbolito = StringField(u'Árbol de categorías', validators=[DataRequired()])
    balde = StringField(u'Página en la que se volcará', validators=[DataRequired()])
    description = StringField(u'Razón para lanzar el script', validators=[DataRequired()])
