#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
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
        is_a_dump,
        is_dy_preset,
        parent=None,
    ):
        super().__init__(name=name, parent=parent)

        self.arg_id=None
        self.dy_arg=dict()
        self.explicit_aliases=dict()
        self.implicit_aliases=None
        self.explicit_aliases_sort=None

        if is_dy_preset is True or is_a_dump is True:
            self.dy=dy
            self.dy["type"]=get_type_from_str(self.dy["type"])
        else:
            self.dy=get_dy(self.location, self.name, dy, self.is_root)
            if self.is_root is False:
                if self.dy["required"] is True:
                    self.parent.dy["required_children"].append(self.name)

        if self.dy["enabled"] is True:
            if is_a_dump is False:
                self.dy["aliases"]=[]
                self.dy["default_alias"]=None
    
            set_explicit_aliases(self, is_a_dump)

            if is_a_dump is False:
                # if len(self.dy["aliases"]) == 0:
                    # self.dy["enabled"]=False
                # else:
                if self.is_root is True:
                    self.dump={ self.name: deepcopy(self.dy)}
                else:
                    self.parent.dump[self.parent.name]["args"][self.name]=deepcopy(self.dy)
                    self.dump=self.parent.dump[self.parent.name]["args"]
                self.dump[self.name]["args"]=dict()
                self.dump[self.name]["type"]=get_type_str(self.dump[self.name]["type"])

                self.set_first_arg()
                if self.is_root is False:
                    setattr(self.parent.get_arg(), self.name, self.get_arg())
                    self.parent.get_arg()._[self.name]=self.get_arg()

    def set_first_arg(self):
        forks=[]
        parent=None
        if self.is_root is False:
            parent=self.parent.get_arg()
        first_arg=CliArg(forks, self.name, self.get_pre_id(), parent=parent)

        self.arg_id=first_arg._id
        self.dy_arg={
            self.arg_id: dict(
                arg=first_arg,
                forks=forks,
                single=None,
            )
        }

    def get_pre_id(self):
        if self.is_root is True:
            return ""
        else:
            return self.parent.arg_id

    def get_arg(self):
        return self.dy_arg[self.arg_id]["arg"]

    def get_forks(self):
        return self.dy_arg[self.arg_id]["forks"]

class CliArg():
    def __init__(self,
        # default_alias,
        forks,
        name,
        pre_id, 
        parent=None,
        default_alias=None,
    ):
        self._alias=None
        self._default_alias=None
        # default_alias
        self._index=len(forks)+1
        if pre_id == "":
            self._id="{}".format(self._index)
        else:
            self._id="{}.{}".format(pre_id, self._index)
        # forks.append(self)
        self._forks=forks
        # self._forks=forks
        self._here=False
        self._name=name
        self._parent=parent
        self._value=None
        self._values=[]

        # to update _alias, _here, _value, _values but not in the self._
        self._=dict(
            _alias=self._alias,
            _default_alias=self._default_alias,
            _index=self._index,
            _id=self._id,
            _forks=self._forks,
            _here=self._here,
            _name=self._name,
            _parent=self._parent,
            _value=self._value,
            _values=self._values,
        )

        if default_alias is not None:
            self.set_default_alias(default_alias)

    def set_default_alias(self, default_alias):
        self._default_alias=default_alias
        self._["_default_alias"]=default_alias

    def get_path(self, explicit=False, wvalues=False):
        path=[]
        arg=None
        arg=self
        while True:
            text=arg._alias
            if text is None:
                text=arg._default_alias
            add_index=len(arg._forks) > 1
            if add_index is True:
                if arg._parent is None and arg._index == 1:
                    pass
                else:
                    text+="_{}".format(arg._index)

            if wvalues is True:
                if len(arg._values) > 0 and arg == self:
                    for value in arg._values:
                        text+=" {}".format(shlex.quote(value))

            path.insert(0, text)

            arg=arg._parent
            if arg is None:
                break
            else:
                if explicit is True:
                    path.insert(0, "-")

        return " ".join(path)
