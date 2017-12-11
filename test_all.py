#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 14:30:23 2017

@author: tcs-user
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 18:13:48 2017
@author: DK
"""

from CulinaryApp import possible_beginnings
from CulinaryApp import find_files
import mock
import pandas as pd
import os


def test_find_files():
    link_list = find_files()
    assert sum(
        [link in beginning for link in link_list for beginning in possible_beginnings]) > 0
