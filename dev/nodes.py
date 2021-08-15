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
    ):
        super().__init__(name=name, parent=parent)
        
        self.current_arg=None
        self.dy_aliases=dict()
        self.explicit_aliases_sort=None

        if is_dy_preset is True:
            self.dy=dy
            self.dy["type"]=get_type_from_str(self.dy["type"])
        else:
            self.dy=get_dy(self.location, self.name, dy, self.is_root, self.level, pretty, app_name)
            if self.is_root is False:
                if self.dy["required"] is True:
                    self.parent.dy["required_children"].append(self.name)

        if self.dy["enabled"] is True:
            self.set_arg("init")
            if is_dy_preset is False:
                set_explicit_aliases(self, pretty, app_name)

    def set_arg(self, action, index=None):
        if action in ["init", "reset", "fork"]:
            forks=[]
            if action == "fork":
                if self.current_arg is not None:
                    forks=self.current_arg._forks

            if self.is_root is True:
                self.current_arg=CliArg(forks, self.name, aliases=self.dy["aliases"], default_alias=self.dy["default_alias"])
            else:
                self.current_arg=CliArg(forks, self.name, parent=self.parent.current_arg, aliases=self.dy["aliases"], default_alias=self.dy["default_alias"])

                if action == "init":
                    self.parent.current_arg._args.append(self.current_arg)
                    setattr(self.parent.current_arg, self.name, self.current_arg)
                    self.parent.current_arg._[self.name]=self.current_arg
                
                elif action == "reset":
                    if hasattr(self.parent.current_arg, self.name):
                        tmp_arg=self.parent.current_arg._[self.name]
                        tmp_index=self.parent.current_arg._args.index(tmp_arg)
                        self.parent.current_arg._args.insert(tmp_index, self.current_arg)
                        self.parent.current_arg._args.remove(tmp_arg)
                    else:
                        self.parent.current_arg._args.append(self.current_arg)

                    setattr(self.parent.current_arg, self.name, self.current_arg)
                    self.parent.current_arg._[self.name]=self.current_arg
                
                elif action == "fork":
                    if not hasattr(self.parent.current_arg, self.name):
                        self.parent.current_arg._args.append(self.current_arg)
                        setattr(self.parent.current_arg, self.name, self.current_arg)
                        self.parent.current_arg._[self.name]=self.current_arg
        
        elif action == "select":
            self.current_arg=self.current_arg._forks[index]

class CliArg():
    def __init__(self,
        forks,
        name,
        aliases=[],
        parent=None,
        default_alias=None,
    ):
        self._alias=None
        self._aliases=[]
        self._args=[]
        self._default_alias=None
        self._forks=forks
        self._here=False
        self._name=name
        self._parent=parent
        self._value=None
        self._values=[]

        # to update _alias, _here, _value, _values but not in the self._
        self._=dict(
            _alias=self._alias,
            _aliases=self._aliases,
            _args=self._args,
            _default_alias=self._default_alias,
            _forks=self._forks,
            _here=self._here,
            _name=self._name,
            _parent=self._parent,
            _value=self._value,
            _values=self._values,
        )

        if default_alias is not None:
            self._default_alias=default_alias
            self._["_default_alias"]=default_alias
            self._aliases=aliases
            self._["_aliases"]=aliases
            
    def get_path(self, wvalues=False):
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

            if alias in implicit_aliases:
                    path.append("-")

            text=alias

            add_index=len(arg._forks) > 1
            if add_index is True:
                arg_index=1
                if arg._here is True:
                    arg_index=arg._forks.index(arg)+1

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
                        if self not in tmp_arg._forks:
                            for tmp_alias in tmp_arg._aliases:
                                if tmp_alias not in implicit_aliases:
                                    implicit_aliases.add(tmp_alias)

        return " ".join(path)
