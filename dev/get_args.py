#!/usr/bin/env python3
from pprint import pprint
import json
import getpass
import os
import re
import shlex
import sys
import traceback


from .get_json import get_json, get_arg_prefix
from .get_path import get_path
from .help import get_help_usage
from .regexes import get_regex
from .style import Style

from ..gpkgs import message as msg

def enable_arg(node, alias, prefix, pretty, cmd_line_index):
    node.current_arg._here=True
    node.current_arg._alias=alias
    node.current_arg._cmd_line_index=cmd_line_index
    node.current_arg._forks.append(node.current_arg)
    num_forks=len(node.current_arg._forks)
    for fork in node.current_arg._forks:
        fork._count=num_forks

    if node.is_root is False:
        if node in node.parent.dy_xor:
            for group_num in sorted(node.parent.dy_xor[node]):
                for tmp_node_dfn in node.parent.dy_xor[node][group_num]:
                    if tmp_node_dfn.current_arg is not None:
                        for tmp_arg in tmp_node_dfn.current_arg._forks:
                            if tmp_arg._parent == node.current_arg._parent:
                                msg.error([
                                    "XOR conflict, the two following arguments can't be provided at the same time:",
                                    "- {}".format(node.current_arg.get_path()),
                                    "- {}".format(tmp_arg.get_path()),
                                ]
                                , prefix=get_arg_prefix(prefix, node.parent, wvalues=False), pretty=pretty)
                                sys.exit(1)

def create_fork(node):
    node.set_arg("fork")
    for tmp_node in node.nodes:
        create_fork(node=tmp_node)

def check_values_min_max(node_dfn, arg, print_usage, prefix, pretty):
    if node_dfn.dy["value_min"] is not None:
        if len(arg._values) < node_dfn.dy["value_min"]:
            if node_dfn.dy["value_min"] == 1:
                msg.error("argument needs at least one value.", prefix=get_arg_prefix(prefix, node_dfn, wvalues=False), pretty=pretty)
            else:
                msg.error("argument '{}' minimum values '{}' is less than '{}'".format(arg._alias, len(arg._values), node_dfn.dy["value_min"]), prefix=get_arg_prefix(prefix, node_dfn, wvalues=True), pretty=pretty)
            print_usage(node_dfn)
            sys.exit(1)
    if node_dfn.dy["value_max"] is not None:
        if len(arg._values) > node_dfn.dy["value_max"]:
            msg.error("argument '{}' maximum value(s) '{}' is greater than '{}'".format(arg._alias, len(arg._values), node_dfn.dy["value_max"]), prefix=get_arg_prefix(prefix, node_dfn, wvalues=True), pretty=pretty)
            print_usage(node_dfn)
            sys.exit(1)

def values_final_check(node_dfn, arg, print_usage, prefix, pretty):
    if len(arg._values) > 0:
        check_values_min_max(node_dfn, arg, print_usage, prefix, pretty)
    else:
        if node_dfn.dy["value_required"] is True:
            if node_dfn.dy["default"] is None:
                check_values_min_max(node_dfn, arg, print_usage, prefix, pretty)
            else:
                in_values=dict()
                if node_dfn.dy["in"] is not None and isinstance(node_dfn.dy["in"], dict):
                    in_values=node_dfn.dy["in"]

                default_values=node_dfn.dy["default"]
                if not isinstance(default_values, list):
                    default_values=[default_values]

                for d, default_value in enumerate(default_values):
                    tmp_default_value=default_value
                    if tmp_default_value in in_values:
                        tmp_default_value=in_values[tmp_default_value]
                    if d == 0:
                        arg._value=tmp_default_value
                    arg._values.append(tmp_default_value)
        else:
            pass

def add_value(
    node,
    value,
    print_usage,
    prefix,
    pretty,
    cmd_line_index,
):
    arg=node.current_arg
    if node.dy["value_max"] is not None:
        if len(arg._values) >= node.dy["value_max"]:
            msg.error("value '{}' can't be added. Maximum number of values '{}' has been reached already.".format(value, node.dy["value_max"]), prefix=get_arg_prefix(prefix, node, wvalues=True, cmd_line_index=cmd_line_index), pretty=pretty)
            print_usage(node)
            sys.exit(1)

    if isinstance(node.dy["type"], str):
        if node.dy["type"] in [ ".json", "json" ]:
            tmp_value=get_json(
                prefix,
                value,
                node,
                pretty,
                cmd_line_index,
                search_file="." in node.dy["type"], 
            )
        elif node.dy["type"] in [ "dir", "file", "path", "vpath" ]:
            tmp_value=get_path(prefix, node, value, node.dy["type"], pretty, cmd_line_index)
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
            msg.error("value '{}' type error. It must match type '{}'.".format(value, node.dy["type"]), prefix=get_arg_prefix(prefix, node, wvalues=True, cmd_line_index=cmd_line_index), pretty=pretty)
            print_usage(node)
            sys.exit(1)

    value=tmp_value

    if node.dy["in"] is not None:
        if value not in node.dy["in"]:
            msg.error("value '{}' not found in {}.".format(value, node.dy["in"]), prefix=get_arg_prefix(prefix, node, wvalues=True, cmd_line_index=cmd_line_index), pretty=pretty)
            print_usage(node)
            sys.exit(1)

    if arg._value is None:
        arg._value=value
    arg._values.append(value)

def set_node(alias, node, print_usage, prefix, pretty, cmd_line_index, index):
    if index is not None:
        if node.dy["repeat"] in ["append", "replace", "error"]:
            if index > 1:
                msg.error("argument '{}' wrong index syntax '_{}' only '_1' is authorized when '_repeat' option is set to '{}'.".format(alias, index, node.dy["repeat"]), prefix=get_arg_prefix(prefix, node, wvalues=False, cmd_line_index=cmd_line_index), pretty=pretty)
                print_usage(node)
                sys.exit(1)
        elif node.dy["repeat"] == "fork":
            if index > len(node.current_arg._forks) + 1:
                msg.error("argument index '_{}' is too big. Biggest index available is '_{}'.".format(index, len(node.current_arg._forks)+1), prefix=get_arg_prefix(prefix, node, wvalues=False, cmd_line_index=cmd_line_index), pretty=pretty)
                print_usage(node)
                sys.exit(1)

    if node.dy["repeat"] == "append":
        if node.current_arg._here is True:
            node.current_arg._alias=alias
            node.current_arg._cmd_line_index=cmd_line_index
        else:
            enable_arg(node, alias, prefix, pretty, cmd_line_index)
    elif node.dy["repeat"] == "replace":
        if node.current_arg._here is True:
            reset_dfn(node)
        enable_arg(node, alias, prefix, pretty, cmd_line_index)
    elif node.dy["repeat"] == "error":
        if node.current_arg._here is True:
            msg.error("argument '{}' can't be repeated.".format(alias), prefix=get_arg_prefix(prefix, node, wvalues=False, cmd_line_index=cmd_line_index), pretty=pretty)
            print_usage(node)
            sys.exit(1)
        else:
            enable_arg(node, alias, prefix, pretty, cmd_line_index)
    elif node.dy["repeat"] == "fork":
        if index is None or index == len(node.current_args._forks)+1:
            create_fork(node)
            enable_arg(node, alias, prefix, pretty, cmd_line_index)
        elif index <= len(node.current_arg._forks):
            # select existing argument
            node.set_arg("select", index-1)

def get_explicit_path(node_dfn,  conflict_node_dfn, alias):
    explicit_notation=None
    argument_type=None
    if node_dfn.level < conflict_node_dfn.level:
        explicit_notation="-"
        argument_type="child"
    elif node_dfn.level == conflict_node_dfn.level:
        explicit_notation="+"
        if node_dfn == conflict_node_dfn:
            argument_type="same"
        else:
            argument_type="sibling"
    else:
        explicit_notation=(node_dfn.level - conflict_node_dfn.level + 1)*"+"
        argument_type="parent"

    return "'{} {} {}' for '{}' argument at siblings level {} with aliases {}.".format(
        node_dfn.current_arg.get_path(),
        explicit_notation,
        alias,
        argument_type,
        conflict_node_dfn.level,
        conflict_node_dfn.dy["aliases"],
    )

def get_closest_parent(nodes):
    min_level=None
    max_level=None

    for node in nodes:
        if min_level is None:
            min_level=node.level
            max_level=node.level
        else:
            if node.level < min_level:
                min_level=node.level

            if node.level > max_level:
                max_level=node.level

    ref_node=None
    if min_level > 1:
        min_level-=1

    while min_level > 1:
        tmp_nodes=[]
        same_parent=True
        for node in nodes:
            tmp_node=node
            while tmp_node.level > min_level:
                tmp_node=tmp_node.parent
            if ref_node is None:
                ref_node=tmp_node
            else:
                if same_parent is True:
                    if tmp_node != ref_node:
                        same_parent=False
                        min_level-=1
            tmp_nodes.append(tmp_node)

        if same_parent is True:
            break
        else:
            nodes=tmp_nodes
        
    if min_level == 1:
        ref_node=nodes[0].root
    
    return dict(
        node=ref_node,
        max_sibling_level=max_level-ref_node.level,
    )

def get_node_from_alias(node, reg_alias, print_usage, prefix, explicit, pretty, cmd_line_index):
    alias=reg_alias.group("alias")
    index=reg_alias.group("index")
    if index is not None:
        index=int(index)

    tmp_node=None
    if alias in node.dy_aliases:
        if explicit is True:
            if node.dy_aliases[alias]["explicit"] is None:
                tmp_node=None
            else:
                tmp_node=node.dy_aliases[alias]["explicit"]
        else:
            lst_error=[]
            nodes_error=[]
            if node.dy_aliases[alias]["explicit"] is None:
                if len(node.dy_aliases[alias]["implicit"]) == 0:
                    tmp_node=None
                elif len(node.dy_aliases[alias]["implicit"]) == 1:
                    tmp_node=node.dy_aliases[alias]["implicit"][0]
                else:
                    lst_error=[
                        "explicit notation is needed because alias '{}' is present multiple times in argument's implicit aliases at paths:".format(alias)
                    ]
                    for imp_dfn in node.dy_aliases[alias]["implicit"]:
                        lst_error.append(get_explicit_path(node, imp_dfn, alias))
                        nodes_error.append(imp_dfn)

                    nodes_error.append(node)
            else:
                if len(node.dy_aliases[alias]["implicit"]) == 0:
                    tmp_node=node.dy_aliases[alias]["explicit"]
                else:
                    lst_error=[
                        "explicit notation is needed because alias '{}' is present multiple times in argument's explicit aliases and implicit aliases at paths:".format(alias)
                    ]
                    
                    for imp_dfn in node.dy_aliases[alias]["implicit"]:
                        lst_error.append(get_explicit_path(node, imp_dfn, alias))
                        nodes_error.append(imp_dfn)

                    lst_error.append(get_explicit_path(node, node.dy_aliases[alias]["explicit"], alias))
                    nodes_error.append(node.dy_aliases[alias]["explicit"])

            if len(lst_error) > 0:
                msg.error(lst_error, prefix=get_arg_prefix(prefix, node, wvalues=False), pretty=pretty)
                closest=get_closest_parent(nodes_error)
                print_usage(closest["node"], closest["max_sibling_level"])
                sys.exit(1)
          
        if tmp_node is not None:
            if reg_alias.group("values") is not None:
                cmd_line_index=cmd_line_index-len(reg_alias.group("values"))
            
            set_node(alias, tmp_node, print_usage, prefix, pretty, cmd_line_index, index)
            process_values(reg_alias, tmp_node, print_usage, prefix, pretty, cmd_line_index)
            
    return tmp_node

# def get_values_str_from_reg(reg_alias):
#     values_str=""
#     for tmp_value in [
#         reg_alias.group("dquotes"),
#         reg_alias.group("squotes"),
#         reg_alias.group("nquotes"),
#     ]:
#         if tmp_value is not None:
#             values=tmp_value
#             break
#     return values_str


def process_values(reg_alias, tmp_node, print_usage, prefix, pretty, cmd_line_index):
    values=[]
    for tmp_value in [
        reg_alias.group("dquotes"),
        reg_alias.group("squotes"),
        reg_alias.group("nquotes"),
    ]:
        if tmp_value is not None:
            values=shlex.split(tmp_value)
            break

    if len(values) > 0:
        if tmp_node.dy["value_required"] is None:
            msg.error("values are not allowed {}.".format(values), prefix=get_arg_prefix(prefix, tmp_node, wvalues=False), pretty=pretty)
            print_usage(tmp_node)
            sys.exit(1)
        else:
            for v, value in enumerate(values):
                add_value(tmp_node, value, print_usage, prefix, pretty, cmd_line_index)

def get_node_from_flags(reg_flags, node, print_usage, prefix, pretty, cmd_line_index):
    dy_reg=reg_flags.groupdict()
    unknown_chars=set(dy_reg["chars"])-set(sorted(node.dy_flags))
    if len(unknown_chars) > 0:
        msg.error("In flags set '{}' unknown char(s) {}.".format(reg_flags.string, list(unknown_chars)), prefix=get_arg_prefix(prefix, node, wvalues=False), pretty=pretty)
        print_usage(node)
        sys.exit(1)

    tmp_node=None
    index=None
    if dy_reg["values"] is not None:
        cmd_line_index-=len(dy_reg["values"])
    if dy_reg["index_str"] is not None:
        cmd_line_index-=len(dy_reg["index_str"])

    cmd_line_index=cmd_line_index-len(dy_reg["chars"])
    for i, c in enumerate(dy_reg["chars"]):
        cmd_line_index+=1
        is_last=i+1==len(dy_reg["chars"])
        if is_last is True:
            if dy_reg["index_str"] is not None:
                cmd_line_index+=len(dy_reg["index_str"])
            if dy_reg["index"] is not None:
                index=int(dy_reg["index"])

        tmp_node=node.dy_flags[c]
        alias=tmp_node.dy["flags_aliases"][c]
        set_node(alias, tmp_node, print_usage, prefix, pretty, cmd_line_index, index)

        if is_last is True:
            process_values(reg_flags, tmp_node, print_usage, prefix, pretty, cmd_line_index)

    return tmp_node

def get_args(
    app_name,
    cmd,
    dy_metadata,
    node_dfn,
    pretty_msg,
    pretty_help,
    substitute,
    theme,
    usage_on_root,
    get_documentation,
    verbose,
    cmd_provided=False,
):
    prefix="For '{}' at Nargs on the command-line".format(app_name)

    if node_dfn is None:
        msg.warning("get_args returns None due to either arguments empty definition or disabled root argument.", prefix=prefix, pretty=pretty_msg)
        return None

    def print_usage(node_dfn, max_sibling_level=1):
        get_help_usage(
            dy_metadata=dy_metadata,
            node_ref=node_dfn,
            output="cmd_usage",
            style=Style(pretty_help=pretty_help, pretty_msg=pretty_msg, output="cmd_usage", theme=theme),
            max_sibling_level=max_sibling_level,
            verbose=verbose,
        )

    from_sys_argv=False
    if cmd is None:
        from_sys_argv=True
        cmd=sys.argv
    else:
        if not isinstance(cmd, str):
            msg.error("cmd type {} must be type {}.".format(type(cmd), str), prefix=prefix, pretty=pretty_msg, exit=1)
        cmd_provided=True
        cmd=shlex.split(cmd)

    cmd_line=" ".join(cmd)

    if len(cmd) == 0:
        msg.error("command must have at least the root argument set.", prefix=prefix, pretty=pretty_msg, exit=1)

    if substitute is True:
        tmp_cmd=[]
        for elem in cmd:
            elem=re.sub(r"(?:__(?P<input>input|hidden)__|__((?P<input_label>input|hidden)(?::))?(?P<label>[a-zA-Z][a-zA-Z0-9]*)__)", lambda m: get_substitute_var(m), elem)
            tmp_cmd.append(elem)
        cmd=tmp_cmd

    at_start=True
    after_explicit=False
    builtin_dfn=None
    node_before_usage=None
    after_concat=False
    trigger_usage_on_root=usage_on_root is True and len(cmd) == 1

    cmd_line_index=0
    elem=None
    while len(cmd) > 0:
        if elem is not None:
            cmd_line_index+=1
        elem=cmd.pop(0)

        cmd_line_index+=len(elem)
        # print(cmd_line[:cmd_line_index])
        
        is_last_elem=len(cmd) == 0
        if at_start is True:
            at_start=False

            elem=os.path.basename(elem)
            enable_arg(node_dfn, elem, prefix, pretty_msg, cmd_line_index)
            node_dfn.current_arg._cmd_line=cmd_line

            if from_sys_argv is False:
                if elem not in node_dfn.dy["aliases"]:
                    msg.error("For provided cmd, root argument alias '{}' not found in {}.".format(elem, sorted(node_dfn.dy["aliases"])), prefix=get_arg_prefix(prefix, node_dfn, wvalues=False), pretty=pretty_msg)
                    print_usage(node_dfn)
                    sys.exit(1)
            
            if trigger_usage_on_root is True:
                if len(node_dfn.dy["required_children"]) > 0:
                    process_required(node_dfn, node_dfn.current_arg, print_usage, prefix, pretty_msg)
                print_usage(node_dfn)
                sys.exit(1)
        else:
            if after_explicit is False:
                reg_explicit=re.match(get_regex("cli_explicit")["rule"], elem)
                if reg_explicit:
                    if is_last_elem is True:
                        msg.error("command must finish with an argument or a value not an explicit notation '{}'.".format(elem), prefix=get_arg_prefix(prefix, node_dfn, wvalues=False, cmd_line_index=cmd_line_index), pretty=pretty_msg)
                        print_usage(node_dfn)
                        sys.exit(1)

                    if reg_explicit.group("minus") is None:
                        level_up=0
                        if reg_explicit.group("equal") is not None:
                            level_up=1
                        elif reg_explicit.group("plus_concat") is not None:
                            level_up=len(reg_explicit.group("plus_concat"))+1
                        else:
                            level_up=int(reg_explicit.group("plus_index"))+1

                        level_up=node_dfn.level - level_up
                        if  level_up < 1:
                            msg.error("explicit level '{}' out of bound. Level value '{}' is lower than limit '1'.".format(elem, level_up), prefix=get_arg_prefix(prefix, node_dfn, wvalues=False), pretty=pretty_msg, exit=1)

                        while node_dfn.level != level_up:
                            node_dfn=node_dfn.parent

                    after_explicit=True
                    continue

            reg_alias=re.match(get_regex("cli_alias")["rule"], elem)
            if reg_alias:
                alias=reg_alias.group("alias")

                node_from_alias=get_node_from_alias(node_dfn, reg_alias, print_usage, prefix, explicit=after_explicit, pretty=pretty_msg, cmd_line_index=cmd_line_index)

                if node_from_alias is None:
                    if after_explicit is True:
                        msg.error("unknown argument '{}'.".format(alias), prefix=get_arg_prefix(prefix, node_dfn, wvalues=False, cmd_line_index=cmd_line_index), pretty=pretty_msg)
                        print_usage(node_dfn)
                        sys.exit(1)
                    else:
                        if node_dfn.dy["value_required"] is None:
                            msg.error("unknown input '{}'.".format(alias), prefix=get_arg_prefix(prefix, node_dfn, wvalues=False), pretty=pretty_msg)
                            print_usage(node_dfn)
                            sys.exit(1)
                        else:
                            add_value(node_dfn, elem, print_usage, prefix, pretty_msg, cmd_line_index)
                else:
                    node_dfn, node_before_usage, builtin_dfn =get_builtin_dfn(node_dfn, node_from_alias, builtin_dfn, node_before_usage)

            else:
                reg_flags=re.match(get_regex("cli_flags")["rule"], elem)
                if reg_flags:
                    node_from_flags=get_node_from_flags(reg_flags, node_dfn, print_usage, prefix, pretty_msg, cmd_line_index)
                    node_dfn, node_before_usage, builtin_dfn =get_builtin_dfn(node_dfn, node_from_flags, builtin_dfn, node_before_usage)
                else:
                    if after_explicit is True:
                        msg.error("unknown argument '{}'".format(elem), prefix=get_arg_prefix(prefix, node_dfn, wvalues=False), pretty=pretty_msg)
                        print_usage(node_dfn)
                        sys.exit(1)
                    else:
                        if node_dfn.dy["value_required"] is None:
                            msg.error("unknown input '{}'.".format(elem), prefix=get_arg_prefix(prefix, node_dfn, wvalues=False), pretty=pretty_msg)
                            print_usage(node_dfn)
                            sys.exit(1)
                        else:
                            add_value(node_dfn, elem, print_usage, prefix, pretty_msg, cmd_line_index)

            if after_explicit is True:
                after_explicit=False

    last_check(
        node_dfn.root,
        print_usage,
        prefix,
        builtin_dfn,
        pretty_msg,
    )

    if builtin_dfn is None:
        clean_builtins(node_dfn.root)
        return node_dfn.root.current_arg._forks[0]
    else:
        builtin_arg=builtin_dfn.current_arg
        if builtin_arg._name == "_cmd_":
            if cmd_provided is True:
                msg.error("Nargs built-in ':cmd' argument can't be provided more than once.", prefix=prefix, pretty=pretty_msg, exit=1)
            lines=[]
            with open(builtin_arg._value, "r") as f:
                for line in f.read().splitlines():
                    line=line.strip()
                    if len(line) > 0 and line[0] != "#":
                        lines.append(line)

            cmd=" ".join(lines)
            reset_dfn(node_dfn.root)
            get_args(
                app_name=app_name,
                cmd=cmd,
                dy_metadata=dy_metadata,
                node_dfn=node_dfn.root,
                pretty_help=pretty_help,
                pretty_msg=pretty_msg,
                substitute=substitute,
                theme=theme,
                usage_on_root=usage_on_root,
                get_documentation=get_documentation,
                verbose=verbose,
                cmd_provided=True,
            )
        elif builtin_arg._name == "_help_":
            if builtin_arg.metadata._here is True:
                for arg_name in ["export", "syntax"]:
                    if builtin_arg._[arg_name]._here is True:
                        msg.error("argument '{}' can't be used with argument '{}'.".format(builtin_arg._[arg_name]._alias, builtin_arg.metadata._alias), prefix=get_arg_prefix(prefix, builtin_dfn, wvalues=False), pretty=pretty_msg, exit=1)
                
                get_values=builtin_arg.metadata.get._alias in ["-v", "--value", "--values"]
                get_keys=builtin_arg.metadata.get._alias in ["-k", "--key", "--keys"]
                to_json=builtin_arg.metadata.json._here

                data=None
                is_list=get_values is True or get_keys is True
                if is_list is True:
                    data=[]
                else:
                    data=dict()

                keys=None
                have_custom_keys=len(builtin_arg.metadata._values) == 0
                if have_custom_keys is True:
                    keys=sorted(dy_metadata)
                else:
                    keys=builtin_arg.metadata._values

                for key in keys:
                    if have_custom_keys is True:
                        if key not in dy_metadata:
                            msg.error("metadata key '{}' not found in {}.".format(key, sorted(dy_metadata)), prefix=get_arg_prefix(prefix, builtin_dfn, wvalues=False), pretty=pretty_msg, exit=1)

                    if get_keys is True:
                        data.append(key)
                    else:
                        value=dy_metadata[key]

                        if get_values is True:
                            data.append(value)
                        else:
                            data[key]=value

                if to_json is True:
                    print(json.dumps(data, sort_keys=True, indent=4))
                else:
                    if is_list is True:
                        for value in data:
                            if isinstance(value, dict):
                                value=json.dumps(value, sort_keys=True)
                            print(value)
                    else:
                        for key in sorted(data):
                            value=data[key]
                            if isinstance(value, dict):
                                value=json.dumps(value, sort_keys=True)
                            print("{}: {}".format(key, value))
                    sys.exit(0)
            else:
                output="cmd_help"
                if builtin_arg.export._here is True:
                    output=builtin_arg.export._value
                get_documentation(
                    output=output,
                    filenpa=builtin_arg.export.to._value,
                    wsyntax=builtin_arg.syntax._here,
                )
                sys.exit(0)

        elif builtin_arg._name == "_usage_":
            tmp_node=node_before_usage
            from_=builtin_arg.from_._value
            if from_ < -1:
                tmp_node_dfn=builtin_dfn.dy_aliases[builtin_arg.from_._alias]["explicit"]
                msg.error("from LEVEL '{}' must be greater or equal than '-1'.".format(from_), prefix=get_arg_prefix(prefix, tmp_node_dfn, wvalues=False), pretty=pretty_msg, exit=1)

            if from_ == 0:
                tmp_node=node_before_usage
            else:
                count=0
                while tmp_node.parent is not None:
                    tmp_node=tmp_node.parent
                    count+=1
                    if count == from_:
                        break

            depth=builtin_arg.depth._value
            if depth < -1:
                tmp_node_dfn=builtin_dfn.dy_aliases[builtin_arg.depth._alias]["explicit"]
                msg.error("depth LEVEL '{}' must be greater or equal than '-1'.".format(builtin_arg.depth._value), prefix=get_arg_prefix(prefix, tmp_node_dfn, wvalues=False), pretty=pretty_msg, exit=1)

            if depth == -1:
                depth=None

            get_help_usage(
                dy_metadata=dy_metadata,
                node_ref=tmp_node,
                output="cmd_usage",
                style=Style(pretty_help=pretty_help, pretty_msg=pretty_msg, output="cmd_usage", theme=theme),
                max_sibling_level=depth,
                wpath=builtin_arg.path._here,
                whint=builtin_arg.hint._here,
                winfo=builtin_arg.info._here,
                wexamples=builtin_arg.examples._here,
            )
            sys.exit(0)

def get_builtin_dfn(previous_node_dfn, node_dfn, builtin_dfn, node_before_usage):
    if node_dfn.dy["is_builtin"] is True and node_dfn.level == 2:
        if node_dfn.name == "_usage_":
            node_before_usage=previous_node_dfn
        builtin_dfn=node_dfn
    return node_dfn, node_before_usage, builtin_dfn

def clean_builtins(node_dfn):
    del_nodes=[]
    if node_dfn.is_root is True:
        for node in node_dfn.nodes:
            if node.dy["is_builtin"] is True:
                clean_builtins(node)
                del_nodes.append(node)
    else:
        for node in node_dfn.nodes:
            clean_builtins(node)
            del_nodes.append(node)

    for del_node in del_nodes.copy():
        if del_node.current_arg is not None:
            for arg_node in del_node.current_arg._forks.copy():
                del_node.current_arg._forks.remove(arg_node)
        del_nodes.remove(del_node)
    del del_nodes

def follow_builtin(builtin_dfn, node_dfn):
    if builtin_dfn is not None:
        if node_dfn.dy["is_builtin"] is True:
            if node_dfn == builtin_dfn or builtin_dfn in node_dfn.parents:
                return True
    return False

def is_related_builtin_fork(builtin_dfn, arg):
    builtin_arg=builtin_dfn.current_arg._forks[0]
    if arg == builtin_arg:
        return True

    parent_arg=arg
    while True:
        parent_arg=parent_arg._parent
        if parent_arg is None:
            break
        elif parent_arg == builtin_arg:
            return True
    return False

def last_check(
    node_dfn,
    print_usage,
    prefix,
    builtin_dfn,
    pretty,
):
    is_builtin=follow_builtin(builtin_dfn, node_dfn)
    check_props=(builtin_dfn is None) or is_builtin
    recurse=(node_dfn.is_root is True) or check_props

    if check_props is True:
        for arg in node_dfn.current_arg._forks:
            if is_builtin is True:
                check_arg=is_builtin is True and is_related_builtin_fork(builtin_dfn, arg)
                if check_arg is False:
                    break

            if node_dfn.dy["value_required"] is not None:
                values_final_check(node_dfn, arg, print_usage, prefix, pretty)

            if len(node_dfn.dy["required_children"]) > 0:
                process_required(node_dfn, arg, print_usage, prefix, pretty)

    if recurse is True:
        for tmp_node in node_dfn.nodes:
            if len(tmp_node.current_arg._forks) > 0:
                last_check(
                    tmp_node,
                    print_usage,
                    prefix,
                    builtin_dfn,
                    pretty,
                )

def get_prompted_value(input_type, label=None):
    if label is None:
        label=input_type
    if input_type == "input":
        return input(label+": ")
    elif input_type == "hidden":
        return getpass.getpass(label+": ")

def get_substitute_var(reg):
    dy=reg.groupdict()
    if dy["input"] is not None:
        return get_prompted_value(dy["input"])
    elif dy["input_label"] is not None:
        return get_prompted_value(dy["input_label"], dy["label"])
    else:
        if dy["label"] in os.environ:
            value=os.environ[dy["label"]].strip()
            return re.sub(r"^\"?(.*?)\"?$", r"\1", value)
        else:
            return reg.group()

def reset_dfn(node):
    arg=node.current_arg
    if len(arg._forks) > 0:
        default_alias=arg._default_alias
        for f, arg_fork in enumerate(arg._forks.copy()):
            arg._forks.remove(arg_fork)
        
    node.set_arg("reset")
    for tmp_node in node.nodes:
        reset_dfn(tmp_node)

def process_required(parent_dfn, parent_arg, print_usage, prefix, pretty):
    for child_name in parent_dfn.dy["required_children"]:
        required_arg=parent_arg._[child_name]
        if required_arg._here is False:
            required_dfn=None
            for tmp_required_dfn in parent_dfn.nodes:
                if tmp_required_dfn.name == child_name:
                    required_dfn=tmp_required_dfn
                    break

            cmd_line_index=parent_arg._cmd_line_index
            if required_dfn.dy["value_required"] is True: 
                if required_dfn.dy["default"] is None:
                    prefix=get_arg_prefix(prefix, parent_dfn, wvalues=False)
                    msg.error("required argument '{}' is missing.".format(required_arg._default_alias), prefix=prefix, pretty=pretty)
                    print_usage(parent_dfn)
                    sys.exit(1)
                else:
                    enable_arg(required_dfn, required_dfn.dy["default_alias"], prefix, pretty, cmd_line_index)
                    values_final_check(required_dfn, required_arg, print_usage, prefix, pretty)
            else:
                enable_arg(required_dfn, required_dfn.dy["default_alias"], prefix, pretty, cmd_line_index)
            process_required(required_dfn, required_arg, print_usage, prefix, pretty)

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


