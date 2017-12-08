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
