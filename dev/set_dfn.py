#!/usr/bin/env python3
from pprint import pprint
import json
import os 
import re
import sys

from .get_types import get_type_str
from .regexes import get_regex, get_regex_hints

from ..gpkgs import message as msg

def get_dfn_prefix(app_name, location=None, option=None):
    prefix="For '{}' at Nargs in definition".format(app_name)

    if location is None and option is None:
        return prefix
    else:
        prefix+=" for argument '{}'".format(location)
        if option is None:
            return prefix
        else:
            return "{} at key '{}'".format(prefix, option)

def get_dy(
    location,
    name,
    dy,
    is_root,
    sibling_level,
    pretty,
    app_name,
    dy_attr_aliases,
):
    tmp_dy=dict()
    tmp_dy["is_builtin"]=get_is_builtin(location, dy)
    chars=get_chars(location, dy, pretty, app_name)
    dy_aliases=get_aliases(location, name, dy, tmp_dy, sibling_level, pretty, app_name, dy_attr_aliases, chars)
    tmp_dy["dfn_aliases"]=dy_aliases["aliases"]
    tmp_dy["aliases"]=[]
    tmp_dy["auto_alias"]=dy_aliases["auto_alias"]
    tmp_dy["default_alias"]=None

    tmp_dy["enabled"]=get_enabled(location, dy, pretty, app_name)
    tmp_dy["examples"]=get_examples(location, dy, pretty, app_name)
    tmp_dy["hint"]=get_hint(location, dy, pretty, app_name)
    tmp_dy["info"]=get_info(location, dy, pretty, app_name)
    tmp_dy["type"]=get_type(location, dy, tmp_dy, pretty, app_name)
    tmp_dy["label"]=get_label(location, dy, tmp_dy, pretty, app_name)
    tmp_dy["repeat"]=get_repeat(location, dy, pretty, app_name)
    tmp_dy["required"]=get_required(location, dy, is_root, tmp_dy, pretty, app_name)
    tmp_dy["required_children"]=[]
    tmp_dy["xor"]=get_xor(location, dy, tmp_dy)

    
    tmp_dy["show"]=get_show(location, dy, pretty, app_name)
    dy_values=get_values(location, dy, tmp_dy, pretty, app_name)
    tmp_dy["value_min"]=dy_values["min"]
    tmp_dy["value_max"]=dy_values["max"]
    tmp_dy["value_required"]=dy_values["required"]

    dy_in=get_in(location, dy, tmp_dy, pretty, app_name)
    tmp_dy["in"]=dy_in["in"]
    tmp_dy["in_labels"]=dy_in["in_labels"]
    tmp_dy["default"]=get_default(location, dy, tmp_dy, name, pretty, app_name)

    return tmp_dy

# def get_xor

def get_xor(location, dy, tmp_dy):
    prefix=get_prefix(location, "_either")
    if "_either" in dy:
        _either=dy["_either"]
        del dy["_either"]

        if isinstance(_either, list):
            pass
        elif isinstance(_either, str):
            _either=[_either]
        else:
            msg.error("type error '{}'. It must be '{}' or '{}'.".format(type(_either), str, list), prefix=prefix, exit=1)

        ret_either=[]
        ret_either_ids=[]
        tmp_dy["either_names"]=[]
        for tmp_either in _either:
            if isinstance(tmp_either, str):
                values=tmp_either.split(",")
                if len(values) < 2:
                    msg.error("at least 2 values are needed in  {}.".format(values), prefix=prefix, exit=1)

                tmp_ret_either=[]
                for value in values:
                    value=value.strip()
                    if value == "":
                        msg.error("empty value not allowed in {}.".format(values), prefix=prefix, exit=1)
                    if value in tmp_ret_either:
                        msg.error("duplicate value not allowed in {}.".format(values), prefix=prefix, exit=1)
                    tmp_ret_either.append(value)
                    if value not in tmp_dy["either_names"]:
                        tmp_dy["either_names"].append(value)

                tmp_ret_either.sort()
                ret_either_id=",".join(tmp_ret_either)
                if ret_either_id in ret_either_ids:
                    msg.error("duplicate lists not allowed {}.".format(tmp_ret_either), prefix=prefix, exit=1)

                ret_either_ids.append(ret_either_id)                    
                ret_either.append(tmp_ret_either)
            else:
                msg.error("for sub-value '{}' type error '{}'. It must be '{}'.".format(_tmp_either, type(_tmp_either), str), prefix=prefix, exit=1)
        # tmp_dy["either_names"].sort()
        return ret_either
    else:
        return None

def get_chars(location, dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_chars")
    if "_chars" in dy:
        _chars=dy["_chars"]
        del dy["_chars"]
        tmp_chars=[]
        if _chars is not None:
            if isinstance(_chars, str):
                for tmp_char in _chars.split(","):
                    tmp_chars.append(tmp_char.strip())
            elif isinstance(_chars, list):
                for tmp_char in _chars:
                    if isinstance(tmp_char, str):
                        tmp_chars.append(tmp_char.strip())
                    else:
                        msg.error("value type {} type must be of type {}.".format(type(tmp_char), str), prefix=prefix, pretty=pretty, exit=1)
            else:
                msg.error("valute type {} must be either type {} or type {}.".format(type(_chars), str, list ), prefix=prefix, pretty=pretty, exit=1)

        tmp_chars=sorted(list(set(tmp_chars)))
        for tmp_char in tmp_chars:
            reg=re.match(get_regex("def_chars")["rule"], tmp_char)
            if not reg:
                msg.error([
                    "char '{}' for concatenated aliases syntax error.".format(tmp_char),
                    "Syntax must match:",
                    *get_regex_hints("def_chars"),
                ], prefix=prefix, pretty=pretty, exit=1)

        return tmp_chars
    else:
        return []

def get_aliases(location, name, dy_user, dy_options, sibling_level, pretty, app_name, dy_attr_aliases, chars):
    dy_aliases=dict(
        auto_alias=False,
        dashless_alias=[],
        long_alias=[],
        short_alias=[],
    )

    aliases=[]

    prefix=get_dfn_prefix(app_name, location, "_aliases")
    auto_alias=True
    if "_aliases" in dy_user:
        _aliases=dy_user["_aliases"]
        del dy_user["_aliases"]
        if _aliases is not None:
            tmp_aliases=[]
            if isinstance(_aliases, str):
                for tmp_alias in _aliases.split(","):
                    tmp_aliases.append(tmp_alias.strip())
            elif isinstance(_aliases, list):
                for tmp_alias in _aliases:
                    if isinstance(tmp_alias, str):
                        tmp_aliases.append(tmp_alias.strip())
                    else:
                        msg.error("value type {} type must be of type {}.".format(type(tmp_alias), str), prefix=prefix, pretty=pretty, exit=1)
            else:
                msg.error("valute type {} must be either type {} or type {}.".format(type(_aliases), str, list ), prefix=prefix, pretty=pretty, exit=1)

            tmp_aliases=sorted(list(set(tmp_aliases)))
            for alias in tmp_aliases:
                auto_alias=False
                dy_regex=get_regex("def_alias")
                reg_str=dy_regex["rule"].format(dy_attr_aliases["alias_prefixes_regstr"])
                if re.match(reg_str, alias) is None:
                    msg.error([
                        "alias '{}' syntax error.".format(alias),
                        "Syntax must match regex rule '{}'".format(reg_str),
                        "- First optional prefix can be any prefix from {}".format(dy_attr_aliases["alias_prefixes_reghint"]),
                        *["- "+txt for txt in dy_regex["hints"]],
                    ], prefix=prefix, pretty=pretty, exit=1)
                else:
                    aliases.append(alias)

    if auto_alias is True:
        style=dy_attr_aliases["auto_alias_style"]
        if dy_options["is_builtin"] is True:
            name=name[1:-1]
        elems=name.split("_")

        if "camelcase" in style:
            tmp_elems=[elem.capitalize() for elem in elems if elem != elems[0]]
            tmp_elems.insert(0, elems[0])
            elems=tmp_elems
        elif "lowercase" in style:
            elems=[elem.lower() for elem in elems]
        elif "pascalcase" in style:
            elems=[elem.capitalize() for elem in elems]
        elif "uppercase" in style:
            elems=[elem.upper() for elem in elems]

        elems_str=dy_attr_aliases["auto_alias_prefix"]
        if "-hyphen" in style:
            elems_str+="-".join(elems)
        else:
            elems_str+="".join(elems)
        aliases.append(elems_str)

    for c in chars:
        aliases.append("{}{}".format(
            dy_attr_aliases["char_prefix"],
            c,
        ))

    return dict(
        auto_alias=auto_alias,
        aliases=aliases,
    )


def get_type(location, dy, tmp_dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_type")
    if "_type" in dy:
        _type=dy["_type"]
        del dy["_type"]
        authorized_types=[
            None,
            ".json",
            "bool",
            "dir",
            "file",
            "float",
            "int",
            "json",
            "path",
            "str",
            "vpath",
        ]

        if _type == "bool":
            return bool
        elif _type == "float":
            return float
        elif _type == "int":
            return int
        elif _type == "str":
            return str
        elif _type in authorized_types:
            return _type
        else:
            msg.error("value '{}' not found in authorized types {}.".format(_type, authorized_types), prefix=prefix, pretty=pretty, exit=1)
    else:
        return None

def get_label(location, dy, tmp_dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_label")
    if "_label" in dy:
        _label=dy["_label"]
        del dy["_label"]
        if _label is None:
            return None
        elif isinstance(_label, str):
            return _label.upper()
        else:
            msg.error("value type {} must be of type {}.".format(type(_label), str), prefix=prefix, pretty=pretty, exit=1)
    else:
        return None

def get_is_builtin(location, dy):
    if "_is_builtin" in dy:
        _is_builtin=dy["_is_builtin"]
        del dy["_is_builtin"]
        return _is_builtin
    else:
        return False

def get_values(location, dy_user, dy_options, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_values")
    dy_values=dict(
        required=None,
        min=None,
        max=None,
    )
    if "_values" in dy_user:
        _values=dy_user["_values"]
        del dy_user["_values"]
        if isinstance(_values, str):
            reg=re.match(get_regex("def_values")["rule"], _values)
            if reg:
                if reg.group("star") is not None:
                    dy_values["min"]=1
                    dy_values["max"]=None
                    dy_values["required"]=False
                elif reg.group("plus") is not None:
                    dy_values["min"]=1
                    dy_values["max"]=None
                    dy_values["required"]=True
                elif reg.group("qmark") is not None:
                    dy_values["min"]=1
                    dy_values["max"]=1
                    dy_values["required"]=False
                elif reg.group("min") is not None:
                    _min=int(reg.group("min"))
                    _max=reg.group("max")

                    if _max is None:
                        dy_values["max"]=_min
                    elif _max == "*":
                        dy_values["max"]=None
                    else:
                        _max=int(_max)
                        if _max <= _min:
                            msg.error("max value '{}' must be greater than min value '{}'.".format(_max, _min), prefix=prefix, pretty=pretty, exit=1)
                        dy_values["max"]=_max

                    dy_values["min"]=_min

                    if reg.group("optional") is None:
                        dy_values["required"]=True
                    else:
                        dy_values["required"]=False
            else:
                msg.error([
                    "value '{}' syntax error.".format(_values),
                    "Value syntax must match regex:",
                    *get_regex_hints("def_values"),
                ], prefix=prefix, pretty=pretty, exit=1)
        elif _values is None:
            dy_values=dict(
                required=None,
                min=None,
                max=None
            )
        else:
            try:
                _values=int(_values)
            except:
                msg.error("value type {} must be either of type {} or of type {}.".format(type(_values), str, int), prefix=prefix, pretty=pretty, exit=1)

            if _values > 0:
                dy_values["min"]=_values
                dy_values["max"]=_values
                dy_values["required"]=True
            else:
                msg.error("when value is of type {} then it must be greater than 0.".format(int), prefix=prefix, pretty=pretty, exit=1)

    if dy_values["required"] is None:
        if dy_options["type"] is None:
            if dy_options["label"] is None:
                pass
            else:
                dy_options["type"]=str
                dy_values["min"]=1
                dy_values["max"]=1
                dy_values["required"]=True
        else:
            dy_values["min"]=1
            dy_values["max"]=1
            dy_values["required"]=True
    else:
        if dy_options["type"] is None:
            dy_options["type"]=str

    return dy_values

def get_show(location, dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_show")
    if "_show" in dy:
        _show=dy["_show"]
        del dy["_show"]
        if _show is None:
            return True
        elif isinstance(_show, bool):
            return _show
        else:
            msg.error("value type {} must be of type {}.".format(type(_show), bool), prefix=prefix, pretty=pretty, exit=1)
    else:
        return True

def get_required(location, dy, is_root, tmp_dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_required")
    if "_required" in dy:
        _required=dy["_required"]
        del dy["_required"]

        if is_root:
            return True
        elif _required is None:
            return False
        elif isinstance(_required, bool):
            return _required
        else:
            msg.error("value type {} must be of type {}.".format(type(_required), bool), prefix=prefix, pretty=pretty, exit=1)
    else:
        if is_root:
            return True
        else:
            return False

def get_repeat(location, dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_repeat")
    if "_repeat" in dy:
        _repeat=dy["_repeat"]
        del dy["_repeat"]

        if _repeat is None:
            return "replace"

        authorized_repeats=["append", "exit", "fork", "replace"]
        if _repeat in authorized_repeats:
            return _repeat
        else:
            msg.error("value '{}' not found in {}.".format(_repeat, authorized_repeats), prefix=prefix, pretty=pretty, exit=1)
    else:
        return "replace"

def get_in(location, dy_user, dy_options, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_in")
    dy_in=dict({
        "in": None,
        "in_labels": [],
    })
    if "_in" in dy_user:
        _in=dy_user["_in"]
        del dy_user["_in"]

        if _in is None:
            return dy_in

        if dy_options["type"] in [".json", "json"]:
            msg.error("option can't be set for type {}.".format(dy_options["type"]), prefix=prefix, pretty=pretty, exit=1)

        if dy_options["type"] is None:
            dy_options["type"]=str

        if dy_options["value_min"] is None and dy_options["value_max"] is None:
            dy_options["value_min"]=1
            dy_options["value_max"]=1
            dy_options["value_required"]=True

        authorized_ins=[ dict, list, str]
        tmp_ins=[]
        if isinstance(_in, str):
            for tmp_in in sorted(_in.split(",")):
                tmp_in=tmp_in.strip()
                if len(tmp_in) > 0:
                    tmp_ins.append(tmp_in.strip())
        elif type(_in) in [ list, dict ]:
            tmp_ins=sorted(_in)
        else:
            msg.error("value type {} not found in authorized types {}.".format(type(_in), authorized_ins), prefix=prefix, pretty=pretty, exit=1)

        if len(tmp_ins) == 0:
            return dy_in
        
        dy_in["in"]=[]
        for tmp_in in tmp_ins:
            new_in=None
            if dy_options["type"] == bool:
                if isinstance(tmp_in, bool):
                    new_in=tmp_in
                else:
                    new_in=None
            elif dy_options["type"] == float:
                try:
                    new_in=float(tmp_in)
                except:
                    new_in=None
            elif dy_options["type"] == int:
                try:
                    new_in=int(tmp_in)
                except:
                    new_in=None
            elif dy_options["type"] == str:
                if isinstance(tmp_in, str):
                    new_in=tmp_in
                else:                    
                    new_in=None
            elif dy_options["type"] in ["dir", "file", "path", "vpath"]:
                if isinstance(tmp_in, str):
                    new_in=tmp_in
                else:                    
                    new_in=None

            if new_in is None:
                if isinstance(_in, dict):
                    msg.error("dictionary key '{}' does not match type {} or can't be converted to type {}.".format(tmp_in, dy_options["type"], dy_options["type"]), prefix=prefix, pretty=pretty, exit=1)
                else:
                    msg.error("value '{}' does not match type {} or can't be converted to type {}.".format(tmp_in, dy_options["type"], dy_options["type"]), prefix=prefix, pretty=pretty, exit=1)
            else:
                if isinstance(_in, dict):
                    value=_in[tmp_in]
                    if not isinstance(value, str):
                        msg.error("at key '{}' value type {} must be of type {}.".format(tmp_in, type(value), str), prefix=prefix, pretty=pretty, exit=1)
                dy_in["in"].append(new_in)

        if dy_options["label"] is not None:
            msg.error("_label must be None when _in is set.", prefix=prefix, pretty=pretty, exit=1)

        dy_in["in"].sort()
        if isinstance(_in, dict):
            for k in dy_in["in"]:
                dy_in["in_labels"].append(_in[k])

        return dy_in
    else:
        return dy_in

def get_hint(location, dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_hint")
    if "_hint" in dy:
        _hint=dy["_hint"]
        del dy["_hint"]
        if _hint is None:
            return None
        elif isinstance(_hint, str):
            _hint=_hint.strip()
            if len(_hint) == 0:
                return None
            elif len(_hint) <= 100:
                return _hint
            else:
                msg.error("value length '{}' must be less or equal than '100'.".format(len(_hint)), prefix=prefix, pretty=pretty, exit=1)
        else:
            msg.error("value type {} must be of type {}.".format(type(_hint), str), prefix=prefix, pretty=pretty, exit=1)
    else:
        return None

def get_info(location, dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_info")
    if "_info" in dy:
        _info=dy["_info"]
        del dy["_info"]
        if _info is None:
            return None
        elif isinstance(_info, str):
            _info=_info.strip()
            if len(_info) == 0:
                return None
            else:
                return _info
        else:
            msg.error("value type {} must be of type {}.".format(type(_info), str), prefix=prefix, pretty=pretty, exit=1)
    else:
        return None

def get_examples(location, dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_examples")
    if "_examples" in dy:
        _examples=dy["_examples"]
        del dy["_examples"]

        if _examples is None:
            return None
    
        tmp_examples=[]
        if isinstance(_examples, str):
            _examples=_examples.strip()
            if _examples != "":
                tmp_examples.append(_examples)
        elif isinstance(_examples, list):
            for example in _examples:
                if isinstance(example, str):
                    example=example.strip()
                    if example != "":
                        tmp_examples.append(example)
                else:
                    msg.error("At least one element in examples list is not of type {}.".format(str), prefix=prefix, pretty=pretty, exit=1)
        else:
            msg.error("value type {} must be either of type {} or type {}.".format(type(_examples), str, list), prefix=prefix, pretty=pretty, exit=1)
        
        if len(tmp_examples) == 0:
            return None
        else:
            return tmp_examples
    else:
        return None

def get_enabled(location, dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_enabled")
    if "_enabled" in dy:
        _enabled=dy["_enabled"]
        del dy["_enabled"]

        if _enabled is None:
            return True
        elif isinstance(_enabled, bool):
            return _enabled
        else:
            msg.error("value type {} must be of type {}.".format(type(_enabled), bool), prefix=prefix, pretty=pretty, exit=1)
    else:
        return True

def get_default(location, dy_user, dy_options, argument_name, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_default")

    if "_default" in dy_user:
        _default=dy_user["_default"]
        del dy_user["_default"]

        if _default is None:
            return None

        if dy_options["type"] in [".json", "json"]:
            msg.error("option can't be set for type {}.".format(dy_options["type"]), prefix=prefix, pretty=pretty, exit=1)

        if dy_options["value_required"] is False:
            msg.error("values can't be optional when _default is set. Set '_values' with at least a required minimum of values.", prefix=prefix, pretty=pretty, exit=1)

        if dy_options["type"] is None:
            dy_options["type"]=str

        list_at_start=True
        if not isinstance(_default, list):
            list_at_start=False
            _default=[_default]

        expected_type=None
        if dy_options["type"] in ["dir", "file", "path", "vpath"]:
            expected_type=str
        else:
            expected_type=dy_options["type"]

        tmp_defaults=[]
        for value in _default:
            if type(value) != expected_type:
                msg.error(" value type '{}' must be of type {}.".format(
                    type(value),
                    expected_type, 
                ), prefix=prefix, pretty=pretty, exit=1)

            if dy_options["in"] is not None:
                if value not in dy_options["in"]:
                    msg.error("value '{}' is not found in option _in values {}.".format(value, sorted(dy_options["in"])), prefix=prefix, pretty=pretty, exit=1)

            tmp_defaults.append(value)

        if dy_options["value_min"] is None and dy_options["value_max"] is None:
            dy_options["value_min"]=len(tmp_defaults)
            dy_options["value_max"]=len(tmp_defaults)
            dy_options["value_required"]=True
        else:
            if len(tmp_defaults) < dy_options["value_min"]:
                msg.error("number of values '{}' does not match minimum number of values '{}'.".format(len(tmp_defaults), dy_options["value_min"]), prefix=prefix, pretty=pretty, exit=1)

            if dy_options["value_max"] is not None:
                if len(tmp_defaults) > dy_options["value_max"]:
                    msg.error("number of values '{}' does not match maximum number of values '{}'.".format(len(tmp_defaults), dy_options["value_max"]), prefix=prefix, pretty=pretty, exit=1)

        if list_at_start is True:
            return tmp_defaults
        else:
            return tmp_defaults[0]
    else:
        return None
