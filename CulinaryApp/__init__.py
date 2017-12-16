from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import urllib.request
import pandas as pd
import os
import json
from Levenshtein import distance

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


class LinkGetter:  # класс для получения ссылок и их парсинга в табицу
    def __init__(self, urls=possible_beginnings.copy(),
                 max_num=50, load=False, print_=True, printstep=50):
        self.max_num = max_num  # верхняя граница числа ссылок
        self.urls = urls
        # начинаем искать с этих адресов
        self.answer = None
        self.print_ = print_  # если print_==True, выводим то, сколько % готово
        self.printstep = printstep  # выводим каждый printstep шагов
        if load:  # тогда просто считываем из файла
            self.answer = pd.read_csv(os.getcwd() + '/Data.csv', sep=';')
            if len(self.urls) == 1:
                for category in categories_en:
                    if category in self.urls[0]:
                        self.answer = self.answer[(
                            self.answer['category'] == category)]

    def get_links(self):
        # на выходе заполненное ссылками self.urls
        i = 0
        str0 = 'Ищем для вас ссылки - '
        str1 = ' процентов завершено'
        for url in self.urls:
            if len(self.urls) < self.max_num + len(possible_beginnings):
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
                                pass
    #       функция возвращает таблицу с рецептами

    def get_tab(self, print_=False, save=True):  # если save - сохраняем
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
                res = urllib.request.urlopen(url).read()  # делаем реквест
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
                ingredients = [(x.strip()).lower() for x in ingredients]
                # аналогично получаем список доз
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
                    ingredients_list.append(list(set(ingredients)))
                    doses_list.append(doses)
                    receipt_list.append(receipt)
                    categories.append(splitted[len(splitted) - 2])
            answer = pd.DataFrame({'category': categories,
                                   'name': titles_list,
                                   'receipt': receipt_list,
                                   'ingredients': ingredients_list,
                                   'doses': doses_list})
            if save:
                answer.to_csv(os.getcwd() + '/Data.csv', sep=';')
            return answer


class WebsiteInteractor():  # класс для взаимодействия с вебсайтом
    # класс будет переписан, скорее всего, как только реальный сайт будет

    def choose_category(self):
        # Предлагаем выйти одну из этих категорий
        # возвращаем ее англоязычное название
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

    def choose_ingredients(self, tab):
        # Получаем на вход таблицу tab
        # формат таблицы by default -  csv файл либо pandas dataframe
        # Вовзращаем выбранные ингредиенты из числа тех, которые имелись в tab
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
            for ingredient in self.total_ingredients:
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

    def get_final_tab(self, final_tab):
        # Получаем на вход итоговую таблицу и показываем ее
        print('Вот блюда, которые Вам проще всего приготовить')
        print(' Число блюд ' + str(len(final_tab)))
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


class BackEnd():
    def __init__(self, tab, tab_is_loaded=True):
        # инициализируем класс таблицей
        self.tab = tab
        if tab_is_loaded and isinstance(tab['ingredients'][tab.index[0]], str):
            for i in self.tab.index:
                self.tab.at[i, 'ingredients'] = (
                    self.tab['ingredients'][i][2:][:-2].split("', '"))
                self.tab.at[i, 'ingredients'] = (
                    self.tab['doses'][i][2:][:-2].split("', '"))
        self.user_ingredients = None
        self.total_ingredients = None
        self.get_total_ingredients()
        self.Interactor = WebsiteInteractor()
        # cjplftv класс для взаимодействия с сайтом

    def get_total_ingredients(self):
        total_ingredients = set()
        for ingredient_portion in self.tab['ingredients']:
            if isinstance(ingredient_portion, str):
                ingr_list = ingredient_portion[2:][:-2].split("', '")
                total_ingredients.update(ingr_list)
            else:
                total_ingredients.update(ingredient_portion)
        self.total_ingredients = total_ingredients

    def choose_category(self):
        # выбираем категорию, пользуясь Interactor
        # выбираем в таблице только те рецепты,
        # у которых категория такая,какую ввел пользователь
        self.category = self.Interactor.choose_category()
        self.tab = self.tab[self.tab['category'] == self.category]
        self.get_total_ingredients()

    def choose_ingredients(self):
        # получаем ингредиенты от WebsiteInteractor
        self.user_ingredients = self.Interactor.choose_ingredients(
            self.user_tab)

    def ingredient_search(self, num_answers=3):
        # сортируем рецепты сначала по числу совпадающих ингредиентов
        # потом по доле совпадающих ингредиентов
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
        self.Interactor.get_final_tab(final_tab)
        return final_tab


class CulinaryApp():  # первый и гравный архитектурный уровень
    def __init__(self, urls=possible_beginnings, load=False, max_num=100,
                 print_=True, printstep=5, num_answers=3):
        self.Getter = LinkGetter(urls, max_num, load, print_, printstep)
        self.Getter.get_links()
        self.tab = self.Getter.get_tab()
        self.BackEnd = BackEnd(self.tab, load)
        self.last_final_tab = None

    def run(self, num_answers=3):
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





def get_ingredients_by_ingredient_list(i, ingredient_list, num_answers=3):
    A = CulinaryApp(possible_beginnings[i], True)
    A.BackEnd.user_ingredients = ingredient_list
    answer = A.BackEnd.ingredient_search(num_answers)
    answer = answer.to_json()
    return answer
