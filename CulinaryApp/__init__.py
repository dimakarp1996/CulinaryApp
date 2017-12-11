#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 16:07:35 2017

@author: tcs-user
"""

from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import urllib.request
import pandas as pd
import os
import Levenshtein
possible_beginnings = [
    'https://eda.ru/recepty/zavtraki',
    'https://eda.ru/recepty/osnovnye-blyuda',
    'https://eda.ru/recepty/sendvichi',
    'https://eda.ru/recepty/sousy-marinady',
    'https://eda.ru/recepty/bulony',
    'https://eda.ru/recepty/napitki',
    'https://eda.ru/recepty/rizotto',
    'https://eda.ru/recepty/zakuski',
    'https://eda.ru/recepty/pasta-picca',
    'https://eda.ru/recepty/supy',
    'https://eda.ru/recepty/salaty',
    'https://eda.ru/recepty/vypechka-deserty']


def find_files(urls=possible_beginnings.copy(), max_num=200):
    i = 0
    for url in urls:
        if len(urls) < max_num:
            for possible_beginning in possible_beginnings:
                if possible_beginning in url:
                    soup = BeautifulSoup(requests.get(url).text, 'lxml')
                    for a in soup.find_all('a'):
                        try:
                            address = a['href']
                            if a['href'][:9] == '/recepty/':
                                address = 'https://eda.ru' + a['href']
                            if address not in urls and 'recepty' in address and address.count(
                                    '/') == 5:
                                urls.append(address)
                                # print(i)
                                # print(address)
                                # i += 1
                        except KeyError:
                            #print('key error')
                            pass
        # urls = [x for x in urls if 'recepty' in x and x.count('/') == 5]
    return urls


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
        ingredients = [(x.strip()).lower() for x in ingredients]
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


def choose_category(tab):
    categories_ru = [
        'Закуски',
        'Напитки',
        'Завтраки',
        'Супы',
        'Салаты',
        'Выпечка и десерты',
        'Ризотто',
        'Бульоны',
        'Паста и пицца',
        'Основные блюда',
        'Сэндвичи',
        'Соусы и маринады']
    categories_en = [
        'zakuski',
        'napitki',
        'zavtraki',
        'supy',
        'salaty',
        'vypechka-deserty',
        'rizotto',
        'bulony',
        'pasta-picca',
        'osnovnye-blyuda',
        'sendvichi',
        'sousy-marinady']
    n = len(categories_en)
    assert n == len(categories_ru)
    for i in range(n):
        print('Введите ' + str(i) +
              ' для выбора категории ' + str(categories_ru[i]))
    inp = input()
    category_index = int(inp)
    category = categories_en[category_index]
    return category


def choose_ingredients(tab):
    print('Введите число ингредиентов(максимум 20)')
    N = input()
    N = int(N)
    N = min(N, 20)
    my_ingredients = set()
    for ingredient_portion in tab['ingredients']:
        my_ingredients.update(ingredient_portion)
    answer = list()
    while len(answer) < N:
        min_dist = 9999
        print('Осталось ингредиентов: ' + str(N - len(answer)))
        print('Вводите ингредиент')
        inputted_ingredient = input()
        inputted_ingredient.lower()
        for ingredient in my_ingredients:
            # ingredient.lower()
            this_dist = Levenshtein.distance(ingredient, inputted_ingredient)
            if this_dist < min_dist:
                min_dist = this_dist
                interpreted_ingredient = ingredient
        print(
            'То, что вы ввели, из имеющегося списка больше всего похоже на ' +
            str(interpreted_ingredient))
        if interpreted_ingredient not in answer:
            print('Добавить это?  Введите ДА, чтобы добавить')
            if input().lower() == 'да':
                answer.append(interpreted_ingredient)
                print('Ингредиент добавлен')
    return answer


# n most relevant queries
def ingredient_search(user_ingredients, category_tab, n=3, print_=True):
    answer = []
    share_match = dict()
    num_match = dict()
    print('Ищем самые похожие рецепты')

    def sort(answer, n):
        for i in range(len(answer)):
            for j in range(len(answer)):
                if i < j and (num_match[answer[i]] < num_match[answer[j]] or (
                        num_match[answer[i]] == num_match[answer[j]] and share_match[answer[i]] < share_match[answer[j]])):
                    answer[i], answer[j] = answer[j], answer[i]
        return answer[:n]
    for i in category_tab.index:
        num_match[i] = sum(
            [x in user_ingredients for x in category_tab['ingredients'][i]])
        share_match[i] = num_match[i] / len(category_tab['ingredients'][i])
        answer.append(i)
        answer = sort(answer, n)
    receipts = category_tab.loc[answer, :]
    for i in answer:
        tmp = list(receipts['ingredients'][i])
        for j in range(len(tmp)):
            if tmp[j] not in user_ingredients:
                tmp[j] = tmp[j] + ' - ДОКУПИТЬ!'
        receipts.loc[i, 'ingredients'] = tmp
    if print_:
        for i in receipts.index:
            print('НАЗВАНИЕ')
            print(receipts['name'][i])
            print('ИНГРЕДИЕНТЫ')
            for j in range(len(receipts['ingredients'][i])):
                doze = ' доза ' + receipts['doses'][i][j]
                print(receipts['ingredients'][i][j] + doze)
            print('РЕЦЕПТ')
            print(receipts['receipt'][i])
    return receipts


def main():
    generate_list = True
    if generate_list:
        list_of_links = find_files()
        tab = parse_links(list_of_links)
        #tab.to_csv(os.getcwd() + '\\Data.csv', sep=';')
    else:
        tab = pd.read_csv(os.getcwd() + '/Data.csv', sep=';')
    user_category = choose_category(tab)
    # НАДО - давать tab веб-приложению и взамен получать user_category
    category_tab = tab[tab['category'] == user_category]
    user_ingredients = choose_ingredients(tab)
    # НАДО - давать tab веб-приложению и взамен получать user_ingredients
    answer = ingredient_search(user_ingredients, category_tab)
    del answer


main()
# НАДО - передавать answer в веб-приложение
