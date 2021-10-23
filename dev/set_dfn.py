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
    parent,
):
    tmp_dy=dict()
    tmp_dy["is_builtin"]=get_is_builtin(location, dy)
    # chars=get_chars(location, dy, pretty, app_name)
    dy_aliases=get_aliases(location, name, dy, tmp_dy, sibling_level, pretty, app_name, dy_attr_aliases)
    tmp_dy["dfn_aliases"]=dy_aliases["aliases"]
    tmp_dy["aliases"]=[]
    tmp_dy["dy_aliases"]=dict()
    tmp_dy["is_auto_alias"]=dy_aliases["is_auto_alias"]
    tmp_dy["aliases_info"]=dy_aliases["aliases_info"]
    tmp_dy["default_alias"]=None
    tmp_dy["flags"]=dict()
    tmp_dy["flag"]=None
    tmp_dy["flags_notation"]=None
    tmp_dy["flags_aliases"]=dict()

    tmp_dy["enabled"]=get_enabled(location, dy, pretty, app_name)
    tmp_dy["need_child"]=get_need_child(location, dy, pretty, app_name, is_root)
    tmp_dy["allow_siblings"]=get_allow_siblings(location, dy, pretty, app_name, is_root)
    tmp_dy["allow_parent_fork"]=get_allow_parent_fork(location, dy, pretty, app_name, is_root)
    tmp_dy["examples"]=get_examples(location, dy, pretty, app_name)
    tmp_dy["hint"]=get_hint(location, dy, pretty, app_name)
    tmp_dy["info"]=get_info(location, dy, pretty, app_name)
    tmp_dy["type"]=get_type(location, dy, tmp_dy, pretty, app_name)
    tmp_dy["label"]=get_label(location, dy, tmp_dy, pretty, app_name)
    tmp_dy["fork"]=get_fork(location, dy, pretty, app_name)
    tmp_dy["repeat"]=get_repeat(location, dy, pretty, app_name)
    tmp_dy["xor"]=get_xor(location, dy, tmp_dy, app_name)
    tmp_dy["xor_notation"]=None
    tmp_dy["xor_groups"]=None
    
    tmp_dy["show"]=get_show(location, dy, pretty, app_name)
    dy_values=get_values(location, dy, tmp_dy, pretty, app_name)
    tmp_dy["value_min"]=dy_values["min"]
    tmp_dy["value_max"]=dy_values["max"]
    tmp_dy["value_required"]=dy_values["required"]

    dy_in=get_in(location, dy, tmp_dy, pretty, app_name)
    tmp_dy["in"]=dy_in["in"]
    tmp_dy["in_labels"]=dy_in["in_labels"]
    tmp_dy["default"]=get_default(location, dy, tmp_dy, name, pretty, app_name)

    tmp_dy["required"]=get_required(location, dy, is_root, tmp_dy, pretty, app_name, parent)
    tmp_dy["required_children"]=[]

    return tmp_dy

def get_xor(location, dy, tmp_dy, app_name):
    prefix=get_dfn_prefix(app_name, location, "_xor")
    if "_xor" in dy:
        _xor=dy["_xor"]
        del dy["_xor"]

        if isinstance(_xor, list):
            pass
        elif isinstance(_xor, str):
            _xor=[_xor]
        else:
            msg.error("type error '{}'. It must be '{}' or '{}'.".format(type(_xor), str, list), prefix=prefix, exit=1)

        ret_xor=[]
        ret_xor_ids=[]
        tmp_dy["xor_names"]=[]
        for tmp_xor in _xor:
            if type(tmp_xor) in [str, list]:
                if isinstance(tmp_xor, str):
                    values=tmp_xor.split(",")
                elif isinstance(tmp_xor, list):
                    values=tmp_xor
                if len(values) < 2:
                    msg.error("at least 2 values are needed in  {}.".format(values), prefix=prefix, exit=1)

                tmp_ret_xor=[]
                for value in values:
                    if isinstance(tmp_xor, list):
                        if not isinstance(value, str):
                            msg.error("for sub-value from list '{}' type error '{}'. It must be of type {}.".format(value, type(value), str), prefix=prefix, exit=1)

                    value=value.strip()
                    if value == "":
                        msg.error("empty value not allowed in {}.".format(values), prefix=prefix, exit=1)
                    if value in tmp_ret_xor:
                        msg.error("duplicate value not allowed in {}.".format(values), prefix=prefix, exit=1)
                    tmp_ret_xor.append(value)
                    if value not in tmp_dy["xor_names"]:
                        tmp_dy["xor_names"].append(value)

                tmp_ret_xor.sort()
                ret_xor_id=",".join(tmp_ret_xor)
                if ret_xor_id in ret_xor_ids:
                    msg.error("duplicate lists not allowed {}.".format(tmp_ret_xor), prefix=prefix, exit=1)

                ret_xor_ids.append(ret_xor_id)                    
                ret_xor.append(tmp_ret_xor)
            else:
                msg.error("for sub-value '{}' type error '{}'. It must be in {}.".format(_tmp_xor, type(_tmp_xor), [list, str]), prefix=prefix, exit=1)

        dy_xor=dict()
        for name in tmp_dy["xor_names"]:
            dy_xor[name]=dict()
            for g, group in enumerate(ret_xor):
                group_num=g+1
                if name in group:
                    tmp_group=group.copy()
                    tmp_group.remove(name)
                    dy_xor[name][str(group_num)]=tmp_group

        return dy_xor
    else:
        return dict()

def get_aliases(location, name, dy_user, dy_options, sibling_level, pretty, app_name, dy_attr_aliases):
    dy_aliases=dict()
    aliases=[]
    is_flag=False
    alias_prefix=None
    msg_prefix=get_dfn_prefix(app_name, location, "_aliases")
    is_auto_alias=True
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
                        msg.error("value type {} type must be of type {}.".format(type(tmp_alias), str), prefix=msg_prefix, pretty=pretty, exit=1)
            else:
                msg.error("valute type {} must be either type {} or type {}.".format(type(_aliases), str, list ), prefix=msg_prefix, pretty=pretty, exit=1)

            tmp_aliases=sorted(list(set(tmp_aliases)))
            for alias in tmp_aliases:
                is_auto_alias=False
                if name == "_usage_" and alias == "?":
                    aliases.append(alias)
                    dy_aliases[alias]=dict(
                        prefix="",
                        text="?",
                        is_flag=True,
                    )
                else:
                    reg=re.match(get_regex("def_alias")["rule"], alias)
                    if reg is None:
                        msg.error([
                            "alias '{}' syntax error.".format(alias),
                            *get_regex_hints("def_alias"),
                        ], prefix=msg_prefix, pretty=pretty, exit=1)
                    else:
                        aliases.append(alias)
                        dy_aliases[alias]=dict(
                            prefix=reg.group(1),
                            text=reg.group(3),
                            is_flag=len(reg.group(3)) == 1,
                        )

    if is_auto_alias is True:
        auto_alias_text=get_auto_alias(dy_attr_aliases, name)
        aliases.append(auto_alias_text)
        alias_text=auto_alias_text[len(dy_attr_aliases["auto_alias_prefix"]):]
        dy_aliases[auto_alias_text]=dict(
            prefix=dy_attr_aliases["auto_alias_prefix"],
            text=alias_text,
            is_flag=len(alias_text) == 1,
        )

    return dict(
        is_auto_alias=is_auto_alias,
        aliases=aliases,
        aliases_info=dy_aliases,
    )

def get_auto_alias(dy_attr_aliases, name):
    style=dy_attr_aliases["auto_alias_style"]
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
    
    return elems_str

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
            return _label
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

def get_required(location, dy, is_root, tmp_dy, pretty, app_name, parent):
    prefix=get_dfn_prefix(app_name, location, "_required")

    is_required=None
    if "_required" in dy:
        _required=dy["_required"]
        del dy["_required"]

        if is_root:
            is_required=True
        elif _required is None:
            is_required=False
        elif isinstance(_required, bool):
            is_required=_required
        else:
            msg.error("value type {} must be of type {}.".format(type(_required), bool), prefix=prefix, pretty=pretty, exit=1)
    else:
        if is_root:
            is_required=True
        else:
            is_required=False

    if is_required is True and is_root is False:
        if parent is not None:
            is_parent_implicit=(parent.dy["required"] is True and parent.dy["value_required"] is True and parent.dy["default"] is not None) or (parent.dy["required"] is True and parent.dy["value_required"] in [False, None])
            is_implicit=(tmp_dy["value_required"] is True and tmp_dy["default"] is not None) or (tmp_dy["value_required"] in [False, None])

            if is_parent_implicit is True:
                if is_implicit is False:
                    msg.error([
                        "A required argument can be added implicitly on the command-line when its parent is on the command-line and if 'argument has required values and argument has default values' or 'argument values are not required' or 'argument does not accept values'.", 
                        "In definition when an argument can be added implicitly on the command-line then its required children argument must also have the properties to be added implicitly on the command-line.",
                        "For current argument '{}', its parent '{}' can be implicitly added but current argument can't be implicitly added.".format(location, parent.name),
                        "Either set parent argument's definition with required values and no default values or set current argument properties so it may be added implicitly on the command-line.",
                    ], prefix=prefix, pretty=pretty, exit=1)

        if tmp_dy["allow_parent_fork"] is False:
            msg.error("when value is '{}' then property '_allow_parent_fork' must be set to '{}'.".format(True, True), prefix=prefix, pretty=pretty, exit=1)
        if tmp_dy["allow_siblings"] is False:
            msg.error("when value is '{}' then property '_allow_siblings' must be set to '{}'.".format(True, True), prefix=prefix, pretty=pretty, exit=1)
        if tmp_dy["need_child"] is True:
            msg.error("when value is '{}' then property '_need_child' must be set to '{}'.".format(True, False), prefix=prefix, pretty=pretty, exit=1)

    return is_required

def get_fork(location, dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_fork")
    if "_fork" in dy:
        _fork=dy["_fork"]
        del dy["_fork"]
        if _fork is None:
            return True
        elif isinstance(_fork, bool):
            return _fork
        else:
            msg.error("value type {} must be of type {}.".format(type(_fork), bool), prefix=prefix, pretty=pretty, exit=1)
    else:
        return False

def get_repeat(location, dy, pretty, app_name):
    prefix=get_dfn_prefix(app_name, location, "_repeat")
    if "_repeat" in dy:
        _repeat=dy["_repeat"]
        del dy["_repeat"]

        if _repeat is None:
            return "replace"

        authorized_repeats=["append", "error", "replace"]
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

def get_allow_siblings(location, dy, pretty, app_name, is_root):
    prefix=get_dfn_prefix(app_name, location, "_allow_siblings")
    if "_allow_siblings" in dy:
        _allow_siblings=dy["_allow_siblings"]
        del dy["_allow_siblings"]

        if _allow_siblings is None:
            return True
        elif isinstance(_allow_siblings, bool):
            if is_root is True:
                return True
            else:
                return _allow_siblings
        else:
            msg.error("value type {} must be of type {}.".format(type(_allow_siblings), bool), prefix=prefix, pretty=pretty, exit=1)
    else:
        return True

def get_allow_parent_fork(location, dy, pretty, app_name, is_root):
    prefix=get_dfn_prefix(app_name, location, "_allow_parent_fork")
    if "_allow_parent_fork" in dy:
        _allow_parent_fork=dy["_allow_parent_fork"]
        del dy["_allow_parent_fork"]

        if _allow_parent_fork is None:
            return True
        elif isinstance(_allow_parent_fork, bool):
            if is_root is True:
                return True
            else:
                return _allow_parent_fork
        else:
            msg.error("value type {} must be of type {}.".format(type(_allow_parent_fork), bool), prefix=prefix, pretty=pretty, exit=1)
    else:
        return True

def get_need_child(location, dy, pretty, app_name, is_root):
    prefix=get_dfn_prefix(app_name, location, "_need_child")

    if "_need_child" in dy:
        _need_child=dy["_need_child"]
        del dy["_need_child"]

        if _need_child is None:
            if is_root is True:
                return True
            else:
                return False
        elif isinstance(_need_child, bool):
            return _need_child
        else:
            msg.error("value type {} must be of type {}.".format(type(_need_child), bool), prefix=prefix, pretty=pretty, exit=1)
    else:
        if is_root is True:
            return True
        else:
            return False

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
