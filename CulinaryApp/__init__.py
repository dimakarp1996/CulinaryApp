#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import urllib.request
import pandas as pd
import os
import json
from Levenshtein import distance
from string import punctuation
import sys
import sqlite3
possible_beginnings = [  # начала адресов
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
rus_letters = 'абвгдеёжзийклмпнопрстуфхцчшщъыьэюя'
PROJECT_DIR = 'C://CulinaryApp'  # project directory


def save(database_name, tab):  # сохраняем базу данных database_name
    connection = sqlite3.connect(database_name, check_same_thread=False)
    cursor = connection.cursor()
    connection.execute("PRAGMA foreign_keys=ON")
    cursor.execute('''CREATE TABLE IF NOT EXISTS tab (
                            name TEXT PRIMARY KEY,
                                category TEXT,
                             doses TEXT, ingredients TEXT, receipt TEXT)''')
    for i in tab.index:  # tab это pd.DataFrame
        try:
            cursor.execute("INSERT INTO tab VALUES (?,?,?,?,?)",
                           (tab['name'][i],
                            tab['category'][i],
                            str(tab['doses'][i]),
                            str(tab['ingredients'][i]),
                            tab['receipt'][i]))
        except (sqlite3.OperationalError, sqlite3.IntegrityError):
            print("Ошибка - обнаружен дубликат имени рецепта")
    connection.commit()
    print('База данных проекта сохранена(либо уже имеется)')


def load(database_name):
    connection = sqlite3.connect(database_name, check_same_thread=False)
    tab = pd.read_sql_query("SELECT * FROM tab", connection)
    print("Taблица успешно загружена")
    return tab


class LinkGetter:
    '''
    Класс предназначен для парсинга ссылок.
    Исходные параметры: urls - ссылки, с которых начинается парсинг
    (по умолчанию - заданные адреса),
    max_num - число ссылок, начинающихся с urls, которые надо распарсить
    (по умолчанию - 50),
    load - нужно ли загружать SQL базу данных(по умолчанию False)
    print_ - нужно ли выводить в консоль информацию о ходе парсинга
    (по умолчанию True)
    printstep - как часто выводим в консоль информацию о ходе парсинга,
    если выводим(по умолчанию каждые 50 ссылок)
    Имеются функции get_links для формирования списка ссылок
    и get_tab для формирования таблицы из материала по этим ссылкам
    '''

    def __init__(self, urls=possible_beginnings.copy(),
                 max_num=50, load=False, print_=True, printstep=50):
        self.max_num = max_num  # верхняя граница числа ссылок
        self.urls = urls
        # начинаем искать с этих адресов
        self.answer = None
        self.print_ = print_  # если print_==True, выводим то, сколько % готово
        self.printstep = printstep  # выводим каждый printstep шагов
        if load:  # тогда просто считываем из файла
            self.answer = load(PROJECT_DIR + "/Data.db")
            if len(self.urls) == 1:
                for category in categories_en:
                    if category in self.urls[0]:
                        self.answer = self.answer[(
                            self.answer['category'] == category)]

    def get_links(self):
        '''
        Функция для парсинга ссылок. Добавляет новые ссылки в self.urls
        '''
        i = 0
        print('Getting links')
        str0 = 'Ищем для вас ссылки - '
        str1 = ' процентов завершено'
        for url in self.urls:
            if len(self.urls) < self.max_num:
                for possible_beginning in possible_beginnings:
                    if possible_beginning in url:
                        soup = BeautifulSoup(requests.get(url).text, 'lxml')
                        for a in soup.find_all('a'):
                            try:
                                if a['href'][:9] == '/recepty/':
                                    address = 'https://eda.ru' + a['href']
                                    u1 = address not in self.urls
                                    u2 = address.count('/') == 5
                                    if u1 and u2:
                                        self.urls.append(address)
                                        i += 1
                                        u3 = i % self.printstep == 0
                                        if self.print_ and u3:
                                            percent = 100 * i / self.max_num
                                            percent = str(round(percent, 3))
                                            print(str0 + percent + str1)
                            except KeyError:
                                print('KeyError')
                                pass
    #       функция возвращает таблицу с рецептами

    def get_tab(self, print_=False, save=True):  # если save - сохраняем
        '''
        Функция для парсинга информации по ссылкам self.urls
        и создания из них DataFrame
        Возвращает pd.DataFrame со следующими данными -
        название, категория, дозы, ингредиенты, рецепт
        Исходные параметры: print_
        если True, то печатаем информацию о ходе парсинга
        save_ если True, то сохраняем распарсенный DataFrame в .db файл
        '''
        regex = re.compile('[^a-zA-Zа-я0-9]!,-?:().')
        if self.answer is not None:
            return self.answer
        else:
            str0 = 'Считываем данные - '
            str1 = ' процентов завершено'
            titles_list = []
            ingredients_list = []
            doses_list = []
            categories = []
            receipt_list = []
            i = 0
            for url in self.urls:
                i += 1
                if self.print_ and i % self.printstep == 0:  # печать
                    percent = 100 * i / len(self.urls)
                    percent = str(round(percent, 3))
                    print(str0 + str(percent) + str1)
                splitted = url.split('/')
                try:
                    res = urllib.request.urlopen(url).read()  # делаем реквест
                except urllib.HTTPError:
                    pass
                bs0 = BeautifulSoup(res, 'lxml')
                # парсим имя
                name = (bs0.find('h1', 'recipe__name g-h1'))
                name = re.sub("<.*?>", " ", str(name))
                name = re.sub('\n', '', name).strip()
                # сужаем область поиска
                text1 = str(bs0.find('div', 'ingredients-list__content'))
                bs1 = BeautifulSoup(text1, 'lxml')
                ingredients = (
                    bs1.find_all(
                        'span',
                        'js-tooltip js-tooltip-ingredient'))
                ingredients = re.sub("<.*?>", " ", str(ingredients))
                # убираем скобки и получаем список ингредиентов
                ingredients = ingredients[1:][:-1].split(',  \n')
                ingredients = [regex.sub(' ', x) for x in ingredients]
                ingredients = [(x.strip()).lower() for x in ingredients]
                # аналогично получаем список доз
                doses = (
                    bs1.find_all(
                        'span',
                        'content-item__measure js-ingredient-measure-amount'))

                doses = re.sub("<.*?>", " ", str(doses))[1:][:-1].split(' ,  ')
                doses = [regex.sub(' ', x) for x in doses]
                doses = [x.strip() for x in doses]

                if name != 'None':
                    bs2 = str(bs0).split('"recipeInstructions":["')
                    receipt = bs2[1].split('"],"recipeYield":')
                    receipt = re.sub('","', '\n', receipt[0])
                    receipt = re.sub('—', '-', receipt)
                    receipt = regex.sub(' ', receipt)
                    titles_list.append(name)
                    ingredients_list.append(list(set(ingredients)))
                    doses_list.append(doses)
                    receipt_list.append(receipt)
                    categories.append(splitted[len(splitted) - 2])
            answer = pd.DataFrame({
                'name': titles_list,
                'category': categories,
                'doses': doses_list,
                'ingredients': ingredients_list,
                'receipt': receipt_list})
            if save:
                save(PROJECT_DIR + "/Data.db", answer)
            return answer


class ConsoleInteractor():  # класс для взаимодействия через станд.поток
    '''
    Класс для взаимодействия с пользователем через стандартный поток(консоли)
    Имеются функции для выбора категории и ингредиентов
    '''

    def choose_category(self):
        '''
        Функция для выбора категории -
        предлагает пользователю выбрать индекс категории
        и передает дальше ее англоязычное наименование
        '''
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
        n = len(categories_en)
        assert n == len(categories_ru)
        for i in range(n):
            print('Введите ' + str(i) +
                  ' для выбора категории ' + str(categories_ru[i]))
        category_index = None
        while category_index not in range(12):
            inp = input()
            try:
                category_index = int(inp)
            except ValueError:
                print("Вы ввели не число")
            if category_index not in range(12):
                print("Вы ввели не то число")
        category = categories_en[category_index]
        return category

    def choose_ingredients(self, total_ingredients):
        '''
        Функция для выбора ингредиентов.
        Исходные аргументы:
        total_ingredients список всех ингредиентов, которые только могут быть
        '''
        print('Введите число ингредиентов(максимум 20)')
        N = None
        while N not in range(20):
            inp = input()
            try:
                N = int(inp)
            except ValueError:
                print("Вы ввели не число")
            if N not in range(20):
                print("Вы ввели не то число")
        chosen_ingredients = list()
        while len(chosen_ingredients) < N:
            min_dist = 9999
            print('Осталось ингредиентов: ' + str(N - len(chosen_ingredients)))
            print('Вводите ингредиент')
            inputted_ingredient = input()
            inputted_ingredient.lower()
            for ingredient in total_ingredients:
                ingredient.lower()
                this_dist = distance(ingredient, inputted_ingredient)
                if this_dist < min_dist:
                    min_dist = this_dist
                    interpreted_ingredient = ingredient
            print(
                'Это из имеющегося списка больше всего похоже на ' +
                str(interpreted_ingredient))
            if interpreted_ingredient not in chosen_ingredients:
                print('Добавить это?  Введите ДА, чтобы добавить')
                if input().lower() == 'да':
                    chosen_ingredients.append(interpreted_ingredient)
                    print('Ингредиент добавлен')
        return chosen_ingredients

    def get_final_tab(self, final_tab, print_answer=True, save_answer=True):
        '''
        Функция для демонстрации финальной таблицы через консоль
        Исходные аргументы:
        final_tab - собственно финальная таблица
        print_answer: если True, то ответ печатаем
        save_answer: если True, то сохраняем ответ в файл Receipts.txt
        '''
        if print_answer:
            try:
                print('Вот блюда, которые Вам проще всего приготовить')
                print(' Число блюд ' + str(len(final_tab)) + '\n')
                for i in final_tab.index:
                    print('НАЗВАНИЕ')
                    print(final_tab['name'][i])
                    print('Число совпадающих ингредиентов')
                    print(final_tab['num_match'][i])
                    print('Доля совпадающих ингредиентов')
                    print(final_tab['share_match'][i])
                    print('ИНГРЕДИЕНТЫ')
                    for j in range(len(final_tab['ingredients'][i])):
                        doze = ' доза ' + final_tab['doses'][i][j]
                        print(final_tab['ingredients'][i][j] + doze)
                    print('РЕЦЕПТ')
                    print(final_tab['receipt'][i])
            except UnicodeEncodeError:
                print('Какие-то проблемы с кодировкой')
                print('Мы не можем отобразить информацию о блюдах на экране')
                print('Поэтому мы запишем ее в файл ' +
                      'в Вашей главной директории проекта')
                save_answer = True
        if save_answer:
            file = open(PROJECT_DIR + "//Receipts.txt", "w", encoding="utf-8")
            file.write('Вот блюда, которые Вам проще всего приготовить\n')
            file.write(' Число блюд ' + str(len(final_tab)) + '\n')
            for i in final_tab.index:
                file.write('НАЗВАНИЕ\n')
                file.write(final_tab['name'][i])
                file.write('\nЧисло совпадающих ингредиентов\n')
                file.write(str(final_tab['num_match'][i]))
                file.write('\nДоля совпадающих ингредиентов\n')
                file.write(str(final_tab['share_match'][i]))
                file.write('\nИНГРЕДИЕНТЫ\n')
                for j in range(len(final_tab['ingredients'][i])):
                    doze = ' доза ' + final_tab['doses'][i][j]
                    file.write(final_tab['ingredients'][i][j] + doze + '\n')
                file.write('\nРЕЦЕПТ\n')
                file.write(final_tab['receipt'][i] + '\n')
            file.close()
            print('Проверьте вашу главную директорию проекта - файл там')


class BackEnd():
    '''
    Класс отвечает за бэкэнд
    Исходные параметры: tab - pd.DataFrame, с которой работаем
    tab_is_loaded = True, если таблицу загрузили из базы данных
    и False, если нет(по умолчанию True)

    Функции: get_total_ingredients
    формирует список всех возможных ингредентов для данной категории
    choose_category делает вызов Interactor-у, чтобы тот выбрал категорию,
    формирует таблицу user_tab
    (где присутствуют только представители данной категории)
    и обновляет total_ingredients так, чтобы там были
    только ингреденты из user_tab
    ingredient_search после того, как список ингредиентов сформирован,
    ищет максимально подходящие наименования блюд.
    Сходство ищется по числу совпадений с пользовательским вводом
    '''

    def __init__(self, tab, tab_is_loaded=True):
        '''
        если загрузили таблицу из б.д -
        преобразуем ingredients и doses из строк в списки
        также делаем get_total_ingredients (сначала для исходной таблицы)
        '''
        self.tab = tab
        if tab_is_loaded and isinstance(tab['ingredients'][tab.index[0]], str):
            for i in self.tab.index:
                self.tab.at[i, 'ingredients'] = (
                    self.tab['ingredients'][i][2:][:-2].split("', '"))
                self.tab.at[i, 'ingredients'] = (
                    self.tab['doses'][i][2:][:-2].split("', '"))
        self.user_tab = None
        self.user_ingredients = None
        self.total_ingredients = None
        self.get_total_ingredients(self.tab)
        self.Interactor = ConsoleInteractor()
        # cjplftv класс для взаимодействия с сайтом

    def get_total_ingredients(self, tab):
        '''
        Функция формирует список
        всех возможных ингредентов для данной категории
        и записывает его в поле класса total_ingredients
        Исходные параметры: pd.DataFrame tab
        '''
        total_ingredients = set()
        for ingredient_portion in tab['ingredients']:
            if isinstance(ingredient_portion, str):
                ingr_list = ingredient_portion[2:][:-2].split("', '")
                for ingredient_portion in ingr_list:
                    # print(ingredient_portion)
                    if ingredient_portion[0] in rus_letters:
                        total_ingredients.update(ingredient_portion)
            else:
                # print(ingredient_portion)
                if ingredient_portion[0][0] in rus_letters:
                    total_ingredients.update(ingredient_portion)
        tmp = sorted(total_ingredients)
        self.total_ingredients = set(tmp)

    def choose_category(self):
        '''
        функция вызывает функцию choose_category у ConsoleInteractor
        и записывает результат в self.category
        Далее функция записывает в переменную user_tab
        только те ряды таблицы tab,
        у которых category та же, что и в self.category
        и вызывает функцию get_total_ingredients, но уже для user_tab
        '''
        self.category = self.Interactor.choose_category()
        self.user_tab = self.tab[self.tab['category'] == self.category]
        self.get_total_ingredients(self.user_tab)

    def choose_ingredients(self):
        '''функция вызывает choose_ingredients
        у ConsoleInteractor, хранит ответ'''
            self.user_ingredients = self.Interactor.choose_ingredients(
                self.total_ingredients)

    def ingredient_search(self, num_answers=3,
                          print_answer=True, save_answer=False):
        '''
        Функция для поиска наиболее подходящих рецептов
        Рецепты сортируются сначала по числу
        совпадений с пользовательским вводом, потом по доле совпадений
        Аргументы:
        num_answers (по умолчанию 3) -
        сколько самых подходящих рецептов выводим
        print_answer (по умолчанию True) -
        если True, то выводим ответ в консоль
        save_answer(по умолчанию False) -
        если True, то сохраняем ответ в директори проекта в Receipts.txt
        '''
        answer = []
        share_match = dict()
        num_match = dict()
        print('Ищем самые похожие рецепты')

        def sort(answer, n):
            for i in range(len(answer)):
                for j in range(i + 1, len(answer)):
                    cond1 = num_match[answer[i]] < num_match[answer[j]]
                    cond2 = num_match[answer[i]] == num_match[answer[j]]
                    cond3 = share_match[answer[i]] < share_match[answer[j]]
                    if i < j and cond1 or (cond2 and cond3):
                        answer[i], answer[j] = answer[j], answer[i]
            return answer[:n]
        for i in self.tab.index:
            num_match[i] = sum(
                [x in self.user_ingredients
                 for x in self.tab['ingredients'][i]])
            share_match[i] = num_match[i] / \
                len(self.tab['ingredients'][i])
            answer.append(i)
            answer = sort(answer, num_answers)
        final_tab = self.tab.loc[answer, :]
        # пишем ДОКУПИТЬ, если какой-то ингредиент пользователь не ввел
        final_tab['num_match'] = ''
        final_tab['share_match'] = ''
        for i in answer:
            tmp = list(final_tab['ingredients'][i])
            for j in range(len(tmp)):
                if tmp[j] not in self.user_ingredients:
                    tmp[j] = tmp[j] + ' - ДОКУПИТЬ!'
            final_tab.at[i, 'ingredients'] = tmp
            final_tab.at[i, 'share_match'] = share_match[i]
            final_tab.at[i, 'num_match'] = num_match[i]
        self.Interactor.get_final_tab(final_tab, print_answer, save_answer)
        return final_tab


class CulinaryApp():
    '''
    Это главный архитектурный уровень
    Исходные параметры: urls - ссылки, с которых начинается парсинг
    (по умолчанию - заданные адреса),
    max_num - число ссылок, начинающихся с urls, которые надо распарсить
    (по умолчанию - 300),
    load - нужно ли загружать SQL базу данных(по умолчанию False)
    save_ - нужно ли сохранять sql базу данных(по умолчанию False)
    print_ - нужно ли выводить в консоль информацию о ходе парсинга
    (по умолчанию True)
    printstep - как часто выводим в консоль информацию о ходе парсинга,
    если выводим(по умолчанию каждые 5 ссылок)
    num_answers - сколько наилучших рецептов выводим(по умолчанию 3)
    '''

    def __init__(self, urls=possible_beginnings.copy(),
                 load=False, max_num=300,
                 print_=True, save_=False, printstep=5, num_answers=3):
        '''
        В конструкторе запускается LinkGetter,
        парсятся ссылки, строится таблица из ссылок
        и запускается конструктор класса  BackEnd
        '''
        self.Getter = LinkGetter(urls, max_num, load, print_, printstep)
        self.Getter.get_links()
        self.tab = self.Getter.get_tab(print_, save_)
        self.BackEnd = BackEnd(self.tab, load)
        self.last_final_tab = None

    def run(self, num_answers=3):
        '''
        Параметры: num_answers - число ответов для отображения
        В цикле много раз(сколько захочет юзер) запускается BackEnd
        т.е у BackEnd выполняются функции
        choose_category и choose_ingredients и ingredient_search
        также в переменную last_final_tab
        сохраняется итоговая таблица с ингредиентами,
        полученная в ходе последнего ingredient_search
        '''
        while True:  # много раз в цикле вызываем бэкэнд
            print('Это наше приложение.')
            print('Хотите понять,что можно приготовить из ваших ингредиентов?')
            print('Нажмите В для выхода. ')
            print('Нажмите любую другую кнопку для запуска приложения')
            if input() in ['В', 'в', 'b', 'B']:
                return 0
            self.BackEnd.choose_category()
            self.BackEnd.choose_ingredients()
            self.last_final_tab = self.BackEnd.ingredient_search(num_answers)


def main():  # i is category
    A = CulinaryApp()
    A.run()
