from CulinaryApp import LinkGetter
from CulinaryApp import BackEnd
from CulinaryApp import possible_beginnings
from CulinaryApp import categories_en
# import mock
# import pandas as pd
# import os


def test_LinkGetter():
    obj = LinkGetter(100)
    obj.get_links()
    assert sum(
        [link in beginning for link in obj.urls
         for beginning in possible_beginnings]) == len(possible_beginnings)
    tab = obj.get_tab()
    rus_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    for i in tab.index:
        assert tab['category'][i] in categories_en
        assert tab['name'][i] != 'None'
        assert len(tab['doses'][i]) > 0
        assert len(tab['ingredients'][i]) == len(tab['doses'][i])
        assert sum([x in rus_letters
                    for x in tab['receipt'][i]]) > len(tab['receipt'][i]) / 2
