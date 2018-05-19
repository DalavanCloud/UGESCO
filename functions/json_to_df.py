# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 07:25:25 2018

@author: ettor
"""
import json
import pandas as pd
from flatten_json import flatten


def json_to_df(json_file):
    """
    Input a json file, flatten it and return it as dataframe
    """
    with open(json_file, encoding="utf8") as f:
        json_file = json.load(f)

    df = pd.DataFrame([flatten(line) for line in json_file])

    return df
