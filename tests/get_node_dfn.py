#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys
import traceback
import yaml

from ..dev.nargs import Nargs
from ..dev.exceptions import DeveloperError, EndUserError
from .helpers import CatchEx, err

from ..dev.get_json import has_yaml_module
from ..gpkgs import message as msg


def test_get_node_dfn(
    dy_metadata,

):
    with CatchEx(DeveloperError) as c:
        c.text="name '@@@' does not match argument regex"
        Nargs(
            metadata=dy_metadata,
            args={
                "@@@": dict()
            },
            raise_exc=True,
        )

    with CatchEx(DeveloperError) as c:
        c.text="Name '_@@@' not found in available properties"
        Nargs(
            metadata=dy_metadata,
            args={
                "_@@@": dict()
            },
            raise_exc=True,
        )

    with CatchEx(DeveloperError) as c:
        c.text="Argument name '1' wrong type <class 'int'>. Type must match <class 'str'>."
        Nargs(
            metadata=dy_metadata,
            args={
                1: dict()
            },
            raise_exc=True,
        )

    with CatchEx(DeveloperError) as c:
        c.text="nested argument 'arg_one' type <class 'str'> must be of type <class 'dict'>"
        Nargs(
            metadata=dy_metadata,
            args=dict(
                arg_one="text"
            ),
            raise_exc=True,
        )

    with CatchEx(DeveloperError) as c:
        c.text="nested argument 'arg_one' type <class 'str'> must be of type <class 'dict'>"
        Nargs(
            metadata=dy_metadata,
            args=dict(
                arg_one="text"
            ),
            raise_exc=True,
        )

    with CatchEx(DeveloperError) as c:
        c.text="for argument 'args.@': Wrong value type <class 'int'> in list. It must be <class 'str'>"
        Nargs(
            metadata=dy_metadata,
            args={
                "@":[1]
            },
            raise_exc=True,
        )

    with CatchEx(DeveloperError) as c:
        c.text="argument 'args.@': Wrong value type <class 'dict'>. It must be either <class 'str'> or <class 'list'>"
        Nargs(
            metadata=dy_metadata,
            args={
                "@":dict()
            },
            raise_exc=True,
        )

    tmp_args=dict(
        _xor="arg_one,arg_two",
        arg_one=dict(
            _preset=True,
        ),
        arg_two=dict(
            _preset=True,
        ),
    )
    with CatchEx(DeveloperError) as c:
        c.text="have both '_preset=True' and are part of the same xor group"
        Nargs(args=tmp_args, metadata=dy_metadata, raise_exc=True, builtins=dict())

    with CatchEx(DeveloperError) as c:
        c.text="for argument 'args': at key '_xor' child argument name 'arg_three' not found"
        Nargs(
            cache=False,
            metadata=dy_metadata,
            raise_exc=True,
            args=dict(
                _xor="arg_two,arg_three"
            )
        )

    with CatchEx(DeveloperError) as c:
        c.text="property '_is_usage' can only be declared for one argument"
        Nargs(
            cache=False,
            metadata=dy_metadata,
            raise_exc=True,
            args=dict(
                arg_one=dict(
                    _is_usage=True,
                )
            )
        )

    with CatchEx(DeveloperError) as c:
        c.text="argument 'arg_one' can't be duplicated at location 'args' because one sibling argument has already the same name."
        Nargs(
            cache=False,
            metadata=dy_metadata,
            raise_exc=True,
            args={
                "arg_one": {},
                "@": "args.arg_one",
            },
        )

    with CatchEx(DeveloperError) as c:
        c.text="Infinite recursion at address args.arg_one with loop ['args.arg_one', 'args.arg_two', 'args.arg_three', 'args.arg_one']"
        Nargs(
            cache=False,
            metadata=dy_metadata,
            raise_exc=True,
            args={
                "arg_one": {
                    "@": "args.arg_two",
                },
                "arg_two": {
                    "@": "args.arg_three",
                },
                "arg_three": {
                    "@": "args.arg_one",
                }
            },
        )

    with CatchEx(DeveloperError) as c:
        c.text="Infinite recursion at address args.arg_one.nested with loop ['args.arg_one.nested', 'args.arg_one']"
        Nargs(
            cache=False,
            metadata=dy_metadata,
            raise_exc=True,
            args={
                "arg_one": {
                    "nested":{
                        "@": "args.arg_one",
                    }
                },
            },
        )

    with CatchEx(DeveloperError) as c:
        c.text="Built-in argument '_help_' can't be duplicated"
        Nargs(
            cache=False,
            metadata=dy_metadata,
            raise_exc=True,
            args={
                "arg_one": {
                    "nested": {
                        "@": "args._help_",
                    }
                }
            },
        )

    with CatchEx(DeveloperError) as c:
        c.text="'@' does not accept empty string"
        Nargs(
            cache=False,
            metadata=dy_metadata,
            raise_exc=True,
            args={
                "arg_one": {
                    "nested": {
                        "@": [""],
                    }
                }
            },
        )

    with CatchEx(DeveloperError) as c:
        c.text="'@' does not accept empty string"
        Nargs(
            cache=False,
            metadata=dy_metadata,
            raise_exc=True,
            args={
                "arg_one": {
                    "nested": {
                        "@": "",
                    }
                }
            },
        )

    with CatchEx(DeveloperError) as c:
        c.text="argument path 'other' does not exist in arguments tree"
        Nargs(
            cache=False,
            metadata=dy_metadata,
            raise_exc=True,
            args={
                "arg_one": {
                    "nested": {
                        "@": "other",
                    }
                }
            },
        )

    args="""
        _need_child: false
        usage:
            _is_usage: true
            _allow_parent_fork: false
        arg:
    """
    with CatchEx(DeveloperError) as c:
        c.text="'_is_usage' node at key 'allow_parent_fork' value 'False' must be 'True'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=True)

    args="""
        _need_child: false
        _xor: "arg,usage"
        usage:
            _is_usage: true
        arg:
    """
    with CatchEx(DeveloperError) as c:
        c.text="'_is_usage' node can't be present in parent 'args' '_xor' groups"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=True)

    args=dict(
        direction=dict(
            version=dict(
                direction=dict(
                    direction=dict(),
                ),
            ),
            direction=dict(),
        ),
        version=dict(),
    )
    nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())

    root=nargs.dfn
    print(root.name, root)
    pprint(root.implicit_aliases)

    print()
    node=root.dy_nodes["direction"]
    print(node.current_arg._get_path(), node)
    pprint(node.implicit_aliases)
    if node != node.implicit_aliases["--direction"]: err()
    if root.dy_nodes["version"] != node.implicit_aliases["--version"]: err()

    print()
    node=root.dy_nodes["version"]
    print(node.current_arg._get_path(), node)
    pprint(node.implicit_aliases)
    if node != node.implicit_aliases["--version"]: err()
    if root.dy_nodes["direction"] != node.implicit_aliases["--direction"]: err()

    print()
    node=root.dy_nodes["direction"].dy_nodes["version"]
    print(node.current_arg._get_path(), node)
    pprint(node.implicit_aliases)
    if node != node.implicit_aliases["--version"]: err()
    if root.dy_nodes["direction"].dy_nodes["direction"] != node.implicit_aliases["--direction"]: err()

    print()
    node=root.dy_nodes["direction"].dy_nodes["direction"]
    print(node.current_arg._get_path(), node)
    pprint(node.implicit_aliases)
    if node != node.implicit_aliases["--direction"]: err()
    if root.dy_nodes["direction"].dy_nodes["version"] != node.implicit_aliases["--version"]: err()

    print()
    node=root.dy_nodes["direction"].dy_nodes["version"].dy_nodes["direction"]
    print(node.current_arg._get_path(), node)
    pprint(node.implicit_aliases)
    if node != node.implicit_aliases["--direction"]: err()
    if root.dy_nodes["direction"].dy_nodes["version"] != node.implicit_aliases["--version"]: err()

    print()
    node=root.dy_nodes["direction"].dy_nodes["version"].dy_nodes["direction"].dy_nodes["direction"]
    print(node.current_arg._get_path(), node)
    pprint(node.implicit_aliases)
    if node != node.implicit_aliases["--direction"]: err()
    if root.dy_nodes["direction"].dy_nodes["version"] != node.implicit_aliases["--version"]: err()