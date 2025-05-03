from wsgiref.simple_server import make_server
from urllib.parse import parse_qs

multi_lang_message = {
    "en": 'Hello!',
    "it": 'Ciao!',
    "fr": 'Bonjour!',
    "ja": 'こんにちは',
}


# A basic WSGI application.
def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    # Determine the language from the environment's LANG_CODE
    # Defaulting to English.
    default = 'en'
    message = environ.get('LANG_CODE', 'en')
    # Attempt to use the end-user provided language, if it exists.
    # If the key doesn't exist return the default message.
    try:
        message = multi_lang_message[message]
    except KeyError:
        message = multi_lang_message[default]
    # .encode() converts the str into a bytestr.
    yield f'{message}\n'.encode()


class Middleware():
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Parse the query string and extract the `lang` parameter.
        # Assigning the extracted language code to the environment's LANG_CODE key.
        environ['LANG_CODE'] = parse_qs(environ['QUERY_STRING']).get('lang')
        # Run the next WSGI application.
        return self.wsgi_app(environ, start_response)


###############################################################################
#
# Application unit tests.
#
###############################################################################
import unittest
from unittest.mock import MagicMock


class TestWSGI(unittest.TestCase):

    def test_app(self):
        for lang in 'en it fr ja'.split():
            # build the final actual result by first calling the WSGI middleware app.
            actual = app({'LANG_CODE': lang}, MagicMock())
            # WSGI applications return an iterable.
            actual = ''.join([i.decode() for i in actual])
            # The app adds a newline at the end of the greeting.
            actual = actual.rstrip('\n')
            expect = multi_lang_message[lang]
            self.assertEqual(actual, expect)

    def test_app_has_default(self):
        actual = app({'LANG_CODE': 'FAKE'}, MagicMock())
        actual = ''.join([i.decode() for i in actual])
        actual = actual.rstrip('\n')
        expect = multi_lang_message['en']
        self.assertEqual(actual, expect)

    def test_middleware(self):
        for lang in 'en it fr ja'.split():
            wsgi_app = Middleware(app)
            actual = wsgi_app({'QUERY_STRING': f'lang={lang}'}, MagicMock())
            actual = ''.join([i.decode() for i in actual])
            actual = actual.rstrip('\n')
            expect = multi_lang_message[lang]
            self.assertEqual(actual, expect)


if __name__ == '__main__':
    print(unittest.main(verbosity=1, failfast=True))