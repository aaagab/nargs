#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import traceback

from ..dev.nargs import Nargs
from ..dev import nargs

from ..gpkgs import message as msg

def single_test(
    dy_metadata,

):
    nargs.debug=True
    nargs.cache=True
    # nargs.cache=False
  

    narg=Nargs(
        builtins=[],
        options_file="settings-3.yaml",
        metadata=dy_metadata,
    )

    args=narg.get_args("--args --arg-one --arg-two")
    print(args.arg_one._here)
    print(args.arg_two._here)
    print(args.arg_three._here)
    
