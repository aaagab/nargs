#!/usr/bin/env python3
from pprint import pprint
import json
import getpass
import os
import re
import shlex
import sys
import traceback


from .get_json import get_json
from .get_path import get_path
from .help import get_help_usage
from .nodes import CliArg
from .regexes import get_regex
from .style import Style

from ..gpkgs import message as msg


def enable_arg(node, alias, required_dfns, print_usage, prefix):
    process_node=False

    if node.get_arg()._here is True:
        if node.dy["repeat"] == "replace":
            reset_dfn(node, required_dfns)
            process_node=True
    else:
        process_node=True

    if process_node is True:
        node.get_arg()._here=True
        node.get_arg()._["_here"]=True
        node.get_arg()._alias=alias
        node.get_arg()._["_alias"]=alias
        node.get_forks().append(node.get_arg())

        if len(node.dy["required_children"]) > 0:
            if node not in required_dfns:
                required_dfns.append(node)

        if node.is_root is False:
            single=node.parent.dy_arg[node.get_arg()._parent._id]["single"]


            if single is None:
                if node.dy["single"] is True:
                    node.parent.dy_arg[node.get_arg()._parent._id]["single"]=node.get_arg()
            else:
                if single != node.get_arg():
                    msg.error("argument '{}' is single and does not accept other arguments '{}'".format(single._alias, alias), prefix=prefix.format(node.get_arg().get_path()))
                    print_usage(node.parent)
                    sys.exit(1)

            if node.parent.dy["either"] is not None:
                if node.name in node.parent.dy["either"]:
                    either_names=node.parent.dy["either"][node.name]
                    for either_name in either_names:
                        tmp_either_arg=node.parent.get_arg()._[either_name]
                        if tmp_either_arg._here is True:
                            msg.error("argument '{}' can't be added if sibling argument '{}' is present.".format(alias, tmp_either_arg._alias), prefix=prefix.format(node.get_arg().get_path()))
                            print_usage(node)
                            sys.exit(1)

def create_fork(node, ref_arg=None):
    if ref_arg is None:
        ref_arg=CliArg(node.get_forks(), node.name, node.get_pre_id(), parent=node.get_arg()._parent, default_alias=node.dy["default_alias"])

    node.dy_arg[ref_arg._id]=dict(
        arg=ref_arg,
        forks=node.get_forks(),
    )
    node.arg_id=ref_arg._id

    for tmp_node in node.nodes:
        new_arg=CliArg([], tmp_node.name, tmp_node.get_pre_id(), parent=ref_arg, default_alias=tmp_node.dy["default_alias"])
        setattr(node.get_arg(), tmp_node.name, new_arg)
        node.get_arg()._[tmp_node.name]=new_arg

        create_fork(
            node=tmp_node,
            ref_arg=new_arg,
        )

def update_fork(node, arg):
    node.arg_id=arg._id
    for tmp_node in node.nodes:
        update_fork(
            node=tmp_node,
            arg=node.get_arg()._[tmp_node.name],
        )

def check_values_min_max(node, print_usage, prefix):
    arg=node.get_arg()
    if len(arg._values) == 0 and node.dy["default"] is not None:

        in_values=dict()
        if node.dy["in"] is not None and isinstance(node.dy["in"], dict):
            in_values=node.dy["in"]

        default_values=node.dy["default"]
        if not isinstance(default_values, list):
            default_values=[default_values]

        for d, default_value in enumerate(default_values):
            tmp_default_value=default_value
            if tmp_default_value in in_values:
                tmp_default_value=in_values[tmp_default_value]
            if d == 0:
                arg._value=tmp_default_value
                arg._["_value"]=tmp_default_value
            arg._values.append(tmp_default_value)

    if node.dy["value_min"] is not None:
        if len(arg._values) < node.dy["value_min"]:
            msg.error("argument '{}' minimum value(s) '{}' is less than '{}'".format(arg._alias, len(arg._values), node.dy["value_min"]), prefix=get_arg_prefix(prefix, node))
            print_usage(node)
            sys.exit(1)
    if node.dy["value_max"] is not None:
        if len(arg._values) > node.dy["value_max"]:
            msg.error("argument '{}' maximum value(s) '{}' is greater than '{}'".format(arg._alias, len(arg._values), node.dy["value_max"]), prefix=get_arg_prefix(prefix, node))
            print_usage(node)
            sys.exit(1)

def add_value(
    node,
    value,
    print_usage,
    prefix,
):
    arg=node.get_arg()
    if node.dy["value_max"] is not None:
        if len(arg._values) >= node.dy["value_max"]:
            msg.error("value '{}' can't be added. Maximum number of values '{}' has been reached already.".format(value, node.dy["value_max"]), prefix=prefix)
            print_usage(node)
            sys.exit(1)

    if isinstance(node.dy["type"], str):
        if node.dy["type"] in [ ".json", "json" ]:
            tmp_value=get_json(
                prefix,
                value,
                search_file="." in node.dy["type"], 
            )
        elif node.dy["type"] in [ "dir", "file", "path", "vpath" ]:
            tmp_value=get_path(prefix, value, node.dy["type"])
    else:
        tmp_value=None
        if node.dy["type"] == bool:
            tmp_value=get_boolean(value)
        elif node.dy["type"] == float:
            try:
                tmp_value=float(value)
            except:
                tmp_value=None
        elif node.dy["type"] == int:
            try:
                tmp_value=int(value)
            except:
                tmp_value=None
        elif node.dy["type"] == str:
            tmp_value=value

        if tmp_value is None:
            msg.error("value '{}' type error. It must match type '{}'.".format(value, node.dy["type"]), prefix=prefix)
            print_usage(node)
            sys.exit(1)

    value=tmp_value

    if node.dy["in"] is not None:
        if value in node.dy["in"]:
            if isinstance(node.dy["in"], dict):
                value=node.dy["in"][value]
        else:
            msg.error("value '{}' not in {}.".format(value, node.dy["in"]), prefix=prefix)
            print_usage(node)
            sys.exit(1)

    if arg._value is None:
        arg._value=value
        arg._["_value"]=value
    arg._values.append(value)

def get_arg_prefix(prefix, node):
    prefix=prefix.format(node.get_arg().get_path(explicit=True, wvalues=True))
    return prefix

def get_node(alias, aliases, required_dfns, print_usage, prefix, index=None):
    node=aliases[alias]
    if node.dy["repeat"] in ["append", "replace"]:
        if index is not None:
            if index > 1:
                msg.error("arg '{}' wrong index syntax only '_1' is authorized.".format(alias), prefix=prefix)
                print_usage(node)
                sys.exit(1)
        enable_arg(node, alias, required_dfns, print_usage, prefix)
    elif node.dy["repeat"] == "exit":
        if node.get_arg()._here is True:
            msg.error("arg '{}' can't be repeated.".format(alias), prefix=prefix)
            print_usage(node)
            sys.exit(1)
        else:
            enable_arg(node, alias, required_dfns, print_usage, prefix)
    elif node.dy["repeat"] == "create":
        if index is None:
            if len(node.get_forks()) == 0:
                enable_arg(node, alias, required_dfns, print_usage, prefix)
            else:
                create_fork(node)
                enable_arg(node, alias, required_dfns, print_usage, prefix)
        elif index == len(node.get_forks()):
            if len(node.get_forks()) == 0:
                enable_arg(node, alias, required_dfns, print_usage, prefix)
            else:
                if node.get_arg()._index != index-1:
                    update_fork(node, node.get_forks()[index-1])
        elif index == len(node.get_forks()) + 1:
            create_fork(node)
            enable_arg(node, alias, required_dfns, print_usage, prefix)
        else:
            msg.error("argument '{}' index too big. Biggest index available is '{}'".format(index, len(node.get_forks())+1), prefix=prefix)
            print_usage(node)
            sys.exit(1)

    return node


def process_concat_alias(reg_concat, node, required_dfns, print_usage, prefix):
    tmp_node=None
    dy_alias=node.explicit_aliases
    for c in reg_concat.group("short_aliases"):
        tmp_alias="-{}".format(c)
        if tmp_alias in dy_aliases:
            tmp_node=dy_aliases[tmp_alias]
            if tmp_node.dy["value_required"] is None:
                tmp_node=get_node(tmp_alias, dy_aliases, required_dfns, print_usage, get_arg_prefix(prefix, node)+" , in concatenated aliases '{}'".format(tmp_alias), index=None)
            else:
                msg.error("In concatenated aliases '{}' alias '{}' can't be an argument that accepts values in its definition.".format(elem, alias), prefix=get_arg_prefix(prefix, node))
                print_usage(node)
                sys.exit(1)
        else:
            msg.error("In concatenated aliases '{}' unknown alias '{}'.".format(elem, alias), prefix=get_arg_prefix(prefix, node))
            print_usage(node)
            sys.exit(1)

def get_implicit_aliases(node):
    if node.implicit_aliases is None:
        node.implicit_aliases=[]
        for parent in node.parents:
            for tmp_alias, tmp_node in parent.explicit_aliases.items():
                ignore= parent.level == node.level - 1 and tmp_node == node
                if ignore is False:
                    node.implicit_aliases[tmp_alias]=tmp_node
    return node.implicit_aliases

def get_node_from_long_short_dashless_alias(node, reg_alias, print_usage, prefix, required_dfns, rule_name, add_implicit=False):
    alias=reg_alias.group("alias")
    index=reg_alias.group("index")
    if index is None:
        index=1
    else:
        index=int(index)

    lst_dy_aliases=[node.explicit_aliases]
    if add_implicit is True:
        lst_dy_aliases.append(None)

    alias_found=False
    for dy_aliases in lst_dy_aliases:
        if dy_aliases is None:
            dy_aliases=get_implicit_aliases(node)
        if alias in dy_aliases:
            alias_found=True
            if node.dy["value_required"] is not None:
                check_values_min_max(node, print_usage, prefix)
            node=get_node(alias, dy_aliases, required_dfns, print_usage, get_arg_prefix(prefix, node), index)
            
            # if rule_name != "cli_dashless_alias":
            values=[]
            for tmp_value in [
                reg_alias.group("dquotes"),
                reg_alias.group("squotes"),
            ]:
                if tmp_value is not None:
                    values=shlex.split(tmp_value)
                    break

            if len(values) > 0:
                if node.dy["value_required"] is None:
                    msg.error("values are not allowed {}.".format(values), prefix=get_arg_prefix(prefix, node))
                    print_usage(node)
                    sys.exit(1)
                else:
                    for v, value in enumerate(values):
                        add_value(node, value, print_usage, prefix=get_arg_prefix(prefix, node))
            return node
    return None

def get_implicit_aliases(node):
    if node.implicit_aliases is None:
        node.implicit_aliases=dict()
        for parent in node.parents:
            for tmp_alias, tmp_node in parent.explicit_aliases.items():
                ignore= parent.level == node.level - 1 and tmp_node == node
                if ignore is False:
                    node.implicit_aliases[tmp_alias]=tmp_node
    return node.implicit_aliases

def get_args(
    cmd,
    dy_metadata,
    explicit,
    node_dfn,
    pretty,
    substitute,
    theme,
    usage_on_root,
    get_documentation,
    cmd_provided=False,
):
    node=node_dfn
    if node is None:
        msg.warning("Nargs get_args returns None due to either arguments empty definition or disabled root argument.")
        return None

    def print_usage(node):
        get_help_usage(
            dy_metadata=dy_metadata,
            special_cmd=":",
            node_ref=node,
            output="cmd_usage",
            style=Style(pretty=pretty, output="cmd_usage", theme=theme),
        )

    from_sys_argv=False
    if cmd is None:
        from_sys_argv=True
        cmd=sys.argv
    else:
        if not isinstance(cmd, str):
            msg.error("Nargs on the command-line cmd type {} must be type {}.".format(type(cmd), str), exit=1)
        cmd_provided=True
        cmd=shlex.split(cmd)

    if len(cmd) == 0:
        msg.error("Nargs on the command-line command must have at least the root argument set.", exit=1)

    prefix="Nargs on the command-line \"{}\""

    if usage_on_root is True:
        if len(cmd) == 1:
            if len(node.dy["required_children"]) > 0:
                process_required(node_dfn, node_dfn.get_arg(), print_usage, prefix)

            print_usage(node)
            sys.exit(1)


    if substitute is True:
        tmp_cmd=[]
        for elem in cmd:
            elem=re.sub(r"__([a-zA-Z][a-zA-Z0-9]*)__", lambda m: get_env_var(m), elem)
            tmp_cmd.append(elem)
        cmd=tmp_cmd

    at_start=True
    # processed=[]
    explicit_notation=False
    builtin_arg=None
    after_concat=False
    required_dfns=[]

    while len(cmd) > 0:
        elem=cmd.pop(0)
        is_last_elem=len(cmd) == 0
        # processed.append(shlex.quote(elem))
        # if hasattr(node, "dump"):
        #     del node.dump
        if at_start is True:
            at_start=False

            if from_sys_argv is False:
                if elem not in node.dy["aliases"]:
                    msg.error("For provided cmd root argument alias '{}' is not in {}.".format(elem, sorted(node.dy["aliases"])), prefix=get_arg_prefix(prefix, node))
                    print_usage(node)
                    sys.exit(1)

            enable_arg(node, elem, required_dfns, print_usage, prefix)
        elif get_help_usage(
                dy_metadata=dy_metadata,
                special_cmd=elem,
                node_ref=node,
                output="cmd_usage",
                style=Style(pretty=pretty, output="cmd_usage", theme=theme),
                from_get_args=True,
            ):
            sys.exit(0)
        else:
            only_argument=(explicit_notation is True or after_concat is True)
            if only_argument is True:
                if after_concat is True:
                    after_concat=False

                reg_arg_matched=False
                for rule_name in ["cli_long_alias", "cli_short_alias", "cli_dashless_alias"]:
                    reg_alias=re.match(get_regex(rule_name)["rule"], elem)
                    if reg_alias:
                        reg_arg_matched=True
                        alias=reg_alias.group("alias")

                        if explicit is True and explicit_notation is None:
                            msg.error("explicit notation is expected before argument '{}'.".format(alias), prefix=get_arg_prefix(prefix, node))
                            print_usage(node)
                            sys.exit(1)

                        node_from_alias=get_node_from_long_short_dashless_alias(node, reg_alias, print_usage, prefix, required_dfns, rule_name)
                        if node_from_alias is None:
                            msg.error("unknown argument '{}'".format(alias), prefix=get_arg_prefix(prefix, node))
                            print_usage(node)
                            sys.exit(1)
                        else:
                            node=node_from_alias
                            if node.dy["is_builtin"] is True:
                                builtin_arg=node.get_arg()
                    break
                    
                if reg_arg_matched is False:
                    reg_concat=re.match(get_regex("cli_short_alias_concat")["rule"], elem)
                    if reg_concat:
                        after_concat=True
                        process_concat_alias(reg_concat, node, required_dfns, print_usage, prefix)
                    else: # does not match alias syntax
                        msg.error("unknown argument '{}'".format(elem), prefix=get_arg_prefix(prefix, node))
                        print_usage(node)
                        sys.exit(1)
            else:
                # only_argument is False means explicit_notation is False and after_concat is False
                reg_explicit=re.match(get_regex("cli_explicit")["rule"], elem)
                if reg_explicit:
                    if is_last_elem is True:
                        msg.error("command must finish with an argument or a value not an explicit notation '{}'".format(elem), prefix=get_arg_prefix(prefix, node))
                        print_usage(node)
                        sys.exit(1)

                    if node.dy["value_required"] is not None:
                        check_values_min_max(node, print_usage, prefix)

                    explicit_notation=True
                    if reg.explicit.group("minus") is None:
                        level_up=0
                        if reg_explicit.group("plus_concat") is None:
                            level_up=int(reg_explicit.group("plus_index"))
                        else:
                            level_up=len(reg_explicit.group("plus_concat"))
                        level_up=level_up - node.level
                        if  level_up < 1:
                            msg.error("argument explicit level '{}' with value '{}' is smaller than minimum level 1.".format(elem, level_up), prefix=get_arg_prefix(prefix, node), exit=1)

                        for i in range(1, level_up+1):
                            node=node.parent
                else:
                    # because explicit is True, it can only be a value
                    if explicit is True:
                        if node.dy["value_required"] in [True, False]:
                            if elem in node.explicit_aliases:
                                msg.error("argument '{}' is not expected. If it is a value, it can be added this way '{}=\"{}\"'".format(elem, node.get_arg()._alias, elem), prefix=get_arg_prefix(prefix, node))
                                print_usage(node)
                                sys.exit(1)
                            else:
                                for rule_name in ["cli_long_alias", "cli_short_alias", "cli_short_alias_concat"]:
                                    reg_alias=re.match(get_regex(rule_name)["rule"], elem)
                                    if reg_alias:
                                        msg.error("argument '{}' is not expected. If it is a value, it can be added this way '{}=\"{}\"'".format(elem, node.get_arg()._alias, elem), prefix=get_arg_prefix(prefix, node))
                                        print_usage(node)
                                        sys.exit(1)

                                add_value(node, elem, print_usage, prefix=get_arg_prefix(prefix, node))
                        else: # value_required is None
                            tmp_notation=""
                            if node.is_leaf is True:
                                if node.is_root is True:
                                    msg.error("only special command is expected.".format(elem), prefix=get_arg_prefix(prefix, node))
                                    print_usage(node)
                                    sys.exit(1)
                                else:
                                    tmp_notation="+"
                            else:
                                if node.is_root is True:
                                    tmp_notation="-"
                                else:
                                    tmp_notation="+ or -"

                            msg.error("input syntax error '{}' explicit notation ({}) is expected.".format(elem, tmp_notation), prefix=get_arg_prefix(prefix, node))
                            print_usage(node)
                            sys.exit(1)
                    else: # explicit is False
                        # because explicit is False it can be a value or an arg
                        reg_arg_matched=False
                        for rule_name in ["cli_long_alias", "cli_short_alias", "cli_dashless_alias", "cli_short_alias_concat"]:
                            reg_alias=re.match(get_regex(rule_name)["rule"], elem)
                            if reg_alias:
                                reg_arg_matched=True
                                if rule_name in ["cli_long_alias", "cli_short_alias", "cli_dashless_alias"]:
                                    alias=reg_alias.group("alias")

                                    node_from_alias=get_node_from_long_short_dashless_alias(node, reg_alias, print_usage, prefix, required_dfns, rule_name, add_implicit=True)
                                    if node_from_alias is None:
                                        if rule_name in "cli_dashless_alias":
                                            if node.dy["value_required"] is None:
                                                msg.error("unknown input '{}'.".format(alias), prefix=get_arg_prefix(prefix, node))
                                                print_usage(node)
                                                sys.exit(1)
                                            else:
                                                add_value(node, elem, print_usage, prefix=get_arg_prefix(prefix, node))
                                        else:
                                            error="unknown argument '{}'.".format(alias)
                                            if node.dy["value_required"] is not None:
                                                error+=" If it is a value, it can be added this way '{}=\"{}\"'".format(node.get_arg()._alias, alias)

                                            msg.error(error, prefix=get_arg_prefix(prefix, node))
                                            print_usage(node)
                                            sys.exit(1)
                                    else:
                                        node=node_from_alias
                                        if node.dy["is_builtin"] is True:
                                            builtin_arg=node.get_arg()
                                        
                                elif rule_name == "cli_short_alias_concat":
                                    after_concat=True
                                    process_concat_alias(reg_concat, node, required_dfns, print_usage, prefix)
                                break

                        if reg_arg_matched is False:
                            if node.dy["value_required"] is None:
                                msg.error("unknown input '{}'.".format(elem), prefix=get_arg_prefix(prefix, node))
                                print_usage(node)
                                sys.exit(1)
                            else:
                                add_value(node, elem, print_usage, prefix=get_arg_prefix(prefix, node))

    # check values min max on last element 
    if node.dy["value_required"] is not None:
        check_values_min_max(node, print_usage, prefix)

    if builtin_arg is None:
        for parent_dfn in required_dfns:
            for parent_arg in parent_dfn.get_arg()._forks:
                process_required(parent_dfn, parent_arg, print_usage, prefix)  

        return node.root.dy_arg["1"]["arg"]
    else:
        if builtin_arg._name == "cmd":
            if cmd_provided is True:
                msg.error("Nargs built-in --cmd argument can't be provided more than once.", exit=1)
            lines=[]
            with open(builtin_arg._value, "r") as f:
                for line in f.read().splitlines():
                    line=line.strip()
                    if len(line) > 0 and line[0] != "#":
                        lines.append(line)

            cmd=" ".join(lines)
            reset_dfn(node.root)
            get_args(
                cmd=cmd,
                dy_metadata=dy_metadata,
                explicit=explicit,
                node_dfn=node.root,
                pretty=pretty,
                substitute=substitute,
                theme=theme,
                get_documentation=get_documentation,
                cmd_provided=True,
            )
        elif builtin_arg._name == "examples":
            examples=get_examples(node.root, dy_metadata)
            if examples == "":
                sys.exit(1)
            else:
                print(examples)
                sys.exit(0)
        elif builtin_arg._name == "help":
            output="cmd_help"
            if builtin_arg.export._here is True:
                output=builtin_arg.export._value
            get_documentation(
                output=output,
                filenpa=builtin_arg.export.to._value,
                wsyntax=builtin_arg.syntax._here,
            )
            sys.exit(0)
        elif builtin_arg._name == "conf_path":
            conf_path=get_conf_path(dy_metadata)
            if conf_path is None:
                sys.exit(1)
            else:
                print(conf_path)
                sys.exit(0)
        elif builtin_arg._name == "usage":
            print_usage(node.root)
            sys.exit(0)
        elif builtin_arg._name == "uuid4":
            uuid4=get_uuid4(dy_metadata)
            if uuid4 is None:
                sys.exit(1)
            else:
                print(uuid4)
                sys.exit(0)
        elif builtin_arg._name == "version":
            version=get_version(dy_metadata)
            if version is None:
                sys.exit(1)
            else:
                print(version)
                sys.exit(0)

def get_env_var(reg):
    key=next(iter(reg.groups()))
    if key in os.environ:
        value=os.environ[key].strip()
        return re.sub(r"^\"?(.*?)\"?$", r"\1", value)
    else:
        return reg.group()

def reset_dfn(node, required_dfns=None):
    arg=node.get_arg()
    arg_found=len(arg._forks) > 0 
    if arg_found is True:
        for f, arg_fork in enumerate(arg._forks.copy()):
            if required_dfns is not None:
                if arg_fork in required_dfns:
                    required_dfns.remove(arg_fork)
            del node.dy_arg[arg_fork._id]
            forks.remove(arg_fork)
        node.set_first_arg()
        for tmp_node in node.nodes:
            reset_dfn(tmp_node, required_dfns=required_dfns)

def process_required(parent_dfn, parent_arg, print_usage, prefix):                        
    for child_name in parent_dfn.dy["required_children"]:
        required_arg=parent_arg._[child_name]
        if required_arg._here is False:
            required_dfn=None
            for tmp_required_dfn in parent_dfn.nodes:
                if tmp_required_dfn.name == child_name:
                    required_dfn=tmp_required_dfn
                    break

            tmp_prefix=prefix.format(parent_arg.get_path(explicit=True, wvalues=True))
            # if required_dfn.dy["default"] is None:
            msg.error("required argument '{}' is missing.".format(required_arg._default_alias), prefix=tmp_prefix)
            print_usage(parent_dfn)
            sys.exit(1)
            # else:
                # enable_arg(required_dfn, required_dfn.dy["default_alias"], [], print_usage, tmp_prefix)
                # check_values_min_max(required_dfn, print_usage, tmp_prefix)

        # process_required(required_dfn, required_arg, print_usage, prefix)

def get_examples(node_dfn, examples=[]):
    if node_dfn.is_root is True:
        examples=[]
    if node_dfn.dy["examples"] is not None:
        for example in node_dfn.dy["examples"]:
            examples.append("  {}".format(example))
    for node in node_dfn.nodes:
        get_examples(node, examples)

    if node_dfn.is_root is True:
        return "\n".join(examples)

def get_version(dy_metadata):
    if "version" in dy_metadata:
        if dy_metadata["version"] is not None:
            import __main__
            filenpa=os.path.normpath(__main__.__file__)
            drive, filenpa=os.path.splitdrive(filenpa)
            parent_direpa=os.path.basename(os.path.dirname(os.path.dirname(filenpa)))
            if parent_direpa == "beta":
                return "{}-beta".format(dy_metadata["version"])
            else:
                return dy_metadata["version"]
    return None

def get_conf_path(dy_metadata):
    if "conf_path" in dy_metadata:
        if dy_metadata["conf_path"] is not None:
            return dy_metadata["conf_path"]
    return None

def get_uuid4(dy_metadata):
    if "uuid4" in dy_metadata:
        if dy_metadata["uuid4"] is not None:
            return dy_metadata["uuid4"]
    return None

def get_boolean(value):
    if isinstance(value, str):
        if value.lower() in ["true", "1"]:
            return True
        elif value.lower() in ["false", "0"]:
            return True
        else:
            return None
    elif isinstance(value, int):
        if value == 0:
            return False
        elif value == 1:
            return True
    else:
        return None