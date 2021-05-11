#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys

def get_regex(reg_name):
    dy=dict(
        cli_dashless_alias=dict(
            name="command-line dashless alias",
            rule=r"^(?P<alias>[a-zA-Z0-9][a-zA-Z0-9\-]*)(?:_(?P<index>[1-9][0-9]*))?(?:(\=\"(?P<dquotes>.*)\"|\=\'(?P<squotes>.*)\'))?$",
        ),
        cli_long_alias=dict(
            name="command-line long alias",
            rule=r"^(?P<alias>--[a-zA-Z0-9][a-zA-Z0-9\-]*)(?:_(?P<index>[1-9][0-9]*))?(?:(\=\"(?P<dquotes>.*)\"|\=\'(?P<squotes>.*)\'))?$",
        ),
        cli_explicit=dict(
            name="command-line explicit",
            rule=r"^(?:(?P<minus>-)|(?P<plus_concat>\++)|(?:\+(?P<plus_index>[1-9][0-9]*)))$",
        ),
        cli_short_alias=dict(
            name="command-line short alias",
            rule=r"^(?P<alias>-[a-zA-Z0-9])(?:_(?P<index>[1-9][0-9]*))?(?:(\=\"(?P<dquotes>.*)\"|\=\'(?P<squotes>.*)\'))?$",
        ),
        cli_short_alias_concat=dict(
            name="command-line short aliases concatenated",
            rule=r"^-(?P<short_aliases>[a-zA-Z0-9][a-zA-Z0-9]+)$",
        ),
        def_arg_name=dict(
            name="definition argument name",
            rule=r"^[a-zA-Z][a-zA-Z0-9_]*$",
            hints=[
                "Required First char must be either a lowercase letter or an uppercase letter.",
                "Optional next chars can be any char from lowercase letter, uppercase letter, integer, or underscore.",
            ]
        ),
        def_dashless_alias=dict(
            name="definition dashless alias",
            rule=r"^[a-zA-Z0-9][a-zA-Z0-9\-]*$",
            hints=[
                "Required first char must be either a lowercase letter, an uppercase letter, or an integer.",
                "Optional next chars can be any char from lowercase letter, uppercase letter, integer or dash.",
            ]
        ),
        def_long_alias=dict(
            name="definition long alias",
            rule=r"^--[a-zA-Z0-9][a-zA-Z0-9\-]*$",
            hints=[
                "Required first and second char are dashes.",
                "Required third char must be either a lowercase letter, an uppercase letter, or an integer.",
                "Optional next chars can be any char from lowercase letter, uppercase letter, integer or dash.",
            ]
        ),
        def_short_alias=dict(
            name="definition short alias",
            rule=r"^-[a-zA-Z0-9]$",
            hints=[
                "Required first char must be a dash.",
                "Required second char must be either a lowercase letter, an uppercase letter, or an integer.",
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
                "_values can be either '*', '+', '?', an integer or a range",
                "If integer then only a positive integer is accepted",
                "If range then two positive integers separated with a dash are accepted i.e.: 4-5",
                "If range then last positive integer can be a star i.e.: 4-*",
                "A question mark can be appended for integer and range to set values as optional.",
            ],
        ),
        special_cmd=dict(
            name="special command",
            rule=r"^(?:(?P<at1>@{1,3})(?P<cmark1>:{1,3})?|(?P<cmark2>:{1,3})(?P<at2>@{1,3})?)(?P<params>e?h?i?|e?i?h?|h?e?i?|h?i?e?|i?e?h?|i?h?e?)?$",
            hints=[
                "Start with `:` for usage or `@` for argument's path.",
                "Both `:` and `@` can be used in the command and they are related to current argument on the command-line.",
                "`:` and `@` can be repeated three times each for verbosity.",
                "`:`: Print usage of current argument, and first nested arguments.",
                "`::`: Print usage of current argument, nested arguments and sub-nested arguments.",
                "`:::`: Print usage of current argument, and all nested arguments.",
                "`@`: Print current argument's path.",
                "`@@`: Print current argument's path with argument indexes.",
                "`@@@`: Print current argument's path with argument indexes and values.",
                "Params can be added. param `e` print arguments' examples and param `h` print arguments' hint.",
                "Examples: `@:eh`, `:@h`, `@@@?eh`, `:@@@he`, `:ie`",
            ]
        ),
        def_json_data=dict(
            name="definition json data",
            rule="".join([
                r"^(?P<value_type>bool|float|int|str)(?P<list>\[((?P<min>[1-9][0-9]*)(?::(?P<max>[1-9][0-9]*|\*))?)?\])?(?P<qmark>\?)?$",
            ]),
            hints=[
                "Required value type that can be either bool, float, int, or str.",
                "Optional square brackets pair [] to define a list.",
                "Optional one int between brackets for list length.",
                "Optional two ints separated by a comma between brackets for list minimum length and list maximum length.",
                "int minimum length must be smaller than int maximum length.",
                "int minimum must be greater or equal than 1",
                "Optional one int and a star separated by a comma between brackets for list minimum length and list infinite maximum length.",
                "Optional question mark that returns null for a value and returns empty list for a list.",
                "Examples: int, float?, str[], bool[1], int[1:9]?, str[1:*].",
            ]
        ),
    )
    return dy[reg_name]

# e?h?i?|e?h?i?|

# e?h?i?|e?i?h?|h?e?i?|h?i?e?|i?e?h?|i?h?e?
# e i h
# e
# eh
# ei
# ehi
# eih

# h
# he
# hi
# hei
# hie

# i
# ie
# ih
# ieh
# ihe


def get_regex_hints(reg_name):
    dy_regex=get_regex(reg_name)
    tmp_text=[]
    tmp_text.append("Regex name '{}' with rule '{}':".format(dy_regex["name"], dy_regex["rule"]))
    for hint in dy_regex["hints"]:
        tmp_text.append("- {}".format(hint))

    return tmp_text
