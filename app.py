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
import json

app = Flask(__name__)
#app.debug = True
config = json.load(open("config.json"))

app.secret_key = config['secret']

mwoauth = MWOAuth(consumer_key=config['oauth-token'], consumer_secret=config['oauth-secret'],
                    base_url="https://es.wikipedia.org/w", clean_url="https://es.wikipedia.org/wiki",
                    name="es.wikipedia.org")
app.register_blueprint(mwoauth.bp)

@app.route('/')
def index():
    user = mwoauth.get_current_user()
    return render_template('index.html', loginName=user if user is not None else "")

if __name__ == "__main__":
    app.run()
