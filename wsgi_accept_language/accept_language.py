import locale

from datetime import datetime, timedelta


__all__ = ["LangMiddleware"]


DEFAULT_LANGS = "en",
COOKIE_NAME = "lang"
COOKIE_FORMAT = "%a, %d-%b-%Y %H:%M:%S UTC"
COOKIE_EXPIRATION = 30 # days


class LangMiddleware(object):
    """WSGI Middleware that deals with language support for you
    you only have to use environ["lang"] to read/set it
    """

    def __init__(self, application, languages=None, with_cookie=True):
        self.application = application
        if languages is not None:
            self.languages = languages
        else:
            self.languages = DEFAULT_LANGS
        self.with_cookie = with_cookie

    @property
    def default_language(self):
        return self.languages[0]

    def language_from_cookie(self, cookie_string):
        language = None
        if cookie_string:
            pos = cookie_string.find(COOKIE_NAME+"=")

            if pos > -1:
                pos += len(COOKIE_NAME)+2
                lang = cookie_string[pos:pos+2]
                if lang in self.languages:
                    language = lang

        return language

    def preferred_language(self, accept):
        preferred = None
        if accept:
            langs = {}
            l = accept.split(", ")
            for lang in l:
                lang = lang.strip()
                hasq = lang.find(";q=")

                q = 1.
                if hasq > -1:
                    code = lang[:hasq]
                    q = float(lang[hasq+4:])
                else:
                    code = lang

                # ignore region
                if len(code) > 2:
                    code = code[:2]

                langs[code] = q

            score = 0
            for lang in self.languages:
                # ignore region
                l = lang[:2]
                if l in langs and langs[l] > score:
                    score = langs[l]
                    preferred = l

        return preferred

    def cookie_header(self, lang):
        expiration = datetime.utcnow() + timedelta(days=COOKIE_EXPIRATION)

        # Prevent non-english output
        current_locale = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")

        expires = expiration.strftime(COOKIE_FORMAT)

        locale.setlocale(locale.LC_TIME, current_locale)

        return ('Set-Cookie',
                '%s="%s"; expires=%s; path=/' %
                    (COOKIE_NAME,
                     lang,
                     expires))

    def __call__(self, environ, start_response):
        lang = None

        if self.with_cookie:
            lang = self.language_from_cookie(environ.get("HTTP_COOKIE", None))


        if lang is None:
            accept = environ.get("HTTP_ACCEPT_LANGUAGE", None)
            lang = self.preferred_language(accept)

        if lang is None:
            lang = self.default_language

        def _start_response(status, response_headers, exc_info=None):
            # Removing any existing content-language
            response_headers = [(name, value)
                                for name, value in response_headers
                                    if name.lower() != 'content-language']

            # lang changed
            lang = environ['lang.origin']
            if lang != environ['lang']:
                if environ['lang'] not in self.languages:
                    environ['lang'] = lang
                else:
                    lang = environ['lang']

                if self.with_cookie:
                    response_headers.append(self.cookie_header(lang))

            response_headers.append(('Content-Language', lang))

            return start_response(status, response_headers)

        environ['lang'] = lang
        environ['lang.origin'] = lang # shouldn't be touched

        response = self.application(environ, _start_response)
        return response
