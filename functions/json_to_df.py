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


#df2 = pd.melt(df1, id_vars=["beeldid",
#                            "imageclassification_class1",
#                            "imageclassification_class2",
#                            "imageclassification_prob1",
#                            "imageclassification_prob2"],
#              value_vars=["spatial_key_0",
#                          "spatial_key_1",
#                          "spatial_key_2",
#                          "spatial_key_3",
#                          "spatial_key_4",
#                          "spatial_key_5",
#                          "spatial_key_6",
#                          "spatial_key_7",
#                          "spatial_value_0",
#                          "spatial_value_1",
#                          "spatial_value_2",
#                          "spatial_value_3",
#                          "spatial_value_4",
#                          "spatial_value_5",
#                          "spatial_value_6",
#                          "spatial_value_7"])
#print(df2)


