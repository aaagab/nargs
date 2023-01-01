#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import traceback

from ..dev.nargs import Nargs
from ..dev.exceptions import EndUserError, DeveloperError
from .helpers import CatchEx, err

from ..dev.set_dfn import get_casted_value, implement_implicit_logic

from ..gpkgs import message as msg

import yaml

def test_set_dfn(
    dy_metadata,

):
    with CatchEx(DeveloperError)as c:
        c.text="property can't be set for type file"
        get_casted_value(
            "mytext", 
            dict(
                auto_set_type=False,
                type="file",
            ),
            dict(
                exc=DeveloperError,
                location='args',
                prefix="For 'Nested Arguments' at Nargs in definition for argument 'args'",
                pretty=True
            ),
            "For 'Nested Arguments' at Nargs in definition for argument 'args' at property '_default'",
        )

    with CatchEx(DeveloperError)as c:
        c.text="value type '<class 'str'>' must be of type <class 'float'>"
        get_casted_value(
            "mytext", 
            dict(
                auto_set_type=False,
                type=float,
            ),
            dict(
                exc=DeveloperError,
                location='args',
                prefix="For 'Nested Arguments' at Nargs in definition for argument 'args'",
                pretty=True
            ),
            "For 'Nested Arguments' at Nargs in definition for argument 'args' at property '_default'",
        )

    with CatchEx(DeveloperError)as c:
        c.text="Type has been implicitly set to default <class 'float'>"
        get_casted_value(
            "mytext", 
            dict(
                auto_set_type=True,
                type=float,
            ),
            dict(
                exc=DeveloperError,
                location='args',
                prefix="For 'Nested Arguments' at Nargs in definition for argument 'args'",
                pretty=True
            ),
            "For 'Nested Arguments' at Nargs in definition for argument 'args' at property '_default'",
        )
        
    with CatchEx(DeveloperError)as c:
        c.text="Set '_values' with at least a required minimum of values."
        implement_implicit_logic(
            dict(
                default=[1],
                **{"in": None},
                label=None,
                type=float,
                values_authorized=True,
                values_required=False,
            ),
            dict(
                exc=DeveloperError,
                location='args',
                prefix="For 'Nested Arguments' at Nargs in definition for argument 'args'",
                pretty=True
            )
        )

    with CatchEx(DeveloperError)as c:
        c.text="number of values '1' is less than minimum number of values '2'"
        implement_implicit_logic(
            dict(
                default=[1],
                **{"in": None},
                label=None,
                type=float,
                values_authorized=True,
                values_required=True,
                values_min=2,
                values_max=2,
            ),
            dict(
                exc=DeveloperError,
                location='args',
                prefix="For 'Nested Arguments' at Nargs in definition for argument 'args'",
                pretty=True
            )
        )

    with CatchEx(DeveloperError)as c:
        c.text="number of values '3' is greater than maximum number of values '2'"
        implement_implicit_logic(
            dict(
                default=[1, 2, 3],
                **{"in": None},
                label=None,
                type=float,
                values_authorized=True,
                values_required=True,
                values_min=1,
                values_max=2,
            ),
            dict(
                exc=DeveloperError,
                location='args',
                prefix="For 'Nested Arguments' at Nargs in definition for argument 'args'",
                pretty=True
            )
        )

    with CatchEx(DeveloperError)as c:
        c.text="at property '_in': _label must be None when _in is set."
        implement_implicit_logic(
            dict(
                default=None,
                **{"in": [1,2]},
                label="VALUES",
                type=None,
                values_authorized=False,
                values_required=False,
                values_min=None,
                values_max=None,
            ),
            dict(
                exc=DeveloperError,
                location='args',
                prefix="For 'Nested Arguments' at Nargs in definition for argument 'args'",
                pretty=True
            )
        )

    with CatchEx(DeveloperError)as c:
        c.text="at dict key '1' value '{}' with type <class 'dict'> must be any type from [<class 'bool'>, <class 'float'>, <class 'int'>, <class 'str'>, <class 'NoneType'>]"
        implement_implicit_logic(
            dict(
                default=None,
                **{"in": {1:dict(),2:"pear"}},
                label=None,
                in_labels=[],
                type=float,
                values_authorized=False,
                values_required=False,
                values_min=None,
                values_max=None,
            ),
            dict(
                exc=DeveloperError,
                location='args',
                prefix="For 'Nested Arguments' at Nargs in definition for argument 'args'",
                pretty=True
            )
        )

    with CatchEx(DeveloperError)as c:
        c.text="'apple' is not found in property _in values ['1', '2']"

        implement_implicit_logic(
            dict(
                default=["apple"],
                **{"in": {1:"apple",2:"pear"}},
                label=None,
                in_labels=[],
                type=str,
                values_authorized=False,
                values_required=False,
                values_min=None,
                values_max=None,
            ),
            dict(
                exc=DeveloperError,
                location='args',
                prefix="For 'Nested Arguments' at Nargs in definition for argument 'args'",
                pretty=True
            )
        )

    arg_def="""
        _xor: 
            - "apple,"
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_xor': empty value not allowed in ['apple', '']"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _xor: 
            - "apple,apple"
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_xor': duplicate value not allowed in ['apple', 'apple']"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _xor: 
            - - 1
    """
    with CatchEx(DeveloperError)as c:
        c.text="type error <class 'int'>. It must be of type <class 'str'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _xor: 
            - - ""
              - apple
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_xor': empty value not allowed in ['', 'apple']"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _xor: 
            - - apple
              - apple
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_xor': duplicate value not allowed in ['apple', 'apple']"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)    
    
    arg_def="""
        _xor: 
            - 1
    """
    with CatchEx(DeveloperError)as c:
        c.text="In list [1] for sub-value '1' type error '<class 'int'>'. It must be of type <class 'str'>."
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)    
    
    arg_def="""
        _xor: 
            - apple
            - apple,pear
    """
    with CatchEx(DeveloperError)as c:
        c.text="a multiple elements list ['apple', 'pear'] is present"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)    
    
    arg_def="""
        _xor: 
            - apple,pear
            - apple
    """
    with CatchEx(DeveloperError)as c:
        c.text="a single element list ['apple'] is present"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _xor: 
            - apple,pear
            - apple,pear
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_xor': duplicate lists not allowed ['apple', 'pear']"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _xor: "apple,"
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_xor': empty value not allowed in ['apple', '']"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _xor: "apple,apple"
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_xor': duplicate value not allowed in ['apple', 'apple']"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)    
    
    arg_def="""
        _xor: "apple"
    """
    with CatchEx(DeveloperError)as c:
        c.text="At least two values are needed in _xor list ['apple']"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)    
    
    arg_def="""
        _xor: 1
    """
    with CatchEx(DeveloperError)as c:
        c.text="_xor': type error '<class 'int'>'. It must be '<class 'str'>' or '<class 'list'>'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _aliases: 
            - 1
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_aliases': value type <class 'int'> type must be of type <class 'str'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _aliases: 1
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_aliases': value type <class 'int'> must be either type <class 'str'> or type <class 'list'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _aliases: "@arg-def"
    """
    with CatchEx(DeveloperError)as c:
        c.text="alias '@arg-def' syntax error"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _type: "custom_type"
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_type': value 'custom_type' not found in authorized types"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _label: 1
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_label': value type <class 'int'> must be of type <class 'str'>."
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _is_builtin: 1
    """
    with CatchEx(DeveloperError)as c:
        c.text="_is_builtin': value type <class 'int'> must be of type <class 'bool'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _values: "3-1"
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_values': max value '1' must be greater than min value '3'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _values: "3,1"
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_values': value '3,1' syntax error."
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _values: {}
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_values': value type <class 'dict'> must be either of type <class 'str'> or of type <class 'int'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _values: -1
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_values': when value is of type <class 'int'> then it must be greater than 0"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _is_usage: True
    """
    with CatchEx(DeveloperError)as c:
        c.text="at property '_is_usage': when '_is_usage' is 'True' argument node level must be '2' not '1'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        arg_one:
            _aliases: "?"
    """
    with CatchEx(DeveloperError)as c:
        c.text="for alias '?' first char can be a question mark '?' only when argument property '_is_usage' is set to 'True'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        arg_one:
            _aliases: "/?apple"
            _is_usage: true
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_aliases': for alias '/?apple' when first char is a question mark '?' no other chars are allowed"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(), cache=False, raise_exc=True)
    
    arg_def="""
        _show: -1
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_show': value type <class 'int'> must be of type <class 'bool'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        arg_one:
            _required: -1
    """
    with CatchEx(DeveloperError)as c:
        c.text="'args.arg_one' at property '_required': value type <class 'int'> must be of type <class 'bool'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        arg:
            _required: true
            narg:
                _required: true
                nnarg:
                    _required: true
                    _values: 1
    """
    with CatchEx(DeveloperError)as c:
        c.text="set current argument properties so it may be implicitly added on the command-line"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        arg:
            narg:
                _allow_parent_fork: false
                _required: true
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_required': when value is 'True' then property '_allow_parent_fork' must be set to 'True'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        arg:
            narg:
                _allow_siblings: false
                _required: true
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_required': when value is 'True' then property '_allow_siblings' must be set to 'True'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        arg:
            narg:
                _need_child: true
                _required: true
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_required': when value is 'True' then property '_need_child' must be set to 'False'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        arg:
            _xor: narg,narg2
            narg:
                _required: true
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_required': argument name 'narg' can't be both required and part of parent xor group at 'args.arg'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)

    args=dict(
        arg_one=dict(
            _preset=True,
            arg_two=dict(
                _required=True,
                _values=1,
            ),
        ),
    )
    with CatchEx(DeveloperError) as c:
        c.text="then parent 'arg_one' property '_preset' must be set to 'False'"
        nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())

    args=dict(
        arg_one=dict(
            _preset="text",
        ),
    )
    with CatchEx(DeveloperError) as c:
        c.text="'_preset': value type <class 'str'> must be of type <class 'bool'>"
        nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())

    args=dict(
        arg_one=dict(
            _preset=True,
            _values=1,
        ),
    )
    with CatchEx(DeveloperError) as c:
        c.text="when value is 'True' and argument's values are required then default values must be set with property '_default'"
        nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())

    args=dict(
        arg_one=dict(
            _default=1,
            _preset=True,
            _values=1,
        ),
    )
    nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    if nargs.dfn.dy_nodes["arg_one"].dy["default"][0] != "1": err()

    args=dict(
        arg_one=dict(
            _allow_parent_fork=False,
            _preset=True,
        ),
    )
    with CatchEx(DeveloperError) as c:
        c.text="when value is 'True' then property '_allow_parent_fork' must be set to 'True'"
        nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())

    args=dict(
        arg_one=dict(
            _preset=True,
        ),
        arg_two=dict(
            _allow_siblings=False,
            _preset=True,
        )
    )
    with CatchEx(DeveloperError) as c:
        c.text="sibling node 'arg_one' has property '_preset=True' then property '_allow_siblings' must be set to 'True'"
        nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())

    args=dict(
        arg_one=dict(
            _allow_siblings=False,
            _preset=True,
        ),
        arg_two=dict(
            _preset=True,
        )
    )
    with CatchEx(DeveloperError) as c:
        c.text="'_preset': value can't be set to 'True' when another sibling node 'arg_one' has property '_preset=True' with '_allow_siblings=False'"
        nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())

    args=dict(
        arg_one=dict(
            _need_child=True,
            _preset=True,
        ),
    )
    with CatchEx(DeveloperError) as c:
        c.text="when value is 'True' then property '_need_child' must be set to 'False'"
        nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())

    args=dict(
        arg_one=dict(
            _required=True,
            _preset=True,
        ),
    )
    with CatchEx(DeveloperError) as c:
        c.text="when value is 'True' then property '_required' must be set to 'False'"
        nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    
    arg_def="""
        _repeat: 23.34
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_repeat': value '23.34' not found in ['append', 'error', 'fork', 'replace']"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _in: 23.34
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_in': value type <class 'float'> not found in authorized types [<class 'dict'>, <class 'list'>, <class 'str'>]"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _hint: "this hint is too long and it is going to trigger an error because hint are supposed to be short and that hint is not."
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_hint': value length '117' must be less or equal than '100'"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _hint: 23.34
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_hint': value type <class 'float'> must be of type <class 'str'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _info: 23.34
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_info': value type <class 'float'> must be of type <class 'str'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _examples:
            - text
            - 123
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_examples': At least one element in examples list is not of type <class 'str'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _examples: {}
    """
    with CatchEx(DeveloperError)as c:
        c.text="'_examples': value type <class 'dict'> must be either of type <class 'str'> or type <class 'list'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _allow_siblings: {}
    """
    with CatchEx(DeveloperError)as c:
        c.text="_allow_siblings': value type <class 'dict'> must be of type <class 'bool'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _allow_parent_fork: {}
    """
    with CatchEx(DeveloperError)as c:
        c.text="_allow_parent_fork': value type <class 'dict'> must be of type <class 'bool'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _need_child: {}
    """
    with CatchEx(DeveloperError)as c:
        c.text="_need_child': value type <class 'dict'> must be of type <class 'bool'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _enabled: {}
    """
    with CatchEx(DeveloperError)as c:
        c.text="_enabled': value type <class 'dict'> must be of type <class 'bool'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)
    
    arg_def="""
        _enabled: {}
    """
    with CatchEx(DeveloperError)as c:
        c.text="_enabled': value type <class 'dict'> must be of type <class 'bool'>"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(arg_def), builtins=dict(usage=None), cache=False, raise_exc=True)