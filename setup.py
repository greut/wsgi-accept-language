#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


setup(name='wsgi-accept-language',
      version='0.1',
      description='WSGI to deal with accept-language letting you only playing with environ["lang"]',
      author='Yoan Blanc',
      author_email='yoan@dosimple.ch',
      license='BSD',
      url='http://github.com/greut/wsgi-accept-language',
      packages=find_packages(exclude=['tests']),
      install_requires=[],
      entry_points="""# -*- Entry points: -*-
[paste.filter_factory]
main = wsgi_accept_language.wsgiapp:make_filter
""",
      test_suite='tests',
      tests_require=['WebTest'])
