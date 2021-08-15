#!/usr/bin/env python3
from pprint import pprint
import os
import re 
import sys

from .set_dfn import get_dfn_prefix

from ..gpkgs import message as msg

def unset_previous_node_alias(previous_node, alias):
    node_dfn.dy["aliases"].remove(alias)

    if previous_node.dy["default_alias"] == alias:
        previous_node.dy["default_alias"]=None

    if len(previous_node.dy["aliases"]) > 0:
        if previous_node.dy["default_alias"] == alias:
            previous_node.dy["default_alias"]=previous_node.dy["aliases"][0]

def set_explicit_alias(node_dfn, alias):
    if node_dfn.is_root is False:
        node_dfn.parent.dy_aliases[alias]=dict(explicit=node_dfn, implicit=[])

    if node_dfn.dy["default_alias"] is None:
        node_dfn.dy["default_alias"]=alias

def set_explicit_aliases(node_dfn, pretty, app_name):
    prefix=None
    pnode_dfn=None

    if node_dfn.is_root is True:
        prefix=get_dfn_prefix(app_name, node_dfn.location)
    elif node_dfn.is_root is False:
        prefix=get_dfn_prefix(app_name, node_dfn.parent.location)
        pnode_dfn=node_dfn.parent

    node_dfn.dy["aliases"]=[]
    check_nodes=set()
    conflict_nodes=set()
    for alias in node_dfn.dy["dfn_aliases"]:
        node_dfn.dy["aliases"].append(alias)
        if node_dfn.is_root is True:
            set_explicit_alias(node_dfn, alias)
        else:
            if alias in pnode_dfn.dy_aliases:
                previous_node=pnode_dfn.dy_aliases[alias]["explicit"]
                check_nodes.add(previous_node)
                if node_dfn.dy["is_builtin"] is True:
                    if previous_node.dy["is_builtin"] is True:
                        msg.error("alias conflict '{}' between two built-in arguments '{}' and '{}'. This is a developer bug, it shouldn't happen.".format(alias, node_dfn.location, previous_node.location), prefix=prefix, pretty=pretty, exit=1)
                    else:
                        node_dfn.dy["aliases"].remove(alias)
                        conflict_nodes.add(previous_node)
                else:
                    if previous_node.dy["is_builtin"] is True:
                        unset_previous_node_alias(previous_node, alias)
                        set_explicit_alias(node_dfn, alias)
                    else:
                        if node_dfn.dy["auto_aliases"] is True:
                            node_dfn.dy["aliases"].remove(alias)
                            conflict_nodes.add(previous_node)
                        else:
                            if previous_node.dy["auto_aliases"] is True:
                                unset_previous_node_alias(previous_node, alias)
                                set_explicit_alias(node_dfn, alias)
                            else:
                                msg.error("alias '{}' already exists at the same siblings level for argument '{}' and argument '{}'. This is a developer bug, it shouldn't happen.".format(alias, node_dfn.location, previous_node.location), prefix=prefix, pretty=pretty, exit=1)
            else:
                set_explicit_alias(node_dfn, alias)

    if node_dfn.dy["is_builtin"] is False:
        check_nodes.add(node_dfn)
        for node in check_nodes:
            if len(node.dy["aliases"]) == 0:
                if node.dy["is_builtin"] is False:
                    if node != node_dfn:
                        conflict_nodes={node_dfn}

                    dy_conflict=dict()
                    for cnode in conflict_nodes:
                        dy_conflict[cnode.name]=cnode.dy["dfn_aliases"]

                    msg.error("'{}' aliases {} need to be explicitly defined because they conflict with sibling argument(s) {}.".format(node.location, 
                    node.dy["dfn_aliases"],
                    dy_conflict,
                    ), prefix=prefix, pretty=pretty, exit=1)