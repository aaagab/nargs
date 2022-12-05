#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
import json
import os 
import shlex
import sys

from .regexes import get_flags_precedence

class NodeDfn():
    def __init__(self,
        dy,
        location,
        name,
        parent=None,
    ):
        self.current_arg=None
        self.dy=dy
        self.dy_nodes=dict()
        self.dy_xor=dict()
        self.explicit_aliases=dict()
        self.implicit_aliases=dict()
        self.is_root=None
        self.level=None
        self.location=location
        self.name=name
        self.nodes=[]
        self.parent=parent
        self.root=None

        self._dy_flags=None
        self._dy_flags_aliases=None
        self._explicit_aliases_sort=None
        self._explicit_flags=dict()
        self._implicit_flags=dict()
        self._pool_aliases=None
        self._pool_flags=None
        
        if self.parent is None:
            self.root=self
            self.is_root=True
            self.level=1
            for alias in self.dy["aliases"]:
                self.implicit_aliases[alias]=self
                set_root_flags(self, alias)
        else:
            self.root=self.parent.root
            self.is_root=False
            self.level=self.parent.level+1
            self.parent.nodes.append(self)
            self.parent.dy_nodes[self.name]=self

            for alias in self.dy["aliases"]:
                self.parent.explicit_aliases[alias]=self
                set_explicit_flags(self, alias, self.parent)

            if self.parent._pool_aliases is None:
                self.parent._pool_aliases={}
                self.parent._pool_flags={}

                if self.parent.is_root is True:
                    for alias in self.parent.dy["aliases"]:
                        self.parent._pool_aliases[alias]=self.parent
                        set_implicit_flags(self.parent, alias, self.parent)
                else:
                    for alias in self.parent.parent._pool_aliases:
                        node=self.parent.parent._pool_aliases[alias]
                        self.parent._pool_aliases[alias]=node
                        set_implicit_flags(node, alias, self.parent)

            set_implicit_aliases_and_flags(self.parent, self)
            self.implicit_aliases=self.parent._pool_aliases
            self._implicit_flags=self.parent._pool_flags
            self._set_parent_xor()

        parent_arg=None
        if self.is_root is False:
            parent_arg=self.parent.current_arg
        self.current_arg=CliArg(
            branches=[],
            node_dfn=self,
            parent=parent_arg,
        )

    def _set_parent_xor(self):
        if self.name in self.parent.dy["xor"]:
            if len(self.parent.dy_xor) == 0:
                for name in self.parent.dy["xor"]:
                    if name == self.name:
                        self.parent.dy_xor[self]=dict()
                    else:
                        self.parent.dy_xor[name]=dict()

                    for group_num in self.parent.dy["xor"][name]:
                        append_group=[]
                        if name == self.name:
                            self.parent.dy_xor[self][group_num]=[]
                        else:
                            self.parent.dy_xor[name][group_num]=[]
                        for ref_name in self.parent.dy["xor"][name][group_num]:
                            if name == self.name:
                                if ref_name == self.name:
                                    self.parent.dy_xor[self][group_num].append(self)
                                else:
                                    self.parent.dy_xor[self][group_num].append(ref_name)
                            else:
                                if ref_name == self.name:
                                    self.parent.dy_xor[name][group_num].append(self)
                                else:
                                    self.parent.dy_xor[name][group_num].append(ref_name)
            else:
                self.parent.dy_xor[self]=self.parent.dy_xor.pop(self.name)
                for name in self.parent.dy_xor:
                    if name != self:
                        for group_num in self.parent.dy_xor[name]:
                            if self.name in self.parent.dy_xor[name][group_num]:
                                index_elem=self.parent.dy_xor[name][group_num].index(self.name)
                                self.parent.dy_xor[name][group_num].remove(self.name)
                                self.parent.dy_xor[name][group_num].insert(index_elem, self)

    def get_dy_flags(self):
        if self._dy_flags is None:
            self._dy_flags=dict()
            for flag, dy in self._implicit_flags.items():
                self._dy_flags[flag]=dict(node=dy["node"], alias=dy["alias"])

            for flag, dy in self._explicit_flags.items():
                if flag in self._dy_flags and self._dy_flags[flag]["node"].dy["show"] != dy["node"].dy["show"]:
                    if dy["node"].dy["show"] is True:
                        self._dy_flags[flag]=dict(node=dy["node"], alias=dy["alias"])
                else:
                    self._dy_flags[flag]=dict(node=dy["node"], alias=dy["alias"])
        return self._dy_flags

def set_implicit_flags(flag_node, alias, node_to_set_flag):
    if flag_node.dy["aliases_info"][alias]["is_flag"] is True:
        c=flag_node.dy["aliases_info"][alias]["text"]
        to_set=None
        if has_xor_conflict(flag_node, node_to_set_flag) is False:
            if c in node_to_set_flag._pool_flags:
                tmp_flag_node=node_to_set_flag._pool_flags[c]["node"]
                if tmp_flag_node.level > flag_node.level:
                    to_set=False
                elif tmp_flag_node.level == flag_node.level:
                    to_set=has_precedence(alias, flag_node, tmp_flag_node, node_to_set_flag._pool_flags[c]["alias"])
                else: # tmp_flag_node.level < flag_node.level:
                    to_set=True
            else:
                to_set=True
        else:
            to_set=False

        if to_set is True:
            node_to_set_flag._pool_flags[c]=dict(node=flag_node, alias=alias)

def set_implicit_aliases_and_flags(tree_node, ref_node):
    if tree_node._pool_aliases is not None:
        for alias in ref_node.dy["aliases"]:
            if alias in tree_node._pool_aliases:
                if tree_node._pool_aliases[alias].level < ref_node.level:
                    tree_node._pool_aliases[alias]=ref_node
            else:
                tree_node._pool_aliases[alias]=ref_node
            set_implicit_flags(ref_node, alias, tree_node)

        for tmp_node in tree_node.nodes:
            set_implicit_aliases_and_flags(tmp_node, ref_node)

def has_xor_conflict(first_node, second_node):
    if first_node != second_node:
        if first_node.level == second_node.level:
            if first_node in first_node.parent.dy_xor:
                for group_num in first_node.parent.dy_xor[first_node]:
                    xor_group=first_node.parent.dy_xor[first_node][group_num]
                    if second_node in xor_group:
                        return True
    return False

def set_root_flags(flag_node, alias):
    if flag_node.dy["aliases_info"][alias]["is_flag"] is True:
        c=flag_node.dy["aliases_info"][alias]["text"]
        to_set=None
        if c in flag_node._implicit_flags:
            to_set=has_precedence(alias, flag_node, flag_node._implicit_flags[c]["node"], flag_node._implicit_flags[c]["alias"])
        else:
            to_set=True

        if to_set is True:
            flag_node._implicit_flags[c]=dict(node=flag_node, alias=alias)

def set_explicit_flags(flag_node, alias, node_to_set_flag):
    if flag_node.dy["aliases_info"][alias]["is_flag"] is True:
        c=flag_node.dy["aliases_info"][alias]["text"]
        to_set=None
        if c in node_to_set_flag._explicit_flags:
            to_set=has_precedence(alias, flag_node, node_to_set_flag._explicit_flags[c]["node"], node_to_set_flag._explicit_flags[c]["alias"])
        else:
            to_set=True

        if to_set is True:
            node_to_set_flag._explicit_flags[c]=dict(node=flag_node, alias=alias)

def has_precedence(flag_candidate_alias, flag_candidate_node, existing_flag_node, existing_flag_alias):
    if flag_candidate_node.dy["show"] != existing_flag_node.dy["show"]:
        if flag_candidate_node.dy["show"] is True:
            return True
        else:
            return False
    else:
        flags_precedence=get_flags_precedence()
        existing_flag_node_prefix=existing_flag_node.dy["aliases_info"][existing_flag_alias]["prefix"]
        flag_node_prefix=flag_candidate_node.dy["aliases_info"][flag_candidate_alias]["prefix"]
        if flags_precedence.index(flag_node_prefix) < flags_precedence.index(existing_flag_node_prefix):
            return True
        else:
            return False



class CliArg():
    def __init__(self,
        branches,
        node_dfn,
        parent=None,
        branch_index=None,
    ):
        self._=dict()
        self._alias=None
        self._aliases=node_dfn.dy["aliases"]
        self._args=[]
        self._branches=branches
        if branch_index is None:
            self._branches.append(self)
        else:
            self._branches.insert(branch_index, self)
        self._cmd_line_index=None
        self._count=0
        self._default_alias=node_dfn.dy["default_alias"]
        self._dy_indexes=dict(
            aliases=dict(),
            values=[],
        )
        self._here=False
        self._has_explicit_nodes=False
        self._implicit=False
        self._name=node_dfn.name
        self._dfn=node_dfn
        self._parent=parent
        self._previous_dfn=None
        self._value=None
        self._values=[]

        is_first_branch=self._branches.index(self) == 0

        if self._parent is None:
            self._root=self
            self._is_root=True
            if is_first_branch is True:
                self._cmd_line=None
        else:
            self._root=self._parent._root
            self._is_root=False

            if is_first_branch is True:
                setattr(self._parent, self._name, self)
                self._parent._[self._name]=self

    def _get_cmd_line(self, cmd_line_index=None):
        if cmd_line_index is None:
            if self._cmd_line_index is None:
                return None
            else:
                return self._root._branches[0]._cmd_line[:self._cmd_line_index]
        else:
            return self._root._branches[0]._cmd_line[:cmd_line_index]
            
    def _get_path(self, wvalues=False, keep_default_alias=False):
        path=[]
        arg=self
        args=[]
        while True:
            args.insert(0, arg)
            arg=arg._parent
            if arg is None:
                break

        implicit_aliases=set()

        for arg in args:
            alias=arg._alias

            if alias is None: 
                alias=arg._default_alias
            elif keep_default_alias is True:
                if arg._is_root is False:
                    alias=arg._default_alias

            if alias in implicit_aliases:
                path.append("+")

            text=alias

            add_index=len(arg._branches) > 1
            if add_index is True:
                arg_index=1
                if arg._here is True:
                    arg_index=arg._branches.index(arg)+1

                if arg_index == 1:
                    pass
                else:
                    text+="+{}".format(arg_index)

            if wvalues is True:
                if len(arg._values) > 0 and arg == self:
                    for value in arg._values:
                        if isinstance(value, dict):
                            value=json.dumps(value)
                        else:
                            value=str(value)
                        text+=" {}".format(shlex.quote(value))

            path.append(text)

            if arg == self:
                break
            else:
                for tmp_alias in arg._dfn.dy["aliases"]:
                    if tmp_alias not in implicit_aliases:
                        implicit_aliases.add(tmp_alias)

                if arg._parent is not None:
                    for tmp_arg in arg._parent._args:
                        if self not in tmp_arg._branches:
                            for tmp_alias in tmp_arg._dfn.dy["aliases"]:
                                if tmp_alias not in implicit_aliases:
                                    implicit_aliases.add(tmp_alias)

        return " ".join(path)
