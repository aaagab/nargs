#!/usr/bin/env python3
# authors: Gabriel Auger
# name: Nested Arguments
# licenses: MIT 
__version__= "1.1.1"

from .dev.nargs import Nargs
from .dev.exceptions import EndUserError, DeveloperError

try:
    from .tests.get_args import test_get_args
    from .tests.get_node_dfn import test_get_node_dfn
    from .tests.aliases import test_aliases
    from .tests.get_json import test_get_json
    from .tests.get_path import test_get_path
    from .tests.nargs import test_nargs
    from .tests.set_dfn import test_set_dfn
    from .tests.set_options import test_set_options
    from .tests.style import test_style
    from .tests.implementation import test_implementation
    from .tests.single_test import single_test
    from .tests.performance import test_performance
    from .gpkgs import message as msg
except BaseException as e:
    if e.__class__.__name__ != "ModuleNotFoundError":
        raise e

