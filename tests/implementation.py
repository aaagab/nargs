#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys
import traceback
import time
import tempfile
import yaml

from ..dev.nargs import Nargs
from ..dev.exceptions import EndUserError, DeveloperError
from .helpers import CatchEx, err, Elapsed

from ..gpkgs import message as msg

def test_implementation(
    dy_metadata,
    filenpa_cache_json,
    filenpa_cache_pickle,
    filenpa_tmp_query,
    manual=False,
):
    elapsed=Elapsed()
    direpa_script=os.path.dirname(os.path.realpath(__file__))

    nargs=Nargs(metadata=dy_metadata, args=None, builtins=dict(), cache=False, raise_exc=True)
    if nargs.dfn is not None: err()

    nargs=Nargs(metadata=dy_metadata, args=dict(), builtins=dict(), cache=False, raise_exc=True)
    if len(nargs.dfn.dy_nodes) != 0: err()

    nargs=Nargs(metadata=dy_metadata, args=dict(), builtins=dict(usage=None), cache=False, raise_exc=True)
    if len(nargs.dfn.dy_nodes) != 1: err()

    if nargs.dfn.nodes[0].name != "_usage_": err()

    for prefix in ["", "+", "-", "--", "/", ":", "_"]:
        nargs=Nargs(auto_alias_prefix=prefix, metadata=dy_metadata, args=dict(arg_one=dict()), builtins=dict(usage=None), cache=False, raise_exc=True)

        alias=nargs.dfn.dy_nodes["arg_one"].dy["default_alias"]
        if alias != '{}arg-one'.format(prefix): err()
        
        alias=nargs.dfn.dy_nodes["_usage_"].dy["default_alias"]
        if alias != '{}usage'.format(prefix): err()

        if prefix == "--":
            if "-u" not in nargs.dfn.dy_nodes["_usage_"].dy["aliases"]: err()

        args=nargs.get_args("{}args {}arg-one".format(prefix, prefix))
        if args.arg_one._here is False: err()

    for alias_style in ["camelcase", "camelcase-hyphen", "lowercase", "lowercase-hyphen", "pascalcase", "pascalcase-hyphen", "uppercase", "uppercase-hyphen",]:
        nargs=Nargs(auto_alias_style=alias_style, metadata=dy_metadata, args=dict(arg_one=dict()), builtins=dict(usage=None), cache=False, raise_exc=True)
        alias=nargs.dfn.dy_nodes["arg_one"].dy["default_alias"]
        tmp_alias=None
        if alias_style == "camelcase":
            tmp_alias="--argOne"
        elif alias_style == "camelcase-hyphen":
            tmp_alias="--arg-One"
        elif alias_style == "lowercase":
            tmp_alias="--argone"
        elif alias_style == "lowercase-hyphen":
            tmp_alias="--arg-one"
        elif alias_style == "pascalcase":
            tmp_alias="--ArgOne"
        elif alias_style == "pascalcase-hyphen":
            tmp_alias="--Arg-One"
        elif alias_style == "uppercase":
            tmp_alias="--ARGONE"
        elif alias_style == "uppercase-hyphen":
            tmp_alias="--ARG-ONE"
        if tmp_alias != alias: err()

    nargs=Nargs(metadata=dy_metadata, builtins=dict(usage="/u, /usage, /?", version="/v,/version"), cache=False, raise_exc=True)

    aliases=nargs.dfn.dy_nodes["_usage_"].dy["aliases"]
    for alias in "/u,/usage,/?".split(","):
        if alias not in aliases: err()

    aliases=nargs.dfn.dy_nodes["_version_"].dy["aliases"]
    for alias in "/v,/version".split(","):
        if alias not in aliases: err()

    nargs=Nargs(metadata=dy_metadata, builtins=dict(
        help="+help",
        path_etc="+path-etc",
        query="+query",
        usage="+usage", 
        version="+version",
    ), cache=False, path_etc="/tmp", raise_exc=True)

    for alias in ["+help", "+path-etc", "+query", "+usage", "+version"]:
        if alias not in nargs.dfn.explicit_aliases: err()
        

    filenpa_options=os.path.join(direpa_script, "assets/settings-3.yaml")
    try:
        os.remove(filenpa_cache_json)
    except:
        pass
    elapsed.start()
    nargs=Nargs(metadata=dy_metadata, cache_file=filenpa_cache_json, options_file=filenpa_options, raise_exc=True)
    print("cached {:<5}: {}".format(str(nargs._from_cache), elapsed.show()))
    elapsed.start()
    nargs=Nargs(metadata=dy_metadata, cache_file=filenpa_cache_json, options_file=filenpa_options, raise_exc=True)
    print("cached {:<5}: {}".format(str(nargs._from_cache), elapsed.show()))
    elapsed.start()
    nargs=Nargs(metadata=dy_metadata, cache_file=filenpa_cache_json, options_file=filenpa_options, only_cache=True, raise_exc=True)
    print("cached {:<5}: {}".format(str(nargs._from_cache), elapsed.show()))

    args=nargs.get_args("--args --arg-six --n-arg1 --nn-arg1 --nnn-arg1")
    if args.arg_six.n_arg1.nn_arg1.nnn_arg1._here is False: err()

    try:
        os.remove(filenpa_cache_pickle)
    except:
        pass
    elapsed.start()
    nargs=Nargs(metadata=dy_metadata, cache_file=filenpa_cache_pickle, options_file=filenpa_options, raise_exc=True)
    print("cached {:<5}: {}".format(str(nargs._from_cache), elapsed.show()))
    elapsed.start()
    nargs=Nargs(metadata=dy_metadata, cache_file=filenpa_cache_pickle, options_file=filenpa_options, raise_exc=True)
    print("cached {:<5}: {}".format(str(nargs._from_cache), elapsed.show()))
    elapsed.start()
    nargs=Nargs(metadata=dy_metadata, cache_file=filenpa_cache_pickle, options_file=filenpa_options, only_cache=True, raise_exc=True)
    print("cached {:<5}: {}".format(str(nargs._from_cache), elapsed.show()))

    args=nargs.get_args("--args --arg-six --n-arg1 --nn-arg1 --nnn-arg1")
    if args.arg_six.n_arg1.nn_arg1.nnn_arg1._here is False: err()



    nargs=Nargs(metadata=dict(name="My prog", executable="prog"), args=dict(), builtins=dict(usage=None), cache=False, raise_exc=True)

    dy_files=dict(
        user_json=os.path.join(direpa_script, ".nargs-user.json"),
        user_yaml=os.path.join(direpa_script, ".nargs-user.yaml"),
        user_etc_json=os.path.join(tempfile.gettempdir(), ".nargs-user.json"),
        user_etc_yaml=os.path.join(tempfile.gettempdir(), ".nargs-user.yaml"),
        options_json=os.path.join(direpa_script, "tmp-options.json"),
        options_yaml=os.path.join(direpa_script, "tmp-options.yaml"),
    )

    def set_file(filenpa, dy):
        with open(filenpa, "w") as f:
            f.write(json.dumps(dy, indent=4, sort_keys=True))

    def reset_files(dy_files):
        for name, filenpa in dy_files.items():            
            try:
                os.remove(filenpa)
            except:
                pass

    reset_files(dy_files)
    nargs=Nargs(metadata=dy_metadata, args=dict(), cache=False, raise_exc=True, pretty_help=False)
    if nargs._pretty_help is True: err()

    set_file(dy_files["options_json"], dict(pretty_help=True))
    nargs=Nargs(metadata=dy_metadata, args=dict(), options_file=dy_files["options_json"], cache=False, raise_exc=True, pretty_help=False)
    if nargs._pretty_help is False: err()

    set_file(dy_files["options_yaml"], dict(pretty_help=True))
    nargs=Nargs(metadata=dy_metadata, args=dict(), options_file=dy_files["options_yaml"], cache=False, raise_exc=True, pretty_help=False)
    if nargs._pretty_help is False: err()

    set_file(dy_files["options_json"], dict(pretty_help=False))
    set_file(dy_files["user_json"], dict(pretty_help=True))
    nargs=Nargs(metadata=dy_metadata, args=dict(), options_file=dy_files["options_json"], cache=False, raise_exc=True, pretty_help=False)
    if nargs._pretty_help is False: err()
    
    set_file(dy_files["options_json"], dict(pretty_help=False))
    set_file(dy_files["user_json"], dict(pretty_help=False))
    set_file(dy_files["user_yaml"], dict(pretty_help=True))
    nargs=Nargs(metadata=dy_metadata, args=dict(), options_file=dy_files["options_json"], cache=False, raise_exc=True, pretty_help=False)
    if nargs._pretty_help is False: err()
    
    set_file(dy_files["options_json"], dict(pretty_help=False))
    set_file(dy_files["user_json"], dict(pretty_help=False))
    set_file(dy_files["user_yaml"], dict(pretty_help=False))
    set_file(dy_files["user_etc_json"], dict(pretty_help=True))
    nargs=Nargs(metadata=dy_metadata, args=dict(), options_file=dy_files["options_json"], cache=False, path_etc=tempfile.gettempdir(), raise_exc=True, pretty_help=False)
    if nargs._pretty_help is False: err()

    set_file(dy_files["options_json"], dict(pretty_help=False))
    set_file(dy_files["user_json"], dict(pretty_help=False))
    set_file(dy_files["user_yaml"], dict(pretty_help=False))
    set_file(dy_files["user_etc_json"], dict(pretty_help=False))
    set_file(dy_files["user_etc_yaml"], dict(pretty_help=True))
    nargs=Nargs(metadata=dy_metadata, args=dict(), options_file=dy_files["options_json"], cache=False, path_etc=tempfile.gettempdir(), raise_exc=True, pretty_help=False)
    if nargs._pretty_help is False: err()

    reset_files(dy_files)

    nargs=Nargs(metadata=dy_metadata, args=dict(), builtins=dict(path_etc=None), path_etc=tempfile.gettempdir(), cache=False, raise_exc=True)

    if nargs._path_etc != tempfile.gettempdir(): err()

    try:
        print("testing pretty_help: True")
        nargs=Nargs(metadata=dy_metadata, args=dict(), builtins=dict(usage=None), cache=False, raise_exc=False)
        nargs.get_args("--args ?")
    except:
        pass
    
    try:
        print("testing pretty_help: False")
        nargs=Nargs(metadata=dy_metadata, args=dict(), builtins=dict(usage=None), cache=False, pretty_help=False, raise_exc=False)
        nargs.get_args("--args ?")
    except:
        pass    

    try:
        print("testing pretty_msg: True")
        nargs=Nargs(metadata=1, args=dict(), builtins=dict(path_etc=None), path_etc=tempfile.gettempdir(), cache=False, raise_exc=False)
    except:
        pass
    
    try:
        print("testing pretty_msg: False")
        nargs=Nargs(metadata=1, args=dict(), builtins=dict(path_etc=None), path_etc=tempfile.gettempdir(), cache=False, pretty_msg=False, raise_exc=False)
    except:
        pass

    try:
        print("testing raise_exc: True")
        nargs=Nargs(metadata=1, args=dict(), builtins=dict(), cache=False, raise_exc=True)
    except DeveloperError as e:
        print(e)
        pass
    
    try:
        print("testing raise_exc: False")
        nargs=Nargs(metadata=1, args=dict(), builtins=dict(), cache=False, raise_exc=False)
    except:
        pass

    nargs=Nargs(metadata=dy_metadata, args=dict(_values="+"), builtins=dict(), cache=False, raise_exc=False, substitute=True)

    os.environ["one"]="apple"
    os.environ["two"]="pear"
    os.environ["three"]="orange"
    args=nargs.get_args("--args __one__ __two__ __three__")
    if " ".join(args._cmd_line) != "--args apple pear orange": err()

    if manual is True:
        args=nargs.get_args("--args __input__")
        print(" ".join(args._cmd_line))
        args=nargs.get_args("--args __hidden__")
        print(" ".join(args._cmd_line))
        args=nargs.get_args("--args __hidden:password__")
        print(" ".join(args._cmd_line))


    for output in [
        "asciidoc",
        "cmd_help",
        "cmd_usage",
        "markdown",
        "html",
        "text",
    ]:
        print("# EXPORT DOCUMENTATION:", output)
        print(nargs.get_documentation(output=output))


    filenpa_documentation=os.path.join(direpa_script, "documentation.txt")
    for output in [
        "asciidoc",
        "cmd_help",
        "cmd_usage",
        "markdown",
        "html",
        "text",
    ]:
        nargs.get_documentation(output=output, filenpa=filenpa_documentation, wsyntax=True, overwrite=True)
    os.remove(filenpa_documentation)

    print()
    print("metadata template:")
    pprint(nargs.get_metadata_template())

    print()
    print("default theme:")
    pprint(nargs.get_default_theme())


    nargs=Nargs(metadata=dy_metadata, args=dict(_repeat="fork"), builtins=dict(), cache=False, raise_exc=False, substitute=True)

    args=nargs.get_args("--args --args --args")
    
    if len(args._branches) != 3: err()

    if args._branches.index(args) != 0: err()

    args="""
        narg:
            narg:
                narg:
                    narg:
                        narg:
                            narg:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), builtins=dict(), cache=False, raise_exc=False, substitute=True)
    args=nargs.get_args("--args --narg + --narg + --narg + --narg + --narg + --narg")

    if args.narg.narg.narg.narg.narg.narg._here is False: err()


    args="""
        narg:
            narg:
                narg:
                    arg1:
                    arg2:
                    arg3:
                    arg4:
                    arg5:
                    arg6:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), builtins=dict(), cache=False, raise_exc=False, substitute=True)

    dy_args=nargs.dfn.dy_nodes["narg"].dy_nodes["narg"].dy_nodes["narg"].current_arg._
    for i in range(6):
        name="arg{}".format(i+1)
        if name not in dy_args: err()

    args="""
        _aliases: "--arg-1,--arg-2,--arg-3"
        _repeat: fork
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), builtins=dict(), cache=False, raise_exc=False, substitute=True)

    args=nargs.get_args("--arg-1 --arg-2 --arg-3")
    index=1
    for branch in args._branches:
        alias="--arg-{}".format(index)
        if alias != branch._alias: err()

        for i in range(3): 
            tmp_alias="--arg-{}".format(i+1)
            if tmp_alias not in branch._aliases: err()
        index+=1

    args="""
        _repeat: fork
        arg1:
            _repeat: append
        arg2:
            _repeat: replace
        arg3:
        arg4:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False, substitute=True)

    args=nargs.get_args("args arg4 arg3 arg2 arg1 args arg3 arg2 arg1 arg4 args arg1 arg2 arg3 arg2 arg1")

    for arg in args._branches[0]._args:
        if arg._alias == "arg1":
            if args._branches[0]._args.index(arg) != 3: err()
        elif arg._alias == "arg2":
            if args._branches[0]._args.index(arg) != 2: err()
        elif arg._alias == "arg3":
            if args._branches[0]._args.index(arg) != 1: err()
        elif arg._alias == "arg4":
            if args._branches[0]._args.index(arg) != 0: err()
            
    for arg in args._branches[1]._args:
        if arg._alias == "arg1":
            if args._branches[1]._args.index(arg) != 2: err()
        elif arg._alias == "arg2":
            if args._branches[1]._args.index(arg) != 1: err()
        elif arg._alias == "arg3":
            if args._branches[1]._args.index(arg) != 0: err()
        elif arg._alias == "arg4":
            if args._branches[1]._args.index(arg) != 3: err()

    for arg in args._branches[2]._args:
        if arg._alias == "arg1":
            if args._branches[2]._args.index(arg) != 2: err()
        elif arg._alias == "arg2":
            if args._branches[2]._args.index(arg) != 1: err()
        elif arg._alias == "arg3":
            if args._branches[2]._args.index(arg) != 0: err()

    if len(args._branches[2]._args) != 3: err()

    if "arg4" in [arg._alias for arg in args._branches[2]._args]: err()

    args=nargs.get_args("args arg4 arg3 arg2 arg1 args arg3 arg2 arg1 arg4 args arg1 arg2 arg3 arg2 arg1")

    for arg in args._branches[0]._args:
        if arg._alias == "arg1":
            if args._branches[0]._args.index(arg) != 3: err()
        elif arg._alias == "arg2":
            if args._branches[0]._args.index(arg) != 2: err()
        elif arg._alias == "arg3":
            if args._branches[0]._args.index(arg) != 1: err()
        elif arg._alias == "arg4":
            if args._branches[0]._args.index(arg) != 0: err()
            
    for arg in args._branches[1]._args:
        if arg._alias == "arg1":
            if args._branches[1]._args.index(arg) != 2: err()
        elif arg._alias == "arg2":
            if args._branches[1]._args.index(arg) != 1: err()
        elif arg._alias == "arg3":
            if args._branches[1]._args.index(arg) != 0: err()
        elif arg._alias == "arg4":
            if args._branches[1]._args.index(arg) != 3: err()

    for arg in args._branches[2]._args:
        if arg._alias == "arg1":
            if args._branches[2]._args.index(arg) != 2: err()
        elif arg._alias == "arg2":
            if args._branches[2]._args.index(arg) != 1: err()
        elif arg._alias == "arg3":
            if args._branches[2]._args.index(arg) != 0: err()

    if len(args._branches[2]._args) != 3: err()

    if "arg4" in [arg._alias for arg in args._branches[2]._args]: err()

    args="""
        _need_child: false
        arg1:
            _repeat: fork
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False, substitute=True)

    args=nargs.get_args("args")

    if len(args.arg1._branches) != 1: err()

    if args.arg1._here is True: err()

    if len(args._args) != 0: err()

    args="""
        _need_child: false
        arg1:
            _repeat: replace
            nested:
        arg2:
            _repeat: append
            nested:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False, substitute=True)

    args=nargs.get_args("args arg1 nested arg1 arg2 nested arg2")
    if args.arg1.nested._here is True: err()

    if args.arg1.nested._count != 0: err()

    if args.arg1._count != 1: err()

    if args.arg2.nested._here is False: err()

    if args.arg2.nested._count != 1: err()

    if args.arg2._count != 2: err()

    args="""
        _need_child: false
        arg:
            _repeat: fork
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False, substitute=True)
    args=nargs.get_args("args arg arg arg")
    if len(args._args) != 3: err()

    args="""
        _repeat: replace
        arg:
            arg:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False)

    args=nargs.get_args("args + arg + arg")
    if args._cmd_line != "args + arg + arg": err()

    args=nargs.get_args("args + arg + arg args + arg")
    if args._cmd_line != "args + arg + arg args + arg": err()

    args="""
        _repeat: append
        arg:
            arg:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False)

    args=nargs.get_args("args + arg + arg")
    if args._cmd_line != "args + arg + arg": err()

    args=nargs.get_args("args + arg + arg args + arg")
    if args._cmd_line != "args + arg + arg args + arg": err()

    args="""
        _repeat: fork
        _need_child: false
        _repeat: replace
        arg:
            arg:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False)

    args=nargs.get_args("args + arg + arg args + arg")
    if args._cmd_line != "args + arg + arg args + arg": err()

    args=nargs.get_args("args + arg + arg args + arg")
    if args._cmd_line != "args + arg + arg args + arg": err()

    args=nargs.get_args("args args args args args args args")
    if args._cmd_line != "args args args args args args args": err()

    args="""
        _repeat: fork
        _repeat: append
        arg:
            arg:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False)

    args=nargs.get_args("args + arg + arg args + arg")
    if args._cmd_line != "args + arg + arg args + arg": err()

    args=nargs.get_args("args + arg + arg args + arg")
    if args._cmd_line != "args + arg + arg args + arg": err()

    args="""
        arg1:
        arg2:
        arg3:
        arg4:
        arg5:
        arg6:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False)

    args=nargs.get_args("args arg1 arg2 arg3 arg4 arg5 arg6")
    if args._cmd_line_index != 4: err()

    if args.arg1._cmd_line_index != 9: err()

    if args.arg2._cmd_line_index != 14: err()

    if args.arg3._cmd_line_index != 19: err()
    
    if args.arg4._cmd_line_index != 24: err()
    
    if args.arg5._cmd_line_index != 29: err()
    
    if args.arg6._cmd_line_index != 34: err()

    if args._cmd_line[:args.arg6._cmd_line_index] != "args arg1 arg2 arg3 arg4 arg5 arg6": err()

    args="""
        _repeat: replace
        _aliases: args,arg1,arg2,arg3,arg4,arg5,arg6
        _values: "*"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False)

    args=nargs.get_args("args arg1 arg2 arg3 arg4 arg5 arg6")
    if len(args._dy_indexes["aliases"]) != 1: err()

    if args._cmd_line[:args._cmd_line_index] != "args arg1 arg2 arg3 arg4 arg5 arg6": err()

    args=nargs.get_args("args value1 value2 value3")
    if len(args._dy_indexes["values"]) != 3: err()

    count=1
    for index in args._dy_indexes["values"]:
        if count == 1:
            if index != 11: err()
        elif count == 2:
            if index != 18: err()
        elif count == 3:
            if index != 25: err()
        count+=1

    args="""
        _repeat: append
        _aliases: args,arg1,arg2,arg3,arg4,arg5,arg6
        _values: "*"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False)

    args=nargs.get_args("args arg1 arg2 arg3 arg4 arg5 arg6")

    count=1
    cmd_lines=[
        "args",
        "args arg1",
        "args arg1 arg2",
        "args arg1 arg2 arg3",
        "args arg1 arg2 arg3 arg4",
        "args arg1 arg2 arg3 arg4 arg5",
        "args arg1 arg2 arg3 arg4 arg5 arg6",
    ]

    if len(args._dy_indexes["aliases"]) != len(cmd_lines): err()

    count=0
    for index in sorted(args._dy_indexes["aliases"]):
        cmd_line=args._cmd_line[:index]
        if cmd_line != cmd_lines[count]: err()
        count+=1


    args="""
        arg:
            _required: true
            narg:
                _required: true
                nnarg:
                    _required: true
                    _default: "apple"
            other:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=False)
    args=nargs.get_args("args")

    if args.arg.narg.nnarg._here is False: err()

    if args.arg.narg.nnarg._value != "apple": err()

    if args.arg.other._here is True: err()

    if args._implicit is True: err()

    if args.arg._implicit is False: err()

    if args.arg.narg._implicit is False: err()

    if args.arg.narg.nnarg._implicit is False: err()

    args=nargs.get_args("args arg")

    if args._implicit is True: err()

    if args.arg._implicit is True: err()

    if args.arg.narg._implicit is False: err()

    if args.arg.narg.nnarg._implicit is False: err()
    

    args="""
        _need_child: false
        arg1:
        usage:
            _aliases: usage,?
            _is_usage: true
            _is_custom_builtin: true
    """

    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=True)
    
    for args in [
        nargs.get_args("args ?"),
        nargs.get_args("args arg1 ?"),
        nargs.get_args("args ? ?"),
    ]:
        if args.usage._here:
            if args.usage._previous_dfn is None: err()

            print("Custom help for '{}'".format(args.usage._previous_dfn.name))

    args="""
        _need_child: false
        usage:
            _allow_parent_fork: false
            _is_usage: true
            _is_custom_builtin: true
    """
    try:
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=True)
    except DeveloperError as e:
        print("Managed DeveloperError \"{}\"".format(e))

    args="""
        usage:
            _is_usage: true
            _is_custom_builtin: true
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), cache=False, raise_exc=True)
    try:
        pass
        nargs.get_args("args")
    except EndUserError as e:
        print("Managed EndUserError \"{}\"".format(e))


    args="""
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), cache=False, raise_exc=True)
    nargs.get_args("args")

    args="""
        arg1:
            narg:
        arg2:
            narg:
                nnarg:
        usage:
            _aliases: usage,?
            _is_usage: true
            _is_custom_builtin: true
        help:
            _is_custom_builtin: true
    """

    try:
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
        args=nargs.get_args("args arg1")

        if args.usage._here:
            if args.usage._previous_dfn is None: err()

        if args.help._here:
            def process_dfn(dfn):
                print(dfn.name)
                print(dfn.level)
                pprint(dfn.dy)
                for child_dfn in dfn.nodes:
                    process_dfn(child_dfn)
            process_dfn(args._dfn)
            sys.exit(0)
        
        if args.arg1._here is True:
            print("implement logic for arg1")
            if args.arg1.narg._here:
                print("implement logic for arg1 narg")

        if args.arg2._here is True:
            print("implement logic for arg2")
            if args.arg2.narg._here:
                print("implement logic for arg2 narg")
                if args.arg2.narg.nnarg._here:
                    print("implement logic for arg2 narg nnarg")

    except DeveloperError as e:
        print("Managed DeveloperError \"{}\"".format(e))
        sys.exit(1)
    except EndUserError as e:
        print("Managed EndUserError \"{}\"".format(e))
        sys.exit(1)

    args="""
        usage:
            _aliases: usage,?
            _is_usage: true
            _is_custom_builtin: true
        help:
            _is_custom_builtin: true
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("args")

    args="""
        _values: "*"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("args")

    if args._value is not None: err()

    if not isinstance(args._values, list): err()

    args=nargs.get_args("args value1 value2")
    if args._value != "value1": err()

    if len(args._values) != 2: err()

    if args._values[0] != "value1": err()

    if args._values[1] != "value2": err()


    args="""
        arg:
            narg:
                nnarg:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)    
    args=nargs.get_args("args arg narg nnarg")
    if args.arg.narg.nnarg._get_cmd_line() != "args arg narg nnarg": err()

    if args.arg.narg.nnarg._get_path() != "args arg narg nnarg": err()

    args="""
        arg:
            _aliases: "--other,arg"
            _repeat: fork
            _values: '*'
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)    
    args=nargs.get_args("args arg arg arg")
    
    if args.arg._branches[2]._get_path() != "args arg+3": err()
    
    args=nargs.get_args("args arg arg")

    if args.arg._branches[1]._get_path() != "args arg+2": err()
    
    if args.arg._get_path(keep_default_alias=True) != "args --other": err()

    args=nargs.get_args("args arg value1 value2 value3")

    if args.arg._get_path(wvalues=True) != "args arg value1 value2 value3": err()

    args="""
        arg:
            arg:
                _repeat: fork
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    if nargs.dfn.dy_nodes["arg"].dy_nodes["arg"].current_arg._get_path() != "args arg + arg": err()

    args=nargs.get_args("args arg + arg")
    if args.arg.arg._get_path() != "args arg + arg": err()

    args=nargs.get_args("args arg + arg = arg")
    if args.arg.arg._branches[0]._get_path() != "args arg + arg": err()

    if args.arg.arg._branches[1]._get_path() != "args arg + arg+2": err()

    args="""
        arg1:
            sample:
                env:
        arg2:
            location:
                reason:
            places:
        arg3:
            "@": "args.arg1.sample,args.arg2.location"
        arg4:
            steps:
                "@": [
                    args.arg2.places,
                    args.arg5
                ]
        arg5:
            "@": args.arg6.safe
        arg6:
            safe:
                _hint: this is a safe location
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    if "location" not in nargs.dfn.dy_nodes["arg3"].dy_nodes: err()

    if "reason" not in nargs.dfn.dy_nodes["arg3"].dy_nodes["location"].dy_nodes: err()

    if "sample" not in nargs.dfn.dy_nodes["arg3"].dy_nodes: err()

    if "env" not in nargs.dfn.dy_nodes["arg3"].dy_nodes["sample"].dy_nodes: err()

    if "places" not in nargs.dfn.dy_nodes["arg4"].dy_nodes["steps"].dy_nodes: err()

    if nargs.dfn.dy_nodes["arg4"].dy_nodes["steps"].dy_nodes["arg5"].dy_nodes["safe"].dy["hint"] != "this is a safe location": err()

    if nargs.dfn.dy_nodes["arg5"].dy_nodes["safe"].dy["hint"] != "this is a safe location": err()

    args="""
        _repeat: fork
        arg:
            _repeat: fork
            _allow_parent_fork: false
            narg:
                _repeat: fork
                nnarg:
                    _allow_parent_fork: false
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)

    with CatchEx(EndUserError) as c:
        c.text="parent argument has more than one branch"
        nargs.get_args("args args arg")

    with CatchEx(EndUserError) as c:
        c.text="'args' can't be forked"
        nargs.get_args("args arg args")

    args=nargs.get_args("args arg arg")
    if len(args.arg._branches) != 2: err()

    args=nargs.get_args("args arg arg narg narg narg")
    if len(args.arg._branches[1].narg._branches) != 3: err()

    with CatchEx(EndUserError) as c:
        c.text="parent argument has more than one branch"
        args=nargs.get_args("args arg arg narg narg narg nnarg")

    args="""
        arg1:
            _allow_siblings: false
            narg1:
            narg2:
        arg2:
            narg:
                _allow_siblings: false
        arg3:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)

    args=nargs.get_args("args arg1")
    if args.arg1._here is False: err()

    args=nargs.get_args("args arg2 arg3")
    if args.arg2._here is False and args.arg3._here is False: err()

    args=nargs.get_args("args arg1 narg1 narg2")
    if args.arg1.narg1._here is False and args.arg1.narg2._here is False: err()

    with CatchEx(EndUserError) as c:
        c.text="'arg2' can't be added"
        nargs.get_args("args arg1 arg2")

    args="""
        _default: "apple"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("args")
    if args._value != "apple": err()

    args="""
        _default: apple, pear, prune
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("args")
    if ",".join(args._values) != "apple,pear,prune": err()

    
    args="""
        _enabled: false
        arg:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("args")
    if args is not None: err()

    args="""
        arg1:
        arg2:
            _enabled: false
        arg3:
            narg:
                _enabled: false

    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("args arg1")
    if args.arg1._here is False: err()
    with CatchEx(EndUserError) as c:
        c.text="argument 'args' does not accept value(s) 'arg2'"
        nargs.get_args("args arg2")

    args=nargs.get_args("args arg3")
    if args.arg3._here is False: err()
    with CatchEx(EndUserError) as c:
        c.text="argument 'arg3' does not accept value(s) 'narg'"
        nargs.get_args("args arg3 narg")

    args="""
        _examples: prog.py
        arg1:
            _examples:
                - prog.py arg examples
                - prog.py arg examples

    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)

    cmd='nargs.dfn.dy["examples"][0] != "prog.py"'
    if eval(cmd): err(cmd)

    if nargs.dfn.dy_nodes["arg1"].dy["examples"][1] != "prog.py arg examples":
        err()

    args="""
        _repeat: fork
        _need_child: false
        arg:
            _repeat: fork
            narg:
                _repeat: fork
                nnarg:
                    _repeat: fork
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)

    args=nargs.get_args("args args args")
    if len(args._branches) != 3:
        err()

    args=nargs.get_args("args args arg arg arg arg narg")
    if len(args._branches[1].arg._branches) != 4:
        err()

    if args._branches[1].arg._branches[3].narg._here is False:
        err()

    args=nargs.get_args("args arg narg nnarg nnarg args arg arg arg arg narg args arg narg nnarg nnarg")
    if len(args._branches[0].arg.narg.nnarg._branches) != 2:
        err()

    if args._branches[0].arg.narg.nnarg._branches[1]._here is False:
        err()

    args=nargs.get_args("args")
    if len(args._branches) != 1:
        err()

    args=nargs.get_args("args arg narg nnarg nnarg args arg arg args arg narg nnarg nnarg")
    if len(args.arg._branches) != 1:
        err()

    if len(args._branches[0].arg.narg.nnarg._branches) != 2:
        err()

    if args._branches[0].arg.narg.nnarg._branches[1]._here is False:
        err()

    args="""
        _hint: prog.py hint
        arg1:
            _hint: prog.py arg hint

    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)

    if nargs.dfn.dy["hint"] != "prog.py hint": 
        err(nargs.dfn.dy["hint"] != "prog.py hint")

    if nargs.dfn.dy_nodes["arg1"].dy["hint"] != "prog.py arg hint":
        err()

    args="""
        _info: prog.py info
        arg1:
            _info: prog.py arg info

    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)

    if nargs.dfn.dy["info"] != "prog.py info": 
        err(nargs.dfn.dy["info"] != "prog.py info")

    if nargs.dfn.dy_nodes["arg1"].dy["info"] != "prog.py arg info":
        err()

    args="""
        _in: apple, orange, pear
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)

    if len(nargs.dfn.dy["in"]) != 3:
        err()

    args=nargs.get_args("args pear")
    if args._value != "pear":
        err()

    with CatchEx(EndUserError) as c:
        c.text="value 'prune' not found in ['apple', 'orange', 'pear']"
        nargs.get_args("args prune")

    args="""
        _in: [apple, orange, pear]
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    if len(nargs.dfn.dy["in"]) != 3:
        err()

    args=nargs.get_args("args pear")
    if args._value != "pear":
        err()

    try:
        nargs.get_args("args ?")
    except:
        pass

    with CatchEx(EndUserError) as c:
        c.text="value 'prune' not found in ['apple', 'orange', 'pear']"
        nargs.get_args("args prune")

    
    args="""
        _in: 
            1: apple
            2: orange
            3: pear
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    try:
        nargs.get_args("args ?")
    except:
        pass

    if len(nargs.dfn.dy["in"]) != 3:
        err()

    args=nargs.get_args("args 1")
    if args._value != "1":
        err()

    with CatchEx(EndUserError) as c:
        c.text="value '4' not found in ['1', '2', '3']"
        nargs.get_args("args 4")

    args="""
        _in: 
            1: apple
            2: orange
            3: pear
        _type: int
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    if len(nargs.dfn.dy["in"]) != 3:
        err()

    args=nargs.get_args("args 1")
    if args._value != 1:
        err()

    with CatchEx(EndUserError) as c:
        c.text="value '4' not found in [1, 2, 3]"
        nargs.get_args("args 4")

    try:
        nargs.get_args("args ?")
    except:
        pass

    args="""
        help:
            _is_custom_builtin: true
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("args")

    if args.help._dfn.dy["is_custom_builtin"] is False:
        err()

    args="""
        usage:
            _aliases: "/usage,/?"
            _is_usage: true
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("args /?")

    if args.usage._here is False:
        err()

    if args.usage._dfn.dy["is_usage"] is False:
        err()

    args="""
        _label: LOCATION
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    try:
        args=nargs.get_args("args ?")
    except:
        pass
    args=nargs.get_args("args India")
    if args._value != "India":
        err()

    args="""
        arg: 
            _need_child: True
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)
    args=nargs.get_args("args arg")
    if args.arg._dfn.dy["need_child"] is True:
        err()

    args="""
        arg: 
            _need_child: True
            narg:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)
    if nargs.dfn.dy["need_child"] is False:
        err()
    
    with CatchEx(EndUserError) as c:
        c.text="'arg' at least one child argument is needed"
        args=nargs.get_args("args arg")
    
    args="""
        _need_child: false
        _repeat: "replace"
        _values: "?"
        arg:
            _repeat: "replace"
            _values: "?"
            narg:
                _repeat: "replace"
                _values: "?"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    args=nargs.get_args("args value1 arg value1 narg value1 narg value2")
    if args.arg.narg._count != 1: err()
    if args.arg.narg._value != "value2": err()

    args=nargs.get_args("args value1 arg value1 narg value1 narg value2 args value2")
    if args.arg.narg._count != 0: err()
    if args._value != "value2": err()
    if args.arg._here is True: err()

    args="""
        _need_child: false
        _repeat: "error"
        _values: "?"
        arg:
            _repeat: "error"
            _values: "?"
            narg:
                _repeat: "error"
                _values: "?"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    with CatchEx(EndUserError) as c:
        c.text="'args' can't be repeated"
        args=nargs.get_args("args args")

    with CatchEx(EndUserError) as c:
        c.text="'arg' can't be repeated"
        args=nargs.get_args("args arg arg")

    with CatchEx(EndUserError) as c:
        c.text="'narg' can't be repeated"
        args=nargs.get_args("args arg narg narg")

    args="""
        _need_child: false
        _repeat: "append"
        _values: "*"
        arg:
            _repeat: "append"
            _values: "*"
            narg:
                _repeat: "append"
                _values: "*"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    args=nargs.get_args("args value1 args value2 arg value1 narg value1 arg value2 narg value2 args value3")
    if args._count != 3: err()
    if args.arg._count != 2: err()
    if args.arg.narg._count != 2: err()
    for i in range(3):
        value="value{}".format(i+1)
        if value not in args._values: err()
        if i+1 in [1,2]:
            if value not in args.arg._values: err()
            if value not in args.arg.narg._values: err()

    if len(args._values) != 3: err()
    if len(args.arg._values) != 2: err()
    if len(args.arg.narg._values) != 2: err()

    args="""
        arg:
            _required: true
            _values: "*"
            narg:
                _required: true
                _values: 1
    """
    with CatchEx(DeveloperError) as c:
        c.text="current argument can't be implicitly added"
        nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    args="""
        arg:
            _required: true
            _values: "*"
            narg:
                _required: true
                _values: "*"
    """

    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)
    args=nargs.get_args("args")
    if args.arg._here is False: err()
    if args.arg.narg._here is False: err()
    if "arg" not in args._dfn.dy["required_children"]: err()

    args="""
        arg1:
            narg1:
                _show: false
                nnarg:
            narg2:
                nnarg:
                    _show: false
        arg2:
            _aliases: "arg2,a"
            _show: false
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)
    try:
        args=nargs.get_args("args ?@d=-1")
    except:
        pass

    args=nargs.get_args("args a")
    if args.arg2._here is False: err()

    args=nargs.get_args("args arg1 narg1 nnarg narg2 nnarg")
    if args.arg1.narg1.nnarg._here is False: err()
    if args.arg1.narg2.nnarg._here is False: err()

    args="""
        arg1:
            _type: bool
        arg2:
            _type: float
        arg3:
            _type: int
        arg4:
            _type: str
        arg5:
            _type: dir
        arg6:
            _type: file
        arg7:
            _type: path
        arg8:
            _type: vpath
        arg9:
            _type: json
        arg10:
            _type: .json
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    args=nargs.get_args("args arg1 true arg2 2.34 arg3 19 arg4 text arg5 tests arg6 tests/implementation.py arg7 tests/aliases.py arg8 tests/unknown.txt arg9 \"{'fruit': 'apple'}\" arg10 tests/assets/small.json")

    direpa_tests=os.path.dirname(os.path.realpath(__file__))

    if args.arg1._value is not True: err()
    if args.arg2._value != 2.34: err()
    if args.arg3._value != 19: err()
    if args.arg4._value != "text": err()
    if args.arg5._value != direpa_tests: err()
    if args.arg6._value != os.path.join(direpa_tests, "implementation.py"): err()
    if args.arg7._value != os.path.join(direpa_tests, "aliases.py"): err()
    if args.arg8._value != os.path.join(direpa_tests, "unknown.txt"): err()
    if args.arg9._value["fruit"] != "apple": err()
    if args.arg10._value["fruit"] != "apple": err()

    args=nargs.get_args("args arg9 \"fruit: apple\"")
    if args.arg9._value["fruit"] != "apple": err()

    args="""
        arg1:
            _values: "*"
            _type: int
        arg2:
            _values: "+"
            _type: int
        arg3:
            _values: "?"
            _type: int
        arg4:
            _values: "5?"
            _type: int
        arg5:
            _values: "1-9?"
            _type: int
        arg6:
            _values: "2-*?"
            _type: int
        arg7:
            _values: "5"
            _type: int
        arg8:
            _values: "1-9"
            _type: int
        arg9:
            _values: "2-*"
            _type: int
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)


    args=nargs.get_args("args arg1 1 arg2 1 arg3 1 arg4 1 2 3 4 5 arg5 1 arg6 1 2 arg7 1 2 3 4 5 arg8 1 2 arg9 1 2")

    if args.arg1._value != 1: err()
    if args.arg1._dfn.dy["values_authorized"] != True: err()
    if args.arg1._dfn.dy["values_required"] != False: err()
    if args.arg1._dfn.dy["values_min"] != 1: err()
    if args.arg1._dfn.dy["values_max"] is not None: err()

    if len(args.arg2._values) != 1: err()
    if args.arg2._dfn.dy["values_authorized"] != True: err()
    if args.arg2._dfn.dy["values_required"] != True: err()
    if args.arg2._dfn.dy["values_min"] != 1: err()
    if args.arg2._dfn.dy["values_max"] is not None: err()

    if len(args.arg3._values) != 1: err()
    if args.arg3._dfn.dy["values_authorized"] != True: err()
    if args.arg3._dfn.dy["values_required"] != False: err()
    if args.arg3._dfn.dy["values_min"] != 1: err()
    if args.arg3._dfn.dy["values_max"] != 1: err()

    if len(args.arg4._values) != 5: err()
    if args.arg4._dfn.dy["values_authorized"] != True: err()
    if args.arg4._dfn.dy["values_required"] != False: err()
    if args.arg4._dfn.dy["values_min"] != 5: err()
    if args.arg4._dfn.dy["values_max"] != 5: err()

    if len(args.arg5._values) != 1: err()
    if args.arg5._dfn.dy["values_authorized"] != True: err()
    if args.arg5._dfn.dy["values_required"] != False: err()
    if args.arg5._dfn.dy["values_min"] != 1: err()
    if args.arg5._dfn.dy["values_max"] != 9: err()

    if len(args.arg6._values) != 2: err()
    if args.arg6._dfn.dy["values_authorized"] != True: err()
    if args.arg6._dfn.dy["values_required"] != False: err()
    if args.arg6._dfn.dy["values_min"] != 2: err()
    if args.arg6._dfn.dy["values_max"] is not None: err()

    if len(args.arg7._values) != 5: err()
    if args.arg7._dfn.dy["values_authorized"] != True: err()
    if args.arg7._dfn.dy["values_required"] != True: err()
    if args.arg7._dfn.dy["values_min"] != 5: err()
    if args.arg7._dfn.dy["values_max"] != 5: err()

    if len(args.arg8._values) != 2: err()
    if args.arg8._dfn.dy["values_authorized"] != True: err()
    if args.arg8._dfn.dy["values_required"] != True: err()
    if args.arg8._dfn.dy["values_min"] != 1: err()
    if args.arg8._dfn.dy["values_max"] != 9: err()

    if len(args.arg9._values) != 2: err()
    if args.arg9._dfn.dy["values_authorized"] != True: err()
    if args.arg9._dfn.dy["values_required"] != True: err()
    if args.arg9._dfn.dy["values_min"] != 2: err()
    if args.arg9._dfn.dy["values_max"] is not None: err()

    args=nargs.get_args("args arg1 arg3 arg4 arg5 arg6")
    if len(args.arg1._values) != 0: err()
    if len(args.arg2._values) != 0: err()
    if len(args.arg3._values) != 0: err()
    if len(args.arg4._values) != 0: err()
    if len(args.arg4._values) != 0: err()
    if len(args.arg6._values) != 0: err()

    with CatchEx(EndUserError) as c:
        c.text="Maximum number of values '1'"
        nargs.get_args("args arg3 1 2")

    with CatchEx(EndUserError) as c:
        c.text="minimum values '3' is less than '5'"
        nargs.get_args("args arg4 1 2 3")

    with CatchEx(EndUserError) as c:
        c.text="Maximum number of values '9'"
        nargs.get_args("args arg5 1 2 3 4 5 6 7 8 9 10")

    with CatchEx(EndUserError) as c:
        c.text="minimum values '1' is less than '2'"
        nargs.get_args("args arg6 1")

    with CatchEx(EndUserError) as c:
        c.text="Maximum number of values '5'"
        nargs.get_args("args arg7 1 2 3 4 5 6")

    with CatchEx(EndUserError) as c:
        c.text="needs at least one value"
        nargs.get_args("args arg8")

    with CatchEx(EndUserError) as c:
        c.text="minimum values '1' is less than '2'"
        nargs.get_args("args arg9 1")

    args="""
        _xor:
            - "arg1,arg2"
            - "arg1,arg3"
        arg1:
            _xor:
                - "narg1,narg2"
                - "narg1,narg3"
            narg1:
            narg2:
            narg3:
        arg2:
            _xor:
                - - narg1
                  - narg2
                - - narg1
                  - narg3
            narg1:
            narg2:
            narg3:
        arg3:
            _xor:
                - narg1
                - narg2
            narg1:
            narg2:
            narg3:
        arg4:
            narg:
                _xor:
                    - nnarg1
                    - nnarg2
                nnarg1:
                nnarg2:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(usage=None), raise_exc=True)

    with CatchEx(EndUserError) as c:
        c.text="two following arguments can't be provided at the same time"
        nargs.get_args("args arg1 arg2")

    with CatchEx(EndUserError) as c:
        c.text="two following arguments can't be provided at the same time"
        nargs.get_args("args arg1 arg3")

    with CatchEx(EndUserError) as c:
        c.text="two following arguments can't be provided at the same time"
        nargs.get_args("args arg1 narg1 narg2")

    with CatchEx(EndUserError) as c:
        c.text="two following arguments can't be provided at the same time"
        nargs.get_args("args arg1 narg1 narg3")

    with CatchEx(EndUserError) as c:
        c.text="two following arguments can't be provided at the same time"
        nargs.get_args("args arg2 narg1 narg2")

    with CatchEx(EndUserError) as c:
        c.text="two following arguments can't be provided at the same time"
        nargs.get_args("args arg2 narg1 narg3")

    with CatchEx(EndUserError) as c:
        c.text="two following arguments can't be provided at the same time"
        nargs.get_args("args arg3 narg1 narg2")

    with CatchEx(EndUserError) as c:
        c.text="two following arguments can't be provided at the same time"
        nargs.get_args("args arg4 narg nnarg1 nnarg2")

    args=nargs.get_args("args arg1")
    if args.arg1._here is False: err()
    args=nargs.get_args("args arg1 narg1")
    if args.arg1.narg1._here is False: err()
    args=nargs.get_args("args arg1 narg2 narg3")
    if args.arg1.narg2._here is False: err()
    if args.arg1.narg3._here is False: err()
    args=nargs.get_args("args arg2 arg3")
    if args.arg2._here is False: err()
    if args.arg3._here is False: err()
    args=nargs.get_args("args arg2 narg2 narg3")
    if args.arg2.narg2._here is False: err()
    if args.arg2.narg3._here is False: err()
    args=nargs.get_args("args arg3 narg1 narg3")
    if args.arg3.narg1._here is False: err()
    if args.arg3.narg3._here is False: err()

    if len(args.arg1._dfn.dy["xor_groups"]) != 2: err()
    if 1 not in args.arg1._dfn.dy["xor_groups"]: err()
    if 2 not in args.arg1._dfn.dy["xor_groups"]: err()
    if len(args.arg2._dfn.dy["xor_groups"]) != 1: err()
    if 1 not in args.arg2._dfn.dy["xor_groups"]: err()
    if len(args.arg3._dfn.dy["xor_groups"]) != 1: err()
    if 2 not in args.arg3._dfn.dy["xor_groups"]: err()

    dy_xor=args._dfn.dy["xor"]
    if "1" not in dy_xor["arg1"]: err()
    if "2" not in dy_xor["arg1"]: err()
    if "1" not in dy_xor["arg2"]: err()
    if "2" not in dy_xor["arg3"]: err()
    if "arg2" not in dy_xor["arg1"]["1"]: err()
    if "arg3" not in dy_xor["arg1"]["2"]: err()
    if "arg1" not in dy_xor["arg2"]["1"]: err()
    if "arg1" not in dy_xor["arg3"]["2"]: err()

    if len(args.arg1.narg1._dfn.dy["xor_groups"]) != 2: err()
    if 1 not in args.arg1.narg1._dfn.dy["xor_groups"]: err()
    if 2 not in args.arg1.narg1._dfn.dy["xor_groups"]: err()
    if len(args.arg1.narg2._dfn.dy["xor_groups"]) != 1: err()
    if 1 not in args.arg1.narg2._dfn.dy["xor_groups"]: err()
    if len(args.arg1.narg3._dfn.dy["xor_groups"]) != 1: err()
    if 2 not in args.arg1.narg3._dfn.dy["xor_groups"]: err()

    dy_xor=args._dfn.dy_nodes["arg1"].dy["xor"]
    if "1" not in dy_xor["narg1"]: err()
    if "2" not in dy_xor["narg1"]: err()
    if "1" not in dy_xor["narg2"]: err()
    if "2" not in dy_xor["narg3"]: err()
    if "narg2" not in dy_xor["narg1"]["1"]: err()
    if "narg3" not in dy_xor["narg1"]["2"]: err()
    if "narg1" not in dy_xor["narg2"]["1"]: err()
    if "narg1" not in dy_xor["narg3"]["2"]: err()

    if len(args.arg2.narg1._dfn.dy["xor_groups"]) != 2: err()
    if 1 not in args.arg2.narg1._dfn.dy["xor_groups"]: err()
    if 2 not in args.arg2.narg1._dfn.dy["xor_groups"]: err()
    if len(args.arg2.narg2._dfn.dy["xor_groups"]) != 1: err()
    if 1 not in args.arg2.narg2._dfn.dy["xor_groups"]: err()
    if len(args.arg2.narg3._dfn.dy["xor_groups"]) != 1: err()
    if 2 not in args.arg2.narg3._dfn.dy["xor_groups"]: err()

    dy_xor=args._dfn.dy_nodes["arg2"].dy["xor"]
    if "1" not in dy_xor["narg1"]: err()
    if "2" not in dy_xor["narg1"]: err()
    if "1" not in dy_xor["narg2"]: err()
    if "2" not in dy_xor["narg3"]: err()
    if "narg2" not in dy_xor["narg1"]["1"]: err()
    if "narg3" not in dy_xor["narg1"]["2"]: err()
    if "narg1" not in dy_xor["narg2"]["1"]: err()
    if "narg1" not in dy_xor["narg3"]["2"]: err()

    if len(args.arg3.narg1._dfn.dy["xor_groups"]) != 1: err()
    if 1 not in args.arg3.narg1._dfn.dy["xor_groups"]: err()
    if len(args.arg3.narg2._dfn.dy["xor_groups"]) != 1: err()
    if 1 not in args.arg3.narg2._dfn.dy["xor_groups"]: err()

    dy_xor=args._dfn.dy_nodes["arg3"].dy["xor"]
    if "1" not in dy_xor["narg1"]: err()
    if "1" not in dy_xor["narg2"]: err()
    if "narg2" not in dy_xor["narg1"]["1"]: err()
    if "narg1" not in dy_xor["narg2"]["1"]: err()

    dy_xor=args._dfn.dy_nodes["arg4"].dy_nodes["narg"].dy["xor"]
    if "1" not in dy_xor["nnarg1"]: err()
    if "1" not in dy_xor["nnarg2"]: err()
    if "nnarg2" not in dy_xor["nnarg1"]["1"]: err()
    if "nnarg1" not in dy_xor["nnarg2"]["1"]: err()

    args="""
        _aliases: r,root
        _need_child: false
        ancestor:
            gd_parent:
                parent:
                    self:
                        child:
                    sibling:
                uncle:
            gd_uncle:
        ancestor_uncle:
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("root ancestor gd-parent parent self")
    if args.ancestor.gd_parent.parent.self._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self")
    if args.ancestor.gd_parent.parent.self._here is False: err()

    args=nargs.get_args("root ancestor gd-parent parent self child")
    if args.ancestor.gd_parent.parent.self.child._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self + child")
    if args.ancestor.gd_parent.parent.self.child._here is False: err()

    args=nargs.get_args("root ancestor gd-parent parent self sibling")
    if args.ancestor.gd_parent.parent.sibling._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self = sibling")
    if args.ancestor.gd_parent.parent.sibling._here is False: err()

    args=nargs.get_args("root ancestor gd-parent parent self parent")
    if args.ancestor.gd_parent.parent._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self - parent")
    if args.ancestor.gd_parent.parent._here is False: err()

    args=nargs.get_args("root ancestor gd-parent parent self uncle")
    if args.ancestor.gd_parent.uncle._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self - uncle")
    if args.ancestor.gd_parent.uncle._here is False: err()

    args=nargs.get_args("root ancestor gd-parent parent self gd-parent")
    if args.ancestor.gd_parent._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self -- gd-parent")
    if args.ancestor.gd_parent._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self -2 gd-parent")
    if args.ancestor.gd_parent._here is False: err()

    args=nargs.get_args("root ancestor gd-parent parent self gd-uncle")
    if args.ancestor.gd_uncle._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self -- gd-uncle")
    if args.ancestor.gd_uncle._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self -2 gd-uncle")
    if args.ancestor.gd_uncle._here is False: err()

    args=nargs.get_args("root ancestor gd-parent parent self ancestor")
    if args.ancestor._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self --- ancestor")
    if args.ancestor._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self -3 ancestor")
    if args.ancestor._here is False: err()

    args=nargs.get_args("root ancestor gd-parent parent self ancestor-uncle")
    if args.ancestor_uncle._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self --- ancestor-uncle")
    if args.ancestor_uncle._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self -3 ancestor-uncle")
    if args.ancestor_uncle._here is False: err()

    args=nargs.get_args("root ancestor gd-parent parent self root")
    if args._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self ---- root")
    if args._here is False: err()
    args=nargs.get_args("root + ancestor + gd-parent + parent + self -4 root")
    if args._here is False: err()

    args=nargs.get_args("root + ancestor + gd-parent + parent + self -4 r")
    if args._here is False: err()
    if args.ancestor._here is True: err()

    args="""
        _aliases: "args,r"
        _need_child: false
        _values: "?"
        arg:
            _aliases: "--arg,-a"
            _values: "+"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)

    args=nargs.get_args("args value")

    args=nargs.get_args("args -a value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a value1 value2 \"this is value3\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args -a value1 value2 'this is value3'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("args -a=value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a=\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a='value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a='value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args -a=\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("args -a:value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a:\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a:'value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a:'value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args -a:\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("args --arg value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args --arg value1 value2 \"this is value3\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args --arg value1 value2 'this is value3'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("args --arg=value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args --arg=\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("args --arg='value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("args --arg='value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args --arg=\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("args --arg:value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args --arg:\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("args --arg:'value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("args --arg:'value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args --arg:\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("args  -a=value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args  -a=\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("args  -a='value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("args  -a='value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args  -a=\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("args  -a:value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args  -a:\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("args  -a:'value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("args  -a:'value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args  -a:\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("args -a=value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a=\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a='value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a='value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args -a=\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("args -a:value")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a:\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a:'value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("args -a:'value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("args -a:\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("ra=value")
    if args.arg._value != "value": err()
    args=nargs.get_args("ra=\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("ra='value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("ra='value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("ra=\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

    args=nargs.get_args("ra:value")
    if args.arg._value != "value": err()
    args=nargs.get_args("ra:\"value\"")
    if args.arg._value != "value": err()
    args=nargs.get_args("ra:'value'")
    if args.arg._value != "value": err()
    args=nargs.get_args("ra:'value1 value2 \"this is value3\"'")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()
    args=nargs.get_args("ra:\"value1 value2 'this is value3'\"")
    if len(args.arg._values) != 3: err() 
    if "this is value3" not in args.arg._values: err()

   # rules of precedence show
    args="""
        _aliases: "args,-r"
        _need_child: false
        _repeat: append
        arg:
            _aliases: "arg,r"
            _repeat: append
            _show: false
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True, cache=False)
    args=nargs.get_args("args -r")
    if args._count != 2: err()
    if args.arg._here is True: err()

    # rules of precedence node level
    args="""
        _aliases: "args,-r"
        _need_child: false
        _repeat: append
        arg:
            _aliases: "arg,r"
            _repeat: append
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True, cache=False)
    args=nargs.get_args("args r")
    if args._count != 1: err()
    if args.arg._count != 1: err()
    if args.arg._here is False: err()

    # rules of precedence prefix
    # ['+', '-', '', '/', ':', '_', '--']
    args="""
        _aliases: "args,-r,/r"
        _need_child: false
        _repeat: append
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True, cache=False)
    args=nargs.get_args("args -r")
    if args._count != 2: err()
    if args._dfn.get_dy_flags()["r"]["alias"] != "-r": err()

    args="""
        _need_child: false
        _repeat: append
        arg1:
            _aliases: "arg1,/r"
        arg2:
            _aliases: "arg2,-r"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True, cache=False)
    args=nargs.get_args("args -r")
    if args.arg1._here is True: err()
    if args.arg2._here is False: err()
    if args._dfn.get_dy_flags()["r"]["alias"] != "-r": err()
    if args.arg2._dfn.get_dy_flags()["r"]["alias"] != "-r": err()

    args="""
        _need_child: false
        _repeat: append
        arg1:
            _aliases: "arg1,/r"
        arg2:
            _aliases: "arg2,-r"
            _show: false
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True, cache=False)
    args=nargs.get_args("args /r")
    if args.arg2._here is True: err()
    if args.arg1._here is False: err()
    if args._dfn.get_dy_flags()["r"]["alias"] != "/r": err()
    if args.arg1._dfn.get_dy_flags()["r"]["alias"] != "/r": err()

    # concatenated flags set
    args="""
        _aliases: "args,r"
        _repeat: fork
        _need_child: false
        _values: '*'
        arg:
            _aliases: "arg,a"
            _repeat: append
            narg:
                _aliases: "narg,n"
                _repeat: append
                nnarg:
                    _aliases: "nnarg,o"
                    _repeat: fork
                    _values: '*'
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True, cache=False)
    args=nargs.get_args("args arg narg nnarg nnarg narg arg args args")
    if len(args._branches) != 3: err()
    if args.arg._count != 2: err()
    if args.arg.narg._count != 2: err()
    if args.arg.narg.nnarg._count != 1: err()

    args=nargs.get_args("args ranoo")
    if args._branches[1]._count != 1: err()
    if args._branches[1].arg._count != 1: err()
    if args._branches[1].arg.narg._count != 1: err()
    if args._branches[1].arg.narg.nnarg._count != 1: err()

    args=nargs.get_args("args arg arg narg nnarg rano")
    if args._count != 1: err()
    if args.arg._count != 2: err()
    if args.arg.narg._count != 1: err()
    if args.arg.narg.nnarg._count != 1: err()

    # values notation
    args=nargs.get_args("args r=val1")
    if args._branches[1]._value != "val1": err()
    args=nargs.get_args("args r='val1 val2'")
    if args._branches[1]._values[0] != "val1": err()
    if args._branches[1]._values[1] != "val2": err()
    args=nargs.get_args("args r='val1 val2 \"val 3\"'")
    if args._branches[1]._values[0] != "val1": err()
    if args._branches[1]._values[1] != "val2": err()
    if args._branches[1]._values[2] != "val 3": err()

    args=nargs.get_args("args arg narg nnarg rano=val1")
    if args._branches[1].arg.narg.nnarg._value != "val1": err()
    args=nargs.get_args("args arg narg nnarg rano='val1 val2'")
    if args._branches[1].arg.narg.nnarg._values[0] != "val1": err()
    if args._branches[1].arg.narg.nnarg._values[1] != "val2": err()
    args=nargs.get_args("args arg narg nnarg rano='val1 val2 \"val 3\"'")
    if args._branches[1].arg.narg.nnarg._values[0] != "val1": err()
    if args._branches[1].arg.narg.nnarg._values[1] != "val2": err()
    if args._branches[1].arg.narg.nnarg._values[2] != "val 3": err()

    # branch index notation
    args=nargs.get_args("args r args")
    if len(args._branches) != 3: err()
    args=nargs.get_args("args r")
    if len(args._branches) != 2: err()
    args=nargs.get_args("args r:val1")
    if len(args._branches) != 2: err()
    if args._value is not None: err()
    if args._branches[1]._value != "val1": err()

    args=nargs.get_args("args arg narg nnarg rano")
    if len(args._branches[1].arg.narg.nnarg._branches) != 1: err()

    args=nargs.get_args("args arg narg nnarg raannoo")
    if len(args.arg.narg.nnarg._branches) != 1: err()
    if args.arg.narg.nnarg._branches[0]._count != 1: err()
    if len(args.arg.narg.nnarg._branches) != 1: err()
    if len(args.arg.narg._branches) != 1: err()
    if args._branches[1].arg.narg._count != 2: err()
    if len(args.arg._branches) != 1: err()
    if args._branches[1].arg._count != 2: err()
    if len(args._branches) != 2: err()
    if args._count != 1: err()

    for c in ["a", "r"]:
        if c not in args._dfn.get_dy_flags(): err()

    for c in ["a", "r", "n"]:
        if c not in args.arg._dfn.get_dy_flags(): err()

    for c in ["a", "r", "n", "o"]:
        if c not in args.arg.narg._dfn.get_dy_flags(): err()

    for c in ["a", "r", "n", "o"]:
        if c not in args.arg.narg.nnarg._dfn.get_dy_flags(): err()

    # flag set and level 0
    args="""
        _aliases: "args,-r,/r"
        _need_child: false
        _repeat: append
        arg:
            _aliases: "arg,-a"
            _repeat: append
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True, cache=False)

    args=nargs.get_args("/ra")
    if args.arg._here is False: err()
    
    args=nargs.get_args("/r = /r")
    if args._count != 2: err()

    args=nargs.get_args("args arg - /ra")
    if args._count !=2: err()


    args=nargs.get_args("args arg - /rra")
    if args._count != 3: err()
    if args.arg._count != 2: err()

    args="""
        arg:
            _values: "?"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True, cache=False)
    with CatchEx(EndUserError) as c:
        c.text="not an explicit notation '-4'"
        args=nargs.get_args("args arg -4")

    args=nargs.get_args("args arg=-4")
    if args.arg._value != "-4": err()

    args="""
        arg:
            _values: "*"
        other:
            _aliases: "-4"
    """
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(query=None), raise_exc=True, cache=False)
    with CatchEx(EndUserError) as c:
        c.text="not an explicit notation '-4'"
        args=nargs.get_args("args arg -4")

    args=nargs.get_args("args arg = -4")
    if args.other._here is False: err()

    args=nargs.get_args("args arg /value")
    if args.arg._value != "/value": err()

    args=nargs.get_args("args arg=@value")
    if args.arg._value != "@value": err()

    args=nargs.get_args("args arg -value")
    if args.arg._value != "-value": err()

    args=nargs.get_args("args arg=-value")
    if args.arg._value != "-value": err()

    dy_args=dict(
        fruit=dict(
            _type="str",
        ),
        hobby=dict(
            _type="str",
            _values="*",
        ),
    )

    with open(filenpa_tmp_query, "w") as f:
        f.write(json.dumps(dict()))
    nargs=Nargs(args=dy_args, metadata=dy_metadata, raise_exc=True)

    args=nargs.get_args("--args --fruit ?", values=["--fruit"])
    if args.fruit._value != "--fruit": err()

    args=nargs.get_args(["--args", "--fruit", "?"], values=["--fruit"])
    if args.fruit._value != "--fruit": err()

    args=nargs.get_args("--args --hobby ? ? ? ?", values=["--fruit", "--hobby", "sport", "3d printing"])
    if "--fruit" not in args.hobby._values: err()
    if "--hobby" not in args.hobby._values: err()
    if "sport" not in args.hobby._values: err()
    if "3d printing" not in args.hobby._values: err()

    args=nargs.get_args(["--args", "--hobby", "?", "?", "?", "?"], values=["--fruit", "--hobby", "sport", "3d printing"])
    if "--fruit" not in args.hobby._values: err()
    if "--hobby" not in args.hobby._values: err()
    if "sport" not in args.hobby._values: err()
    if "3d printing" not in args.hobby._values: err()

    with open(filenpa_tmp_query, "w") as f:
        f.write(json.dumps(dict(
            cmd="--args --fruit ?",
            values=["--fruit"],
        )))
    args=nargs.get_args("--args --query {}".format(filenpa_tmp_query))
    if args.fruit._value != "--fruit": err()

    with open(filenpa_tmp_query, "w") as f:
        f.write(json.dumps(dict(
            cmd=["--args", "--fruit", "?"],
            values=["--fruit"],
        )))
    args=nargs.get_args("--args --query {}".format(filenpa_tmp_query))
    if args.fruit._value != "--fruit": err()

    with open(filenpa_tmp_query, "w") as f:
        f.write(json.dumps(dict(
            cmd="--args --hobby ? ? ? ?",
            values=["--fruit", "--hobby", "sport", "3d printing"],
        )))
    args=nargs.get_args("--args --query {}".format(filenpa_tmp_query))
    if "--fruit" not in args.hobby._values: err()
    if "--hobby" not in args.hobby._values: err()
    if "sport" not in args.hobby._values: err()
    if "3d printing" not in args.hobby._values: err()

    with open(filenpa_tmp_query, "w") as f:
        f.write(json.dumps(dict(
            cmd=["--args", "--hobby", "?", "?", "?", "?"],
            values=["--fruit", "--hobby", "sport", "3d printing"],
        )))
    args=nargs.get_args("--args --query {}".format(filenpa_tmp_query))
    if "--fruit" not in args.hobby._values: err()
    if "--hobby" not in args.hobby._values: err()
    if "sport" not in args.hobby._values: err()
    if "3d printing" not in args.hobby._values: err()