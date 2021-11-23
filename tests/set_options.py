#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import traceback

from ..dev.nargs import Nargs
from ..dev.exceptions import EndUserError, DeveloperError
from .helpers import CatchEx, err


from ..gpkgs import message as msg

import yaml

def test_set_options(
    dy_metadata,

):
    with CatchEx(DeveloperError) as c:
        c.text="cache_file option: path is not a file"
        nargs=Nargs(metadata=dy_metadata, cache_file="assets/file.json", raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="JSON syntax error for file"
        nargs=Nargs(metadata=dy_metadata, cache_file="assets/bad-file.json", raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="Pickle syntax error for file"
        nargs=Nargs(metadata=dy_metadata, cache_file="assets/bad-file.pickle", raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="options file extension '.txt' must be in ['.json', '.yaml']"
        nargs=Nargs(metadata=dy_metadata, options_file="assets/bad-file.txt", cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="JSON syntax error in options file"
        nargs=Nargs(metadata=dy_metadata, options_file="assets/bad-file.json", cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="options file path type <class 'int'> must be either type <class 'str'> or type <class 'NoneType'"
        nargs=Nargs(metadata=dy_metadata, options_file=1, cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="options file path not found"
        nargs=Nargs(metadata=dy_metadata, options_file="not-a-path.json", cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="'pretty_help' wrong type <class 'int'>. It must be of type <class 'bool'>."
        nargs=Nargs(metadata=dy_metadata, pretty_help=1, cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="'metadata' wrong type <class 'int'>. It must be of type <class 'dict'>"
        nargs=Nargs(metadata=2, cache=False, raise_exc=True)


    filenpa_gpm=os.path.join(os.path.dirname(os.path.realpath(__file__)), "gpm.json")
    with open(filenpa_gpm, "w") as f:
        f.write("{}}")
    with CatchEx(DeveloperError) as c:
        c.text="when setting options at option 'metadata': JSON syntax error in gpm file"
        nargs=Nargs(builtins=dict(cmd=dict()), cache=False, raise_exc=True)
    os.remove(filenpa_gpm)

    with CatchEx(DeveloperError) as c:
        c.text="'args' has wrong type <class 'int'>. Type can be any type from [<class 'dict'>, <class 'NoneType'>]"
        nargs=Nargs(metadata=dy_metadata, args=2, cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="option 'auto_alias_style' value 'apple' is not in ['camelcase', 'camelcase-hyphen', 'lowercase', 'lowercase-hyphen', 'pascalcase', 'pascalcase-hyphen', 'uppercase', 'uppercase-hyphen']"
        nargs=Nargs(metadata=dy_metadata, auto_alias_style="apple", cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="option 'auto_alias_prefix' value '@' is not in ['', '+', '--', '-', '/', ':', '_']"
        nargs=Nargs(metadata=dy_metadata, auto_alias_prefix="@", cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="At Nargs when setting options: option 'builtins' key 'apple' is not in ['cmd', 'help', 'path_etc', 'usage', 'version']."
        nargs=Nargs(metadata=dy_metadata, builtins=dict(apple=None), cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="option 'builtins' at key 'cmd' for values '[1]' with value '1' wrong type <class 'int'> it must be <class 'str'> for alias"
        nargs=Nargs(metadata=dy_metadata, builtins=dict(cmd=[1]), cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="option 'builtins' for key 'cmd' value '{}' type <class 'dict'> is not in [<class 'NoneType'>, <class 'str'>, <class 'list'>"
        nargs=Nargs(metadata=dy_metadata, builtins=dict(cmd=dict()), cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="at option 'metadata': key 'name' not set."
        nargs=Nargs(builtins=dict(), cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="key 'name' value type <class 'dict'> must be of type <class 'str'>."
        nargs=Nargs(metadata=dict(name=dict(), executable=dict()), builtins=dict(), cache=False, raise_exc=True)

    with CatchEx(DeveloperError) as c:
        c.text="key 'version' value type <class 'int'> must be of type <class 'str'>"
        nargs=Nargs(metadata=dict(name="prog", executable="prog.py", version=32), builtins=dict(), cache=False, raise_exc=True)
