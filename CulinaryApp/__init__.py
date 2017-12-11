from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import urllib.request
import pandas as pd
import os
from Levenshtein import distance

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


class LinkGetter:
    def __init__(self, max_num, load=True, print_=True, printstep=50):
        self.max_num = max_num
        self.urls = possible_beginnings.copy()
        self.answer = None
        self.print_ = print_
        self.printstep = printstep
        if load:
            self.answer = pd.read_csv(os.getcwd() + '\\Data.csv', sep=';')

    def get_links(self):
        i = 0
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
                                pass

    def get_tab(self, print_=False, save=True):
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
                if self.print_ and i % self.printstep == 0:
                    percent = 100 * i / len(self.urls)
                    percent = str(round(percent, 3))
                    print(str0 + str(percent) + str1)
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
            if save:
                answer.to_csv(os.getcwd() + '\\Data.csv', sep=';')
            return answer


class WebsiteInteractor():
    # def __init__():
        # pass

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
        assert int(inp) in range(n)
        category_index = int(inp)
        category = categories_en[category_index]
        return category

    def choose_ingredients(self, tab):
        # Получаем на вход таблицу tab
        # формат таблицы by default -  csv файл либо pandas dataframe
        # Вовзращаем выбранные ингредиенты из числа тех, которые имелись в tab
        print('Введите число ингредиентов(максимум 20)')
        N = input()
        N = int(N)
        N = min(N, 20)
        total_ingredients = set()
        for ingredient_portion in tab['ingredients']:
            total_ingredients.update(ingredient_portion)
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
    def __init__(self, tab):
        self.tab = tab
        self.user_tab = None
        self.user_ingredients = None
        self.Interactor = WebsiteInteractor()

    def choose_category(self):
        self.category = self.Interactor.choose_category()
        self.user_tab = self.tab[self.tab['category'] == self.category]

    def choose_ingredients(self):
        self.user_ingredients = self.Interactor.choose_ingredients(
            self.user_tab)

    def ingredient_search(self, num_answers=3):
        answer = []
        share_match = dict()
        num_match = dict()
        print('Ищем самые похожие рецепты')

        def sort(answer, n):
            for i in range(len(answer)):
                for j in range(len(answer)):
                    cond1 = num_match[answer[i]] < num_match[answer[j]]
                    cond2 = num_match[answer[i]] == num_match[answer[j]]
                    cond3 = share_match[answer[i]] < share_match[answer[j]]
                    if i < j and cond1 or (cond2 and cond3):
                        answer[i], answer[j] = answer[j], answer[i]
            return answer[:n]
        for i in self.user_tab.index:
            num_match[i] = sum(
                [x in self.user_ingredients
                 for x in self.user_tab['ingredients'][i]])
            share_match[i] = num_match[i] / \
                len(self.user_tab['ingredients'][i])
            answer.append(i)
            answer = sort(answer, num_answers)
        final_tab = self.user_tab.loc[answer, :]
        final_tab['num_match'] = ''
        final_tab['share_match'] = ''
        for i in answer:
            tmp = list(final_tab['ingredients'][i])
            for j in range(len(tmp)):
                if tmp[j] not in self.user_ingredients:
                    tmp[j] = tmp[j] + ' - ДОКУПИТЬ!'
            final_tab.loc[i, 'ingredients'] = tmp
            final_tab.loc[i, 'share_match'] = share_match[i]
            final_tab.loc[i, 'num_match'] = num_match[i]
        self.Interactor.get_final_tab(final_tab)
        return final_tab


class CulinaryApp():
    def __init__(self, max_num=100, load=False,
                 print_=True, printstep=5, num_answers=3):
        self.Getter = LinkGetter(max_num, load, print_, printstep)
        self.Getter.get_links()
        self.tab = self.Getter.get_tab()
        self.BackEnd = BackEnd(self.tab)
        self.run(num_answers)
        self.last_final_tab = None

    def run(self, num_answers=3):
        while True:
            print('Это наше приложение.')
            print('Хотите понять,что можно приготовить из ваших ингредиентов?')
            print('Нажмите В для выхода. ')
            print('Нажмите любую другую кнопку для запуска приложения')
            if input() in ['В', 'в', 'b', 'B']:
                return 0
            self.BackEnd.choose_category()
            self.BackEnd.choose_ingredients()
            self.last_final_tab = self.BackEnd.ingredient_search(num_answers)


def main():
    A = CulinaryApp()
    A.run()
