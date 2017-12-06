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
import re
import urllib.request
import pandas as pd
import Levenshtein
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


def find_files(urls=possible_beginnings.copy()):
    i = 0
    for url in urls:
        for possible_beginning in possible_beginnings:
            if possible_beginning in url:
                soup = BeautifulSoup(requests.get(url).text, 'lxml')
                for a in soup.find_all('a'):
                    try:
                        address = a['href']
                        if a['href'][:9] == '/recepty/':
                            address = 'https://eda.ru' + a['href']
                        if address not in urls and 'recepty' in address:
                            urls.append(address)
                            # print(i)
                            # print(address)
                            i += 1
                    except KeyError:
                        #print('key error')
                        pass
    urls = [x for x in urls if 'recepty' in x and x.count('/') == 5]
    return urls


list_of_links = find_files()


def parse_links(list_of_links):
    titles_list = []
    ingredients_list = []
    doses_list = []
    categories = []
    receipt_list = []
    counter = 0
    for url in list_of_links:
        counter += 1
        print(counter)
        if counter % 20 == 0:
            percent = 100 * counter / len(list_of_links)
            percent = round(percent, 3)
            print('Extracting data ' + str(percent) + ' percent completed')
        splitted = url.split('/')
        res = urllib.request.urlopen(url).read()
        bs0 = BeautifulSoup(res, 'lxml')
        name = (bs0.find('h1', 'recipe__name g-h1'))
        name = re.sub("<.*?>", " ", str(name))
        name = re.sub('\n', '', name).strip()
        text1 = str(bs0.find('div', 'ingredients-list__content'))
        bs1 = BeautifulSoup(text1, 'lxml')
        ingredients = (
            bs1.find_all(
                'span',
                'js-tooltip js-tooltip-ingredient'))
        ingredients = re.sub("<.*?>", " ", str(ingredients))
        ingredients = ingredients[1:][:-1].split(',  \n')
        ingredients = [x.strip() for x in ingredients]
        # ingredients[0]=ingredients[0][1:]
        # ingredients[len(ingredients)-1]=ingredients[len(ingredients)-1][]
        doses = (
            bs1.find_all(
                'span',
                'content-item__measure js-ingredient-measure-amount'))
        doses = re.sub("<.*?>", " ", str(doses))[1:][:-1].split(' ,  ')
        doses = [x.strip() for x in doses]
        if name != 'None':
            bs2 = str(bs0).split('"recipeInstructions":["')
            receipt = bs2[1].split('"],"recipeYield":')
            receipt = re.sub('","', '\n', receipt[0])
            titles_list.append(name)
            ingredients_list.append(set(ingredients))
            doses_list.append(doses)
            receipt_list.append(receipt)
            categories.append(splitted[len(splitted) - 2])
    answer = pd.DataFrame({'category': categories,
                           'name': titles_list,
                           'receipt': receipt_list,
                           'ingredients': ingredients_list,
                           'doses': doses_list})
    return answer

categories_ru=['салаты','закуски','соусы и маринады','выпечка и десерты','супы','напитки',
             'паста и пицца','завтраки','бульоны','сэндвичи','ризотто','основные блюда']
tab = parse_links(list_of_links)
tab.to_csv('Data.csv', sep=';')
ingredient_list= make_ingredients_list(tab)
def make_category_list(tab):

    answer=[]
    for i in tab.index:
        answer=answer+([tab['category'][i]])
    answer=list(set(answer))
    return answer
categories_en = make_category_list(tab)
def make_ingredients_list(tab):
    answer=[]
    for i in tab.index:
        answer=answer+(tab['ingredients'][i])
    answer=list(set(answer))
    return answer
def make_ingredient_dict(tab):
    answer={}
    for i in tab.index:
        if tab['category'][i] not in answer.keys():
            answer[tab['category'][i]]=set(tab['ingredients'][i])
        else:
            answer[tab['category'][i]]=answer[tab['category'][i]]|set(tab['ingredients'][i])
def predict_most_similar_ingredient(category_ru,user_input):#Assuming user is about to input N ingredients
    #Levenschtein_distanse
    answer=[]
    for i in range()
def predict_most_similar_by_ingredients(ingredient_list,N):
    
def choose_category(categories_ru,categories_en):
    for i in range(n):
        print('Введите '+str(i)+' для выбора категории '+str(categories_ru[i]))
    inp=input()
    category_index = int(inp)
    category=categories_en[category_index]
    return category
def choose_ingredients(ingredient_dict, category):
    this_category_ingredients = ingredients[]
    #We have ingredient list and we predict N most similar receipts from the par
#end = 'teplij-kartofelnij-salat-s-maslinami-i-percem-21445'
#url = 'https://eda.ru/recepty/salaty/' + end
