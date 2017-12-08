# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 18:13:48 2017

@author: DK
"""

from CulinaryApp import choose_category
from CulinaryApp import possible_beginnings
from CulinaryApp import find_files
import mock


def test_choose_category():
    categories_en = ['zakuski', 'napitki', 'zavtraki', 'supy',
                     'salaty', 'vypechka-deserty', 'rizotto', 'bulony',
                     'pasta-picca', 'osnovnye-blyuda', 'sendvichi', 'sousy-marinady']
    for i in range(12):
        with mock.patch('builtins.input', side_effect=str(i)):
            assert choose_category() == categories_en[i]


def test_find_files():
    link_list = find_files()
    for link in link_list:
        assert any(possible_beginnings in link)
