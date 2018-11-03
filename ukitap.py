from requests import get, post, Session, RequestException
from user_agent import generate_user_agent
from random import choice
from lxml import html

# A demo code for my talk on web scraping @ Istanbul Bilgi University
# Berkay Öztürk
class UKitapScraper:

    def __init__(self):
        # User-Agent Spoofing
        self.ua = generate_user_agent(device_type="all", os=('linux', 'mac'))

        # Decrease the session timeout if you won't use a proxy (e.g. 5 seconds)
        self.timeout = 15

        # URL and paths
        self.url = 'http://www.ukitap.com/'
        self.login_path = 'uye'
        self.cheap_path = 'ucuz-kitaplar/'

        # Proxy Variables 
        self.proxy_num_fetch = 10   # Range: 1-20
        self.proxy_pool = []
        self.proxies = []

    # (GET) Fetching proxies - Experimental
    # Implemented only for demo purposes, not necessarily required
    def __fetch_proxies(self):
        try:
            print('Fetching Proxies...')
            # RATE LIMIT: 100 requests per day
            # API Docs: http://pubproxy.com/#settings
            r = get('http://pubproxy.com/api/proxy', timeout=self.timeout, params={
                'https': 'true',
                'post': 'true',
                'level': 'elite',
                'limit': str(self.proxy_num_fetch),
                # You can use TR for Turkey based proxy. Codes: https://www.wikiwand.com/en/ISO_3166-1#/Current_codes
                'country': 'DE',    
                'user_agent': 'true',
                'cookies': 'true',
                'referer': 'true',
                'format': 'txt'
                # 'speed': '2' Range: 1-60, how many seconds it takes for the proxy to connect
            })
            if r.status_code == 200:
                self.proxy_pool = r.content.decode('UTF-8').splitlines()
                print('Proxy Pool Generated: %d proxy added to the pool!' % (len(self.proxy_pool)))
        except RequestException as e:
            print(e)

    # Chooses a random proxy from the proxy pool
    def set_proxies(self):
        if len(self.proxy_pool) == 0: self.__fetch_proxies()
        random_proxy = choice(self.proxy_pool)
        self.proxies = {
            'http': random_proxy,
            'https': random_proxy
        }
        print('Random Proxy Chosen: %s' % (random_proxy))

    # (POST) Starts the session and logins to the website
    def login(self, payload: dict, use_proxies: bool):
        # Payload for our POST request to login
        payload = {
            'eposta': payload['eposta'],
            'giris': 'Giri%C5%9F',  # URL encoded
            'parola': payload['parola']
        }
        with Session() as session:
            if use_proxies:
                self.set_proxies()
            else:
                self.proxies = None
            try:
                r = session.post('%s%s' % (self.url, self.login_path), headers={'User-Agent': self.ua}, proxies=self.proxies, data=payload, timeout=self.timeout)
                # Making sure that:
                    # 1) After the login request, there was a redirection (Status Code = 302)
                    # 2) Redirected page loaded successfully (Status Code = 200)
                    # 3) The loaded page is the home page
                if len(r.history) != 0 and str(r.history[0]) == '<Response [302]>' and r.status_code == 200 and r.url == self.url:
                    doc = html.document_fromstring(r.content)
                    # Fetching the username, just to be fancy :)
                    print('User %sLogged In!' % (doc.xpath('//li[@id="uye_menu_ana"]/span/text()')[0]))
                    return session
                else:
                    print('Login Unsuccessful!')
                    return False
            except RequestException as e:
                print(e)

    # (GET) Fetch the books on sale by filtering them with a price tag
    def get_books_by_price(self, session, price: int, num_fetch: int, use_proxies: bool) -> dict:
        with session:
            page = 1
            books = {}
            max_books_per_page = 50
            while len(books) < num_fetch:
                try:
                    r = session.get('%s%s%d/%d/' % (self.url, self.cheap_path, price, page), headers={'User-Agent': self.ua}, proxies=self.proxies, timeout=self.timeout)
                    if r.status_code == 200:
                        print('Fetching books on sale for %d₺ on page %d...' % (price, page))
                        doc = html.document_fromstring(r.content)
                        # Alternative: if (len(doc.xpath('//tr')) == 1):
                        if (doc.xpath('//tr/td[last()] = //tr/td[1]')):
                            print('No books found at the price of %d₺. Ending the requests!' % (price))
                            return books
                        for i, row in enumerate(doc.xpath('//tr')[1:]):
                            if len(books) < num_fetch:
                                # Making sure each book entry has the correct index value
                                # Pages start from 1, each page can have 50 books in total
                                # On Page 1: i + (0 x 50) = 0, 1, 2, ...49
                                # On Page 2: i + (1 x 50) = 50, 51, 52...
                                # ...
                                books[i+((page-1)*max_books_per_page)] = {
                                    'title': row.xpath('.//td[2]/a[1]/text()')[0],
                                    'author': row.xpath('.//td[2]/a[2]/text()')[0],
                                    # Getting rid of the " TL" and only storing the price value
                                    'price': [int(s) for s in row.xpath('.//td[3]/text()')[0].split() if s.isdigit()][0]
                                }
                        # Predicting if a next page exists by querying the page navigation buttons
                        if num_fetch > 0 and len(doc.xpath('//ul[@class="sayfalar"]/li[last()]/a/text()')) == 0:
                            print('No more pages avaiable! Ending the requests!\n%d books fetched in total.' % (len(books)))
                            return books
                        elif len(books) < num_fetch: page += 1
                except RequestException as e:
                    print(e)
            return books
