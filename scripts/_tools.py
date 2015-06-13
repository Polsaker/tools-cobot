import cookielib
import urllib2
import json
from urllib import urlencode
from urllib import quote_plus

class MediaWikiAPI(object):
    def __init__(self, user, password):
        self.cookiejar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))

        self.user = user
        self.password = password
    
    def request(self, url, poststuff=None):
        #print(url)
        if poststuff is not None:
            login_data = urlencode(poststuff).encode('utf-8')
            return self.opener.open(url, login_data).read().decode()
        return self.opener.open(url).read().decode()

    def gettoken(self, wiki="es.wikipedia"):
        req = self.request("https://" + wiki + ".org/w/api.php?action=query&meta=tokens&format=json&continue")
        #print(req)
        return json.loads(req)['query']['tokens']['csrftoken']

    def login(self, wiki="es.wikipedia"):
        # check if we're already logged in
        resp = json.loads(self.request("https://" + wiki +".org/w/api.php?action=query&meta=userinfo&format=json"))
        try:
            resp['query']['userinfo']['anon']
        except:
            return
            
        resp = json.loads(self.request("https://" + wiki +".org/w/api.php?action=login&format=json",
                {'lgname': self.user, 'lgpassword': self.password}))
        if resp['login']['result'] == "NeedToken":
            resp = json.loads(self.request("https://" + wiki + ".org/w/api.php?action=login&format=json",
                {'lgname': self.user, 'lgpassword': self.password, 'lgtoken': resp['login']['token']}))
            if resp['login']['result'] != "Success":
                print(resp)
        elif resp['login']['result'] != "Success":
            print(resp)
