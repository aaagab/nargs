#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys

from ..dev.nargs import Nargs
from ..dev.exceptions import DeveloperError
from .helpers import CatchEx, err
from .performance import get_dict

def test_nargs(
    dy_metadata,
    filenpa_cache,
    filenpa_cache_pickle,
):
    with CatchEx(DeveloperError) as c:
        c.text="'raise_exc' option wrong type <class 'int'>"
        nargs=Nargs(
            metadata=dy_metadata,
            args=dict(
                _need_child=False,
            ),
            raise_exc=1,
        )

    with CatchEx(DeveloperError) as c:
        c.text="'only_cache' option must be set to 'False' when cache is 'False'"
        nargs=Nargs(
            metadata=dy_metadata,
            args=dict(
                _need_child=False,
            ),
            cache=False,
            only_cache=True,
            raise_exc=True,
        )

    with CatchEx(DeveloperError) as c:
        c.text="cache_file option file extension '.txt' not found in '['.json', '.pickle']'"
        nargs=Nargs(
            metadata=dy_metadata,
            args=dict(
                _need_child=False,
            ),
            cache_file="nargs-cache.txt",
            raise_exc=True,
        )

    with CatchEx(DeveloperError) as c:
        c.text="cache_file option wrong type <class 'dict'>"
        nargs=Nargs(
            metadata=dy_metadata,
            args=dict(
                _need_child=False,
            ),
            cache_file=dict(),
            raise_exc=True,
        )

    try:
        os.remove(filenpa_cache)
    except:
        pass

    open(filenpa_cache, "w").close()

    with CatchEx(DeveloperError) as c:
        c.text="option 'only_cache' is set to True but Nargs retrieved cache from cache_file"
        nargs=Nargs(
            metadata=dy_metadata,
            args=dict(
                _need_child=False,
            ),
            cache_file=filenpa_cache,
            only_cache=True,
            raise_exc=True,
        )

    try:
        os.remove(filenpa_cache_pickle)
    except:
        pass

    args=get_dict(5, 10, 900)
    with CatchEx(DeveloperError) as c:
        c.text="Please switch cache_file option to '.json'"
        nargs=Nargs(
            metadata=dy_metadata,
            args=args,
            builtins=dict(),
            cache_file=filenpa_cache_pickle,
            raise_exc=True,
        )

    nargs=Nargs(
        metadata=dy_metadata,
        args=dict(
            _need_child=False,
        ),
        raise_exc=True,
    )

    with CatchEx(DeveloperError) as c:
        c.text="Nargs get_documentation: output 'doc' not found in ['asciidoc', 'cmd_help', 'cmd_usage', 'html', 'markdown', 'text']"
        nargs.get_documentation("doc")
    
    with CatchEx(DeveloperError) as c:
        c.text="filenpa type <class 'int'> is not type <class 'str'>"
        nargs.get_documentation("html", filenpa=2)
    
    with CatchEx(DeveloperError) as c:
        c.text="option wsyntax must be 'True' when option only_syntax is 'True'"
        nargs.get_documentation("html", filenpa="tests/assets/doc.html", wsyntax=False, only_syntax=True)
    
    with CatchEx(DeveloperError) as c:
        c.text="Nargs get_documentation: file already exists"
        nargs.get_documentation("html", filenpa="tests/assets/doc.html")
    