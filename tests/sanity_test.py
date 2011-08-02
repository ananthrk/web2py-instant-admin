PREFIX = '/demo/plugin_instant_admin/'
WELCOME_URL = PREFIX + 'welcome'
RESET_URL = PREFIX + 'reset'
LOGIN_URL = PREFIX + 'user/login'

PUBLIC_URLS = []
PRIVATE_URLS = [
    'index',
    'list/dogs',
    'new/dogs',
    'show/dogs/1',
    'edit/dogs/1',
    'delete/dogs/1',
    'confirm_delete/dogs'
]

PUBLIC_URLS = [PREFIX + url for url in PUBLIC_URLS]
PRIVATE_URLS = [PREFIX + url for url in PRIVATE_URLS]
VALID_URLS = PUBLIC_URLS + PRIVATE_URLS


class TestAsAnonymous(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.app = webtest()

    def test_that_all_private_urls_are_protected_with_login_required(self):
        for url in PRIVATE_URLS:
            response = self.app.get(url, status=303)
            response = response.follow()
            response.mustcontain('login', 'password')



class TestAsAuthenticated(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.app = webtest()


    def setUp(self):
        # Load Data
        response = self.app.get(RESET_URL)

        # Login
        response = self.app.get(WELCOME_URL)
        response = response.follow()
        response = response.follow()
        form = response.form
        form['username'] = 'a'
        form['password'] = 'a'
        response = form.submit()
        response = response.follow()

        #response.showbrowser()
        response.mustcontain('Logged in')


    def test_that_valid_urls_do_not_throw_404(self):
        for url in VALID_URLS:
            response = self.app.get(url)

