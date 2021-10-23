#!/usr/bin/env python3
from pprint import pprint
import json
import getpass
import os
import re
import shlex
import sys
import traceback

from .nodes import CliArg
from .get_json import get_json, get_arg_prefix
from .get_path import get_path
from .help import get_help_usage
from .regexes import get_regex
from .style import Style

from ..gpkgs import message as msg

def set_arg(node, alias, cmd_line_index, is_implicit):
    # print("set_arg:", node.name)
    if node.is_root is False:
        node.current_arg._parent._args.append(node.current_arg)

    node.current_arg._alias=alias
    node.current_arg._count+=1
    node.current_arg._implicit=is_implicit
    node.current_arg._cmd_line_index=cmd_line_index
    node.current_arg._dy_indexes["aliases"][cmd_line_index]=alias

def get_first_sibling(arg, node_dfn):
    if arg._is_root is True:
        return None, None
    elif arg._name == "_usage_":
        return None, None
    else:
        for name in arg._parent._:
            if name not in [arg._name, "_usage_"]:
                sibling_arg=arg._parent._[name]
                if sibling_arg._here is True:
                    sibling_dfn=node_dfn.parent.dy_nodes[sibling_arg._name]
                    return sibling_arg, sibling_dfn

        return None, None

def activate_arg(node, alias, dy_error, cmd_line_index, is_implicit=False):
    node.current_arg._here=True
    set_arg(node, alias, cmd_line_index, is_implicit=is_implicit)

    if node.is_root is True:
        if node.current_arg._branches.index(node.current_arg) == 0:
            node.current_arg._cmd_line=dy_error["cmd_line"]
    else:
        if is_implicit is False:
            if node in node.parent.dy_xor:
                for group_num in sorted(node.parent.dy_xor[node]):
                    for tmp_node_dfn in node.parent.dy_xor[node][group_num]:

                        tmp_arg=node.current_arg._parent._[tmp_node_dfn.name]
                        if tmp_arg._here is True:
                            msg.error([
                                "XOR conflict, the two following arguments can't be provided at the same time:",
                                "- {}".format(node.current_arg._get_path()),
                                "- {}".format(tmp_arg._get_path()),
                            ]
                            , prefix=get_arg_prefix(dy_error, node.parent.current_arg._cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
                            sys.exit(1)

            if node.dy["allow_parent_fork"] is False:
                if len(node.current_arg._parent._branches) > 1:
                    msg.error(
                        [
                            "argument '{}' property 'allow_parent_fork' is set to '{}' but parent argument has more than one branch:".format(node.current_arg._alias, False),
                            *[arg._get_path() for arg in node.current_arg._parent._branches],
                        ], prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"], exit=1)

            if len(node.current_arg._parent._args) >= 2:
                if node.dy["allow_siblings"] is True:
                    if len(node.current_arg._parent._args) in [2, 3]:
                        sibling_arg, sibling_dfn=get_first_sibling(node.current_arg, node)
                        if sibling_arg is not None:
                            if node.dy["allow_siblings"] is True:
                                if sibling_dfn.dy["allow_siblings"] is False:
                                    msg.error(
                                        [
                                            "argument '{}' can't be added because it already has a sibling argument with property 'allow_siblings' set to '{}':".format(node.current_arg._alias, False),
                                            sibling_arg._get_path(),
                                        ], prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"], exit=1
                                    )
                else:
                    sibling_arg, sibling_dfn=get_first_sibling(node.current_arg, node)
                    if sibling_arg is not None:
                        msg.error(
                            [
                                "argument '{}' property 'allow_siblings' is set to '{}' but at least one sibling is present already:".format(node.current_arg._alias, False),
                                sibling_arg._get_path(),
                            ], prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"], exit=1
                        )

def check_values_min(node_dfn, arg, dy_error):
    if node_dfn.dy["value_min"] is not None:
        if len(arg._values) < node_dfn.dy["value_min"]:
            if node_dfn.dy["value_min"] == 1:
                msg.error("argument '{}' needs at least one value.".format(arg._alias), prefix=get_arg_prefix(dy_error, arg._cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
            else:
                msg.error("argument '{}' minimum values '{}' is less than '{}'.".format(arg._alias, len(arg._values), node_dfn.dy["value_min"]), prefix=get_arg_prefix(dy_error, arg._cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
            dy_error["print_usage"](node_dfn)
            sys.exit(1)

def values_final_check(node_dfn, arg, dy_error, is_implicit=False):
    if len(arg._values) > 0:
        if is_implicit is False:
            check_values_min(node_dfn, arg, dy_error)
    else:
        if node_dfn.dy["value_required"] is True:
            if node_dfn.dy["default"] is None:
                if is_implicit is False:
                    check_values_min(node_dfn, arg, dy_error)
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
    dy_error,
    cmd_line_index,
):
    arg=node.current_arg
    if node.dy["value_max"] is not None:
        if len(arg._values) >= node.dy["value_max"]:
            msg.error("value '{}' can't be added. Maximum number of values '{}' has been reached already.".format(value, node.dy["value_max"]), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
            dy_error["print_usage"](node)
            sys.exit(1)

    if isinstance(node.dy["type"], str):
        if node.dy["type"] in [ ".json", "json" ]:
            tmp_value=get_json(
                value,
                node,
                dy_error,
                cmd_line_index,
                search_file="." in node.dy["type"], 
            )
        elif node.dy["type"] in [ "dir", "file", "path", "vpath" ]:
            tmp_value=get_path(node, value, node.dy["type"], dy_error, cmd_line_index)
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
            msg.error("argument '{}' value '{}' type error. It must match type '{}'.".format(node.current_arg._alias, value, node.dy["type"]), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
            dy_error["print_usage"](node)
            sys.exit(1)

    value=tmp_value

    if node.dy["in"] is not None:
        if value not in node.dy["in"]:
            msg.error("value '{}' not found in {}.".format(value, node.dy["in"]), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
            dy_error["print_usage"](node)
            sys.exit(1)

    if arg._value is None:
        arg._value=value
    arg._values.append(value)
    arg._dy_indexes["values"].append(cmd_line_index)

def set_node(alias, node, dy_error, cmd_line_index, branch_num):
    
    enabled_branches=[branch for branch in node.current_arg._branches if branch._here is True]
    has_one_enabled_branch=(len(enabled_branches) > 0)
    increment=(branch_num == "_")
    if branch_num is None:
        if has_one_enabled_branch is True:
            branch_num=len(node.current_arg._branches)
        else:
            branch_num=1
    elif branch_num == "_":
        if has_one_enabled_branch is True:
            branch_num=len(node.current_arg._branches)+1
        else:
            branch_num=1
    else:
        pass

    # print("set_node:", node.name, branch_num, node.current_arg._branches, len(node.current_arg._branches)+1)

    

    if branch_num > len(enabled_branches)+1:
        msg.error("argument branch '{}' number '_{}' is too big. Biggest branch number available is '_{}'.".format(alias, branch_num, len(node.current_arg._branches)+1), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
        sys.exit(1)

    
    is_new_enabled_branch=(branch_num == len(enabled_branches)+1)

    if is_new_enabled_branch is True:
        if has_one_enabled_branch is True:
            if node.dy["fork"] is True:
                for branch in node.current_arg._branches:
                    for arg in branch._args:
                        tmp_node=node.dy_nodes[arg._name]
                        if tmp_node.dy["allow_parent_fork"] is False:
                            msg.error("argument '{}' can't be forked because its child argument '{}' property 'allow_parent_fork' is set to '{}'.".format(alias, tmp_node.current_arg._alias, False), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"], exit=1)
                
                parent_arg=None
                if node.current_arg._is_root is False:
                    parent_arg=node.current_arg._parent
                create_branch(node, node.current_arg._branches, parent_arg, dy_error["cmd_line"])
            else:
                if increment is True:
                    msg.error("A new branch can't be created for argument '{}' using notation '_' because one branch already exists and argument 'fork' property is set to '{}'.".format(alias, node.dy["fork"]), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
                else:
                    msg.error("argument '{}' wrong branch number '_{}'. Only '_1' is authorized when 'fork' property is set to '{}'.".format(alias, branch_num, node.dy["fork"]), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
                dy_error["print_usage"](node)
                sys.exit(1)
        activate_arg(node, alias, dy_error, cmd_line_index)
    else: # branch_num < len(node.current_arg._branches)+1 (only for existing branches)
        if node.dy["repeat"] == "error":
            msg.error("argument '{}' can't be repeated because its 'repeat' property is set to '{}'.".format(alias, node.dy["repeat"]), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
            dy_error["print_usage"](node)
            sys.exit(1)
        else:
            current_branch_num=node.current_arg._branches.index(node.current_arg)+1
            if current_branch_num != branch_num:
                node.current_arg=node.current_arg._branches[branch_num-1]
            if node.dy["repeat"] == "append":
                if node.is_root is False:
                    node.current_arg._parent._args.remove(node.current_arg)
                set_arg(node, alias, cmd_line_index, is_implicit=False)
            elif node.dy["repeat"] == "replace":
                branches=node.current_arg._branches
                branch_index=branches.index(node.current_arg)

                # print(node.current_arg._name)

                delete_branch(node.current_arg)
                
                parent_arg=None
                if node.current_arg._is_root is False:
                    parent_arg=node.current_arg._parent
                create_branch(node, branches, parent_arg, dy_error["cmd_line"], branch_index)

                # branches.remove(node.current_arg)
                # branches.insert(branch_index, node.current_arg)

                activate_arg(node, alias, dy_error, cmd_line_index)



def create_branch(node, branches, parent_arg, cmd_line, branch_index=None):
    new_arg=CliArg(
        node.dy["aliases"],
        node.dy["default_alias"],
        node.name,
        branches=branches,
        cmd_line=cmd_line,
        parent=parent_arg,
        branch_index=branch_index,
    )

    node.current_arg=new_arg
    for child_node in node.nodes:
        create_branch(node=child_node, branches=[], parent_arg=new_arg, cmd_line=cmd_line, branch_index=branch_index)

def delete_branch(arg):
    for child_name in sorted(arg._):
        child_arg=arg._[child_name]
        for branch in child_arg._branches:
            delete_branch(branch)

    arg._branches.remove(arg)
    if arg._parent is not None:
        if arg in arg._parent._args:
            arg._parent._args.remove(arg)
        
        # if arg._name in arg._parent._:
        #     del arg._parent._[arg._name]
        #     delattr(arg._parent, arg._name)

    del arg._
    del arg._aliases
    del arg._args
    del arg._dy_indexes
    del arg._values
    del arg._branches
    del arg

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
        node_dfn.current_arg._get_path(),
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

def get_node_from_alias(
    node,

    alias,
    branch_num,
    values,

    explicit,
    dy_error,
    cmd_line_index,
):
    # alias=reg_alias.group("alias")
    # branch_num=reg_alias.group("branch_num")
    # if reg_alias.group("branch_num_str") is not None:
    #     if reg_alias.group("branch_num") is None:
    #         branch_num=reg_alias.group("branch_num_str")
    #     else:
    #         branch_num=int(branch_num)

    tmp_node=None
    # print()
    # print("here", node.name, alias)
    # pprint(node.dy_aliases)
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
                msg.error(lst_error, prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
                closest=get_closest_parent(nodes_error)
                dy_error["print_usage"](closest["node"], closest["max_sibling_level"])
                sys.exit(1)
          
        if tmp_node is not None:
            # if reg_alias.group("values") is not None:
            #     cmd_line_index=cmd_line_index-len(reg_alias.group("values_str"))
            
            set_node(alias, tmp_node, dy_error, cmd_line_index, branch_num)
            process_values(values, tmp_node, dy_error, cmd_line_index)
            
    return tmp_node

def process_values(values, tmp_node, dy_error, cmd_line_index):
    # print("reg.string:", reg.string)
    # print("reg.values:", reg.group("values"))
    # if reg.group("values") is not None:
    #     values=shlex.split(reg.group("values"))
    if values is not None:
        values=shlex.split(values)

        if len(values) > 0:
            if tmp_node.dy["value_required"] is None:
                msg.error("for argument '{}' values are not allowed {}.".format(tmp_node.current_arg._alias, values), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
                dy_error["print_usage"](tmp_node)
                sys.exit(1)
            else:
                cmd_line=dy_error["cmd_line"]
                for v, value in enumerate(values):
                    cmd_line_index+=len(value)
                    # print("value:", value)
                    while True:
                        if cmd_line_index >= len(cmd_line)-1:
                            cmd_line_index=len(cmd_line)+1
                            break
                        else:
                            cmd_line_index+=1
                            if cmd_line[cmd_line_index] == " ":
                                break
                            
                    # print(cmd_line[:cmd_line_index])
                    add_value(tmp_node, value, dy_error, cmd_line_index)

def get_nodes_from_flags(
    chars,
    branch_num,
    branch_num_str,
    values,
    values_str,
    node_dfn,
    node_before_usage,
    builtin_dfn,
    dy_error,
    cmd_line_index,
):
    tmp_cmd_line_index=cmd_line_index
    if values is not None:
        tmp_cmd_line_index-=len(values_str)

    if branch_num_str is not None:
        tmp_cmd_line_index-=len(branch_num_str)
    tmp_cmd_line_index=tmp_cmd_line_index-len(chars)

    flag_sets=chars.split("@")
    flags_node=node_dfn

    for i, flag_set in enumerate(flag_sets):
        is_last_set=i+1==len(flag_sets)
        unknown_chars=set(flag_set)-set(sorted(flags_node.dy_flags))
        if len(unknown_chars) > 0:
            tmp_cmd_line_index+=len(flag_set)
            msg.error("Unknown char(s) {} in flags set '{}'.".format(list(unknown_chars), node_dfn.dy["flags_notation"]), prefix=get_arg_prefix(dy_error, tmp_cmd_line_index), pretty=dy_error["pretty"], to_raise=dy_error["debug"])
            dy_error["print_usage"](flags_node)
            sys.exit(1)

        for j, c in enumerate(flag_set):
            is_last_char=j+1==len(flag_set)
            tmp_cmd_line_index+=1
            # print("flag:", c)
            # print(cmd_line[:tmp_cmd_line_index])
            if is_last_set and is_last_char is True:
                if branch_num_str is not None:
                    tmp_cmd_line_index+=len(branch_num_str)
                    if branch_num is None:
                        branch_num=branch_num_str
                    else:
                        branch_num=int(branch_num)
                
            # pprint(tmp_node_dfn.dy_flags)
            tmp_node_dfn=flags_node.dy_flags[c]
            alias=tmp_node_dfn.dy["flags_aliases"][c]
            set_node(alias, tmp_node_dfn, dy_error, tmp_cmd_line_index, branch_num)
            # print(node_dfn.name, node_dfn.current_arg)

            if is_last_set and is_last_char is True:
                process_values(values, tmp_node_dfn, dy_error, tmp_cmd_line_index)

            node_dfn, node_before_usage, builtin_dfn =get_builtin_dfn(node_dfn, tmp_node_dfn, builtin_dfn, node_before_usage)

        flags_node=node_dfn
        tmp_cmd_line_index+=1

    return node_dfn, node_before_usage, builtin_dfn

def get_args(
    app_name,
    cmd,
    debug,
    dy_metadata,
    node_dfn,
    path_etc,
    pretty_msg,
    pretty_help,
    substitute,
    theme,
    get_documentation,
    cmd_provided=False,
    reset_dfn_tree=False,
):
    prefix="For '{}' at Nargs on the command-line".format(app_name)

    if node_dfn is None:
        # msg.warning("get_args returns None due to either arguments empty definition or disabled root argument.", prefix=prefix, pretty=pretty_msg)
        return None

    if reset_dfn_tree is True:
        for branch in node_dfn.root.current_arg._branches:
            delete_branch(branch)

    def print_usage(node_dfn, max_sibling_level=1):
        get_help_usage(
            dy_metadata=dy_metadata,
            node_ref=node_dfn,
            output="cmd_usage",
            style=Style(pretty_help=pretty_help, pretty_msg=pretty_msg, output="cmd_usage", theme=theme),
            max_sibling_level=max_sibling_level,
        )

    from_sys_argv=False
    if cmd is None:
        from_sys_argv=True
        cmd=sys.argv
    else:
        if not isinstance(cmd, str):
            msg.error("cmd type {} must be type {}.".format(type(cmd), str), prefix=prefix, pretty=pretty_msg, to_raise=debug, exit=1)
        # cmd_provided=True
        cmd=shlex.split(cmd)

    cmd_line=" ".join(cmd)
    create_branch(node_dfn.root, branches=[], parent_arg=None, cmd_line=cmd_line)


    if len(cmd) == 0:
        msg.error("command must have at least the root argument set.", prefix=prefix, pretty=pretty_msg, to_raise=debug, exit=1)

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

    dy_error=dict(
        cmd_line=cmd_line,
        debug=debug,
        prefix=prefix,
        pretty=pretty_msg,
        print_usage=print_usage,
    )

    cmd_line_index=0
    elem=None
    while len(cmd) > 0:
        if elem is not None:
            cmd_line_index+=1
        elem=cmd.pop(0)

        cmd_line_index+=len(elem)
        
        is_last_elem=len(cmd) == 0
        if at_start is True:
            at_start=False
            elem=os.path.basename(elem)
            if from_sys_argv is True:
                activate_arg(node_dfn, elem, dy_error, cmd_line_index)
                continue

        if after_explicit is False:
            reg_explicit=re.match(get_regex("cli_explicit")["rule"], elem)
            if reg_explicit:
                if is_last_elem is True:
                    msg.error("command must finish with an argument or a value not an explicit notation '{}'.".format(elem), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=pretty_msg, to_raise=debug)
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
                        msg.error("explicit level '{}' out of bound. Level value '{}' is lower than limit '1'.".format(elem, level_up), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=pretty_msg, to_raise=debug, exit=1)

                    while node_dfn.level != level_up:
                        node_dfn=node_dfn.parent

                after_explicit=True
                continue

        reg_alias=re.match(get_regex("cli_alias")["rule"], elem)
        if reg_alias:
            alias=reg_alias.group("alias")
            alias_branch_num=reg_alias.group("branch_num")
            flags_str=reg_alias.group("flags_str")
            values_str=reg_alias.group("values_str")
            if reg_alias.group("branch_num_str") is not None:
                if reg_alias.group("branch_num") is None:
                    alias_branch_num=reg_alias.group("branch_num_str")
                else:
                    alias_branch_num=int(alias_branch_num)

            tmp_values=reg_alias.group("values")
            alias_cmd_line_index=cmd_line_index

            if tmp_values is not None:
                alias_cmd_line_index=cmd_line_index-len(values_str)
            
            alias_values=None
            if flags_str is None:
                alias_values=tmp_values
            else:
                alias_cmd_line_index-=len(flags_str)

            node_from_alias=get_node_from_alias(
                node_dfn,
                alias,
                alias_branch_num,
                alias_values,
                after_explicit,
                dy_error,
                alias_cmd_line_index,
            )

            if node_from_alias is None:
                if after_explicit is True or (reg_alias.group("prefix") is not None and len(reg_alias.group("prefix"))) > 0:
                    msg.error("unknown argument '{}'.".format(alias), prefix=get_arg_prefix(dy_error, alias_cmd_line_index), pretty=pretty_msg, to_raise=debug)
                    print_usage(node_dfn)
                    sys.exit(1)
                else:
                    if node_dfn.dy["value_required"] is None:
                        msg.error("unknown input '{}'.".format(alias), prefix=get_arg_prefix(dy_error, alias_cmd_line_index), pretty=pretty_msg, to_raise=debug)
                        print_usage(node_dfn)
                        sys.exit(1)
                    else:
                        add_value(node_dfn, elem, dy_error, cmd_line_index)
            else:
                node_dfn, node_before_usage, builtin_dfn =get_builtin_dfn(node_dfn, node_from_alias, builtin_dfn, node_before_usage)

                if flags_str is not None:
                    flags_branch_num=reg_alias.group("branch_num2")
                    flags_branch_num_str=reg_alias.group("branch_num_str2")
                    chars=reg_alias.group("chars")
                    flags_values=tmp_values

                    node_dfn, node_before_usage, builtin_dfn = get_nodes_from_flags(
                        chars,
                        flags_branch_num,
                        flags_branch_num_str,
                        flags_values,
                        values_str,
                        node_dfn,
                        node_before_usage,
                        builtin_dfn,
                        dy_error,
                        cmd_line_index,
                    )
        else:
            reg_flags=re.match(get_regex("cli_flags")["rule"], elem)
            if reg_flags:
                branch_num=reg_flags.group("branch_num")
                branch_num_str=reg_flags.group("branch_num_str")
                chars=reg_flags.group("chars")
                values=reg_flags.group("values")
                values_str=reg_flags.group("values_str")

                node_dfn, node_before_usage, builtin_dfn = get_nodes_from_flags(
                    chars,
                    branch_num,
                    branch_num_str,
                    values,
                    values_str,
                    node_dfn,
                    node_before_usage,
                    builtin_dfn,
                    dy_error,
                    cmd_line_index,
                )

            else:
                if after_explicit is True:
                    msg.error("unknown argument '{}'".format(elem), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=pretty_msg, to_raise=debug)
                    print_usage(node_dfn)
                    sys.exit(1)
                else:
                    if node_dfn.dy["value_required"] is None:
                        msg.error("unknown input '{}'.".format(elem), prefix=get_arg_prefix(dy_error, cmd_line_index), pretty=pretty_msg, to_raise=debug)
                        print_usage(node_dfn)
                        sys.exit(1)
                    else:
                        add_value(node_dfn, elem, dy_error, cmd_line_index)

        if after_explicit is True:
            after_explicit=False

    if builtin_dfn is not None and builtin_dfn.name == "_usage_":
        last_check(
            builtin_dfn,
            builtin_dfn.current_arg,
            dy_error,
        )
    else:
        for branch in node_dfn.root.current_arg._branches:
            last_check(
                node_dfn.root,
                branch,
                dy_error,
            )

    if builtin_dfn is None:
        # clean_builtins(node_dfn.root)
        return node_dfn.root.current_arg._branches[0]
    else:
        builtin_arg=builtin_dfn.current_arg
        if builtin_arg._name == "_cmd_":
            if cmd_provided is True:
                msg.error("Nargs built-in 'cmd' argument with alias '{}' can't be provided more than once.".format(builtin_arg._alias), prefix=get_arg_prefix(dy_error, builtin_arg._cmd_line_index), pretty=pretty_msg, exit=1, to_raise=debug)
            lines=[]
            with open(builtin_arg._value, "r") as f:
                for line in f.read().splitlines():
                    line=line.strip()
                    if len(line) > 0 and line[0] != "#":
                        lines.append(line)

            cmd=" ".join(lines)

            get_args(
                app_name=app_name,
                cmd=cmd,
                debug=debug,
                dy_metadata=dy_metadata,
                node_dfn=node_dfn.root,
                path_etc=path_etc,
                pretty_help=pretty_help,
                pretty_msg=pretty_msg,
                substitute=substitute,
                theme=theme,
                get_documentation=get_documentation,
                cmd_provided=True,
                reset_dfn_tree=True,
            )
        elif builtin_arg._name == "_help_":
            if builtin_arg.metadata._here is True:
                get_values=builtin_arg.metadata.values._here is True
                get_keys=builtin_arg.metadata.keys._here is True
                to_json=builtin_arg.metadata.json._here

                data=None
                is_list=get_values is True or get_keys is True
                if is_list is True:
                    data=[]
                else:
                    data=dict()

                keys=None
                has_user_keys=len(builtin_arg.metadata._values) > 0
                if has_user_keys is True:
                    keys=builtin_arg.metadata._values
                else:
                    keys=sorted(dy_metadata)

                for key in keys:
                    if has_user_keys is True:
                        if key not in dy_metadata:
                            msg.error("metadata key '{}' not found in {}.".format(key, sorted(dy_metadata)), prefix=get_arg_prefix(dy_error, builtin_arg.metadata._cmd_line_index), pretty=pretty_msg, exit=1, to_raise=debug)

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
                    overwrite=builtin_arg.export.overwrite._here,
                )
                sys.exit(0)
        elif builtin_arg._name == "_path_etc_":
            print(path_etc)
            sys.exit(0)
        elif builtin_arg._name == "_usage_":
            tmp_node=node_before_usage
            from_=builtin_arg.from_._value
            if from_ < -1:
                tmp_node_dfn=builtin_dfn.dy_aliases[builtin_arg.from_._alias]["explicit"]
                msg.error("from LEVEL '{}' must be greater or equal than '-1'.".format(from_), prefix=get_arg_prefix(dy_error, builtin_arg.from_._cmd_line_index), pretty=pretty_msg, to_raise=debug, exit=1)

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
                msg.error("depth LEVEL '{}' must be greater or equal than '-1'.".format(builtin_arg.depth._value), prefix=get_arg_prefix(dy_error, builtin_arg.depth._cmd_line_index), pretty=pretty_msg, to_raise=debug, exit=1)

            if depth == -1:
                depth=None

            allproperties=None
            if builtin_arg.properties._here is True:
                props_node=node_dfn.root.dy_nodes["_usage_"].dy_nodes["properties"]
                allproperties=props_node.dy["in"]

            get_help_usage(
                dy_metadata=dy_metadata,
                node_ref=tmp_node,
                output="cmd_usage",
                style=Style(pretty_help=pretty_help, pretty_msg=pretty_msg, output="cmd_usage", theme=theme),
                max_sibling_level=depth,
                allflags=builtin_arg.flags._here,
                allproperties=allproperties,
                properties=sorted(list(set(builtin_arg.properties._values))),
                wpath=builtin_arg.path._here,
                wproperties=builtin_arg.properties._here,
                whint=builtin_arg.hint._here,
                winfo=builtin_arg.info._here,
                wexamples=builtin_arg.examples._here,
                keep_default_alias=True,
            )
            sys.exit(0)
        elif builtin_arg._name == "_version_":
            if "version" in dy_metadata:
                print(dy_metadata["version"])
                sys.exit(0)
            else:
                msg.error("version not provided.", prefix=prefix, pretty=pretty_msg, to_raise=debug, exit=1)

def last_check(
    node_dfn,
    arg,
    dy_error,
):
    if node_dfn.dy["value_required"] is not None:
        values_final_check(node_dfn, arg, dy_error)

    if len(node_dfn.dy["required_children"]) > 0:
        process_required(node_dfn, arg, dy_error)

    if node_dfn.dy["need_child"] is True:
        if len(arg._args) == 0:
            prefix=get_arg_prefix(dy_error, arg._cmd_line_index)
            msg.error("For argument '{}' at least one child argument is needed.".format(arg._alias), prefix=prefix, pretty=dy_error["pretty"], to_raise=dy_error["debug"])
            dy_error["print_usage"](node_dfn)
            sys.exit(1)

    dy_nodes_dfn=dict()
    for branch_arg in arg._branches:
        for child_name in sorted(branch_arg._):
            child_dfn=None
            if child_name in dy_nodes_dfn:
                child_dfn=dy_nodes_dfn[child_name]
            else:
                child_dfn=node_dfn.dy_nodes[child_name]
                dy_nodes_dfn[child_name]=child_dfn

            child_arg=branch_arg._[child_name]
            if child_arg._here is True:
                last_check(
                    child_dfn,
                    child_arg,
                    dy_error,
                )

def get_builtin_dfn(previous_node_dfn, node_dfn, builtin_dfn, node_before_usage):
    if node_dfn.dy["is_builtin"] is True and node_dfn.level == 2:
        if builtin_dfn is None:
            builtin_dfn=node_dfn
        else:
            if builtin_dfn.name == "_usage_":
                if node_dfn.name == "_usage_":
                    builtin_dfn=node_dfn
            else:
                builtin_dfn=node_dfn

    if node_dfn.name == "_usage_":
        node_before_usage=previous_node_dfn
    
    return node_dfn, node_before_usage, builtin_dfn

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

def process_required(parent_dfn, parent_arg, dy_error, from_implicit=False):
    for child_name in parent_dfn.dy["required_children"]:
        required_arg=parent_arg._[child_name]
        if required_arg._here is False:
            required_dfn=parent_dfn.dy_nodes[child_name]

            cmd_line_index=parent_arg._cmd_line_index
            if required_dfn.dy["value_required"] is True: 
                if from_implicit is False:
                    if required_dfn.dy["default"] is None:
                        prefix=get_arg_prefix(dy_error, required_arg._parent._cmd_line_index)
                        msg.error("required argument '{}' is missing.".format(required_arg._default_alias), prefix=prefix, pretty=dy_error["pretty"], to_raise=dy_error["debug"])
                        dy_error["print_usage"](parent_dfn)
                        sys.exit(1)

            activate_arg(required_dfn, required_dfn.dy["default_alias"], dy_error, cmd_line_index, is_implicit=True)
            values_final_check(required_dfn, required_arg, dy_error, is_implicit=True)
            process_required(required_dfn, required_arg, dy_error, from_implicit=True)

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


