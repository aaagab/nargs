#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import tempfile
import traceback

from ..dev.nargs import Nargs
from ..dev.exceptions import EndUserError
from ..gpkgs import message as msg
from .helpers import CatchEx, err

def test_get_args(
    dy_metadata,
    filenpa_cache,
):
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
    args=nargs.get_args("--args --arg-one --args+ --arg-one")

    for branch in args._branches:
        if branch.arg_one._here is False: err()

        pprint(vars(branch.arg_one))
        if branch.arg_one.narg_one._here is True: err()

    args=nargs.get_args("--args --arg-one --args+ --arg-one --arg-one+")
    if args.arg_one._count != 1: err()

    args=nargs.get_args("--args --arg-two")
    if args._branches[0].arg_two._here is False: err()

    if args._branches[0].arg_two._count != 1: err()

    args=nargs.get_args("--args --arg-two --args+ --arg-two --arg-two")
    if args._branches[1].arg_two._here is False: err()

    if args._branches[1].arg_two._count != 2: err()


    args=nargs.get_args("--args --arg-two --args+ --arg-two --args+ --arg-two")
    args=nargs.get_args("--args --arg-two --arg-two --arg-two")
    if args.arg_two._count != 3: err()

    try:
        args=nargs.get_args("--args --arg-two --arg-two --usage --arg-two")
    except:
        pass

    args=nargs.get_args("--args --arg-two+  --arg-two+ --arg-two+ --arg-two+1=marc --arg-two+2=tom --arg-two+3=john")
    if args.arg_two._branches[0]._value != "marc": err()
    if args.arg_two._branches[1]._value != "tom": err()
    if args.arg_two._branches[2]._value != "john": err()

    args=nargs.get_args("--args --arg-three+  --arg-three+ --arg-three+ --arg-three+1=marc --arg-three+2=tom --arg-three+3=john --arg-three+2=harry")
    if args.arg_three._branches[1]._value != "harry": err()

    nargs=Nargs(
        options_file="assets/settings-2.yaml",
        cache_file=filenpa_cache,
        metadata=dy_metadata,
        raise_exc=True,
    )

    args=nargs.get_args("--args+=barry  --args+ --args+ --args+1=marc --args+2=tom --args+3=john --args+2=harry")
    if args._branches[1]._value != "harry": err()

    args=nargs.get_args("@a=tom")
    if args._value != "tom": err()

    args=nargs.get_args("@a@b")
    if args.arg_one._here is False: err()

    print(
        args.arg_one._here,
        args._cmd_._here,
        args._help_._here,
        args._help_.export.overwrite._here,
        args._help_.export.to._here,
        args._help_.metadata.json._here,
        args._help_.metadata.keys._here,
        args._help_.metadata.values._here,
        args._help_.syntax._here,
        args._usage_.depth._here,
        args._usage_.examples._here,
        args._usage_.flags._here,
        args._usage_.from_._here,
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
        c.text="unknown argument '--arg-unknown'"
        nargs.get_args("--args --arg-one --arg-unknown")

    with CatchEx(EndUserError) as c:
        c.text="unknown argument '--arg-unknown'"
        nargs.get_args("--args --arg-two --arg-unknown")

    with CatchEx(EndUserError) as c:
        c.text="unknown argument '<tag>'"
        nargs.get_args("--args + <tag>")

    with CatchEx(EndUserError) as c:
        c.text="unknown input '<tag>'"
        nargs.get_args("--args --arg-one <tag>")

    with CatchEx(EndUserError) as c:
        c.text="'--cmd' can't be provided more than once."
        nargs.get_args("--args --cmd tests/assets/cmd.txt")

    with CatchEx(EndUserError) as c:
        c.text="metadata key 'unknown-key' not found"
        nargs.get_args("--args --help --metadata unknown-key")

    with CatchEx(EndUserError) as c:
        c.text="from LEVEL '-2' must be greater or equal than '-1'"
        nargs.get_args("--args --usage --from=-2")

    with CatchEx(EndUserError) as c:
        c.text="depth LEVEL '-2' must be greater or equal than '-1'"
        nargs.get_args("--args @u@d=-2")

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
        nargs.get_args("--args@v")

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
        args=nargs.get_args("--args --arg-four --arg-four+ --nested-arg1")

    with CatchEx(EndUserError) as c:
        c.text="'--arg-four' can't be forked"
        args=nargs.get_args("--args --arg-four --nested-arg1 --arg-four+")

    args=nargs.get_args("--args --arg-four --nested-arg2 --arg-four+")
    if not (args.arg_four.nested_arg2._here is True): err()
    if not (args.arg_four._branches[1].nested_arg2._here is False): err()
    args=nargs.get_args("--args --arg-four --arg-four+ --nested-arg2 --arg-four+")
    
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
        c.text="Biggest branch number available is '+1'"
        args=nargs.get_args("--args --arg-two+2")

    with CatchEx(EndUserError) as c:
        c.text="Biggest branch number available is '+3'"
        args=nargs.get_args("--args --arg-four --arg-four+ --arg-four+4")

    with CatchEx(EndUserError) as c:
        c.text="can't be forked because its child argument '--nested-arg1'"
        args=nargs.get_args("--args --arg-four --nested-arg1 --arg-four+")

    with CatchEx(EndUserError) as c:
        c.text="A new branch can't be created for argument '--arg-one'"
        args=nargs.get_args("--args --arg-one+ --arg-one+")

    with CatchEx(EndUserError) as c:
        c.text="wrong branch number '+2'. Only '+1' is authorized"
        args=nargs.get_args("--args --arg-one+ --arg-one+2")

    with CatchEx(EndUserError) as c:
        c.text="can't be repeated because its 'repeat' property is set to 'error'"
        args=nargs.get_args("--args --arg-three --arg-three")

    with CatchEx(EndUserError) as c:
        c.text="'--arg-five' is present multiple times in argument's implicit aliases"
        args=nargs.get_args("--args --arg-five --n-arg1 --nn-arg1 --arg-five")

    args=nargs.get_args("--args --arg-five --n-arg1 --nn-arg1 - --arg-five")
    if not (args.arg_five._count == 1): err()

    if not (args.arg_five.n_arg1._count == 2): err()

    args=nargs.get_args("--args --arg-five --n-arg1 --nn-arg1 -- --arg-five")
    if not (args.arg_five._count == 2): err()

    if not (args.arg_five.n_arg1._count == 1): err()

    with CatchEx(EndUserError) as c:
        c.text="'--arg-six' is present multiple times in argument's explicit aliases and implicit"
        args=nargs.get_args("--args --arg-six --n-arg1 --nn-arg1 --arg-six")

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
        c.text="Unknown char(s) ['p'] in flag set"
        args=nargs.get_args("--args@ap")

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
        c.text="'--args --arg-nine': required argument '--n-arg' is missing"
        args=nargs.get_args("--args --arg-nine")

    args=nargs.get_args("--args --arg-nine --n-arg value")
    if not (len(args.arg_nine.n_arg._values) == 1): err()
