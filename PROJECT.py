#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 10:33:03 2017

@author: tcs-user
"""
# PROBLEM - it goes only to page 5 and no more
from bs4 import BeautifulSoup
from lxml import html
import requests


def find_files():
    i = 0
    url = "https://eda.ru/recepty"
    possible_beginnings = [
        'http://eda.ru/recepty/zavtraki',
        'http://eda.ru/recepty/osnovnye-blyuda',
        'http://eda.ru/recepty/sendvichi',
        'http://eda.ru/recepty/sousy-marinady',
        'http://eda.ru/recepty/bulony',
        'http://eda.ru/recepty/napitki',
        'http://eda.ru/recepty/rizotto',
        'http://eda.ru/recepty/zakuski',
        'http://eda.ru/recepty/pasta-picca',
        'http://eda.ru/recepty/supy',
        'http://eda.ru/recepty/salaty',
        'http://eda.ru/recepty/vypechka-deserty']

    ingredients = []
    dishes = []
    urls = possible_beginnings.copy()
    for url in urls:
        for possible_beginning in possible_beginnings:
            if possible_beginning in url:
                textt = requests.get(url).text
                soup = BeautifulSoup(requests.get(url).text, 'lxml')
                for a in soup.find_all('a'):
                    address = a['href']
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
url = 'https://eda.ru/recepty/salaty/teplij-kartofelnij-salat-s-maslinami-i-percem-21445'
data = requests.get(url).text
tree = html.fromstring(data)
title = tree.xpath('//div[@class = "title"]')[0]
