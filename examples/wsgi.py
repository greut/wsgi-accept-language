#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Yoan Blanc <yoan@dosimple.ch>"

import cgi
import locale

from datetime import datetime
from wsgiref.simple_server import make_server
from wsgi_accept_language import LangMiddleware


LOCALES = {
    "en": "en_US.UTF8",
    "fr": "fr_FR.UTF8",
    "de": "de_DE.UTF8",
    "it": "it_IT.UTF8",
}
LANGS = "en", "de", "fr", "it" # order matter
PORT = 8080
TEMPLATE = """
<!doctype HTML>
<html>
    <meta charset=utf-8>
    <title>WSGI Accept Language middleware Demo</title>
    <style>
        body{text-align:center;background:#222;color:#fff;}
        #page{margin:1em auto;text-align:left;width:40em;padding:1em;}
        pre {background:#ffe;border:2px solid #ffc;color:#000;padding:1em;}
    </style>
    <div id=page>
    <h1>WSGI Accept Language middleware Demo</h1>
    <form method="GET">
        <label for=lang>Select language:</label>
        <select name=lang id=lang>
            <option value=en%(opt.en)s>English</option>
            <option value=fr%(opt.fr)s>Français</option>
            <option value=de%(opt.de)s>Deutsch</option>
            <option value=it%(opt.it)s>Italiano</option>
        </select>
        <input type=submit value="Send">
    </form>
    <p>Now: %(now)s</p>
    <pre><code>%(code)s</code></pre>
    <address>By: %(by)s</address>
    </div>
</html>"""


def application(environ, start_response):
    # primitive QS parsing, use WebOb instead
    qs = environ["QUERY_STRING"].split("&")
    GET = {}
    for item in qs:
        if item.find("=") > -1:
            key, value = item.split("=", 1)
            GET[key] = value

    
    if "lang" in GET:
        environ["lang"] = GET["lang"]

    try:
        locale.setlocale(locale.LC_TIME, LOCALES.get(environ["lang"], "C"))
    except locale.Error, e:
        print "Unsupported locale: %s" % LOCALES.get(environ["lang"])
    
    # source code
    fp = open(__file__)
    code = fp.read()
    fp.close()

    body = TEMPLATE % {
        "now": datetime.utcnow().strftime("%A %d %B %Y"),
        "opt.en": " selected" if environ["lang"] == "en" else "",
        "opt.fr": " selected" if environ["lang"] == "fr" else "",
        "opt.de": " selected" if environ["lang"] == "de" else "",
        "opt.it": " selected" if environ["lang"] == "it" else "",
        "code": cgi.escape(code),
        "by": cgi.escape(__author__)
    }

    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [body]


application = LangMiddleware(application,
                             LANGS,
                             with_cookie=True)

if __name__ == "__main__":
    httpd = make_server('', PORT, application)
    print "Serving on port %d…" % PORT
    try:
        httpd.serve_forever()
    except KeyboardInterrupt, ki:
        print "…Quitting."

