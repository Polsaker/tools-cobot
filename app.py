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
from flask import render_template
from flask_mwoauth import MWOAuth
from peewee import SqliteDatabase, Model, CharField, IntegerField
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
        
    return render_template('index.html', loginName=user if user is not None else "")

@app.route('/apps')
def scripts(): # List scripts
    if mwoauth.get_current_user(False) is None:
        return
    
    user = Privs.get(Privs.username == mwoauth.get_current_user())
    if user.privs == 0:
        return

@app.route('/script/<script>/', methods=('GET', 'POST'))
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

class Privs(Model):
    username = CharField()
    privs = IntegerField()

    class Meta:
        database = db

Privs.create_table(True)

if __name__ == "__main__":
    app.run()
