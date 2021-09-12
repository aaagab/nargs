#!/usr/bin/env python3
from pprint import pprint
import os
import re 
import sys

from .set_dfn import get_dfn_prefix
from ..gpkgs import message as msg

def unset_previous_node_alias(previous_node, alias):
    previous_node.dy["aliases"].remove(alias)
    if previous_node.dy["default_alias"] == alias:
        previous_node.dy["default_alias"]=None
        if len(previous_node.dy["aliases"]) > 0:
            previous_node.dy["default_alias"]=previous_node.dy["aliases"][0]

def set_default_alias(node_dfn, alias):
    if node_dfn.dy["default_alias"] is None:
        node_dfn.dy["default_alias"]=alias

def remove_builtin_alias(builtin_node, alias):
    builtin_node.dy["aliases"].remove(alias)
    del builtin_node.dy["aliases_info"][alias]
    if builtin_node.dy["default_alias"] == alias:
        builtin_node.dy["default_alias"]=None
        if len(builtin_node.dy["aliases"]) > 0:
            builtin_node.dy["default_alias"]=builtin_node.dy["aliases"][0]

def set_explicit_aliases(node_dfn, pretty, app_name):
    prefix=None

    if node_dfn.is_root is True:
        prefix=get_dfn_prefix(app_name, node_dfn.location)
    elif node_dfn.is_root is False:
        prefix=get_dfn_prefix(app_name, node_dfn.parent.location)

    # node_dfn.dy["aliases"]=[]
    # for alias in node_dfn.dy["dfn_aliases"].copy():
    for alias in node_dfn.dy["aliases"].copy():
        # node_dfn.dy["aliases"].append(alias)
        if node_dfn.is_root is True:
            set_default_alias(node_dfn, alias)
        else:
            if alias in node_dfn.parent.dy_aliases:
                previous_node=node_dfn.parent.dy_aliases[alias]["explicit"]
                if node_dfn.dy["is_builtin"] is True:
                    if previous_node.dy["is_builtin"] is True:
                        msg.error("alias conflict '{}' between two built-in arguments '{}' and '{}'. This is a developer bug, it shouldn't happen.".format(alias, node_dfn.location, previous_node.location), prefix=prefix, pretty=pretty, exit=1)
                    else:
                        remove_builtin_alias(node_dfn, alias)
                        if len(node_dfn.dy["aliases"]) == 0:
                            node.dy["enabled"]=False
                            break
                else:
                    if previous_node.dy["is_builtin"] is True:
                        remove_builtin_alias(previous_node, alias)
                        if len(previous_node.dy["aliases"]) == 0:
                            remove_builtin_node(previous_node)
                        set_default_alias(node_dfn, alias)
                    else:
                        node_text="explicitly set"
                        if node_dfn.dy["is_auto_alias"] is True:
                            node_text="auto-generated"

                        previous_node_text="explicitly set"
                        if previous_node.dy["is_auto_alias"] is True:
                            previous_node_text="auto-generated"

                        msg.error("'{}' alias '{}' for argument '{}' has already been '{}' for sibling argument '{}'. Please explicitly set a different alias for one of the arguments.".format(
                            node_text,
                            alias,
                            node_dfn.location,
                            previous_node_text,
                            previous_node.location,
                        ), prefix=prefix, pretty=pretty, exit=1)
            else:
                set_default_alias(node_dfn, alias)

def remove_builtin_node(node):
    for tmp_node in node.nodes:
        remove_builtin_node(tmp_node)
    node.parent.nodes.remove(node)
    del node
