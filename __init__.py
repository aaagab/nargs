#!/usr/bin/env python3
# authors: Gabriel Auger
# name: Nested Arguments
# licenses: MIT 
__version__ = "0.1.0"

from .dev.nargs import Nargs
try:
    from .tests.all_tests import run_tests
    from .tests.single_test import single_test
except Exception as e:
    if e.__class__.__name__ != "ModuleNotFoundError":
        raise e
