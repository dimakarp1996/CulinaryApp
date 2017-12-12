from CulinaryApp import LinkGetter
from CulinaryApp import BackEnd
from CulinaryApp import possible_beginnings
from CulinaryApp import categories_en
import pandas as pd
import random
# import os


def test_LinkGetter():
    obj = LinkGetter(100)
    obj.get_links()
    assert sum(
        [link in beginning for link in obj.urls
         for beginning in possible_beginnings]) == len(possible_beginnings)
    tab = obj.get_tab(True, False)
    rus_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    for i in tab.index:
        assert tab['category'][i] in categories_en
        assert tab['name'][i] != 'None'
        assert len(tab['doses'][i]) > 0
        assert len(tab['ingredients'][i]) == len(tab['doses'][i])
        assert sum([x in rus_letters
                    for x in tab['receipt'][i]]) > len(tab['receipt'][i]) / 2


def test_BackEnd():
    def cond1(final_tab, i):
        return final_tab['num_match'][i] >= max(final_tab['num_match'][i + 1:])

    def cond2(final_tab, i):
        equal_cond = final_tab['num_match'] == final_tab['num_match'][i]
        if len(final_tab['share_match'][i + 1:][equal_cond]) > 0:
            this_max = max(final_tab['share_match'][i + 1:][equal_cond])
            assert final_tab['share_match'][i] >= this_max
        return True
    random.seed(0)
    max_ingr = 3  # maximal number of ingredients
    max_trys = 4  # number of tries on each # of ingredients
    f = LinkGetter(200)
    f.get_links()
    tab = f.get_tab(True, False)
    for category in categories_en:
        print('Тестируем ' + str(category))
        user_tab = tab[tab['category'] == category]
        obj = BackEnd(user_tab, True)
        total_ingredients = set()
        for ingredient_portion in obj.tab['ingredients']:
            total_ingredients.update(ingredient_portion)
        for i in range(2, min(max_ingr, 20)):
            for j in range(min(max_trys, len(total_ingredients))):
                fake_user_input = random.sample(total_ingredients, i)
                obj.user_ingredients = fake_user_input
                final_tab = obj.ingredient_search(len(user_tab))
                final_tab.index = range(len(final_tab))
                for k in range(3):
                    assert cond1(final_tab, k)
                    assert cond2(final_tab, k)
