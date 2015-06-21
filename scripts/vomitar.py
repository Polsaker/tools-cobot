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
from .. import app

import _vomitar


class Script(object):
    def __init__(self, config):
        pass
    
    def execute(self, qapp, request):
        self.logger = app.EventLogger("vomitar.py", request.form['description'])
        self.mediawiki.login()
        thread.start_new_thread(self.categorize, (request.form['pages'], request.form['category']))
        return render_template('taskProgress.html', taskId=self.logger.logentry.id)
    
    def render(self, qapp, request):
        form = SubstForm()
        if form.validate_on_submit():
            return self.execute(qapp, request)
            
        return render_template('vomitar.html', form=form)


class SubstForm(Form):
    pages = TextAreaField(u'Páginas a categorizar', validators=[DataRequired()])
    category = StringField(u'Categoría a añadir', validators=[DataRequired()])
    description = StringField(u'Razón para lanzar el script', validators=[DataRequired()])

    #def validate_category(form, field):
    #    if not field.data.startswith("Categoría:"):
    #        raise ValidationError("Eso no es una categoría!")
