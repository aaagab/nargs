#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys

# test def_alias regex 

def get_alias_prefixes():
    return ["", "+", "--", "-", "/", ":", "_"]
    
def get_flags_precedence():
    return ['+', '-', '', '/', ':', '_', '--']

def get_regex(reg_name):
    # quotes=r"(?P<values>(?:\=|:)((?P<dquotes>\".*\")|(?P<squotes>\'.*\')|(?P<nquotes>.*)))?"
    # quotes=r"(?:\=?|\:?)(?P<values>(.*))?"
    # quotes=r"(?:\=?)(?P<values>(.*))?"
    values=r"(?P<values_str>(?:\=|:)(?P<values>.*))?"
    prefixes=r"(?P<prefix>\+|--|-|/|:|_)?"
    branch_num=r"(?P<branch_num_str>_(?P<branch_num>[1-9][0-9]*)?)?"
    branch_num2=r"(?P<branch_num_str2>_(?P<branch_num2>[1-9][0-9]*)?)?"
    flags=r"@(?P<chars>[a-zA-Z0-9\?][a-zA-Z0-9@\?]*(?<!@))"
    dy=dict(
        alias_sort_regstr=dict(
            rule=r"^(\+|--|-|/|:|_)",
        ),
        cli_alias=dict(
            # rule=r"^(?P<alias>{}[a-zA-Z0-9\?][a-zA-Z0-9\-_]*?(?<!\-|_)){}{}$".format(prefixes, branch_num, values),
            rule=r"^(?P<alias>{}[a-zA-Z0-9\?][a-zA-Z0-9\-_]*?(?<!\-|_)){}(?P<flags_str>{}{})?{}$".format(prefixes, branch_num, flags, branch_num2, values),
        ),
        cli_flags=dict(
            rule=r"^{}{}{}$".format(flags, branch_num, values),
        ),
        cli_explicit=dict(
            rule=r"^(?:(?P<minus>-)|(?P<equal>=)|(?P<plus_concat>\++)|(?:\+(?P<plus_index>[1-9][0-9]*)))$",
        ),
        def_arg_name=dict(
            name="definition argument name",
            rule=r"^[a-zA-Z][a-zA-Z0-9_]*$",
            hints=[
                "Required First char must be either a lowercase letter or an uppercase letter.",
                "Optional next chars can be any char from lowercase letter, uppercase letter, integer, or underscore.",
            ]
        ),
        def_alias=dict(
            name="definition alias",
            rule=r"^({})([a-zA-Z0-9][a-zA-Z0-9\-_]*)(?<![\-_])$".format(prefixes),
            hints=[
                "First optional prefix can be any prefix from {}".format(get_alias_prefixes()),
                "Required next char must be either a lowercase letter, an uppercase letter, or an integer.",
                "Optional next chars can be any char from lowercase letter, uppercase letter, integer, underscore or hyphen.",
                "Last optional char can't be an underscore or a hyphen.",
            ]
        ),
        def_theme_hexa=dict(
            name="definition theme hexadecimal color",
            rule=r"^(?:#)?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$",
            hints=[
                "Start with optional hash pound.",
                "Then 6 case insensitive hexadecimal numbers are needed.",
            ],
        ),
        def_theme_rgb=dict(
            name="definition theme rgb color",
            rule=r"^([0-9]{1,3});([0-9]{1,3});([0-9]{1,3})$",
            hints=[
                "Required three positive integers separated with a semi-colon.",
                "Positive integers must be less or equal than 255.",
            ],
        ),
        def_values=dict(
            name="definition values",
            rule=r"^(?P<star>\*)|(?P<plus>\+)|(?P<qmark>\?)|(?P<min>[1-9][0-9]*)(?:\-(?P<max>(?:[1-9][0-9]*|\*)))?(?P<optional>\?)?$",
            hints=[
                "_values can be either '*', '+', '?', an integer or a range.",
                "If an integer is given then only a positive integer is authorized.",
                "If a range is given then two positive integers separated with a hyphen are authorized i.e.: 4-5.",
                "If a range is given then last positive integer can also be a star i.e.: 4-*.",
                "A question mark can be appended for integer and range to set values as optional.",
            ],
        ),
    )
    return dy[reg_name]

def get_regex_hints(reg_name):
    dy_regex=get_regex(reg_name)
    tmp_text=[]
    tmp_text.append("Regex name '{}' with rule '{}':".format(dy_regex["name"], dy_regex["rule"]))
    for hint in dy_regex["hints"]:
        tmp_text.append("- {}".format(hint))

    return tmp_text
