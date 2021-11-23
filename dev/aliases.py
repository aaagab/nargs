#!/usr/bin/env python3
from pprint import pprint
import os
import re 
import sys

from ..gpkgs import message as msg

def check_aliases_conflict(pnode_dfn, dy_args, dy_err):
    is_root=(pnode_dfn is None)
    for alias in dy_args["aliases"]:
        if is_root is False:
            if alias in pnode_dfn.explicit_aliases:
                node_text=None
                previous_node_text=None
                previous_node=pnode_dfn.explicit_aliases[alias]
                
                if dy_args["is_builtin"] is True:
                    node_text="set ('built-in')"

                    if previous_node.dy["is_builtin"] is True:
                        previous_node_text="set ('built-in')"
                    else:
                        previous_node_text="explicitly set"
                        if previous_node.dy["is_auto_alias"] is True:
                            previous_node_text="auto-generated"
                else:
                    node_text="explicitly set"
                    if dy_args["is_auto_alias"] is True:
                        node_text="auto-generated"

                    if previous_node.dy["is_builtin"] is True:
                        previous_node_text="set ('built-in')"
                        if previous_node.dy["is_auto_alias"] is True:
                            previous_node_text="auto-generated ('built-in')"
                    else:
                        previous_node_text="explicitly set"
                        if previous_node.dy["is_auto_alias"] is True:
                            previous_node_text="auto-generated"

                msg.error("'{}' alias '{}' has already been '{}' for sibling argument '{}'. Please explicitly set a different alias for one of the arguments.".format(
                    node_text,
                    alias,
                    previous_node_text,
                    previous_node.location,
                ), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    