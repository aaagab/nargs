#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
import json
import os 
import shlex
import sys

from .get_types import get_type_str, get_type_from_str
from .set_dfn import get_dy

from .aliases import set_explicit_aliases

class Node():
    def __init__(self, name=None, parent=None):
        self.parent=parent
        self.is_leaf=True
        self.dy_nodes=dict()
        self.nodes=[]
        self.parents=[]
        self.name=name

        if self.parent is None:
            self.root=self
            self.is_root=True
            self.level=1
            self.location=name
        else:
            self.root=self.parent.root
            self.is_root=False
            self.parent.is_leaf=False
            self.level=self.parent.level+1
            self.location="{} > {}".format(self.parent.location, name)
            self.parent.nodes.append(self)
            self.parent.dy_nodes[self.name]=self
            for pnt in self.parent.parents:
                self.parents.append(pnt)
            self.parents.append(parent)

class NodeDfn(Node):
    def __init__(self,
        dy,
        name,
        parent=None,
        is_dy_preset=False,
        pretty=False,
        app_name=None,
        dy_attr_aliases=None,
    ):
        dy_attr_aliases= dy_attr_aliases or dict()
        
        super().__init__(name=name, parent=parent)
        
        self.current_arg=None
        self.dy_aliases=dict()
        self.dy_flags=dict()
        self.explicit_aliases_sort=None
        self.dy_xor=dict()

        if is_dy_preset is True:
            self.dy=dy
            self.dy["type"]=get_type_from_str(self.dy["type"])
        else:
            self.dy=get_dy(
                self.location,
                self.name,
                dy,
                self.is_root,
                self.level,
                pretty,
                app_name,
                dy_attr_aliases,
                parent,
            )
            if self.is_root is False:
                if self.dy["required"] is True:
                    self.parent.dy["required_children"].append(self.name)
                if self.name in self.parent.dy["xor"]:
                    group_nums=sorted([int(num) for num in self.parent.dy["xor"][self.name]])
                    self.dy["xor_notation"]="^"+"^".join(map(str, group_nums))
                    self.dy["xor_groups"]=group_nums

        # if self.dy["enabled"] is True:
        #     parent_arg=None
        #     if self.is_root is False:
        #         parent_arg=self.parent.current_arg
        #     self.current_arg=CliArg(
        #         self.dy["aliases"],
        #         self.dy["default_alias"],
        #         self.name,
        #         branches=[],
        #         parent=parent_arg,
        #     )

class CliArg():
    def __init__(self,
        aliases,
        default_alias,
        name,
        branches,
        cmd_line,
        parent=None,
        branch_index=None,
    ):
        self._=dict()
        self._alias=None
        self._aliases=aliases
        self._args=[]
        self._branches=branches
        if branch_index is None:
            self._branches.append(self)
        else:
            self._branches.insert(branch_index, self)
        self._cmd_line_index=None
        self._count=0
        self._default_alias=default_alias
        self._dy_indexes=dict(
            aliases=dict(),
            values=[],
        )
        self._here=False
        self._implicit=False
        self._name=name
        self._parent=parent
        self._value=None
        self._values=[]

        is_first_branch=self._branches.index(self) == 0

        if self._parent is None:
            self._root=self
            self._is_root=True
            if is_first_branch is True:
                self._cmd_line=cmd_line
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
                    path.append("-")

            text=alias

            add_index=len(arg._branches) > 1
            if add_index is True:
                arg_index=1
                if arg._here is True:
                    arg_index=arg._branches.index(arg)+1

                if arg._parent is None and arg_index == 1:
                    pass
                else:
                    text+="_{}".format(arg_index)

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
                for tmp_alias in arg._aliases:
                    if tmp_alias not in implicit_aliases:
                        implicit_aliases.add(tmp_alias)

                if arg._parent is not None:
                    for tmp_arg in arg._parent._args:
                        if self not in tmp_arg._branches:
                            for tmp_alias in tmp_arg._aliases:
                                if tmp_alias not in implicit_aliases:
                                    implicit_aliases.add(tmp_alias)

        return " ".join(path)
