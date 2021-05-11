#!/usr/bin/env python3
from pprint import pprint
import os
import sys

def get_type_str(_type):
    if _type == str:
        return "str"
    elif _type == float:
        return "float"
    elif _type == int:
        return "int"
    elif _type == bool:
        return "bool"
    else:
        return _type

def get_type_from_str(_type):
    if _type == "str":
        return str
    elif _type == "float":
        return float
    elif _type == "int":
        return int
    elif _type == "bool":
        return bool
    else:
        return _type