from BeautifulSoup import BeautifulStoneSoup, SoupStrainer

PREFIX = '/demo/plugin_instant_admin/'
WELCOME_URL = PREFIX + 'welcome'
RESET_URL = PREFIX + 'reset/3'
INDEX_URL = PREFIX + 'index'
LOGIN_URL = PREFIX + 'user/login'
LOGOUT_URL = PREFIX + 'user/logout'

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


def get_all_links_in_page(html):
    html = str(html)
    if not html:
        return []
    soup = BeautifulStoneSoup(html)
    links = soup.findAll(SoupStrainer('a'))
    return [link['href'] for link in links]


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


    def depth_first_traversal(self, link):
        print "Visiting %s" % link
        self.visited_list.append(link)

        response = self.app.get(link)
        if response.status == 303:
            response = response.follow()
        assert 'ACCESS DENIED' not in response

        links = get_all_links_in_page(response.html)

        for link in links:
            if link not in self.visited_list:
                self.depth_first_traversal(link)


    def test_crawl_and_verify_no_404s(self):
        """This test crawls all links recursively and makes sure that none of them throw 40x or 50x or Access Denied errors.
         """
        self.visited_list = [LOGOUT_URL, '#', '/']
        self.depth_first_traversal(INDEX_URL)
