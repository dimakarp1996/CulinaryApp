from CulinaryApp import possible_beginnings
from CulinaryApp import find_files
import mock
import pandas as pd
import os


def test_find_files():
    link_list = find_files()
    assert sum(
        [link in beginning for link in link_list
         for beginning in possible_beginnings]) > 0
