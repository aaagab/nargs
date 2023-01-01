#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys
import tempfile
import traceback
import yaml

from ..dev.nargs import Nargs
from ..dev.exceptions import EndUserError
from ..gpkgs import message as msg
from .helpers import CatchEx, err

def test_get_args(
    dy_metadata,
    filenpa_cache,
    filenpa_tmp_query,
    manual,
):
    args=dict(
        logout=dict(),
        poweroff=dict(),
        restart=dict(),
    )

    with CatchEx(EndUserError) as c:
        c.text="option query values must be of type <class 'list'>"            
        Nargs(args=args, metadata=dy_metadata, raise_exc=True).get_args("--args --logout", values=1)

    with CatchEx(EndUserError) as c:
        c.text="cmd type <class 'int'> must be of type <class 'str'>"            
        Nargs(args=args, metadata=dy_metadata, raise_exc=True).get_args(cmd=1)


    args=dict(
        logout=dict(
            _values="*"
        ),
    )

    os.environ["fruit"]="apple"
    os.environ["reason"]="for the best"
    nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, substitute=True)
    args=nargs.get_args("--args --logout __fruit__ __reason__")


    if "apple" not in args.logout._values: err()
    if "for the best" not in args.logout._values: err()
    
    if manual is True:
        args=dict(
            password=dict(
                _type="str"
            ),
            user=dict(
                _type="str"
            ),
        )
        nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, substitute=True)
        args=nargs.get_args("--args --user __input:user__ --password __hidden:password__")
        if args.user._value != "user": err()
        if args.password._value != "password": err()

        args=nargs.get_args("--args --user __input__")
        if args.user._value != "input": err()

        args=nargs.get_args("--args --password __hidden__")
        if args.password._value != "hidden": err()

    args=dict(
        user=dict(
            _type="str",
        ),
        password=dict(
            _type="str",
        ),
    )
    nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True)
    with CatchEx(EndUserError) as c:
        c.text="first list element can't be a question mark"
        args=nargs.get_args("? --user", values=["user"])

    with CatchEx(EndUserError) as c:
        c.text="there are less query values than the number of cmd question marks"
        args=nargs.get_args("--args --user ? --password ?", values=["user"])

    with CatchEx(EndUserError) as c:
        c.text="type not found in authorized types"
        args=nargs.get_args("--args --user ? --password ?", values=["user", dict(fruit="apple")])

    with CatchEx(EndUserError) as c:
        c.text="there are more query values than the number of cmd question marks"
        args=nargs.get_args("--args --user ? --password ?", values=["user", "password", "other"])

    args=dict(
        with_deps=dict(
            _type="bool",
            _default=True,
            _required=True,
        )
    )
    nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True)

    args=nargs.get_args("--args --with-deps=false")
    if args.with_deps._value is not False: err()

    nargs=Nargs(options_file="assets/empty.yaml", metadata=dy_metadata, raise_exc=True)

    try:
        nargs.get_args("--args -v")
    except:
        pass

    nargs=Nargs(options_file="assets/empty.json", metadata=dy_metadata, raise_exc=True)
    try:
        args=nargs.get_args("--args -v")
    except:
        pass

    nargs=Nargs(options_file="assets/empty.json", metadata=dy_metadata, builtins=dict(), raise_exc=True)
    args=nargs.get_args("--args")
    if args is not None: err()


    nargs=Nargs(options_file="assets/empty.json", metadata=dy_metadata, builtins=dict(), cache_file=filenpa_cache, raise_exc=True)
    args=nargs.get_args("--args")
    if args is not None: err()

    nargs=Nargs(args=dict(_enabled=False), options_file="assets/empty.json", metadata=dy_metadata, builtins=dict(), cache_file=filenpa_cache, raise_exc=True)
    args=nargs.get_args("--args")
    print(args)
    if args is not None: err()

    nargs=Nargs(
        options_file="assets/settings.yaml",
        cache_file=filenpa_cache,
        metadata=dy_metadata,
        cache=False,
        raise_exc=True,
    )
    args=nargs.get_args("--args --arg-one")
    pprint(vars(args.arg_one))
    print(args.arg_one._get_cmd_line())
    args=nargs.get_args("--args --arg-one")
    args=nargs.get_args("--args --arg-one --args --arg-one")

    for branch in args._branches:
        if branch.arg_one._here is False: err()

        pprint(vars(branch.arg_one))
        if branch.arg_one.narg_one._here is True: err()

    args=nargs.get_args("--args --arg-one --args --arg-one --arg-one")
    if args.arg_one._count != 1: err()

    args=nargs.get_args("--args --arg-two")
    if args._branches[0].arg_two._here is False: err()

    if args._branches[0].arg_two._count != 1: err()

    args=nargs.get_args("--args --arg-two --args --arg-two --arg-two")
    if args._branches[1].arg_two._here is False: err()

    if args._branches[1].arg_two._count != 2: err()


    args=nargs.get_args("--args --arg-two --args --arg-two --args --arg-two")
    args=nargs.get_args("--args --arg-two --arg-two --arg-two")
    if args.arg_two._count != 3: err()

    try:
        args=nargs.get_args("--args --arg-two --arg-two --usage --arg-two")
    except:
        pass

    args=nargs.get_args("--args --arg-one=marc --arg-one=tom --arg-one=john")
    if args.arg_one._branches[0]._value != "marc": err()
    if args.arg_one._branches[1]._value != "tom": err()
    if args.arg_one._branches[2]._value != "john": err()

    args=nargs.get_args("--args --arg-three=marc --arg-three=tom --arg-three=john --arg-three=harry")
    if args.arg_three._branches[0]._value != "harry": err()

    args=dict(
        _aliases="--args,-a,a",
        _repeat="append",
        direction=dict(
            _aliases="--direction,-d",
            _repeat="append",
            directory=dict(
                _aliases="--directory,y",
                _values=1
            ),
            reason=dict(
                _aliases="--reason,/r",
            ),
        ),
        version=dict(),

    )
    nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True, builtins=dict(usage=None))
    args=nargs.get_args("--args -adra")

    if not (args._count == 3): err()
    if not (args.direction._here is True): err()
    if not (args.direction.directory._here is False): err()
    if not (args.direction.reason._here is True): err()

    args=nargs.get_args("--args --direction /rd")
    if not (args.direction._here is True): err()
    if not (args.direction.reason._here is True): err()
    if not (args.direction._count == 2): err()

    with CatchEx(EndUserError) as c:
        c.text="for argument '/r' values are not allowed"
        nargs.get_args("--args -adr='value'")

    args=nargs.get_args("--args -ady='value'")
    if not (args.direction.directory._value == "value"): err()

    nargs=Nargs(
        options_file="assets/settings-2.yaml",
        cache_file=filenpa_cache,
        metadata=dy_metadata,
        raise_exc=True,
    )

    args=nargs.get_args("--args=barry  --args --args --args=marc --args=tom --args=john --args=harry")
    if "harry" not in args._branches[6]._values : err()

    args=nargs.get_args("-a=tom")
    if args._value != "tom": err()

    args=nargs.get_args("-ab")
    if args._here is False: err()
    if args.arg_one._here is False: err()

    with CatchEx(EndUserError) as c:
        c.text="unknown argument '-b'"
        args=nargs.get_args("-a = -b")

    args=nargs.get_args("-a = -a")
    if len(args._branches) != 2: err()
    if args._count != 1: err()

    print(
        args.arg_one._here,
        args._help_._here,
        args._help_.export.overwrite._here,
        args._help_.export.to._here,
        args._help_.metadata.json._here,
        args._help_.metadata.keys._here,
        args._help_.metadata.values._here,
        args._help_.syntax._here,
        args._query_._here,
        args._usage_.depth._here,
        args._usage_.examples._here,
        args._usage_.flags._here,
        args._usage_._["from"]._here,
        args._usage_.hint._here,
        args._usage_.info._here,
        args._usage_.path._here,
        args._usage_.properties._here,
        args._version_._here,
    )

    pprint(args._usage_._)

    with CatchEx(EndUserError) as c:
        c.text="command must have at least the root argument set"
        nargs.get_args("")

    with CatchEx(EndUserError) as c:
        c.text="command must finish with an argument or a value not an explicit notation '-'"
        nargs.get_args("--args -")

    with CatchEx(EndUserError) as c:
        c.text="explicit level '---' out of bound"
        nargs.get_args("--args --- --arg-one")

    with CatchEx(EndUserError) as c:
        c.text="unknown argument '--arg-unknown'"
        nargs.get_args("--args + --arg-unknown")
    
    with CatchEx(EndUserError) as c:
        c.text="argument '--arg-one' does not accept value(s) '--arg-unknown'"
        nargs.get_args("--args --arg-one --arg-unknown")

    with CatchEx(EndUserError) as c:
        c.text="argument '--arg-two' value '--arg-unknown' type error"
        nargs.get_args("--args --arg-two --arg-unknown")

    with CatchEx(EndUserError) as c:
        c.text="unknown argument '<tag>'"
        nargs.get_args("--args + <tag>")

    with CatchEx(EndUserError) as c:
        c.text="argument '--arg-one' does not accept value(s) '<tag>'"
        nargs.get_args("--args --arg-one <tag>")

    with CatchEx(EndUserError) as c:
        c.text="'--query' can't be provided more than once."
        nargs.get_args("--args --query tests/assets/query.json")


    with open(filenpa_tmp_query, "w") as f:
        f.write(json.dumps(dict()))
    nargs2=Nargs(args=dict(
        user=dict(
            _type="str",
        ),
        password=dict(
            _type="str",
        ),
    ), metadata=dy_metadata, raise_exc=True)

    with CatchEx(EndUserError) as c:
        c.text="attribute 'cmd' not found"
        nargs2.get_args("--args --query {}".format(filenpa_tmp_query))

    with CatchEx(EndUserError) as c:
        c.text="JSON syntax error in query file"
        nargs2.get_args("--args --query {}".format("tests/assets/bad-file.json"))

    with CatchEx(EndUserError) as c:
        c.text="metadata key 'unknown-key' not found"
        nargs2.get_args("--args --help --metadata unknown-key")

    with CatchEx(EndUserError) as c:
        c.text="from LEVEL '-2' must be greater or equal than '-1'"
        nargs.get_args("--args --usage --from=-2")

    with CatchEx(EndUserError) as c:
        c.text="depth LEVEL '-2' must be greater or equal than '-1'"
        nargs.get_args("--args -ud=-2")

    version=dy_metadata["version"]
    del dy_metadata["version"]
    nargs=Nargs(
        options_file="assets/settings-2.yaml",
        cache_file=filenpa_cache,
        metadata=dy_metadata,
        raise_exc=True,
    )

    with CatchEx(EndUserError) as c:
        c.text="version not provided"
        nargs.get_args("--args -v")

    nargs=Nargs(
        options_file="assets/settings-3.yaml",
        metadata=dy_metadata,
        raise_exc=True,
    )

    with CatchEx(EndUserError) as c:
        c.text="the two following arguments can't be provided"
        nargs.get_args("--args --arg-one --arg-three")

    nargs=Nargs(
        options_file="assets/settings-3.yaml",
        metadata=dy_metadata,
        raise_exc=True,
    )

    with CatchEx(EndUserError) as c:
        c.text="the two following arguments can't be provided at the same time"
        nargs.get_args("--args --arg-two --arg-three")

    args=nargs.get_args("--args --arg-one --arg-two")

    if not (args.arg_one._here is True and args.arg_two._here is True): err()

    args=nargs.get_args("--args --arg-four --nested-arg1")

    with CatchEx(EndUserError) as c:
        c.text="'allow_parent_fork' is set to 'False' but parent argument has more than one branch"
        args=nargs.get_args("--args --arg-four --arg-four --nested-arg1")

    with CatchEx(EndUserError) as c:
        c.text="'--arg-four' can't be forked"
        args=nargs.get_args("--args --arg-four --nested-arg1 --arg-four")

    args=nargs.get_args("--args --arg-four --nested-arg2 --arg-four")
    if not (args.arg_four.nested_arg2._here is True): err()
    if not (args.arg_four._branches[1].nested_arg2._here is False): err()
    args=nargs.get_args("--args --arg-four --arg-four --nested-arg2 --arg-four")
    
    args=nargs.get_args("--args --arg-two --nested-arg2")
    args=nargs.get_args("--args --arg-two --nested-arg1")
    args=nargs.get_args("--args --arg-two --nested-arg2 --arg-four --nested-arg1")

    if not (args.arg_two.nested_arg2._here is True): err()
    if not (args.arg_four.nested_arg1._here is True): err()

    with CatchEx(EndUserError) as c:
        c.text="already has a sibling argument"
        args=nargs.get_args("--args --arg-two --nested-arg2 --nested-arg1")

    with CatchEx(EndUserError) as c:
        c.text="at least one sibling is present"
        args=nargs.get_args("--args --arg-two --nested-arg1 --nested-arg2")

    with CatchEx(EndUserError) as c:
        c.text="needs at least one value"
        args=nargs.get_args("--args --arg-two --nested-arg3")

    args=nargs.get_args("--args --arg-two --nested-arg3 test-value")
    
    if not (args.arg_two.nested_arg3._value == "test-value"): err()

    if not (args.arg_two.nested_arg3._values[0] == "test-value"): err()

    with CatchEx(EndUserError) as c:
        c.text="minimum values '1' is less than '2'."
        args=nargs.get_args("--args --arg-two --nested-arg4 value1")

    args=nargs.get_args("--args --arg-two --nested-arg4 value1 value2")
    if not (args.arg_two.nested_arg4._values[1] == "value2"): err()

    with CatchEx(EndUserError) as c:
        c.text="Maximum number of values '2' has been reached already."
        args=nargs.get_args("--args --arg-two --nested-arg4 value1 value2 value3")

    with CatchEx(EndUserError) as c:
        c.text="type error. It must match type '<class 'int'>'"
        args=nargs.get_args("--args --arg-two --nested-arg1 value1")

    with CatchEx(EndUserError) as c:
        c.text="value '53' not found in [1, 2, 3]"
        args=nargs.get_args("--args --arg-two --nested-arg5 53")

    with CatchEx(EndUserError) as c:
        c.text="can't be forked because its child argument '--nested-arg1'"
        args=nargs.get_args("--args --arg-four --nested-arg1 --arg-four")

    with CatchEx(EndUserError) as c:
        c.text="can't be repeated because its 'repeat' property is set to 'error'"
        args=nargs.get_args("--args --arg-three --arg-three")

    args=nargs.get_args("--args --arg-five --n-arg1 --nn-arg1 --arg-five")
    if not (args.arg_five.n_arg1._count == 2): err()

    args=nargs.get_args("--args --arg-five --n-arg1 --nn-arg1 - --arg-five")
    if not (args.arg_five._count == 1): err()

    if not (args.arg_five.n_arg1._count == 2): err()

    args=nargs.get_args("--args --arg-five --n-arg1 --nn-arg1 -- --arg-five")
    if not (args.arg_five._count == 2): err()
    if not (args.arg_five.n_arg1._count == 1): err()

    args=nargs.get_args("--args --arg-six --n-arg1 --nn-arg1 --arg-six")
    if not (args.arg_six._count == 1): err()
    if not (args.arg_six.n_arg1.nn_arg1.nnn_arg1._count == 1): err()

    args=nargs.get_args("--args --arg-six --n-arg1 --nn-arg1 - --arg-six")
    if not (args.arg_six._count == 1): err()

    if not (args.arg_six.n_arg1._count == 2): err()

    args=nargs.get_args("--args --arg-six --n-arg1 --nn-arg1 -- --arg-six")
    if not (args.arg_six._count == 2): err()

    if not (args.arg_six.n_arg1._count == 1): err()

    args=nargs.get_args("--args --arg-six --n-arg1 --nn-arg1 + --arg-six")
    if not (args.arg_six._count == 1): err()

    if not (args.arg_six.n_arg1.nn_arg1.nnn_arg1._count == 1): err()

    with CatchEx(EndUserError) as c:
        c.text="for argument '--arg-one' values are not allowed"
        args=nargs.get_args("--args --arg-one=value")

    with CatchEx(EndUserError) as c:
        c.text="argument '--args' does not accept value(s) '-ap'"
        args=nargs.get_args("--args -ap")

    with CatchEx(EndUserError) as c:
        c.text="'--arg-seven' at least one child argument is needed"
        args=nargs.get_args("--args --arg-seven")

    args=nargs.get_args("--args --arg-seven --n-arg1")
    if not (args.arg_seven.n_arg1._count == 1): err()

    with CatchEx(EndUserError) as c:
        c.text="'--arg-seven' at least one child argument is needed"
        args=nargs.get_args("--args --arg-seven")

    args=nargs.get_args("--args --arg-height")
    if not (args.arg_height.n_arg._count == 1): err()
    
    if not (args.arg_height.n_arg._here is True): err()

    with CatchEx(EndUserError) as c:
        c.text="'--args --arg-nine' required argument '--n-arg' is missing"
        args=nargs.get_args("--args --arg-nine")

    tmp_dy_args=dict(
        arg_one=dict(
            _preset=True,
            arg_two=dict(
                _required=True,
                arg_three=dict(
                    _required=True,
                    arg_four=dict(
                        _preset=True,
                    )
                ),
            )
        ),
    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()
    if tmp_args.arg_one.arg_two._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three.arg_four._here is False: err()

    tmp_dy_args=dict(
        arg_one=dict(
            _preset=True,
            arg_two=dict(
                _default="apple",
                _required=True,
                _values=1,
                arg_three=dict(
                    _required=True,
                    arg_four=dict(
                        _default="orange",
                        _preset=True,
                        _values=1,
                    )
                ),
            )
        ),
    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()
    if tmp_args.arg_one.arg_two._here is False: err()
    if tmp_args.arg_one.arg_two._value != "apple": err()
    if tmp_args.arg_one.arg_two.arg_three._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three.arg_four._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three.arg_four._value != "orange": err()

    tmp_dy_args=dict(
        arg_one=dict(
            _default=1,
            _preset=True,
            _values=1,
        ),
    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()
    if tmp_args.arg_one._value != "1" : err()

    tmp_dy_args=dict(
        arg_one=dict(
            _preset=True,
            arg_two=dict(
                _preset=True,
                arg_three=dict(
                    _preset=True,
                    arg_four=dict(
                        _default=1,
                        _preset=True,
                        _type="int"
                    )
                )
            )
        ),
    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()
    if tmp_args.arg_one.arg_two._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three.arg_four._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three.arg_four._value != 1: err()

    tmp_dy_args=dict(
        arg_one=dict(
            _preset=True,
            arg_two=dict(
                _preset=True,
                arg_three=dict(
                    _preset=False,
                    arg_four=dict(
                        _preset=True
                    )
                )
            )
        ),
    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()
    if tmp_args.arg_one.arg_two._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three._here is True: err()
    if tmp_args.arg_one.arg_two.arg_three.arg_four._here is True: err()

    tmp_dy_args=dict(
        arg_one=dict(
            _required=True,
            arg_two=dict(
                _preset=True,
                arg_three=dict(
                    _preset=False,
                    arg_four=dict(
                        _preset=True
                    )
                )
            )
        ),
    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()
    if tmp_args.arg_one.arg_two._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three._here is True: err()
    if tmp_args.arg_one.arg_two.arg_three.arg_four._here is True: err()

    tmp_dy_args=dict(
        arg_one=dict(
            _allow_siblings=False,
            _preset=True,
        ),
        arg_two=dict(),

    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()

    tmp_args=tmp_nargs.get_args("--args --arg-two")
    if tmp_args.arg_one._here is True: err()
    print(tmp_args.arg_one._here)

    tmp_dy_args=dict(
        arg_one=dict(
            _allow_siblings=False,
            _preset=True,
        ),
        arg_two=dict(),
    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()

    tmp_args=tmp_nargs.get_args("--args --arg-two")
    if tmp_args.arg_one._here is True: err()
    if tmp_args.arg_two._here is False: err()

    with CatchEx(EndUserError) as c:
        c.text="argument '--arg-two' can't be added because it already has a sibling argument with property 'allow_siblings' set to 'False'"
        tmp_nargs.get_args("--args --arg-one --arg-two")

    args=nargs.get_args("--args --arg-nine --n-arg value")
    if not (len(args.arg_nine.n_arg._values) == 1): err()


    tmp_dy_args=dict(
        arg_one=dict(
            _preset=True,
        ),
        arg_two=dict(),
        arg_three=dict(),
    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()
    if tmp_args.arg_two._here is True: err()
    if tmp_args.arg_three._here is True: err()

    tmp_args=tmp_nargs.get_args("--args --arg-three")
    if tmp_args.arg_one._here is True: err()
    if tmp_args.arg_two._here is True: err()
    if tmp_args.arg_three._here is False: err()

    tmp_dy_args=dict(
        arg_one=dict(
            _preset=True,
            arg_two=dict(
                _preset=True,
                arg_three=dict(
                    _preset=True,
                )
            )
        ),
        arg_two=dict(
            arg_one=dict(
                _preset=True,
            )
        ),
        arg_three=dict(),
    )
    tmp_nargs=Nargs(args=tmp_dy_args, metadata=dy_metadata, raise_exc=True, builtins=dict())
    tmp_args=tmp_nargs.get_args("--args")
    if tmp_args.arg_one._here is False: err()
    if tmp_args.arg_one.arg_two._here is False: err()
    if tmp_args.arg_one.arg_two.arg_three._here is False: err()
    if tmp_args.arg_two._here is True: err()
    if tmp_args.arg_two.arg_one._here is True: err()
    if tmp_args.arg_three._here is True: err()

    args="""
        arg:
            _values: "*"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    with CatchEx(EndUserError) as c:
        c.text="There is no closing quotation for command-line"
        args=nargs.get_args("args arg=val1'")

    args="""
        arg:
            _values: "*"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    with CatchEx(EndUserError) as c:
        c.text="There is no closing quotation for value(s)"
        args=nargs.get_args("args arg=\"val1'\"")

    args=dict(
        with_deps=dict(
            other=dict()
        ),
    )
    nargs=Nargs(args=args, metadata=dy_metadata, raise_exc=True)
    args=nargs.get_args("--args --with-deps ?f=-1 -d=-1 --other +")


    args=dict(
        with_deps=dict(
            other=dict(
                _required=True,
                _type="str"
            )
        ),
    )
    with CatchEx(EndUserError) as c:
        c.text="at least one child argument is needed"
        Nargs(args=args, metadata=dy_metadata, raise_exc=True).get_args("--args")

    with CatchEx(EndUserError) as c:
        c.text="required argument '--other' is missing"
        Nargs(args=args, metadata=dy_metadata, raise_exc=True).get_args("--args --with-deps")

    with CatchEx(EndUserError) as c:
        c.text="needs at least one value"
        Nargs(args=args, metadata=dy_metadata, raise_exc=True).get_args("--args --with-deps --other")

    args=dict(
        with_deps=dict(
            _required=True,
            _type="str"
        ),
    )
    with CatchEx(EndUserError) as c:
        c.text="required argument '--with-deps' is missing"
        Nargs(args=args, metadata=dy_metadata, raise_exc=True).get_args("--args")

    with CatchEx(EndUserError) as c:
        c.text="needs at least one value"
        Nargs(args=args, metadata=dy_metadata, raise_exc=True).get_args("--args --with-deps")