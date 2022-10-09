#!/usr/bin/env python3
from pprint import pprint
import copy
import json
import getpass
import os
import re
import shlex
import sys
import traceback

from .get_properties import get_arg_properties
from .nodes import CliArg
from .get_json import get_json, get_arg_prefix
from .get_path import get_path
from .help import get_help_usage, get_flags_notation
from .nargs_syntax import get_nargs_syntax
from .help import get_md_text

from .regexes import get_regex
from .style import Style


from ..gpkgs import message as msg

def set_arg(arg, alias, cmd_line_index, is_implicit):
    if arg._is_root is False:
        arg._parent._args.append(arg)

    arg._alias=alias
    arg._count+=1
    arg._implicit=is_implicit
    arg._cmd_line_index=cmd_line_index
    arg._dy_indexes["aliases"][cmd_line_index]=alias

def get_first_sibling(arg):
    if arg._is_root is True:
        return None
    elif arg._name == "_usage_":
        return None
    else:
        for name in arg._parent._:
            if name not in [arg._name, "_usage_"]:
                sibling_arg=arg._parent._[name]
                if sibling_arg._here is True:
                    return sibling_arg
        return None

def activate_arg(arg, alias, dy_err, cmd_line_index, dy_chk, is_implicit=False):
    node_dfn=arg._dfn
    arg._here=True
    set_arg(arg, alias, cmd_line_index, is_implicit=is_implicit)

    if is_implicit is False:
        if len(node_dfn.dy["required_children"]) > 0:
            add_chk_property(dy_chk, arg, "chk_required_children")

        if arg._dfn.dy["need_child"] is True:
            add_chk_property(dy_chk, arg, "chk_need_child")


        if node_dfn.dy["values_min"] is not None:
            add_chk_property(dy_chk, arg, "chk_values_min")

    if node_dfn.is_root is True:
        if arg._branches.index(arg) == 0:
            arg._cmd_line=dy_err["cmd_line"]
    else:
        if is_implicit is False:
            if node_dfn in node_dfn.parent.dy_xor:
                for group_num in sorted(node_dfn.parent.dy_xor[node_dfn]):
                    for tmp_node_dfn in node_dfn.parent.dy_xor[node_dfn][group_num]:
                        tmp_arg=arg._parent._[tmp_node_dfn.name]
                        if tmp_arg._here is True:
                            msg.error([
                                "XOR conflict, the two following arguments can't be provided at the same time:",
                                "- {}".format(arg._get_path()),
                                "- {}".format(tmp_arg._get_path()),
                            ]
                            , prefix=get_arg_prefix(dy_err, node_dfn.parent.current_arg._cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
                            sys.exit(1)

            if node_dfn.dy["allow_parent_fork"] is False:
                if len(arg._parent._branches) > 1:
                    msg.error(
                        [
                            "argument '{}' property 'allow_parent_fork' is set to '{}' but parent argument has more than one branch:".format(arg._alias, False),
                            *[arg._get_path() for arg in arg._parent._branches],
                        ], prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            if len(arg._parent._args) >= 2:
                if node_dfn.dy["allow_siblings"] is True:
                    if len(arg._parent._args) in [2, 3]:
                        sibling_arg=get_first_sibling(arg)
                        if sibling_arg is not None:
                            if node_dfn.dy["allow_siblings"] is True:
                                if sibling_arg._dfn.dy["allow_siblings"] is False:
                                    msg.error(
                                        [
                                            "argument '{}' can't be added because it already has a sibling argument with property 'allow_siblings' set to '{}':".format(arg._alias, False),
                                            sibling_arg._get_path(),
                                        ], prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1
                                    )
                else:
                    sibling_arg=get_first_sibling(arg)
                    if sibling_arg is not None:
                        msg.error(
                            [
                                "argument '{}' property 'allow_siblings' is set to '{}' but at least one sibling is present already:".format(arg._alias, False),
                                sibling_arg._get_path(),
                            ], prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1
                        )

def check_values_min(arg, dy_err):
    if arg._dfn.dy["values_min"] is not None:
        if len(arg._values) < arg._dfn.dy["values_min"]:
            if arg._dfn.dy["values_min"] == 1:
                msg.error("argument '{}' needs at least one value.".format(arg._alias), prefix=get_arg_prefix(dy_err, arg._cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
            else:
                msg.error("argument '{}' minimum values '{}' is less than '{}'.".format(arg._alias, len(arg._values), arg._dfn.dy["values_min"]), prefix=get_arg_prefix(dy_err, arg._cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
            dy_err["print_usage"](arg._dfn)
            sys.exit(1)

def values_final_check(arg, dy_err):
    if len(arg._values) > 0:
        check_values_min(arg, dy_err)
    else:
        if arg._dfn.dy["values_required"] is True:
            if arg._dfn.dy["default"] is None:
                check_values_min(arg, dy_err)
            else:
                for default_value in arg._dfn.dy["default"]:
                    arg._values.append(default_value)

                if len(arg._values) > 0:
                    arg._value=arg._values[0]
        else:
            pass

def add_value(
    arg,
    value,
    dy_err,
    cmd_line_index,
    dy_chk,
):
    node_dfn=arg._dfn
    if node_dfn.dy["values_max"] is not None:
        if len(arg._values) >= node_dfn.dy["values_max"]:
            msg.error("value '{}' can't be added. Maximum number of values '{}' has been reached already.".format(value, node_dfn.dy["values_max"]), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
            dy_err["print_usage"](node_dfn)
            sys.exit(1)

    if isinstance(node_dfn.dy["type"], str):
        if node_dfn.dy["type"] in [ ".json", "json" ]:
            tmp_value=get_json(
                value,
                node_dfn,
                dy_err,
                cmd_line_index,
                search_file="." in node_dfn.dy["type"], 
            )
        elif node_dfn.dy["type"] in [ "dir", "file", "path", "vpath" ]:
            tmp_value=get_path(node_dfn, value, node_dfn.dy["type"], dy_err, cmd_line_index)
    else:
        tmp_value=None
        if node_dfn.dy["type"] == bool:
            tmp_value=get_boolean(value)
        elif node_dfn.dy["type"] == float:
            try:
                tmp_value=float(value)
            except:
                pass
        elif node_dfn.dy["type"] == int:
            try:
                tmp_value=int(value)
            except:
                pass
        elif node_dfn.dy["type"] == str:
            tmp_value=value

        if tmp_value is None:
            msg.error("argument '{}' value '{}' type error. It must match type '{}'.".format(node_dfn.current_arg._alias, value, node_dfn.dy["type"]), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
            dy_err["print_usage"](node_dfn)
            sys.exit(1)

    value=tmp_value

    if node_dfn.dy["in"] is not None:
        if value not in node_dfn.dy["in"]:
            msg.error("value '{}' not found in {}.".format(value, node_dfn.dy["in"]), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
            dy_err["print_usage"](node_dfn)
            sys.exit(1)

    if arg._value is None:
        arg._value=value
    arg._values.append(value)
    arg._dy_indexes["values"].append(cmd_line_index)

def add_chk_property(dy_chk, arg, prop):
    if arg in dy_chk:
        if prop not in dy_chk[arg]:
            dy_chk[arg].append(prop)
    else:
        dy_chk[arg]=[prop]

def set_node(alias, node, dy_err, cmd_line_index, branch_num, dy_chk):
    enabled_branches=[branch for branch in node.current_arg._branches if branch._here is True]
    has_one_enabled_branch=(len(enabled_branches) > 0)
    increment=(branch_num == "+")
    if branch_num is None:
        if has_one_enabled_branch is True:
            branch_num=len(node.current_arg._branches)
        else:
            branch_num=1
    elif branch_num == "+":
        if has_one_enabled_branch is True:
            branch_num=len(node.current_arg._branches)+1
        else:
            branch_num=1
    else:
        pass

    if branch_num > len(enabled_branches)+1:
        msg.error("argument branch '{}' number '+{}' is too big. Biggest branch number available is '+{}'.".format(alias, branch_num, len(enabled_branches)+1), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
        sys.exit(1)

    is_new_enabled_branch=(branch_num == len(enabled_branches)+1)

    if is_new_enabled_branch is True:
        if has_one_enabled_branch is True:
            if node.dy["fork"] is True:
                for branch in node.current_arg._branches:
                    for arg in branch._args:
                        if arg._dfn.dy["allow_parent_fork"] is False:
                            msg.error("argument '{}' can't be forked because its child argument '{}' property 'allow_parent_fork' is set to '{}'.".format(alias, arg._dfn.current_arg._alias, False), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                
                parent_arg=None
                if node.current_arg._is_root is False:
                    parent_arg=node.current_arg._parent
                create_branch(node, node.current_arg._branches, parent_arg)
            else:
                if increment is True:
                    msg.error("A new branch can't be created for argument '{}' using notation '+' because one branch already exists and argument 'fork' property is set to '{}'.".format(alias, node.dy["fork"]), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
                else:
                    msg.error("argument '{}' wrong branch number '+{}'. Only '+1' is authorized when 'fork' property is set to '{}'.".format(alias, branch_num, node.dy["fork"]), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
                dy_err["print_usage"](node)
                sys.exit(1)

        activate_arg(node.current_arg, alias, dy_err, cmd_line_index, dy_chk)
    else: # branch_num < len(node.current_arg._branches)+1 (only for existing branches)
        if node.dy["repeat"] == "error":
            msg.error("argument '{}' can't be repeated because its 'repeat' property is set to '{}'.".format(alias, node.dy["repeat"]), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
            dy_err["print_usage"](node)
            sys.exit(1)
        else:
            current_branch_num=node.current_arg._branches.index(node.current_arg)+1
            if current_branch_num != branch_num:
                node.current_arg=node.current_arg._branches[branch_num-1]
            if node.dy["repeat"] == "append":
                if node.is_root is False:
                    node.current_arg._parent._args.remove(node.current_arg)
                set_arg(node.current_arg, alias, cmd_line_index, is_implicit=False)
            elif node.dy["repeat"] == "replace":
                reset_branch(
                    node.current_arg,
                    parent_arg=node.current_arg._parent,
                    branches=node.current_arg._branches,
                    dy_chk=dy_chk,
                    to_renew=True,
                )
                activate_arg(node.current_arg, alias, dy_err, cmd_line_index, dy_chk)

def create_branch(node, branches, parent_arg, branch_index=None):
    new_arg=CliArg(
        branches=branches,
        node_dfn=node,
        parent=parent_arg,
        branch_index=branch_index,
    )

    node.current_arg=new_arg
    for child_node in node.nodes:
        create_branch(node=child_node, branches=[], parent_arg=new_arg, branch_index=branch_index)

def get_explicit_path(node_dfn,  conflict_node_dfn, alias):
    explicit_notation=None
    argument_type=None
    if node_dfn.level < conflict_node_dfn.level:
        explicit_notation="+"
        argument_type="child"
    elif node_dfn.level == conflict_node_dfn.level:
        explicit_notation="="
        if node_dfn == conflict_node_dfn:
            argument_type="same"
        else:
            argument_type="sibling"
    else:
        explicit_notation=(node_dfn.level - conflict_node_dfn.level)*"-"
        argument_type="parent"

    return "'{} {} {}' for '{}' argument at node level {} with aliases {}.".format(
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
    search_only_root,
    dy_err,
    cmd_line_index,
    dy_chk,
):
    tmp_node=None
    if explicit is True:
        if alias in node.explicit_aliases:
            tmp_node=node.explicit_aliases[alias]
        else:
            tmp_node=None
    elif search_only_root is True:
        if alias in node.root.implicit_aliases:
            tmp_node=node.root.implicit_aliases[alias][0]
        else:
            tmp_node=None
    else:
        in_explicit=False
        in_implicit=False
        if alias in node.explicit_aliases:
            in_explicit=True
        if alias in node.implicit_aliases:
            in_implicit=True

        lst_error=[]
        nodes_error=[]

        if in_explicit is True:
            if in_implicit is True:
                lst_error=[
                    "explicit notation is needed because alias '{}' is present multiple times in argument's explicit aliases and implicit aliases at paths:".format(alias)
                ]
                for imp_dfn in node.implicit_aliases[alias]:
                    lst_error.append(get_explicit_path(node, imp_dfn, alias))
                    nodes_error.append(imp_dfn)
                lst_error.append(get_explicit_path(node, node.explicit_aliases[alias], alias))
                nodes_error.append(node.explicit_aliases[alias])
            else:
                tmp_node=node.explicit_aliases[alias]
        elif in_implicit is True:
            if len(node.implicit_aliases[alias]) > 1:
                lst_error=[
                    "explicit notation is needed because alias '{}' is present multiple times in argument's implicit aliases at paths:".format(alias)
                ]
                for imp_dfn in node.implicit_aliases[alias]:
                    lst_error.append(get_explicit_path(node, imp_dfn, alias))
                    nodes_error.append(imp_dfn)
                nodes_error.append(node)
            else:
                tmp_node=node.implicit_aliases[alias][0]
        else:
            tmp_node=None

        if len(lst_error) > 0:
            msg.error(lst_error, prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
            closest=get_closest_parent(nodes_error)
            dy_err["print_usage"](closest["node"], closest["max_sibling_level"])
            sys.exit(1)
        
    if tmp_node is not None:
        set_node(alias, tmp_node, dy_err, cmd_line_index, branch_num, dy_chk)
        process_values(values, tmp_node, dy_err, cmd_line_index, dy_chk)
            
    return tmp_node

def process_values(values, tmp_node, dy_err, cmd_line_index, dy_chk):
    if values is not None:
        try:
            values=shlex.split(values)
        except ValueError as e:
            if "closing quotation" in str(e):
                msg.error("There is no closing quotation for value(s) '{}'.".format(values), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
            else:
                raise(e) 

        if len(values) > 0:
            if tmp_node.dy["values_authorized"] is True:
                cmd_line=dy_err["cmd_line"]
                for v, value in enumerate(values):
                    cmd_line_index+=len(value)
                    while True:
                        if cmd_line_index >= len(cmd_line)-1:
                            cmd_line_index=len(cmd_line)+1
                            break
                        else:
                            cmd_line_index+=1
                            if cmd_line[cmd_line_index] == " ":
                                break
                    add_value(tmp_node.current_arg, value, dy_err, cmd_line_index, dy_chk)
            else:
                msg.error("for argument '{}' values are not allowed {}.".format(tmp_node.current_arg._alias, values), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
                dy_err["print_usage"](tmp_node)
                sys.exit(1)

def get_nodes_from_flags(
    chars,
    branch_num,
    branch_num_str,
    values,
    values_str,
    node_dfn,
    builtin_dfn,
    dy_err,
    cmd_line_index,
    dy_chk,
    usage_dfn,
    search_only_root,
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
        dy_flags=None
        if search_only_root is True:
            dy_flags=node_dfn.root._implicit_flags
        else:
            dy_flags=flags_node.get_dy_flags()

        is_last_set=i+1==len(flag_sets)
        unknown_chars=set(flag_set)-set(sorted(dy_flags))
        if len(unknown_chars) > 0:
            tmp_cmd_line_index+=len(flag_set)
            msg.error("Unknown char(s) {} in flag set '{}'.".format(sorted(list(unknown_chars)), get_flags_notation(dy_flags)), prefix=get_arg_prefix(dy_err, tmp_cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"])
            dy_err["print_usage"](flags_node, top_flags=True)
            sys.exit(1)

        for j, c in enumerate(flag_set):
            is_last_char=j+1==len(flag_set)
            tmp_cmd_line_index+=1
            tmp_branch_num=None
            if is_last_set is True and is_last_char is True:
                if branch_num_str is not None:
                    tmp_cmd_line_index+=len(branch_num_str)
                    if branch_num is None:
                        tmp_branch_num=branch_num_str
                    else:
                        tmp_branch_num=int(branch_num)
                
            tmp_node_dfn=dy_flags[c]["node"]
            alias=tmp_node_dfn.get_dy_flags()[c]["alias"]
            set_node(alias, tmp_node_dfn, dy_err, tmp_cmd_line_index, tmp_branch_num, dy_chk)

            if is_last_set and is_last_char is True:
                process_values(values, tmp_node_dfn, dy_err, tmp_cmd_line_index, dy_chk)

            node_dfn, builtin_dfn, usage_dfn =get_builtin_dfn(node_dfn, tmp_node_dfn, builtin_dfn, usage_dfn)

        search_only_root=False
        flags_node=node_dfn
        tmp_cmd_line_index+=1

    return node_dfn, builtin_dfn, usage_dfn

def reset_branch(arg, parent_arg, branches, dy_chk=None, to_renew=False, is_renew=True):
    new_arg=None
    if to_renew is True and is_renew is True:
        branch_index=None
        node_dfn=arg._dfn
        try:
            branch_index=branches.index(arg)
        except:
            pass
        new_arg=CliArg(
            branches=branches,
            node_dfn=node_dfn,
            parent=parent_arg,
            branch_index=branch_index,
        )
        node_dfn.current_arg=new_arg

    for child_name in sorted(arg._):
        child_arg=arg._[child_name]
        tmp_is_renew=is_renew
        for branch in child_arg._branches.copy():
            reset_branch(
                branch, 
                branches=[],
                parent_arg=new_arg,
                dy_chk=dy_chk,
                to_renew=to_renew,
                is_renew=tmp_is_renew,
            )
            tmp_is_renew=False

    arg._branches.remove(arg)
    if arg._parent is not None:
        if arg in arg._parent._args:
            arg._parent._args.remove(arg)

    if dy_chk is not None:
        if arg in dy_chk:
            del dy_chk[arg]

    del arg._
    del arg._args
    del arg._dy_indexes
    del arg._values
    del arg._branches
    del arg

def get_args(
    app_name,
    cmd,
    exc,
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
        return None

    if reset_dfn_tree is True:
        to_renew=True
        for branch in node_dfn.root.current_arg._branches.copy():
            tmp_node_dfn=reset_branch(branch, parent_arg=None, branches=[], dy_chk=None, to_renew=to_renew)
            to_renew=False

    def print_usage(node_dfn, max_sibling_level=1, top_flags=False):
        get_help_usage(
            dy_metadata=dy_metadata,
            node_ref=node_dfn,
            output="cmd_usage",
            style=Style(
                pretty_help=pretty_help, 
                output="cmd_usage", 
                theme=theme,
            ),
            max_sibling_level=max_sibling_level,
            top_flags=top_flags,
        )

    from_sys_argv=False
    if cmd is None:
        from_sys_argv=True
        cmd=copy.deepcopy(sys.argv)
        root_arg=os.path.basename(cmd.pop(0))
        cmd.insert(0, root_arg)
    else:
        if not isinstance(cmd, str):
            msg.error("cmd type {} must be type {}.".format(type(cmd), str), prefix=prefix, pretty=pretty_msg, exc=exc, exit=1)
        try:
            cmd=shlex.split(cmd)
        except ValueError as e:
            if "closing quotation" in str(e):
                msg.error("There is no closing quotation for command-line '{}'.".format(cmd), prefix=prefix, pretty=pretty_msg, exc=exc, exit=1)
            else:
                raise(e) 

    cmd_line=" ".join(cmd)

    if len(cmd) == 0:
        msg.error("command must have at least the root argument set.", prefix=prefix, pretty=pretty_msg, exc=exc, exit=1)

    if substitute is True:
        tmp_cmd=[]
        for elem in cmd:
            elem=re.sub(r"^(?:__(?!:)(?P<input>input|hidden)?(?::)?(?P<label>[a-zA-Z][a-zA-Z0-9]*)?(?<!:)__$)", lambda m: get_substitute_var(m), elem)
            tmp_cmd.append(elem)
        cmd_line=tmp_cmd

    at_start=True
    after_explicit=False
    builtin_dfn=None
    after_concat=False
    usage_dfn=None

    dy_err=dict(
        cmd_line=cmd_line,
        exc=exc,
        prefix=prefix,
        pretty=pretty_msg,
        print_usage=print_usage,
    )

    dy_chk=dict()

    cmd_line_index=0
    elem=None
    search_only_root=False
    while len(cmd) > 0:
        if elem is not None:
            cmd_line_index+=1
        elem=cmd.pop(0)

        cmd_line_index+=len(elem)
        
        is_last_elem=len(cmd) == 0
        if at_start is True:
            at_start=False
            if from_sys_argv is True:
                activate_arg(node_dfn.current_arg, elem, dy_err, cmd_line_index, dy_chk)
                continue
            else:
                search_only_root=True
        elif after_explicit is False:
            reg_explicit=re.match(get_regex("cli_explicit")["rule"], elem)
            if reg_explicit:
                if is_last_elem is True:
                    msg.error("command must finish with an argument or a value not an explicit notation '{}'.".format(elem), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=pretty_msg, exc=exc)
                    print_usage(node_dfn)
                    sys.exit(1)

                if reg_explicit.group("plus") is None:
                    level_up=0
                    if reg_explicit.group("equal") is not None:
                        level_up=1
                    elif reg_explicit.group("minus_concat") is not None:
                        level_up=len(reg_explicit.group("minus_concat"))+1
                    else:
                        level_up=int(reg_explicit.group("minus_index"))+1


                    level_up=node_dfn.level - level_up
                    if  level_up < 0:
                        msg.error("explicit level '{}' out of bound. Level value '{}' is lower than limit '0'.".format(elem, level_up), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=pretty_msg, exc=exc, exit=1)
                    elif level_up == 0:
                        node_dfn=node_dfn.root
                        search_only_root=True
                    else:
                        while node_dfn.level != level_up:
                            node_dfn=node_dfn.parent

                if search_only_root is False:
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
                search_only_root,
                dy_err,
                alias_cmd_line_index,
                dy_chk,
            )

            if node_from_alias is None:
                if after_explicit is True or search_only_root is True or (reg_alias.group("prefix") is not None and len(reg_alias.group("prefix")) > 0):
                    msg.error("unknown argument '{}'.".format(alias), prefix=get_arg_prefix(dy_err, alias_cmd_line_index), pretty=pretty_msg, exc=exc)
                    print_usage(node_dfn)
                    sys.exit(1)
                else:
                    if node_dfn.dy["values_authorized"] is True:
                        add_value(node_dfn.current_arg, elem, dy_err, cmd_line_index, dy_chk)
                    else:
                        msg.error("unknown input '{}'.".format(alias), prefix=get_arg_prefix(dy_err, alias_cmd_line_index), pretty=pretty_msg, exc=exc)
                        print_usage(node_dfn)
                        sys.exit(1)
            else:
                node_dfn, builtin_dfn, usage_dfn =get_builtin_dfn(node_dfn, node_from_alias, builtin_dfn, usage_dfn)

                if flags_str is not None:
                    flags_branch_num=reg_alias.group("branch_num2")
                    flags_branch_num_str=reg_alias.group("branch_num_str2")
                    chars=reg_alias.group("chars")
                    flags_values=tmp_values

                    node_dfn, builtin_dfn, usage_dfn = get_nodes_from_flags(
                        chars,
                        flags_branch_num,
                        flags_branch_num_str,
                        flags_values,
                        values_str,
                        node_dfn,
                        builtin_dfn,
                        dy_err,
                        cmd_line_index,
                        dy_chk,
                        usage_dfn,
                        search_only_root=False,
                    )
        else:
            reg_flags=re.match(get_regex("cli_flags")["rule"], elem)
            if reg_flags:
                branch_num=reg_flags.group("branch_num")
                branch_num_str=reg_flags.group("branch_num_str")
                chars=reg_flags.group("chars")
                values=reg_flags.group("values")
                values_str=reg_flags.group("values_str")

                node_dfn, builtin_dfn, usage_dfn = get_nodes_from_flags(
                    chars,
                    branch_num,
                    branch_num_str,
                    values,
                    values_str,
                    node_dfn,
                    builtin_dfn,
                    dy_err,
                    cmd_line_index,
                    dy_chk,
                    usage_dfn,
                    search_only_root,
                )

            else:
                if after_explicit is True or search_only_root is True:
                    msg.error("unknown argument '{}'".format(elem), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=pretty_msg, exc=exc)
                    print_usage(node_dfn)
                    sys.exit(1)
                else:
                    if node_dfn.dy["values_authorized"] is True:
                        add_value(node_dfn.current_arg, elem, dy_err, cmd_line_index, dy_chk)
                    else:
                        msg.error("unknown input '{}'.".format(elem), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=pretty_msg, exc=exc)
                        print_usage(node_dfn)
                        sys.exit(1)

        if after_explicit is True:
            after_explicit=False
        elif search_only_root is True:
            search_only_root=False

    last_check(dy_chk, dy_err, usage_dfn)

    if builtin_dfn is None:
        return node_dfn.root.current_arg._branches[0]
    else:
        builtin_arg=builtin_dfn.current_arg
        if builtin_arg._name == "_cmd_":
            if cmd_provided is True:
                msg.error("Nargs built-in 'cmd' argument with alias '{}' can't be provided more than once.".format(builtin_arg._alias), prefix=get_arg_prefix(dy_err, builtin_arg._cmd_line_index), pretty=pretty_msg, exit=1, exc=exc)
            lines=[]
            with open(builtin_arg._value, "r") as f:
                for line in f.read().splitlines():
                    line=line.strip()
                    if len(line) > 0 and line[0] != "#":
                        lines.append(line)

            cmd=" ".join(lines)

            return get_args(
                app_name=app_name,
                cmd=cmd,
                exc=exc,
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
                            msg.error("metadata key '{}' not found in {}.".format(key, sorted(dy_metadata)), prefix=get_arg_prefix(dy_err, builtin_arg.metadata._cmd_line_index), pretty=pretty_msg, exit=1, exc=exc)

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
            elif builtin_arg.examples._here is True:
                print_examples(builtin_arg._root._dfn)
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
                    only_syntax=builtin_arg.syntax.only._here,
                )
                sys.exit(0)
        elif builtin_arg._name == "_path_etc_":
            print(path_etc)
            sys.exit(0)
        elif builtin_arg._name == "_usage_":
            tmp_node=builtin_arg._previous_dfn
            from_=builtin_arg.from_._value
            if from_ < -1:
                tmp_node_dfn=builtin_dfn.explicit_aliases[builtin_arg.from_._alias]
                msg.error("from LEVEL '{}' must be greater or equal than '-1'.".format(from_), prefix=get_arg_prefix(dy_err, builtin_arg.from_._cmd_line_index), pretty=pretty_msg, exc=exc, exit=1)

            if from_ == 0:
                tmp_node=builtin_arg._previous_dfn
            else:
                count=0
                while tmp_node.parent is not None:
                    tmp_node=tmp_node.parent
                    count+=1
                    if count == from_:
                        break

            depth=builtin_arg.depth._value
            if depth < -1:
                tmp_node_dfn=builtin_dfn.explicit_aliases[builtin_arg.depth._alias]
                msg.error("depth LEVEL '{}' must be greater or equal than '-1'.".format(builtin_arg.depth._value), prefix=get_arg_prefix(dy_err, builtin_arg.depth._cmd_line_index), pretty=pretty_msg, exc=exc, exit=1)

            if depth == -1:
                depth=None

            allproperties=None
            if builtin_arg.properties._here is True:
                allproperties=sorted([prop for prop, dy in get_arg_properties().items() if dy["for_help"] is True])

            get_help_usage(
                dy_metadata=dy_metadata,
                node_ref=tmp_node,
                output="cmd_usage",
                style=Style(pretty_help=pretty_help, output="cmd_usage", theme=theme),
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
                msg.error("version not provided.", prefix=prefix, pretty=pretty_msg, exc=exc, exit=1)

def last_check(
    dy_chk,
    dy_err,
    usage_dfn,
):
    for arg, props in dy_chk.items():
        process=False
        if usage_dfn is None:
            process=True
        else:
            if arg == usage_dfn:
                process=True
            else:
                tmp_arg=arg
                while True:
                    if tmp_arg._dfn == usage_dfn:
                        process=True
                        break
                    if tmp_arg._parent is None:
                        break
                    tmp_arg=tmp_arg._parent

        if process is True:
            if "chk_values_min" in props:
                values_final_check(arg, dy_err)

            if "chk_required_children" in props:
                process_required(arg, dy_err)

            if "chk_need_child" in props:
                if len(arg._args) == 0:
                    prefix=get_arg_prefix(dy_err, arg._cmd_line_index)
                    msg.error("For argument '{}' at least one child argument is needed.".format(arg._alias), prefix=prefix, pretty=dy_err["pretty"], exc=dy_err["exc"])
                    dy_err["print_usage"](arg._dfn)
                    sys.exit(1)

def print_examples(node_dfn):
    if node_dfn.dy["examples"] is not None:
        for example in node_dfn.dy["examples"]:
            print(example)
    for node in node_dfn.nodes:
        print_examples(node)

def get_builtin_dfn(previous_node_dfn, node_dfn, builtin_dfn, usage_dfn):
    if node_dfn.dy["is_usage"] is True:
        usage_dfn=node_dfn
        usage_dfn.current_arg._previous_dfn=previous_node_dfn
        if node_dfn.dy["is_builtin"] is True:
            builtin_dfn=node_dfn
    elif node_dfn.level == 2 and node_dfn.dy["is_builtin"] is True:
        if builtin_dfn is None:
            builtin_dfn=node_dfn
        else:
            ignore=(builtin_dfn.name == "_usage_" and builtin_dfn.dy["is_builtin"] is True)
            if ignore is False:
                builtin_dfn=node_dfn

    return node_dfn, builtin_dfn, usage_dfn

def get_prompted_value(input_type, label=None):
    if label is None:
        label=input_type
    if input_type == "input":
        return input(label+": ")
    elif input_type == "hidden":
        return getpass.getpass(label+": ")

def get_substitute_var(reg):
    dy=reg.groupdict()
    if dy["input"] is None:
        if dy["label"] is None:
            return reg.group()
        else:
            value=os.environ[dy["label"]].strip()
            return re.sub(r"^\"?(.*?)\"?$", r"\1", value)
    else:
        return get_prompted_value(dy["input"], dy["label"])

def process_required(parent_arg, dy_err, from_implicit=False):
    for child_name in parent_arg._dfn.dy["required_children"]:
        required_arg=parent_arg._[child_name]
        if required_arg._here is False:

            cmd_line_index=parent_arg._cmd_line_index
            if from_implicit is False:
                if required_arg._dfn.dy["values_required"] is True: 
                    if required_arg._dfn.dy["default"] is None:
                        prefix=get_arg_prefix(dy_err, required_arg._parent._cmd_line_index)
                        msg.error("required argument '{}' is missing.".format(required_arg._default_alias), prefix=prefix, pretty=dy_err["pretty"], exc=dy_err["exc"])
                        dy_err["print_usage"](parent_arg._dfn)
                        sys.exit(1)

            activate_arg(required_arg, required_arg._dfn.dy["default_alias"], dy_err, cmd_line_index, dy_chk=None, is_implicit=True)
            values_final_check(required_arg, dy_err)
            process_required(required_arg, dy_err, from_implicit=True)

def get_boolean(value):
    if isinstance(value, str):
        if value.lower() in ["true", "1"]:
            return True
        elif value.lower() in ["false", "0"]:
            return False
        else:
            return None
    elif isinstance(value, int):
        if value == 0:
            return False
        elif value == 1:
            return True
    else:
        return None


