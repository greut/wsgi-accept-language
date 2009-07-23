"""
WSGI/PasteDeploy application bootstrap module.
"""
import logging

from wsgi_accept_language import LangMiddleware


log = logging.getLogger(__name__)


def make_filter(global_conf, **app_conf):
    """
    PasteDeploy WSGI application factory.

    Called by PasteDeply (or a compatable WSGI application host) to create the
    whut WSGI application.
    """
    langs = app_conf.get("langs").split(", ")
    with_cookie = app_conf.get("with_cookie") == "True"
    
    def filter(app):
        return LangMiddleware(app, langs, with_cookie=with_cookie)
    return filter

