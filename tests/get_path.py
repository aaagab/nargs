#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys

from ..dev.nargs import Nargs
from ..dev.exceptions import DeveloperError, EndUserError
from .helpers import CatchEx, err


def test_get_path(
    dy_metadata,

):
    nargs=Nargs(
        metadata=dy_metadata,
        args=dict(
            _need_child=False,
            _type="file",
        ),
        raise_exc=True,
    )

    with CatchEx(EndUserError) as c:
        c.text="'--args folder/' Path not found"
        nargs.get_args("--args folder/")

    with CatchEx(EndUserError) as c:
        c.text="'--args tests/' Path is not a file"
        nargs.get_args("--args tests/")

    nargs=Nargs(
        metadata=dy_metadata,
        args=dict(
            _need_child=False,
            _type="dir",
        ),
        raise_exc=True,
    )

    with CatchEx(EndUserError) as c:
        c.text="'--args tests/aliases.py' Path is not a directory"
        nargs.get_args("--args tests/aliases.py")
