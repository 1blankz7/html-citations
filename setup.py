try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A html citation system written in python.',
    'author': 'Christian Blank',
    'download_url': 'Where to download it.',
    'author_email': 'mail@cblank.de',
    'version': '0.1',
    'install_requires': ['lxml', 'pybtex'],
    'packages': ['html_citation'],
    'scripts': [],
    'name': 'Html citation system'
}

setup(**config)
