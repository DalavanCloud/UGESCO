# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 07:25:25 2018

@author: ettor
"""
import json
import pandas as pd
from flatten_json import flatten


def json_to_df(file):
    """
    Input a json file, flatten it and return it as dataframe
    """
    with open(r"C:\Users\ettor\Documents\GitHub\UGESCO\data\jsondata_ugesco.json", "r") as f:
        json_file = json.load(f)

    df = pd.DataFrame([flatten(line) for line in json_file])

    return df
