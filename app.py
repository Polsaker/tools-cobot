# -*- coding: utf-8 -*-
# Copyright (c) 2015, Ramiro Bou
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from flask import Flask
from flask import render_template, request
from flask_mwoauth import MWOAuth
from os import walk
from peewee import SqliteDatabase, Model, CharField, IntegerField, TextField
import json

app = Flask(__name__)
app.debug = True
config = json.load(open("config.json"))

app.secret_key = config['secret']

mwoauth = MWOAuth(consumer_key=config['oauth-token'], consumer_secret=config['oauth-secret'],
                    base_url="https://es.wikipedia.org/w", clean_url="https://es.wikipedia.org/wiki",
                    name="es.wikipedia.org")
app.register_blueprint(mwoauth.bp)

db = SqliteDatabase('stuff.db')
db.connect()

# ---

@app.route('/')
def index():
    user = mwoauth.get_current_user(False)
    if user:
        try:
            dbuser = Privs.get(Privs.username == user)
        except:
            dbuser = Privs(username=user, privs=0)
            dbuser.save()
        privs = dbuser.privs
    else:
        privs = -1

    return render_template('index.html', loginName=user if user is not None else "", privs=privs)

@app.route('/apps')
def scripts(): # List scripts
    if mwoauth.get_current_user(False) is None:
        return "Unauthorized"
    
    user = Privs.get(Privs.username == mwoauth.get_current_user())
    if user.privs <= 0:
        return "Unauthorized"
    
    f = []
    for (dirpath, dirnames, filenames) in walk("./scripts"):
        for filename in filenames:
            if not filename.startswith("_") and filename.endswith(".py"):
                f.append(filename.split(".py")[0])
        break
    
    return render_template('scripts.html', scripts=f)

@app.route('/script/<script>/', methods=['GET', 'POST'])
def execscript(script):
    if mwoauth.get_current_user(False) is None:
        return "Unauthorized"
    
    user = Privs.get(Privs.username == mwoauth.get_current_user())
    if user.privs == 0:
        return "Unauthorized"
    mod = __import__("scripts." + script)
    
    script = getattr(mod, script).Script(config)
        
    return script.render(app, request)
# ---

class EventLogger(object):
    def __init__(self, task_name):
        self.warning = False
        self.logentry = LogEntry(status = 0, log = "", taskName=task_name)
        self.logentry.save()
    
    def finished(self):
        if self.warning:
            self.logentry.status = 3
        else:
            self.logentry.status = 1
        self.logentry.save()
    
    def errored(self):
        self.logentry.status = 2
        self.logentry.save()
    
    def warning(self):
        self.warning = True
    
    def appendLog(self, text):
        self.logentry.log = text + "\n"
        self.logentry.save()

app.cosoEventLogger = EventLogger

class Privs(Model):
    username = CharField()
    privs = IntegerField()

    class Meta:
        database = db

class LogEntry(Model):
    status = IntegerField()  # 0 = running; 1 = finished; 2 = errored; 3 = finished with errors
    log = TextField()
    taskName = CharField()
    class Meta:
        database = db


LogEntry.create_table(True)
Privs.create_table(True)

if __name__ == "__main__":
    app.run()
