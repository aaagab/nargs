#!/usr/bin/env python3
from pprint import pprint
import json
import os 
import re
import sys

from .regexes import get_regex, get_regex_hints
from ..gpkgs import message as msg

def get_prop_prefix(dy_err, prop):
    return "{} at property '{}'".format(dy_err["prefix"], prop)

def get_filtered_dy(
    pnode_dfn,
    arg_name,
    dy_props,
    dy_attr_aliases,
    dy_err,
):
    tmp_dy_props=dict()
    tmp_dy_props["is_builtin"]=get_is_builtin(dy_props, dy_err)
    tmp_dy_props["is_usage"]=get_is_usage(dy_props, dy_err, pnode_dfn)
    tmp_dy_props["is_custom_builtin"]=get_is_custom_builtin(dy_props, dy_err, tmp_dy_props["is_usage"], arg_name)
    dy_aliases=get_aliases(arg_name, dy_props, dy_err, dy_attr_aliases, tmp_dy_props["is_usage"])
    tmp_dy_props["aliases"]=dy_aliases["aliases"]
    tmp_dy_props["default_alias"]=dy_aliases["default_alias"]
    tmp_dy_props["is_auto_alias"]=dy_aliases["is_auto_alias"]
    tmp_dy_props["aliases_info"]=dy_aliases["aliases_info"]

    tmp_dy_props["enabled"]=get_enabled(dy_props, dy_err)
    tmp_dy_props["need_child"]=get_need_child(dy_props, dy_err, pnode_dfn)
    tmp_dy_props["allow_siblings"]=get_allow_siblings(dy_props, dy_err, pnode_dfn)
    tmp_dy_props["allow_parent_fork"]=get_allow_parent_fork(dy_props, dy_err, pnode_dfn)
    tmp_dy_props["examples"]=get_examples(dy_props, dy_err)
    tmp_dy_props["hint"]=get_hint(dy_props, dy_err)
    tmp_dy_props["info"]=get_info(dy_props, dy_err)
    tmp_dy_props["type"]=get_type(dy_props, dy_err)
    tmp_dy_props["label"]=get_label(dy_props, dy_err)
    tmp_dy_props["fork"]=get_fork(dy_props, dy_err)
    tmp_dy_props["repeat"]=get_repeat(dy_props, dy_err)
    tmp_dy_props["xor"]=get_xor(dy_props, tmp_dy_props, dy_err)
    tmp_dy_props["xor_groups"]=None
    
    tmp_dy_props["show"]=get_show(dy_props, dy_err, pnode_dfn)

    dy_values=get_values(dy_props, dy_err)
    tmp_dy_props["values_min"]=dy_values["min"]
    tmp_dy_props["values_max"]=dy_values["max"]
    tmp_dy_props["values_authorized"]=dy_values["authorized"]
    tmp_dy_props["values_required"]=dy_values["required"]

    tmp_dy_props["in"]=get_in(dy_props, dy_err)
    tmp_dy_props["in_labels"]=[]
    tmp_dy_props["default"]=get_default(dy_props, dy_err)

    implement_implicit_logic(tmp_dy_props, dy_err)

    tmp_dy_props["required"]=get_required(dy_props, tmp_dy_props, dy_err, pnode_dfn, arg_name)
    tmp_dy_props["required_children"]=[]

    return tmp_dy_props

def get_casted_value(value, tmp_dy_props, dy_err, prop_prefix):
    if tmp_dy_props["type"] is None:
        tmp_dy_props["auto_set_type"]=True
        tmp_dy_props["type"]=str

    tmp_value=None
    if tmp_dy_props["type"] == bool:
        try:
            tmp_value=bool(value)
        except:
            pass
    elif tmp_dy_props["type"] == float:
        try:
            tmp_value=float(value)
        except:
            pass
    elif tmp_dy_props["type"] == int:
        try:
            tmp_value=int(value)
        except:
            pass
    elif tmp_dy_props["type"] == str:
        try:
            tmp_value=str(value)
        except:
            pass
    else:
        msg.error("property can't be set for type {}.".format(tmp_dy_props["type"]), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    if tmp_value is None:
        error_msg="value type '{}' must be of type {}.".format(type(value), tmp_dy_props["type"])
        if tmp_dy_props["auto_set_type"] is True:
            error_msg+=" Type has been implicitly set to default {}. Either type or value can be modified.".format(tmp_dy_props["type"])
        msg.error(error_msg, prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    return tmp_value

def implement_implicit_logic(tmp_dy_props, dy_err):
    tmp_dy_props["auto_set_type"]=False
    if tmp_dy_props["values_authorized"] is True:
        if tmp_dy_props["type"] is None:
            tmp_dy_props["auto_set_type"]=True
            tmp_dy_props["type"]=str

    if tmp_dy_props["default"] is not None:
        prop_prefix=get_prop_prefix(dy_err, "_default")
        if tmp_dy_props["values_authorized"] is True:
            if tmp_dy_props["values_required"] is False:
                msg.error("values can't be optional when _default is set. Set '_values' with at least a required minimum of values.", prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            if len(tmp_dy_props["default"]) < tmp_dy_props["values_min"]:
                msg.error("number of values '{}' is less than minimum number of values '{}'.".format(len(tmp_dy_props["default"]), tmp_dy_props["values_min"]), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            if tmp_dy_props["values_max"] is not None:
                if len(tmp_dy_props["default"]) > tmp_dy_props["values_max"]:
                    msg.error("number of values '{}' is greater than maximum number of values '{}'.".format(len(tmp_dy_props["default"]), tmp_dy_props["values_max"]), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        else:
            tmp_dy_props["values_authorized"]=True
            tmp_dy_props["values_required"]=True
            tmp_dy_props["values_min"]=len(tmp_dy_props["default"])
            tmp_dy_props["values_max"]=len(tmp_dy_props["default"])
            
        tmp_values=[]
        for value in tmp_dy_props["default"]:
            tmp_values.append(get_casted_value(value, tmp_dy_props, dy_err, prop_prefix))
        tmp_dy_props["default"]=tmp_values

    if tmp_dy_props["in"] is not None:
        prop_prefix=get_prop_prefix(dy_err, "_in")
        if tmp_dy_props["label"] is not None:
            msg.error("_label must be None when _in is set.", prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        if tmp_dy_props["values_authorized"] is False:
            tmp_dy_props["values_authorized"]=True
            tmp_dy_props["values_required"]=True
            tmp_dy_props["values_min"]=1
            tmp_dy_props["values_max"]=1

        if isinstance(tmp_dy_props["in"], list):
            tmp_values=[]
            for value in tmp_dy_props["in"]:
                tmp_values.append(get_casted_value(value, tmp_dy_props, dy_err, prop_prefix))
            tmp_dy_props["in"]=tmp_values
        elif isinstance(tmp_dy_props["in"], dict):
            if tmp_dy_props["type"] is None:
                tmp_dy_props["auto_set_type"]=True
                tmp_dy_props["type"]=str
            
            authorized_values_types=[bool, float, int, str, type(None)]
            tmp_values=[]
            for key in sorted(tmp_dy_props["in"]):
                tmp_values.append(get_casted_value(key, tmp_dy_props, dy_err, prop_prefix))
                
                value=tmp_dy_props["in"][key]
                if type(value) in authorized_values_types:
                    tmp_dy_props["in_labels"].append(value)
                else:
                    msg.error("at dict key '{}' value '{}' with type {} must be any type from {}.".format(key, value, type(value), authorized_values_types), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            tmp_dy_props["in"]=tmp_values

        if tmp_dy_props["default"] is not None:
            prop_prefix=get_prop_prefix(dy_err, "_default")
            for value in tmp_dy_props["default"]:
                if value not in tmp_dy_props["in"]:
                    msg.error("value '{}' is not found in property _in values {}.".format(value, sorted(tmp_dy_props["in"])), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    if tmp_dy_props["label"] is not None:
        if tmp_dy_props["values_authorized"] is False:
            if tmp_dy_props["type"] is None:
                tmp_dy_props["type"]=str

            tmp_dy_props["values_authorized"]=True
            tmp_dy_props["values_required"]=True
            tmp_dy_props["values_min"]=1
            tmp_dy_props["values_max"]=1

    if tmp_dy_props["type"] is not None:
        if tmp_dy_props["values_authorized"] is False:
            tmp_dy_props["values_authorized"]=True
            tmp_dy_props["values_required"]=True
            tmp_dy_props["values_min"]=1
            tmp_dy_props["values_max"]=1

    del tmp_dy_props["auto_set_type"]

def get_xor(dy_props, tmp_dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_xor")
    if "_xor" in dy_props:
        _xor=dy_props["_xor"]
        del dy_props["_xor"]

        groups=[]
        xor_names=[]
        if isinstance(_xor, list):
            is_one_elem=None
            list_ids=[]
            for tmp_xor in _xor:
                group=[]
                if isinstance(tmp_xor, str):
                    for name in tmp_xor.split(","):
                        name=name.strip()
                        if name == "":
                            msg.error("empty value not allowed in {}.".format(tmp_xor.split(",")), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                        elif name in group:
                            msg.error("duplicate value not allowed in {}.".format(tmp_xor.split(",")), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                        group.append(name)
                        if name not in xor_names:
                            xor_names.append(name)

                elif isinstance(tmp_xor, list):
                    for name in tmp_xor:
                        if not isinstance(name, str):
                            msg.error("for _xork list {} at sub-list {} value '{}' type error {}. It must be of type {}.".format(_xor, tmp_xor, name, type(name), str), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                        name=name.strip()
                        if name == "":
                            msg.error("empty value not allowed in {}.".format(tmp_xor), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                        elif name in group:
                            msg.error("duplicate value not allowed in {}.".format(tmp_xor), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                        group.append(name)
                        if name not in xor_names:
                            xor_names.append(name)
                else:
                    msg.error("In list {} for sub-value '{}' type error '{}'. It must be of type {}.".format(_xor, tmp_xor, type(tmp_xor), str), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

                group.sort()
                if is_one_elem is None:
                    if len(group) == 1:
                        is_one_elem=True
                    else:
                        is_one_elem=False
                elif is_one_elem is True:
                    if len(group) > 1:
                        msg.error("_xor list {} started as a one element list but a multiple elements list {} is present. Choose either a multiple elements list or a single element list.".format(_xor, group), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                elif is_one_elem is False:
                    if len(group) == 1:
                        msg.error("_xor list {} started as a multiple elements list but a single element list {} is present. Choose either a multiple elements list or a single element list.".format(_xor, group), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

                if is_one_elem is True:
                    group=group[0]
                else:
                    list_id=",".join(group)
                    if list_id not in list_ids:
                        list_ids.append(list_id)
                    else:
                        msg.error("duplicate lists not allowed {}.".format(group), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

                groups.append(group)
            if is_one_elem is True:
                groups=[groups]

        elif isinstance(_xor, str):
            group=[]
            for name in _xor.split(","):
                name=name.strip()
                if name == "":
                    msg.error("empty value not allowed in {}.".format(_xor.split(",")), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                elif name in group:
                    msg.error("duplicate value not allowed in {}.".format(_xor.split(",")), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                group.append(name)
                if name not in xor_names:
                    xor_names.append(name)

            if len(group) < 2:
                msg.error("At least two values are needed in _xor list {}.".format(group), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            group.sort()
            groups.append(group)
        else:
            msg.error("type error '{}'. It must be '{}' or '{}'.".format(type(_xor), str, list), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        tmp_dy_xor=dict()
        for xor_name in xor_names:
            tmp_dy_xor[xor_name]=dict()
            for g, group in enumerate(groups):
                group_num=g+1
                if xor_name in group:
                    tmp_group=group.copy()
                    tmp_group.remove(xor_name)
                    tmp_dy_xor[xor_name][str(group_num)]=tmp_group

        return tmp_dy_xor
    else:
        return dict()

def get_aliases(arg_name, dy_props, dy_err, dy_attr_aliases, is_usage):
    prop_prefix=get_prop_prefix(dy_err, "_aliases")
    dy_aliases=dict()
    aliases=[]
    is_flag=False
    alias_prefix=None
    is_auto_alias=True
    default_alias=None
    if "_aliases" in dy_props:
        _aliases=dy_props["_aliases"]
        del dy_props["_aliases"]
        if _aliases is not None:
            tmp_aliases=[]
            if isinstance(_aliases, str):
                for tmp_alias in _aliases.split(","):
                    tmp_alias=tmp_alias.strip()
                    if tmp_alias != "":
                        is_auto_alias=False
                        tmp_aliases.append(tmp_alias)
            elif isinstance(_aliases, list):
                for tmp_alias in _aliases:
                    if isinstance(tmp_alias, str):
                        tmp_alias=tmp_alias.strip()
                        if tmp_alias != "":
                            is_auto_alias=False
                            tmp_aliases.append(tmp_alias)
                    else:
                        msg.error("value type {} type must be of type {}.".format(type(tmp_alias), str), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
            else:
                msg.error("value type {} must be either type {} or type {}.".format(type(_aliases), str, list ), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)


            if is_auto_alias is False:
                default_alias=tmp_aliases[0]
                tmp_aliases=sorted(list(set(tmp_aliases)))
                for alias in tmp_aliases:
                    reg=re.match(get_regex("def_alias")["rule"], alias)
                    if reg is None:
                        msg.error([
                            "alias '{}' syntax error.".format(alias),
                            *get_regex_hints("def_alias"),
                        ], prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                    else:
                        text=reg.group(3)
                        if text[0] == "?":
                            if is_usage is False:
                                msg.error("for alias '{}' first char can be a question mark '?' only when argument property '_is_usage' is set to 'True'.".format(alias), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                            elif len(text) > 1:
                                msg.error("for alias '{}' when first char is a question mark '?' no other chars are allowed.".format(alias), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                        aliases.append(alias)
                        dy_aliases[alias]=dict(
                            prefix=reg.group(1),
                            text=text,
                            is_flag=len(reg.group(3)) == 1,
                        )

    if is_auto_alias is True:
        auto_alias_text=get_auto_alias(dy_attr_aliases, arg_name)
        aliases.append(auto_alias_text)
        default_alias=auto_alias_text
        alias_text=auto_alias_text[len(dy_attr_aliases["auto_alias_prefix"]):]
        dy_aliases[auto_alias_text]=dict(
            prefix=dy_attr_aliases["auto_alias_prefix"],
            text=alias_text,
            is_flag=len(alias_text) == 1,
        )

    return dict(
        aliases=aliases,
        aliases_info=dy_aliases,
        default_alias=default_alias,
        is_auto_alias=is_auto_alias,
    )

def get_auto_alias(dy_attr_aliases, arg_name):
    style=dy_attr_aliases["auto_alias_style"]
    elems=arg_name.split("_")

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

def get_type(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_type")
    if "_type" in dy_props:
        _type=dy_props["_type"]
        del dy_props["_type"]
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
            msg.error("value '{}' not found in authorized types {}.".format(_type, authorized_types), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return None

def get_label(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_label")
    if "_label" in dy_props:
        _label=dy_props["_label"]
        del dy_props["_label"]
        if _label is None:
            return None
        elif isinstance(_label, str):
            return _label
        else:
            msg.error("value type {} must be of type {}.".format(type(_label), str), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return None

def get_is_builtin(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_is_builtin")
    if "_is_builtin" in dy_props:
        _is_builtin=dy_props["_is_builtin"]
        del dy_props["_is_builtin"]
        if _is_builtin is None:
            return False
        elif isinstance(_is_builtin, bool):
            return _is_builtin
        else:
            msg.error("value type {} must be of type {}.".format(type(_is_builtin), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return False

def get_is_custom_builtin(dy_props, dy_err, is_usage, arg_name):
    prop_prefix=get_prop_prefix(dy_err, "_is_custom_builtin")
    if "_is_custom_builtin" in dy_props:
        _is_custom_builtin=dy_props["_is_custom_builtin"]
        del dy_props["_is_custom_builtin"]
        if _is_custom_builtin is None:
            if is_usage is True and arg_name != "_usage_":
                return True
            else:
                return False
        elif isinstance(_is_custom_builtin, bool):
            return _is_custom_builtin
        else:
            msg.error("value type {} must be of type {}.".format(type(_is_custom_builtin), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        if is_usage is True and arg_name != "_usage_":
            return True
        else:
            return False

def get_values(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_values")
    dy_values=dict(
        authorized=False,
        required=False,
        min=None,
        max=None,
    )
    if "_values" in dy_props:
        _values=dy_props["_values"]
        del dy_props["_values"]
        if isinstance(_values, str):
            reg=re.match(get_regex("def_values")["rule"], _values)
            if reg:
                dy_values["authorized"]=True
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
                            msg.error("max value '{}' must be greater than min value '{}'.".format(_max, _min), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
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
                ], prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        elif _values is None:
            dy_values=dict(
                authorized=False,
                required=False,
                min=None,
                max=None
            )
        else:
            try:
                _values=int(_values)
            except:
                msg.error("value type {} must be either of type {} or of type {}.".format(type(_values), str, int), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            if _values > 0:
                dy_values["min"]=_values
                dy_values["max"]=_values
                dy_values["authorized"]=True
                dy_values["required"]=True
            else:
                msg.error("when value is of type {} then it must be greater than 0.".format(int), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    return dy_values

def get_is_usage(dy_props, dy_err, pnode_dfn):
    prop_prefix=get_prop_prefix(dy_err, "_is_usage")
    if "_is_usage" in dy_props:
        _is_usage=dy_props["_is_usage"]
        del dy_props["_is_usage"]
        if _is_usage is None:
            return False
        elif isinstance(_is_usage, bool):
            if _is_usage is True:
                node_level=1
                if pnode_dfn is not None:
                    node_level=pnode_dfn.level+1
                if node_level != 2:
                    msg.error("when '_is_usage' is '{}' argument node level must be '2' not '{}'.".format(True, node_level), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
            return _is_usage
        else:
            msg.error("value type {} must be of type {}.".format(type(_is_usage), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return False

def get_show(dy_props, dy_err, pnode_dfn):
    prop_prefix=get_prop_prefix(dy_err, "_show")

    if pnode_dfn is not None and pnode_dfn.dy["show"] is False:
        return False
    else:
        if "_show" in dy_props:
            _show=dy_props["_show"]
            del dy_props["_show"]
            if _show is None:
                return True
            elif isinstance(_show, bool):
                return _show
            else:
                msg.error("value type {} must be of type {}.".format(type(_show), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        else:
            return True

def is_node_implicit(node_dy, is_required):
    if is_required is True:
        if node_dy["values_authorized"] is True:
            if node_dy["values_required"] is True:
                if node_dy["default"] is not None:
                    return True
                else:
                    return False
            else:
                return True
        elif node_dy["values_authorized"] is False:
            return True
        else:
            return False
    else:
        return False

def get_required(dy_props, tmp_dy_props, dy_err, pnode_dfn, arg_name):
    prop_prefix=get_prop_prefix(dy_err, "_required")
    is_root=(pnode_dfn is None)

    is_required=None
    if "_required" in dy_props:
        _required=dy_props["_required"]
        del dy_props["_required"]

        if is_root:
            is_required=True
        elif _required is None:
            is_required=False
        elif isinstance(_required, bool):
            is_required=_required
        else:
            msg.error("value type {} must be of type {}.".format(type(_required), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        if is_root:
            is_required=True
        else:
            is_required=False

    if is_required is True and is_root is False:
        if pnode_dfn is not None:
            if pnode_dfn.is_root is False:
                is_parent_implicit=is_node_implicit(pnode_dfn.dy, pnode_dfn.dy["required"])
                is_implicit=is_node_implicit(tmp_dy_props, is_required)
                if is_parent_implicit is True:
                    if is_implicit is False:
                        msg.error([
                            "A required argument can be implicitly added on the command-line when:",
                            "- Parent argument is on the command-line.",
                            "- Argument has required values and argument has default values' or 'argument values are not required' or 'argument does not accept values'.",
                            "In definition when an argument can be implicitly added on the command-line then its required children argument must also have the properties to be implicitly added on the command-line.",
                            "For current argument '{}', its parent '{}' can be implicitly added but current argument can't be implicitly added.".format(arg_name, pnode_dfn.name),
                            "Either set parent argument's definition with required values and no default values or set current argument properties so it may be implicitly added on the command-line.",
                        ], prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        if tmp_dy_props["allow_parent_fork"] is False:
            msg.error("when value is '{}' then property '_allow_parent_fork' must be set to '{}'.".format(True, True), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        if tmp_dy_props["allow_siblings"] is False:
            msg.error("when value is '{}' then property '_allow_siblings' must be set to '{}'.".format(True, True), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        if tmp_dy_props["need_child"] is True:
            msg.error("when value is '{}' then property '_need_child' must be set to '{}'.".format(True, False), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        if arg_name in pnode_dfn.dy["xor"]:
            msg.error("argument name '{}' can't be both required and part of parent xor group at '{}'.".format(arg_name,  pnode_dfn.location), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    return is_required

def get_fork(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_fork")
    if "_fork" in dy_props:
        _fork=dy_props["_fork"]
        del dy_props["_fork"]
        if _fork is None:
            return True
        elif isinstance(_fork, bool):
            return _fork
        else:
            msg.error("value type {} must be of type {}.".format(type(_fork), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return False

def get_repeat(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_repeat")
    if "_repeat" in dy_props:
        _repeat=dy_props["_repeat"]
        del dy_props["_repeat"]

        if _repeat is None:
            return "replace"

        authorized_repeats=["append", "error", "replace"]
        if _repeat in authorized_repeats:
            return _repeat
        else:
            msg.error("value '{}' not found in {}.".format(_repeat, authorized_repeats), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return "replace"

def get_in(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_in")
    if "_in" in dy_props:
        _in=dy_props["_in"]
        del dy_props["_in"]

        if _in is None:
            return None
        elif isinstance(_in, str):
            tmp_ins=[]
            for tmp_in in sorted(_in.split(",")):
                tmp_in=tmp_in.strip()
                if len(tmp_in) > 0:
                    tmp_ins.append(tmp_in)
            if len(tmp_ins) == 0:
                return None
            else:
                return sorted(tmp_ins)
        elif isinstance(_in, list):
            if len(_in) == 0:
                return None
            else:
                return sorted(_in)
        elif isinstance(_in, dict):
            if len(_in) == 0:
                return None
            else:
                return _in
        else:
            msg.error("value type {} not found in authorized types {}.".format(type(_in), [ dict, list, str]), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return None

def get_hint(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_hint")
    if "_hint" in dy_props:
        _hint=dy_props["_hint"]
        del dy_props["_hint"]
        if _hint is None:
            return None
        elif isinstance(_hint, str):
            _hint=_hint.strip()
            if len(_hint) == 0:
                return None
            elif len(_hint) <= 100:
                return _hint
            else:
                msg.error("value length '{}' must be less or equal than '100'.".format(len(_hint)), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        else:
            msg.error("value type {} must be of type {}.".format(type(_hint), str), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return None

def get_info(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_info")
    if "_info" in dy_props:
        _info=dy_props["_info"]
        del dy_props["_info"]
        if _info is None:
            return None
        elif isinstance(_info, str):
            _info=_info.strip()
            if len(_info) == 0:
                return None
            else:
                return _info
        else:
            msg.error("value type {} must be of type {}.".format(type(_info), str), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return None

def get_examples(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_examples")
    if "_examples" in dy_props:
        _examples=dy_props["_examples"]
        del dy_props["_examples"]

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
                    msg.error("At least one element in examples list is not of type {}.".format(str), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        else:
            msg.error("value type {} must be either of type {} or type {}.".format(type(_examples), str, list), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        
        if len(tmp_examples) == 0:
            return None
        else:
            return tmp_examples
    else:
        return None

def get_allow_siblings(dy_props, dy_err, pnode_dfn):
    prop_prefix=get_prop_prefix(dy_err, "_allow_siblings")
    is_root=(pnode_dfn is None)
    if "_allow_siblings" in dy_props:
        _allow_siblings=dy_props["_allow_siblings"]
        del dy_props["_allow_siblings"]

        if _allow_siblings is None:
            return True
        elif isinstance(_allow_siblings, bool):
            if is_root is True:
                return True
            else:
                return _allow_siblings
        else:
            msg.error("value type {} must be of type {}.".format(type(_allow_siblings), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return True

def get_allow_parent_fork(dy_props, dy_err, pnode_dfn):
    prop_prefix=get_prop_prefix(dy_err, "_allow_parent_fork")
    is_root=(pnode_dfn is None)
    if "_allow_parent_fork" in dy_props:
        _allow_parent_fork=dy_props["_allow_parent_fork"]
        del dy_props["_allow_parent_fork"]

        if _allow_parent_fork is None:
            return True
        elif isinstance(_allow_parent_fork, bool):
            if is_root is True:
                return True
            else:
                return _allow_parent_fork
        else:
            msg.error("value type {} must be of type {}.".format(type(_allow_parent_fork), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return True

def get_need_child(dy_props, dy_err, pnode_dfn):
    prop_prefix=get_prop_prefix(dy_err, "_need_child")
    is_root=(pnode_dfn is None)

    if "_need_child" in dy_props:
        _need_child=dy_props["_need_child"]
        del dy_props["_need_child"]

        if _need_child is None:
            if is_root is True:
                return True
            else:
                return False
        elif isinstance(_need_child, bool):
            return _need_child
        else:
            msg.error("value type {} must be of type {}.".format(type(_need_child), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        if is_root is True:
            return True
        else:
            return False

def get_enabled(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_enabled")
    if "_enabled" in dy_props:
        _enabled=dy_props["_enabled"]
        del dy_props["_enabled"]

        if _enabled is None:
            return True
        elif isinstance(_enabled, bool):
            return _enabled
        else:
            msg.error("value type {} must be of type {}.".format(type(_enabled), bool), prefix=prop_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        return True

def get_default(dy_props, dy_err):
    prop_prefix=get_prop_prefix(dy_err, "_default")
    if "_default" in dy_props:
        _default=dy_props["_default"]
        del dy_props["_default"]
        if _default is None:
            return None
        elif isinstance(_default, str):
            tmp_defaults=[]
            for tmp_default in _default.split(","):
                tmp_defaults.append(tmp_default.strip())

            if len(tmp_defaults) == 0:
                return None
            else:
                return tmp_defaults
        elif isinstance(_default, list):
            if len(_default) == 0:
                return None
            else:
                return _default
        else:
            return [_default]
    else:
        return None