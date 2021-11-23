#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
import os
import sys

from .get_types import get_type_from_str
from .get_types import get_type_str
from .nodes import NodeDfn
from .get_node_dfn import get_location
from .get_properties import get_arg_properties

def get_args_dump(node, props=None, dump=None):
    if node is None:
        return None

    if props is None:
        props=get_arg_properties()

    if node.is_root is True:
        dump=dict()

    dump[node.name]=dict()
    for prop in node.dy:
        if prop == "type":
            value=get_type_str(node.dy[prop])
        else:
            value=deepcopy(node.dy[prop])

        if value != props[prop]["default"]:
            dump[node.name][props[prop]["map"]]=value

    dump[node.name][props["args"]["map"]]=dict()

    for tmp_node in node.nodes:
        get_args_dump(tmp_node, props, dump[node.name][props["args"]["map"]])

    if node.is_root is True:
        return dump

def get_cached_theme(dy_cached):
    theme_defaults=dy_cached["map"]["theme_defaults"]
    theme_props=dy_cached["map"]["theme_props"]
    dy_theme=dict()
    for name, props in dy_cached["theme"].items():
        dy_theme[name]=dict()
        default_props=sorted(theme_props)
        for prop, value in props.items():
            default_props.remove(prop)
            new_prop=theme_props[prop]
            dy_theme[name][new_prop]=value

        for prop in default_props:
            new_prop=theme_props[prop]
            dy_theme[name][new_prop]=theme_defaults[prop]

    return dy_theme

def get_cached_node_dfn(dy_args, arg_defaults, arg_props, arg_name=None, pnode_dfn=None):
    if pnode_dfn is None:
        arg_name=next(iter(dy_args))
    
    tmp_dy_args=dict()
    default_props=sorted(arg_props)
    has_args=False
    for prop, value in dy_args[arg_name].items():
        if arg_props[prop] == "args":
            has_args=True
        else:
            default_props.remove(prop)
            new_prop=arg_props[prop]
            tmp_dy_args[new_prop]=value

    args_map=None
    for prop in default_props:
        new_prop=arg_props[prop]
        if new_prop == "args":
            args_map=prop
        else:
            tmp_dy_args[new_prop]=arg_defaults[prop]

    tmp_dy_args["type"]=get_type_from_str(tmp_dy_args["type"])

    node_dfn=NodeDfn(
        dy=tmp_dy_args,
        location=get_location(pnode_dfn, arg_name),
        name=arg_name,
        parent=pnode_dfn,
    )

    if has_args is True:
        for key in dy_args[arg_name][args_map]:
            get_cached_node_dfn(
                dy_args=dy_args[arg_name][args_map],
                arg_defaults=arg_defaults,
                arg_props=arg_props,
                arg_name=key,
                pnode_dfn=node_dfn,
            )

    if node_dfn.is_root is True:
        return node_dfn
