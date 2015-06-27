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
import datetime
from peewee import SqliteDatabase, Model, CharField, IntegerField, TextField
import json
import random
import time

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

def getPrivs(cache=False):
    user = mwoauth.get_current_user(cache)
    if user:
        try:
            dbuser = Privs.get(Privs.username == user)
        except:
            dbuser = Privs(username=user, privs=0)
            dbuser.save()
        privs = dbuser.privs
    else:
        privs = -1
    return privs

def canUseScript(script, cache=False):
    if getPrivs(cache) > 0:
        dbuser = Privs.get(Privs.username == mwoauth.get_current_user())
        try:
            userprivs = SectionPrivs.get(SectionPrivs.uid == dbuser.id and SectionPrivs.section == "*")
            return True
        except:
            try:
                userprivs = SectionPrivs.get(SectionPrivs.uid == dbuser.id and SectionPrivs.section == script)
                return True
            except:
                return False
    return False
    
# ---

@app.route('/')
def index():
    return render_template('index.html')

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
                if canUseScript(filename.split(".py")[0], True):
                    f.append(filename.split(".py")[0])
        break
    
    return render_template('scripts.html', scripts=f)

@app.route('/script/<script>/', methods=['GET', 'POST'])
def execscript(script):
    if not canUseScript(script + ".py"):
        return "Unauthorized"
        
    mod = __import__("scripts." + script)
    
    script = getattr(mod, script).Script(config)
    
    return script.render(app, request)
    
@app.route('/progress/<task>')
def logapi(task):
    log = LogEntry.get(LogEntry.id == task)
    return str(log.progress)

@app.route('/logs')
def loglist():
    return render_template('logs.html', logs=LogEntry.select().order_by(LogEntry.id.desc()))

# api stuff
@app.route('/api/editprop/<user>')
def editprop(user):
    import scripts._editprop
    f = scripts._editprop.Editprop(config)
    return json.dumps(f.getProp(user))

# ---

def humanDate(timestamp):
    return datetime.datetime.fromtimestamp(
        float(timestamp)
    ).strftime('%Y-%m-%d %H:%M:%S')

@app.context_processor
def inject_globals():
    return dict(
        mwoauth = mwoauth,
        privs = getPrivs(),
        humanDate = humanDate,
        random = random
    )

class EventLogger(object):
    def __init__(self, task_name, descr, nostarted=False):
        self.pwarning = False
        if nostarted:
            startedby = "-"
        else:
            startedby = mwoauth.get_current_user()
        self.logentry = LogEntry(status = 0, log = "", taskName=task_name, startTime=time.time(), endTime="-", description=descr, progress=0, startedBy=startedby)
        self.logentry.save(force_insert=True)
    
    def finished(self):
        if self.pwarning:
            self.logentry.status = 3
        else:
            self.logentry.status = 1
        self.logentry.progress = 100
        self.logentry.endTime = time.time()
        self.logentry.save()
    
    def errored(self):
        self.logentry.status = 2
        self.logentry.progress = 100
        self.logentry.endTime = time.time()
        self.logentry.save()
    
    def warning(self):
        self.pwarning = True
    
    def setProgress(self, progress):
        self.logentry.progress = progress
        self.logentry.save()
    
    def appendLog(self, text):
        self.logentry.log += text + "\n"
        self.logentry.save()

app.cosoEventLogger = EventLogger
app.oauth = mwoauth

class Privs(Model):
    username = CharField()
    privs = IntegerField()

    class Meta:
        database = db
        
class SectionPrivs(Model):
    uid = IntegerField()
    section = CharField()

    class Meta:
        database = db


class LogEntry(Model):
    status = IntegerField()  # 0 = running; 1 = finished; 2 = errored; 3 = finished with errors
    log = TextField()
    taskName = CharField()
    startedBy = CharField()
    description = CharField()
    startTime = CharField() # timestamp
    endTime = CharField()   # ^
    progress = IntegerField()   # 0-100%
    class Meta:
        database = db


LogEntry.create_table(True)
Privs.create_table(True)
SectionPrivs.create_table(True)

if __name__ == "__main__":
    app.run(threaded=True)
