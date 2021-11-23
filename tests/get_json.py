#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys
import traceback

from ..dev.nargs import Nargs
from ..dev.exceptions import DeveloperError, EndUserError
from .helpers import CatchEx, err

from ..dev.get_json import has_yaml_module
from ..gpkgs import message as msg

def test_get_json(
    dy_metadata,

):
    nargs=Nargs(
        metadata=dy_metadata,
        args=dict(
            _need_child=False,
            _type=".json",
        ),
        raise_exc=True,
    )

    with CatchEx(EndUserError) as c:
        c.text="argument '--args' needs at least one value"
        nargs.get_args("--args")

    with CatchEx(EndUserError) as c:
        c.text="'--args tests/assets/bad.json': File not found"
        nargs.get_args("--args tests/assets/bad.json")

    with CatchEx(EndUserError) as c:
        c.text="bad-file.json': json syntax error"
        nargs.get_args("--args tests/assets/bad-file.json")

    with CatchEx(EndUserError) as c:
        c.text="bad-file.yaml': yaml syntax error"
        nargs.get_args("--args tests/assets/bad-file.yaml")

    with CatchEx(EndUserError) as c:
        c.text="'--args {{marc}}': Error when trying to load dict"
        nargs.get_args("--args '{{marc}}'")

    # with CatchEx(EndUserError) as c:
    #     c.text=  test(e, "value length is >= than '100000'"
    #     nargs.get_args("--args '{{{}}}'".format({i:None for i in range(10000)}))