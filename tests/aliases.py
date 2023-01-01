#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import traceback

from ..dev.nargs import Nargs
from ..dev.exceptions import DeveloperError
from .helpers import CatchEx, err

from ..gpkgs import message as msg

def test_aliases(
    dy_metadata,

):
    with CatchEx(DeveloperError) as c:
        c.text="'explicitly set' alias '--arg-one' has already been 'auto-generated' for sibling argument 'args.arg_one'"
        nargs=Nargs(
            metadata=dy_metadata,
            args=dict(
                arg_one=dict(),
                arg_two=dict(
                    _aliases="--arg-one",
                )
            ),
            raise_exc=True,
        )
