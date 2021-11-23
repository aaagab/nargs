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

def test_style(
    dy_metadata,

):
    theme="""
        apple:
    """
    with CatchEx(DeveloperError) as c:
        c.text="Theme element 'apple' unknown"
        nargs=Nargs(metadata=dy_metadata, cache=False, raise_exc=True, theme=yaml.safe_load(theme))

    theme="""
        about_fields: 1
    """
    with CatchEx(DeveloperError) as c:
        c.text="element 'about_fields' type '<class 'int'>' must be of type '<class 'dict'>'"
        nargs=Nargs(metadata=dy_metadata, cache=False, raise_exc=True, theme=yaml.safe_load(theme))

    theme="""
        about_fields: 
            apple:
    """
    with CatchEx(DeveloperError) as c:
        c.text="Theme element 'about_fields' property 'apple' unknown"
        nargs=Nargs(metadata=dy_metadata, cache=False, raise_exc=True, theme=yaml.safe_load(theme))

    theme="""
        about_fields: 
            bold: 1
    """
    with CatchEx(DeveloperError) as c:
        c.text="Theme element 'about_fields' property 'bold' value type <class 'int'> unknown in [<class 'bool'>]"
        nargs=Nargs(metadata=dy_metadata, cache=False, raise_exc=True, theme=yaml.safe_load(theme))

    theme="""
        about_fields: 
            foreground: 1
    """
    with CatchEx(DeveloperError) as c:
        c.text="Theme element 'about_fields' property 'foreground' value type <class 'int'> unknown in [<class 'str'>, <class 'NoneType'>]"
        nargs=Nargs(metadata=dy_metadata, cache=False, raise_exc=True, theme=yaml.safe_load(theme))

    theme="""
        about_fields: 
            foreground: "apple"
    """
    with CatchEx(DeveloperError) as c:
        c.text="property 'foreground' with value 'apple' does not match any regexes from"
        nargs=Nargs(metadata=dy_metadata, cache=False, raise_exc=True, theme=yaml.safe_load(theme))

    theme="""
        about_fields: 
            foreground: "0;255;300"
    """
    with CatchEx(DeveloperError) as c:
        c.text="all integer values from 0;255;300 must be less or equal than 255"
        nargs=Nargs(metadata=dy_metadata, cache=False, raise_exc=True, theme=yaml.safe_load(theme))
