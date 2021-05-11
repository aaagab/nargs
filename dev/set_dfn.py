#!/usr/bin/env python3
from pprint import pprint
import json
import os 
import re
import sys

from .get_types import get_type_str
from .regexes import get_regex, get_regex_hints

from ..gpkgs import message as msg

def get_dfn_prefix(location=None, option=None):
    prefix="Nargs in definition"

    if location is None and option is None:
        return prefix
    else:
        prefix+=" for argument '{}'".format(location)
        if option is None:
            return prefix
        else:
            return "{} at key '{}'".format(prefix, option)

def get_dy(location, name, dy, is_root):
    tmp_dy=dict()

    if dy is None:
        dy=dict()
    elif not isinstance(dy, dict):
        msg.error("value with type {} must be of type {}.".format(type(dy), dict), prefix=get_dfn_prefix(location), exit=1)

    dy_aliases=get_aliases(location, name, dy)
    tmp_dy["dashless_alias"]=dy_aliases["dashless_alias"]
    tmp_dy["long_alias"]=dy_aliases["long_alias"]
    tmp_dy["short_alias"]=dy_aliases["short_alias"]
    tmp_dy["auto_aliases"]=dy_aliases["auto_aliases"]

    tmp_dy["enabled"]=get_enabled(location, dy)
    tmp_dy["examples"]=get_examples(location, dy)
    tmp_dy["hint"]=get_hint(location, dy)
    tmp_dy["info"]=get_info(location, dy)
    tmp_dy["type"]=get_type(location, dy, tmp_dy)
    tmp_dy["label"]=get_label(location, dy, tmp_dy)
    tmp_dy["repeat"]=get_repeat(location, dy)
    tmp_dy["single"]=get_single(location, dy)
    tmp_dy["required"]=get_required(location, dy, is_root, tmp_dy)
    tmp_dy["required_children"]=[]
    
    tmp_dy["either"]=get_either(location, dy, tmp_dy)
    tmp_dy["either_notation"]=None
    
    tmp_dy["show"]=get_show(location, dy)
    dy_values=get_values(location, dy, tmp_dy)
    tmp_dy["value_min"]=dy_values["min"]
    tmp_dy["value_max"]=dy_values["max"]
    tmp_dy["value_required"]=dy_values["required"]

    tmp_dy["in"]=get_in(location, dy, tmp_dy)
    tmp_dy["default"]=get_default(location, dy, tmp_dy, name)

    tmp_dy["is_builtin"]=get_is_builtin(dy)

    return tmp_dy

def get_either(location, dy, tmp_dy):
    prefix=get_dfn_prefix(location, "_either")
    if "_either" in dy:
        _either=dy["_either"]
        del dy["_either"]

        if isinstance(_either, list):
            pass
        elif isinstance(_either, str):
            _either=[_either]
        else:
            msg.error("value type {} must be either of type {} or type {}.".format(type(_either), str, list), prefix=prefix, exit=1)

        ret_either=[]
        ret_either_ids=[]
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

                tmp_ret_either.sort()
                ret_either_id=",".join(tmp_ret_either)
                if ret_either_id in ret_either_ids:
                    msg.error("duplicate lists not allowed {}.".format(tmp_ret_either), prefix=prefix, exit=1)

                ret_either_ids.append(ret_either_id)                    
                ret_either.append(tmp_ret_either)
            else:
                msg.error("for sub-value '{}' value type {} must be of type {}.".format(_tmp_either, type(_tmp_either), str), prefix=prefix, exit=1)
        return ret_either
    else:
        return None

def get_single(location, dy):
    prefix=get_dfn_prefix(location, "_single")
    if "_single" in dy:
        _single=dy["_single"]
        del dy["_single"]
        if _single is None:
            return False
        if isinstance(_single, bool):
            return _single
        else:
            msg.error("value type {} must be of type {}.".format(type(_single), bool), prefix=prefix, exit=1)
    else:
        return False

def get_type(location, dy, tmp_dy):
    prefix=get_dfn_prefix(location, "_type")
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
            msg.error("value '{}' not in authorized types {}.".format(_type, authorized_types), prefix=prefix, exit=1)
    else:
        return None

def get_label(location, dy, tmp_dy):
    prefix=get_dfn_prefix(location, "_label")
    if "_label" in dy:
        _label=dy["_label"]
        del dy["_label"]
        if _label is None:
            return None
        elif isinstance(_label, str):
            return _label.upper()
        else:
            msg.error("value type {} must be of type {}.".format(type(_label), str), prefix=prefix, exit=1)
    else:
        return None

def get_is_builtin(dy):
    if "_is_builtin" in dy:
        _is_builtin=dy["_is_builtin"]
        del dy["_is_builtin"]
        return _is_builtin
    else:
        return False

def get_values(location, dy_user, dy_options):
    prefix=get_dfn_prefix(location, "_values")
    dy_values=dict(
        accepted=False,
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
                            msg.error("max value '{}' must be greater than min value '{}'".format(_max, _min), prefix=prefix, exit=1)
                        dy_values["max"]=_max

                    dy_values["min"]=_min

                    if reg.group("optional") is None:
                        dy_values["required"]=True
                    else:
                        dy_values["required"]=False
            else:
                msg.error([
                    "_values '{}' syntax error.".format(_values),
                    "Syntax must regex:",
                    *get_regex_hints("def_values"),
                ], prefix=prefix, exit=1)
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
                msg.error("value type {} must be either of type {} or type {}.".format(type(_values), str, int), prefix=prefix, exit=1)

            if _values > 0:
                dy_values["min"]=_values
                dy_values["max"]=_values
                dy_values["required"]=True
            else:
                msg.error("when integer value '{}' must be greater than 0.".format(_values), prefix=prefix, exit=1)

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

def get_show(location, dy):
    prefix=get_dfn_prefix(location, "_show")
    if "_show" in dy:
        _show=dy["_show"]
        del dy["_show"]
        if isinstance(_show, bool):
            return _show
        else:
            msg.error("value type {} must be of type {}.".format(type(_show), bool), prefix=prefix, exit=1)
    else:
        return True

def get_required(location, dy, is_root, tmp_dy):
    prefix=get_dfn_prefix(location, "_required")
    if "_required" in dy:
        _required=dy["_required"]
        del dy["_required"]

        if is_root:
            return True
        elif _required is None:
            return False
        elif isinstance(_required, bool):
            if _required is True and tmp_dy["single"] is True:
                msg.error("value can't be 'True' when option '_single' value is 'True'.", prefix=prefix, exit=1)
            return _required
        else:
            msg.error("value type {} must be of type {}.".format(type(_required), bool), prefix=prefix, exit=1)
    else:
        if is_root:
            return True
        else:
            return False

def get_repeat(location, dy):
    prefix=get_dfn_prefix(location, "_repeat")
    if "_repeat" in dy:
        _repeat=dy["_repeat"]
        del dy["_repeat"]

        if _repeat is None:
            return "replace"

        authorized_repeats=["append", "create", "exit", "replace"]
        if _repeat in authorized_repeats:
            return _repeat
        else:
            msg.error("value '{}' not found in {}.".format(_repeat, authorized_repeats), prefix=prefix, exit=1)
    else:
        return "replace"

def get_in(location, dy_user, dy_options):
    prefix=get_dfn_prefix(location, "_in")
    if "_in" in dy_user:
        _in=dy_user["_in"]
        del dy_user["_in"]

        if _in is None:
            return None

        if dy_options["type"] in [".json", "json"]:
            msg.error("option can't be set for type '{}'.".format(dy_options["type"]), prefix=prefix, exit=1)

        if dy_options["type"] is None:
            dy_options["type"]=str

        # if dy_options["type"] in [".json", "json"]:
        #     if isinstance(_in, dict):
        #         prefix+=" for type '{}' in dict '{}'".format(dy_options["type"], json.dumps(_in))
        #         return get_processed_data_dict(prefix, _in)
        #     else:
        #         if isinstance(_in, str):
        #             dy_json_data=get_json_dy(prefix, _in)
        #             if dy_json_data is None:
        #                 return dy_json_data

        #         msg.error([
        #             "For type '{}' _in '{}' must either match type '{}' or type '{}'.".format(dy_options["type"], _in, dict, str),
        #             "If type '{}' it must match regex:".format(str),
        #             *get_regex_hints("def_json_data"),
        #         ], prefix=prefix, exit=1)
        # else:
        if dy_options["value_min"] is None and dy_options["value_max"] is None:
            dy_options["value_min"]=1
            dy_options["value_max"]=1
            dy_options["value_required"]=True

        authorized_ins=[ dict, list, str]
        tmp_ins=[]
        if isinstance(_in, str):
            for tmp_in in sorted(_in.split(",")):
                tmp_ins.append(tmp_in.strip())
        elif type(_in) in [ list, dict ]:
            tmp_ins=sorted(_in)
        else:
            msg.error("value type '{}' not in authorized value types {}.".format(type(_in), authorized_ins), prefix=prefix, exit=1)

        if len(tmp_ins) == 0:
            return None
        
        new_ins=[]
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
                msg.error("value '{}' does not match type or can't be converted to type '{}'.".format(tmp_in, dy_options["type"]), prefix=prefix, exit=1)
            else:
                if isinstance(tmp_ins, dict):
                    value=tmp_ins[tmp_in]
                    authorized_values_types=[bool, float, int, None, str]
                    if value not in authorized_values_types:
                        msg.error("at key '{}' value '{}' is not in authorized types {}.".format(tmp_in, value, authorized_values_types), prefix=prefix, exit=1)
                new_ins.append(new_in)

        if dy_options["label"] is not None:
            msg.error("_label must be None when _in is set.", prefix=prefix, exit=1)

        if isinstance(tmp_ins, list):
            return new_ins
        elif isinstance(tmp_ins, dict):
            tmp_dy=dict()
            for t, tmp_in in enumerate(tmp_ins):
                tmp_dy[new_ins[t]]=tmp_ins[tmp_in]
            return tmp_dy
    else:
        return None

def get_hint(location, dy):
    prefix=get_dfn_prefix(location, "_hint")
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
                msg.error("value length '{}' must be less or equal than '100'.".format(len(_hint)), prefix=prefix, exit=1)
        else:
            msg.error("value type {} must be of type {}.".format(type(_hint), str), prefix=prefix, exit=1)
    else:
        return None

def get_info(location, dy):
    prefix=get_dfn_prefix(location, "_info")
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
            msg.error("value type {} must be of type {}.".format(type(_info), str), prefix=prefix, exit=1)
    else:
        return None

def get_examples(location, dy):
    prefix=get_dfn_prefix(location, "_examples")
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
                    msg.error("At least one element in examples list is not of type {}.".format(str), prefix=prefix, exit=1)
        else:
            msg.error("value type {} must be either of type {} or type {}.".format(type(_examples), str, list), prefix=prefix, exit=1)
        
        if len(tmp_examples) == 0:
            return None
        else:
            return tmp_examples
    else:
        return None

def get_enabled(location, dy):
    prefix=get_dfn_prefix(location, "_enabled")
    if "_enabled" in dy:
        _enabled=dy["_enabled"]
        del dy["_enabled"]

        if _enabled is None:
            return True
        elif isinstance(_enabled, bool):
            return _enabled
        else:
            msg.error("value type {} must be of type {}.".format(type(_enabled), bool), prefix=prefix, exit=1)
    else:
        return True

def get_default(location, dy_user, dy_options, argument_name):
    prefix=get_dfn_prefix(location, "_default")

    if "_default" in dy_user:
        _default=dy_user["_default"]
        del dy_user["_default"]

        if _default is None:
            return None

        # # excluded_types=[".json", "dir", "file", "json", "path", "vpath"]
        if dy_options["type"] in [".json", "json"]:
            msg.error("option can't be set for type '{}'.".format(dy_options["type"]), prefix=prefix, exit=1)

        if dy_options["type"] is None:
            dy_options["type"]=str

        list_at_start=True
        if not isinstance(_default, list):
            list_at_start=False
            _default=[_default]

        # msg.error("here", exit=1)
        if len(_default) > 0:
            if dy_options["value_min"] is None and dy_options["value_max"] is None:
                dy_options["value_min"]=len(_default)
                dy_options["value_max"]=len(_default)
                dy_options["value_required"]=True
            else:
                error_length=False
                if dy_options["value_min"] is not None:
                    if len(_default) < dy_options["value_min"]:
                        error_length=True

                if dy_options["value_max"] is not None:
                    if len(_default) > dy_options["value_max"]:
                        error_length=True

                if error_length is True:
                    msg.error("for values length '{}' does not match min length {} and max length {}.".format(len(_default), dy_options["value_min"], dy_options["value_max"]), prefix=prefix, exit=1)

            expected_type=None
            if dy_options["type"] in ["dir", "file", "path", "vpath"]:
                expected_type=str
            else:
                expected_type=dy_options["type"]

            tmp_defaults=[]
            for value in _default:
                if value is not None:
                    if type(value) != expected_type:
                        if list_at_start is True:
                            msg.error("for value '{}' in {} for type string '{}'. type error. It must be either {} or {}.".format(
                                value,
                                _default,
                                get_type_str(dy_options["type"]),  
                                expected_type, 
                                None,
                            ), prefix=prefix, exit=1)
                        else:
                            msg.error("type error '{}' for type string '{}'. It must be either of type {} or type {} or set _type option with a different type.".format(
                                type(value),
                                get_type_str(dy_options["type"]), 
                                expected_type, 
                                list
                            ), prefix=prefix, exit=1)

                    if dy_options["in"] is not None:
                        if value not in dy_options["in"]:
                            msg.error("'{}' is not in option _in values {}.".format(value, dy_options["in"]), prefix=prefix, exit=1)

                    tmp_defaults.append(value)

            if len(tmp_defaults) == 0:
                return None
            else:
                if list_at_start is True:
                    return tmp_defaults
                else:
                    return tmp_defaults[0]
        else:
            return None
    else:
        return None

def get_aliases(location, name, dy):
    dy_aliases=dict(
        auto_aliases=False,
        dashless_alias=[],
        long_alias=[],
        short_alias=[],
    )
    prefix=get_dfn_prefix(location, "_aliases")
    auto_aliases=True
    if "_aliases" in dy:
        _aliases=dy["_aliases"]
        del dy["_aliases"]
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
                        msg.error("value type {} type must be of type {}.".format(type(tmp_alias), str), prefix=prefix, exit=1)
            else:
                msg.error("valute type {} must be either type {} or type {}.".format(type(_aliases), str, list ), prefix=prefix, exit=1)

            for alias in tmp_aliases:
                auto_aliases=False
                alias_matched=False
                for rule_name in ["dashless_alias", "long_alias", "short_alias"]:
                    reg_str=get_regex("def_{}".format(rule_name))["rule"]
                    reg=re.match(reg_str, alias)
                    if reg:
                        alias_matched=True
                        if alias in dy_aliases[rule_name]:
                            msg.error("duplicate alias '{}' not authorized.".format(alias), prefix=prefix, exit=1)
                        else:
                            dy_aliases[rule_name].append(alias)
                            break

                if alias_matched is False:
                    msg.error([
                        "alias '{}' syntax error.".format(alias),
                        "Syntax must either match:",
                        *get_regex_hints("def_dashless_alias"),
                        *get_regex_hints("def_long_alias"),
                        *get_regex_hints("def_short_alias"),
                    ], prefix=prefix, exit=1)
    dy_aliases["auto_aliases"]=auto_aliases
    if auto_aliases is True:
        dy_aliases["long_alias"].append("--{}".format(name.replace("_", "-")))
        dy_aliases["short_alias"].append("-{}".format(name[0]))

    return dy_aliases
