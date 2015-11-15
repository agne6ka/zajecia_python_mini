# -*- coding: utf-8 -*-
import os
import requests  # import whole module
from bs4 import BeautifulSoup
import unicodecsv as csv  # import whole module as a drop-in replacement for csv module

CATEGORIES_URL = "http://www.ikea.com/pl/pl/catalog/allproducts/"
HEADLINES = ('id', 'Product title', 'Product description')


def get_soup_from_url(url):
    response = requests.get(url)  # a simple HTTP GET request will be used
    response.encoding = 'utf-8'  # but the requests module incorrectly guesses the encoding here
    html_doc = response.text  # that's the decoded content of the response
    return BeautifulSoup(html_doc, 'html.parser')


def get_category_urls(url=CATEGORIES_URL):
    soup = get_soup_from_url(url)
    links = []
    for div in soup.find_all('div', class_='textContainer'):
        for a in div.findChildren('a', href=True):
            category_name = a.text.strip().replace('/', '_')
            category_url = 'http://www.ikea.com' + a['href'].strip()
            links.append((category_name, category_url))
    return links


def get_products_from_category(category_url):
    soup = get_soup_from_url(category_url)
    data = []
    for div in soup.find_all('div', class_='productDetails'):
        try:
            a = div.findChild('a', href=True)['href'].strip()
            product_id = a.split('/')[::-1][1]
        except TypeError:
            continue
        title = div.findChild('div', class_='productTitle').text
        desc = div.findChild('div', class_='productDesp').text
        if all([product_id, title, desc]):
            data.append((product_id, title, desc))
    return data


def category_data_to_csv(data, filepath):
    with open(filepath, 'wb') as f:
        writer = csv.writer(f, encoding='utf-8')
        writer.writerow(HEADLINES)
        writer.writerows(data)


category_urls = get_category_urls()
for category_name, url in category_urls:
    print(u'Getting products for {} ...'.format(category_name))
    products_data = get_products_from_category(url)
    print 'Found {} products.'.format(len(products_data))
    category_data_to_csv(products_data,
                         os.path.relpath(os.path.join('results', category_name.replace(' ', '_') + '.csv')))
