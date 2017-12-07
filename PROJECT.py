from bs4 import BeautifulSoup
import requests


def find_files():
    i = 0
    url = "https://eda.ru/recepty"
    urls = []
    urls.append(url)
    for url in urls:
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        for a in soup.find_all('a'):
            if a['href'][:9] == '/recepty/':
                address = 'https://eda.ru' + a['href']
                if address not in urls:
                    urls.append(address)
                    print(i)
                    print(address)
                    i += 1

    return urls


list_of_links = find_files()
list_of_receipts = [lambda x: 'recepty' in x for x in list_of_links]
print('This app is about choosing the right dish with the certain ingredients from certain category')
# show what you've found:
