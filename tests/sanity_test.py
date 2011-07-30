PREFIX = '/welcome/plugin_instant_admin/'
LOGIN_URL = PREFIX + 'user/login'

PUBLIC_URLS = []
PRIVATE_URLS = [
    '',
    'index',
    'list/dogs',
    'new/dogs',
    'show/dogs/1',
    'edit/dogs/1',
    'delete/dogs/1',
]

PUBLIC_URLS = [PREFIX + url for url in PUBLIC_URLS]
PRIVATE_URLS = [PREFIX + url for url in PRIVATE_URLS]
VALID_URLS = PUBLIC_URLS + PRIVATE_URLS


class TestSanity(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.app = webtest()


    def setUp(self):
        self.abcd = 19


    def test_that_none_of_the_valid_urls_throw_404(self):
        for url in VALID_URLS:
            response = self.app.get(url)
            assert response.status_int != 404, "%s Failed" % url


    def test_that_all_private_urls_are_protected_with_login_required(self):
        for url in PRIVATE_URLS:
            response = self.app.get(url)
            assert response.location == LOGIN_URL, \
                   "%s Failed. Not redirected to Login page" % url
            response = response.follow()
            response.mustcontain('login', 'password')


