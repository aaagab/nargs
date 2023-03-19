#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import traceback

import yaml

from ..dev.nargs import Nargs
from ..dev.exceptions import DeveloperError
from .helpers import CatchEx, err

from ..gpkgs import message as msg

def help_output(
    dy_metadata,
):
    args="""
        _hint: This is the main program
        delete:
        upgrade:
        command:
            _hint: Manage computer state
            hibernate:
                _hint: Hibernate computer
            power_on:
                _hint: Power-on computer
            power_off:
                _hint: Power-off computer
            sleep:
                _hint: Sleep computer
        mirror:
            _type: str
            _hint: Mirror a source folder to a destination folder in order. This is useful for synchronizing.
        synchronise:
            _hint: Copy data between folders
            source:
                _type: str
            destination:
                _type: str
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), raise_exc=True)

    try:
        nargs.get_args("--args --usage")
    except:
        pass
    
    print("\n########################################################\n")
    
    try:
        nargs.get_args("--args --usage --builtins")
    except:
        pass
    
    print("\n########################################################\n")
    
    try:
        nargs.get_args("--args --usage --depth=-1")
    except:
        pass
    
    print("\n########################################################\n")
    
    try:
        nargs.get_args("--args --usage --depth=-1 --builtins")
    except:
        pass

    print("\n########################################################\n")
    
    try:
        nargs.get_args("--args --usage --hint")
    except:
        pass
    
    print("\n########################################################\n")
    
    try:
        nargs.get_args("--args --usage ? --hint")
    except:
        pass

    print("\n########################################################\n")
    
    try:
        nargs.get_args("--args --usage --hint --depth=-1")
    except:
        pass

    print("\n########################################################\n")
    
    try:
        nargs.get_args("--args --usage --hint --builtins")
    except:
        pass
    
    print("\n########################################################\n")
    
    try:
        nargs.get_args("--args --usage ?")
    except:
        pass
