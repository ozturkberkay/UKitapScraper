# UKitapScraper
> A demo from my talk on web scraping @ Istanbul Bilgi University

 This simple Python code demonstrates the process of:
  1. Creating a persistent HTTP session using proxies.
  2. Sending a POST request with a payload to login.
  3. Sending a GET request to fetch the HTML content.
  4. Query the HTML document for scraping using the xPath query language.
  
> "My sincere gratitute and appreciation to my teacher, [Uzay Çetin](https://github.com/uzay00/), for giving me this opportunity."
  
[CMPE 251 - Official Class Repository](https://github.com/uzay00/CMPE251)

## Usage Example

**Requires an account on: http://ukitap.com/**

```python
from ukitap import UKitapScraper
import json

# Create a new scraper object
uks = UKitapScraper()

# Create a session by logging in using your payload
session = uks.login(payload = {
	'eposta': 'your_email', 
	'parola': 'your_password'
}, use_proxies = False)

# If your login is successful, fetch the books on sale by price
if session: 
    books = uks.get_books_by_price(session = session, price = 30, num_fetch = 100, use_proxies = False)

    # Close the session
    session.close()

    # Print the books in a format which won't hurt your eyes :)
    print(json.dumps(obj = books, indent = 2, ensure_ascii = False))
```

## Other Resources

 These are the resources that I have used during my talk:
* xPath Cheatsheet: https://devhints.io/xpath
* Chrome Tamper Plugin: https://goo.gl/Ncrtah

## Changelog

* 0.0.1
    * Initial release

## Meta

Berkay Öztürk – info@berkayozturk.net

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/ozturkberkay/UKitapScraper](https://github.com/ozturkberkay/UKitapScraper)
