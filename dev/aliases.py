#!/usr/bin/env python3
from pprint import pprint
import os
import re 
import sys

from .set_dfn import get_dfn_prefix

from ..gpkgs import message as msg

def unset_previous_node_alias(previous_node, alias_str,  alias):
    previous_node.dy[alias_str].remove(alias)
    node_dfn.dy["aliases"].remove(alias)

    if previous_node.dy["default_alias"] == alias:
        previous_node.dy["default_alias"]=None

    if len(previous_node.dy["aliases"]) == 0:
        if previous_node.dy["is_builtin"] is False:
            msg.error("'{}' aliases need to be defined explicitly because they conflict with siblings arguments.".format(previous_node.location), prefix=prefix, exit=1)
    else:
        if previous_node.dy["default_alias"] == alias:
            previous_node.dy["default_alias"]=previous_node.dy["aliases"][0]

def set_explicit_alias(node_dfn, alias):
    if node_dfn.is_root is False:
        node_dfn.parent.explicit_aliases[alias]=node_dfn
    node_dfn.dy["aliases"].append(alias)

    if node_dfn.dy["default_alias"] is None:
        node_dfn.dy["default_alias"]=alias

def set_explicit_aliases(node_dfn, is_a_dump):
    if is_a_dump is True:
        for alias in node_dfn.dy["aliases"]:
            node_dfn.parent.explicit_aliases[alias]=node_dfn

    else:
        prefix=None
        pnode_dfn=None

        if node_dfn.is_root is True:
            prefix=get_dfn_prefix(node_dfn.location)
        elif node_dfn.is_root is False:
            prefix=get_dfn_prefix(node_dfn.parent.location)
            pnode_dfn=node_dfn.parent

        for alias_str in ["long_alias", "dashless_alias", "short_alias"]:
            for alias in node_dfn.dy[alias_str].copy():
                if node_dfn.is_root is True:
                    set_explicit_alias(node_dfn, alias)
                else:
                    if alias in pnode_dfn.explicit_aliases:
                        previous_node=pnode_dfn.explicit_aliases[alias]
                        if node_dfn.dy["is_builtin"] is True:
                            if previous_node.dy["is_builtin"] is True:
                                msg.error("alias conflict '{}' between two built-in arguments '{}' and '{}'. This is a developer bug, it shouldn't happen.".format(alias, node_dfn.location, previous_node.location), prefix=prefix, exit=1)
                            else:
                                node_dfn.dy[alias_str].remove(alias)
                        else:
                            if previous_node.dy["is_builtin"] is True:
                                unset_previous_node_alias(previous_node, alias_str,  alias)
                                set_explicit_alias(node_dfn, alias)
                            else:
                                if node_dfn.dy["auto_aliases"] is True:
                                    node_dfn.dy[alias_str].remove(alias)
                                else:
                                    if previous_node.dy["auto_aliases"] is True:
                                        unset_previous_node_alias(previous_node, alias_str,  alias)
                                        set_explicit_alias(node_dfn, alias)
                                    else:
                                        msg.error("alias '{}' already exists at the same siblings level for argument '{}' and argument '{}'. This is a developer bug, it shouldn't happen.".format(alias, node_dfn.location, previous_node.location), prefix=prefix, exit=1)
                    else:
                        set_explicit_alias(node_dfn, alias)

                del node_dfn.dy[alias_str]

        if node_dfn.dy["is_builtin"] is False:
            if len(node_dfn.dy["aliases"]) == 0:
                msg.error("'{}' aliases need to be defined explicitly because they conflict with siblings arguments.".format(node_dfn.location), prefix=prefix, exit=1)

            # sort_aliases(node_dfn)   