#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import traceback

from ..dev.nargs import Nargs
from ..dev import nargs

from ..gpkgs import message as msg

def run_tests(
    dy_metadata,

):
    nargs.debug=True
    narg=Nargs(options_file="empty.yaml", metadata=dy_metadata)

    try:
        narg.get_args("--args -v")
    except:
        pass

    narg=Nargs(options_file="empty.json", metadata=dy_metadata)
    try:
        args=narg.get_args("--args -v")
    except:
        pass

    narg=Nargs(options_file="empty.json", metadata=dy_metadata, builtins=[])
    args=narg.get_args("--args")
    if args is not None:
        msg.error("Error args is not None", exit=1, trace=True)


    narg=Nargs(options_file="empty.json", metadata=dy_metadata, builtins=[], cache_file="nargs-cache.pickle")
    args=narg.get_args("--args")
    if args is not None:
        msg.error("Error args is not None", exit=1, trace=True)

    narg=Nargs(args=dict(_enabled=False), options_file="empty.json", metadata=dy_metadata, builtins=[], cache_file="nargs-cache.pickle")
    args=narg.get_args("--args")
    print(args)
    if args is not None:
        msg.error("Error args is not None", exit=1, trace=True)

    narg=Nargs(
        options_file="settings.yaml",
        cache_file="nargs-cache.pickle",
        metadata=dy_metadata,
    )
    args=narg.get_args("--args --arg-one")
    pprint(vars(args.arg_one))
    print(args.arg_one._get_cmd_line())
    args=narg.get_args("--args --arg-one")
    args=narg.get_args("--args --arg-one --args_ --arg-one")

    for branch in args._branches:
        if branch.arg_one._here is False:
            msg.error("Error arg_one is False", exit=1, trace=True)

        pprint(vars(branch.arg_one))
        if branch.arg_one.narg_one._here is True:
            msg.error("Error arg_one._narg_one is True", exit=1, trace=True)

    args=narg.get_args("--args --arg-one --args_ --arg-one --arg-one_")
    if args.arg_one._count != 1:
        msg.error("Error arg_one._count '{}' should be '1'".format(args.arg_one._count), exit=1, trace=True)

    args=narg.get_args("--args --arg-two")
    if args._branches[0].arg_two._here is False:
        msg.error("error args._branches[0].arg_two._here is False", exit=1, trace=True)

    if args._branches[0].arg_two._count != 1:
        msg.error("error args._branches[0].arg_two._here is False", exit=1, trace=True)

    args=narg.get_args("--args --arg-two --args_ --arg-two --arg-two")
    if args._branches[1].arg_two._here is False:
        msg.error("error args._branches[1].arg_two._here is False", exit=1, trace=True)

    if args._branches[1].arg_two._count != 2:
        msg.error("Error args._branches[1].arg_two._count != 2".format(args._branches[1].arg_two._count), exit=1, trace=True)


    args=narg.get_args("--args --arg-two --args_ --arg-two --args_ --arg-two")
    args=narg.get_args("--args --arg-two --arg-two --arg-two")
    if args.arg_two._count != 3:
        msg.error("args.arg_two._count != 3", exit=1, trace=True)

    try:
        args=narg.get_args("--args --arg-two --arg-two --usage --arg-two")
    except:
        pass

    args=narg.get_args("--args --arg-two_  --arg-two_ --arg-two_ --arg-two_1=marc --arg-two_2=tom --arg-two_3=john")
    if args.arg_two._branches[0]._value != "marc":
        msg.error("args.arg_two._branches[0]._value != \"marc\"", exit=1, trace=True)
    if args.arg_two._branches[1]._value != "tom":
        msg.error("args.arg_two._branches[1]._value != \"tom\"", exit=1, trace=True)
    if args.arg_two._branches[2]._value != "john":
        msg.error("args.arg_two._branches[2]._value != \"john\"", exit=1, trace=True)

    args=narg.get_args("--args --arg-three_  --arg-three_ --arg-three_ --arg-three_1=marc --arg-three_2=tom --arg-three_3=john --arg-three_2=harry")
    if args.arg_three._branches[1]._value != "harry":
        msg.error('args.arg_three._branches[1]._value != "harry"', exit=1, trace=True)

    narg=Nargs(
        options_file="settings-2.yaml",
        cache_file="nargs-cache.pickle",
        metadata=dy_metadata,
    )

    args=narg.get_args("--args_=barry  --args_ --args_ --args_1=marc --args_2=tom --args_3=john --args_2=harry")
    if args._branches[1]._value != "harry":
        msg.error('args._branches[1]._value != "harry"', exit=1, trace=True)

    args=narg.get_args("@a=tom")
    if args._value != "tom":
        msg.error('args._value != "tom"', exit=1, trace=True)

    args=narg.get_args("@ab")
    if args.arg_one._here is False:
        msg.error('args.arg_one._here is False', exit=1, trace=True)

    # narg.get_args("@a?@d=-1")
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


    try:
        narg.get_args("")
    except Exception as e:
        text="command must have at least the root argument set"
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args -")
    except Exception as e:
        text="command must finish with an argument or a value not an explicit notation '-'"
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args +++ --arg-one")
    except Exception as e:
        text="explicit level '+++' out of bound"
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args - --arg-unknown")
    except Exception as e:
        text="unknown argument '--arg-unknown'"
        if text not in str(e):
            raise Exception(e)
    
    try:
        narg.get_args("--args --arg-one --arg-unknown")
    except Exception as e:
        text="unknown argument '--arg-unknown'"
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args --arg-two --arg-unknown")
    except Exception as e:
        text="unknown argument '--arg-unknown'"
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args - <tag>")
    except Exception as e:
        text="unknown argument '<tag>'"
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args --arg-one <tag>")
    except Exception as e:
        text="unknown input '<tag>'"
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args --cmd tests/cmd.txt")
    except Exception as e:
        text="'--cmd' can't be provided more than once."
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args --help --metadata unknown-key")
    except Exception as e:
        text="metadata key 'unknown-key' not found"
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args --usage --from=-2")
    except Exception as e:
        text="from LEVEL '-2' must be greater or equal than '-1'"
        if text not in str(e):
            raise Exception(e)

    try:
        narg.get_args("--args @u@d=-2")
    except Exception as e:
        text="depth LEVEL '-2' must be greater or equal than '-1'"
        if text not in str(e):
            raise Exception(e)

    version=dy_metadata["version"]
    del dy_metadata["version"]
    narg=Nargs(
        options_file="settings-2.yaml",
        cache_file="nargs-cache.pickle",
        metadata=dy_metadata,
    )

    try:
        narg.get_args("--args@v")
    except Exception as e:
        text="version not provided"
        if text not in str(e):
            raise Exception(e)

    narg=Nargs(
        options_file="settings-3.yaml",
        metadata=dy_metadata,
    )

    try:
        narg.get_args("--args --arg-one --arg-three")
    except Exception as e:
        text="the two following arguments can't be provided"
        if text not in str(e):
            raise Exception(e)

    narg=Nargs(
        options_file="settings-3.yaml",
        metadata=dy_metadata,
    )

    try:
        narg.get_args("--args --arg-two --arg-three")
    except Exception as e:
        text="the two following arguments can't be provided at the same time"
        if text not in str(e):
            raise Exception(e)

    args=narg.get_args("--args --arg-one --arg-two")

    if not (args.arg_one._here is True and args.arg_two._here is True):
        msg.error('not (args.arg_one._here is True and args.arg_two._here is True)', exit=1, trace=True)

    args=narg.get_args("--args --arg-four --nested-arg1")

    try:
        args=narg.get_args("--args --arg-four --arg-four_ --nested-arg1")
    except Exception as e:
        text="'allow_parent_fork' is set to 'False' but parent argument has more than one branch"
        if text not in str(e):
            raise Exception(e)

    try:
        args=narg.get_args("--args --arg-four --nested-arg1 --arg-four_")
    except Exception as e:
        text="'--arg-four' can't be forked"
        if text not in str(e):
            raise Exception(e)

    args=narg.get_args("--args --arg-four --nested-arg2 --arg-four_")
    if not (args.arg_four.nested_arg2._here is True):
        msg.error('not (args.arg_four.nested_arg2._here is True)', exit=1, trace=True)
    if not (args.arg_four._branches[1].nested_arg2._here is False):
        msg.error('not (args.arg_four._branches[1].nested_arg2._here is True)', exit=1, trace=True)
    args=narg.get_args("--args --arg-four --arg-four_ --nested-arg2 --arg-four_")
    
    args=narg.get_args("--args --arg-two --nested-arg2")
    args=narg.get_args("--args --arg-two --nested-arg1")
    args=narg.get_args("--args --arg-two --nested-arg2 --arg-four --nested-arg1")

    if not (args.arg_two.nested_arg2._here is True):
        msg.error('not (args.arg_two.nested_arg2._here is True)', exit=1, trace=True)
    if not (args.arg_four.nested_arg1._here is True):
        msg.error('not (args.arg_four.nested_arg1._here is True)', exit=1, trace=True)

    try:
        args=narg.get_args("--args --arg-two --nested-arg2 --nested-arg1")
    except Exception as e:
        text="already has a sibling argument"
        if text not in str(e):
            raise Exception(e)

    try:
        args=narg.get_args("--args --arg-two --nested-arg1 --nested-arg2")
    except Exception as e:
        text="at least one sibling is present"
        if text not in str(e):
            raise Exception(e)

    try:
        args=narg.get_args("--args --arg-two --nested-arg3")
    except Exception as e:
        text="needs at least one value"
        if text not in str(e):
            raise Exception(e)

    args=narg.get_args("--args --arg-two --nested-arg3 test-value")
    
    if not (args.arg_two.nested_arg3._value == "test-value"):
        msg.error('args.arg_two.nested_arg3._value == "test-value"', exit=1, trace=True)

    if not (args.arg_two.nested_arg3._values[0] == "test-value"):
        msg.error('args.arg_two.nested_arg3._values[0] == "test-value"', exit=1, trace=True)

    try:
        args=narg.get_args("--args --arg-two --nested-arg4 value1")
    except Exception as e:
        text="minimum values '1' is less than '2'."
        if text not in str(e):
            raise Exception(e)

    args=narg.get_args("--args --arg-two --nested-arg4 value1 value2")
    if not (args.arg_two.nested_arg4._values[1] == "value2"):
        msg.error('args.arg_two.nested_arg4._values[1] == "value2"', exit=1, trace=True)

    try:
        args=narg.get_args("--args --arg-two --nested-arg4 value1 value2 value3")
    except Exception as e:
        text="Maximum number of values '2' has been reached already."
        if text not in str(e):
            raise Exception(e)

    try:
        args=narg.get_args("--args --arg-two --nested-arg1 value1")
    except Exception as e:
        text="type error. It must match type '<class 'int'>'"
        if text not in str(e):
            raise Exception(e)