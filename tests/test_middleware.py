import unittest

from webtest import TestApp

from wsgi_accept_language import LangMiddleware

class TestLang(unittest.TestCase):
    
    @staticmethod
    def app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])

        return [environ['lang']]

    @staticmethod
    def app2(environ, start_response):
        environ['lang'] = 'fr'
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [environ['lang']]

    def testDefaultConfig(self):
        app = LangMiddleware(self.app)
        app = TestApp(app)
        res = app.get("/")
        assert res.headers.get("Content-Language") == "en"
        assert res.body == "en"

    def testDefaultLanguage(self):
        app = LangMiddleware(self.app, ["fr"])
        app = TestApp(app)
        res = app.get("/")
        assert res.headers.get("Content-Language") == "fr"
        assert res.body == "fr"

    def testDiscovery(self):
        app = LangMiddleware(self.app, ["en", "fr"])
        app = TestApp(app)
        environ = {"HTTP_ACCEPT_LANGUAGE": "fr, en;q=0.8"}
        res = app.get("/", extra_environ=environ)
        assert res.headers.get("Content-Language") == "fr"

    def testDiscoveryWithRegion(self):
        app = LangMiddleware(self.app, ["en", "fr"])
        app = TestApp(app)
        environ = {"HTTP_ACCEPT_LANGUAGE": "fr-ch, en;q=0.8"}
        res = app.get("/", extra_environ=environ)
        assert res.headers.get("Content-Language") == "fr"
    
    def testDiscroveryWithRegionAltFormatting(self):
        app = LangMiddleware(self.app, ["en", "fr"])
        app = TestApp(app)
        environ = {"HTTP_ACCEPT_LANGUAGE": "de-CH,de;q=0.9,en;q=0.8"}
        res = app.get("/", extra_environ=environ)
        assert res.headers.get("Content-Language") == "en"

    def testSetLangFromApp(self):
        app = LangMiddleware(self.app2, ["en", "fr"])
        app = TestApp(app)
        res = app.get("/")
        assert res.headers.get("Content-Language") == "fr"
    
    def testSetCookie(self):
        app = LangMiddleware(self.app2, ["en", "fr"], with_cookie=True)
        app = TestApp(app)
        res = app.get("/")
        assert res.headers.get("Set-Cookie") is not None

    def testReadCookie(self):
        app = LangMiddleware(self.app, ["en", "fr"], with_cookie=True)
        app = TestApp(app)
        environ = {"HTTP_COOKIE": '''foo="bar"; lang="fr"'''}
        res = app.get("/", extra_environ=environ)
        assert res.headers.get("Content-Language") == "fr"


if __name__ == "__main__":
    unittest.main()
