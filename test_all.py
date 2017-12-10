# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 18:13:48 2017

@author: DK
"""

from CulinaryApp import choose_category
from CulinaryApp import possible_beginnings
from CulinaryApp import find_files
import mock
import pandas as pd
import os


def test_find_files():
    link_list = find_files()
    for link in link_list:
        assert any(possible_beginnings in link)

        
def test_choose_category():
    categories_en = ['zakuski', 'napitki', 'zavtraki', 'supy',
                     'salaty', 'vypechka-deserty', 'rizotto', 'bulony',
                     'pasta-picca', 'osnovnye-blyuda', 'sendvichi', 'sousy-marinady']
    tab = pd.read_csv(os.getcwd() + '/Data.csv', sep=';')
    # for i in range(len(categories_en)):
    for i in [5]:
        j = str(i)
        with mock.patch('raw_input', side_effect=j):
            # print(categories_en[int(side_effect)])
            chosen = choose_category(tab)
        assert chosen == categories_en[i]
