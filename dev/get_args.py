#!/usr/bin/env python3
from json.decoder import JSONDecodeError
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
from .exceptions import EndUserError, ErrorTypes
from .nodes import CliArg
from .get_json import get_json
from .get_path import get_path
from .help import get_help_usage

from .regexes import get_regex_cli, get_regex_cli_explicit
from .style import Style


from ..gpkgs import message as msg

def set_arg(arg, alias, cmd_line_index, is_implicit):
    if arg._is_root is False:
        arg._parent._args.append(arg)

    arg._alias = alias
    arg._count += 1
    arg._implicit = is_implicit
    arg._cmd_line_index = cmd_line_index
    arg._dy_indexes["aliases"][cmd_line_index] = alias

def get_first_sibling(arg):
    if arg._is_root is True:
        return None
    elif arg._name == "_usage_":
        return None
    else:
        for name in arg._parent._:
            if name not in [arg._name, "_usage_"]:
                sibling_arg = arg._parent._[name]
                if sibling_arg._here is True:
                    return sibling_arg
        return None

def activate_arg(arg, alias, dy_err, cmd_line_index, dy_chk, is_implicit=False):
    node_dfn = arg._dfn
    arg._here = True
    set_arg(arg, alias, cmd_line_index, is_implicit=is_implicit)

    if is_implicit is False:
        if len(node_dfn.dy["required_children"]) > 0:
            add_chk_property(dy_chk, arg, "chk_required_children")

        if len(node_dfn.dy["preset_children"]) > 0:
            add_chk_property(dy_chk, arg, "chk_preset_children")

        if arg._dfn.dy["need_child"] is True:
            add_chk_property(dy_chk, arg, "chk_need_child")

        if node_dfn.dy["values_min"] is not None:
            add_chk_property(dy_chk, arg, "chk_values_min")

    if node_dfn.is_root is True:
        if arg._branches.index(arg) == 0:
            arg._cmd_line = dy_err["cmd_line"]
    else:
        if is_implicit is False:
            arg._parent._has_explicit_nodes = True
            if node_dfn in node_dfn.parent.dy_xor:
                for group_num in sorted(node_dfn.parent.dy_xor[node_dfn]):
                    for tmp_node_dfn in node_dfn.parent.dy_xor[node_dfn][group_num]:
                        tmp_arg = arg._parent._[tmp_node_dfn.name]
                        if tmp_arg._here is True:
                            raise EndUserError(dict(
                                attributes=dict(
                                    arg_one_path=arg._get_path(),
                                    arg_two_path=tmp_arg._get_path(),
                                ),
                                cmd_line=dy_err["cmd_line"][:node_dfn.parent.current_arg._cmd_line_index],
                                error_type=ErrorTypes().XorError,
                                message=[
                                    "XOR conflict, the two following arguments can't be provided at the same time:",
                                    "- {arg_one_path}",
                                    "- {arg_two_path}",
                                ],
                                node_usage=tmp_arg._dfn,
                                show_usage=False,
                                stack_trace="".join(traceback.format_stack()),
                                show_stack=False,
                                prefix=dy_err["prefix"],
                            ))

            if node_dfn.dy["allow_parent_fork"] is False:
                if len(arg._parent._branches) > 1:
                    parent_paths=[arg._get_path() for arg in arg._parent._branches]
                    raise EndUserError(dict(
                        attributes=dict(
                            arg_alias=arg._alias,
                            set_to=False,
                            parent_paths=parent_paths,
                        ),
                        cmd_line=dy_err["cmd_line"][:cmd_line_index],
                        error_type=ErrorTypes().AllowParentForkError,
                        message=[
                            "argument '{arg_alias}' property 'allow_parent_fork' is set to '{set_to}' but parent argument has more than one branch:",
                            *parent_paths,
                        ],
                        node_usage=arg._dfn,
                        show_usage=False,
                        stack_trace="".join(traceback.format_stack()),
                        show_stack=False,
                        prefix=dy_err["prefix"],
                    ))

            if len(arg._parent._args) >= 2:
                if node_dfn.dy["allow_siblings"] is True:
                    if len(arg._parent._args) in [2, 3]:
                        sibling_arg = get_first_sibling(arg)
                        if sibling_arg is not None:
                            if node_dfn.dy["allow_siblings"] is True:
                                if sibling_arg._dfn.dy["allow_siblings"] is False:
                                    sibling_path=sibling_arg._get_path()
                                    raise EndUserError(dict(
                                        attributes=dict(
                                            arg_alias=arg._alias,
                                            set_to=False,
                                            sibling_path=sibling_path,
                                        ),
                                        cmd_line=dy_err["cmd_line"][:cmd_line_index],
                                        error_type=ErrorTypes().AllowSiblingsError,
                                        message=[
                                            "argument '{arg_alias}' can't be added because it already has a sibling argument with property 'allow_siblings' set to '{set_to}':",
                                            sibling_path,
                                        ],
                                        node_usage=arg._dfn,
                                        show_usage=False,
                                        stack_trace="".join(traceback.format_stack()),
                                        show_stack=False,
                                        prefix=dy_err["prefix"],
                                    ))
                else:
                    sibling_arg = get_first_sibling(arg)
                    if sibling_arg is not None:
                        sibling_path=sibling_arg._get_path()
                        raise EndUserError(dict(
                            attributes=dict(
                                arg_alias=arg._alias,
                                set_to=False,
                                sibling_path=sibling_path,
                            ),
                            cmd_line=dy_err["cmd_line"][:cmd_line_index],
                            error_type=ErrorTypes().AllowSiblingsError,
                            message=[
                                "argument '{arg_alias}' property 'allow_siblings' is set to '{set_to}' but at least one sibling is present already:",
                                sibling_path,
                            ],
                            node_usage=arg._dfn,
                            show_usage=False,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=False,
                            prefix=dy_err["prefix"],
                        ))


def check_values_min(arg, dy_err):
    if arg._dfn.dy["values_min"] is not None:
        if len(arg._values) < arg._dfn.dy["values_min"]:
            if arg._dfn.dy["values_min"] == 1:
                raise EndUserError(dict(
                    attributes=dict(
                        arg_alias=arg._alias,
                    ),
                    cmd_line=dy_err["cmd_line"][:arg._cmd_line_index],
                    error_type=ErrorTypes().NeedValueError,
                    node_usage=arg._dfn,
                    show_usage=True,
                    stack_trace="".join(traceback.format_stack()),
                    show_stack=False,
                    message="argument '{arg_alias}' needs at least one value.",
                    prefix=dy_err["prefix"],
                ))
            else:
                raise EndUserError(dict(
                    attributes=dict(
                        arg_alias=arg._alias,
                        len_values=len(arg._values),
                        min_values=arg._dfn.dy["values_min"],
                    ),
                    cmd_line=dy_err["cmd_line"][:arg._cmd_line_index],
                    error_type=ErrorTypes().MinValuesNumNotReached,
                    message="argument '{arg_alias}' minimum values '{len_values}' is less than '{min_values}'.",
                    node_usage=arg._dfn,
                    show_usage=False,
                    stack_trace="".join(traceback.format_stack()),
                    show_stack=False,
                    prefix=dy_err["prefix"],
                ))


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
                    arg._value = arg._values[0]
        else:
            pass


def add_value(
    arg,
    value,
    dy_err,
    cmd_line_index,
):
    node_dfn = arg._dfn
    if node_dfn.dy["values_max"] is not None:
        if len(arg._values) >= node_dfn.dy["values_max"]:
            raise EndUserError(dict(
                attributes=dict(
                    value=value,
                    values_max=node_dfn.dy["values_max"],
                ),
                cmd_line=dy_err["cmd_line"][:cmd_line_index],
                error_type=ErrorTypes().MaxValuesNumReached,
                node_usage=node_dfn,
                show_usage=True,
                stack_trace="".join(traceback.format_stack()),
                show_stack=False,
                message="value '{value}' can't be added. Maximum number of values '{values_max}' has been reached already.",
                prefix=dy_err["prefix"],
            ))

    if isinstance(node_dfn.dy["type"], str):
        if node_dfn.dy["type"] in [".json", "json"]:
            tmp_value = get_json(
                value,
                node_dfn,
                dy_err,
                cmd_line_index,
                search_file="." in node_dfn.dy["type"],
            )
        elif node_dfn.dy["type"] in ["dir", "file", "path", "vpath"]:
            tmp_value = get_path(node_dfn, value, node_dfn.dy["type"], dy_err, cmd_line_index)
    else:
        tmp_value = None
        if node_dfn.dy["type"] == bool:
            tmp_value = get_boolean(value)
        elif node_dfn.dy["type"] == float:
            try:
                tmp_value = float(value)
            except:
                pass
        elif node_dfn.dy["type"] == int:
            try:
                tmp_value = int(value)
            except:
                pass
        elif node_dfn.dy["type"] == str:
            tmp_value = value

        if tmp_value is None:
            raise EndUserError(dict(
                attributes=dict(
                    arg_alias=node_dfn.current_arg._alias,
                    value=value,
                    match_type=node_dfn.dy["type"],
                ),
                cmd_line=dy_err["cmd_line"][:cmd_line_index],
                error_type=ErrorTypes().ValueTypeError,
                message="argument '{arg_alias}' value '{value}' type error. It must match type '{match_type}'.",
                node_usage=node_dfn,
                show_usage=True,
                stack_trace="".join(traceback.format_stack()),
                show_stack=False,
                prefix=dy_err["prefix"],
            ))

    value = tmp_value

    if node_dfn.dy["in"] is not None:
        if value not in node_dfn.dy["in"]:
            raise EndUserError(dict(
                attributes=dict(
                    in_values=node_dfn.dy["in"],
                    value=value,
                ),
                cmd_line=dy_err["cmd_line"][:cmd_line_index],
                error_type=ErrorTypes().ValueNotFound,
                message="value '{value}' not found in {in_values}.",
                node_usage=node_dfn,
                show_usage=True,
                stack_trace="".join(traceback.format_stack()),
                show_stack=False,
                prefix=dy_err["prefix"],
            ))

    if arg._value is None:
        arg._value = value
    arg._values.append(value)
    arg._dy_indexes["values"].append(cmd_line_index)


def add_chk_property(dy_chk, arg, prop):
    if arg in dy_chk:
        if prop not in dy_chk[arg]:
            dy_chk[arg].append(prop)
    else:
        dy_chk[arg] = [prop]


def set_node(alias, node, dy_err, cmd_line_index, dy_chk):
    enabled_branches = [
        branch for branch in node.current_arg._branches if branch._here is True]
    has_one_enabled_branch = (len(enabled_branches) > 0)

    branch_num = None
    if has_one_enabled_branch is True:
        branch_num = len(node.current_arg._branches)
    else:
        branch_num = 1

    is_new_enabled_branch = (branch_num == len(enabled_branches)+1)

    if node.dy["repeat"] == "fork":
        if has_one_enabled_branch is True:
            for branch in node.current_arg._branches:
                for arg in branch._args:
                    if arg._dfn.dy["allow_parent_fork"] is False:
                        raise EndUserError(dict(
                            attributes=dict(
                                arg_alias=alias,
                                child_arg_alias=arg._dfn.current_arg._alias,
                                set_to=False,
                            ),
                            cmd_line=dy_err["cmd_line"][:cmd_line_index],
                            error_type=ErrorTypes().AllowParentForkError,
                            message="argument '{arg_alias}' can't be forked because its child argument '{child_arg_alias}' property 'allow_parent_fork' is set to '{set_to}'.",
                            node_usage=node,
                            show_usage=False,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=False,
                            prefix=dy_err["prefix"],
                        ))

            parent_arg = None
            if node.current_arg._is_root is False:
                parent_arg = node.current_arg._parent
            create_branch(node, node.current_arg._branches, parent_arg)

        activate_arg(node.current_arg, alias, dy_err, cmd_line_index, dy_chk)
    elif is_new_enabled_branch is True:
        activate_arg(node.current_arg, alias, dy_err, cmd_line_index, dy_chk)
    elif node.dy["repeat"] == "error":
        raise EndUserError(dict(
            attributes=dict(
                arg_alias=alias,
                set_to=node.dy["repeat"],
            ),
            cmd_line=dy_err["cmd_line"][:cmd_line_index],
            error_type=ErrorTypes().RepeatError,
            message="argument '{arg_alias}' can't be repeated because its 'repeat' property is set to '{set_to}'.",
            node_usage=node,
            show_usage=True,
            stack_trace="".join(traceback.format_stack()),
            show_stack=False,
            prefix=dy_err["prefix"],
        ))
    elif node.dy["repeat"] == "append":
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
    else:
        raise NotImplementedError


def create_branch(node, branches, parent_arg, branch_index=None):
    new_arg = CliArg(
        branches=branches,
        node_dfn=node,
        parent=parent_arg,
        branch_index=branch_index,
    )

    node.current_arg = new_arg
    for child_node in node.nodes:
        create_branch(node=child_node, branches=[],
                      parent_arg=new_arg, branch_index=branch_index)


def get_node_from_alias(
    node,
    alias,
    after_explicit,
    search_only_root,
):
    tmp_node = None
    if after_explicit is True:
        if alias in node.explicit_aliases:
            tmp_node = node.explicit_aliases[alias]
        else:
            tmp_node = None
    elif search_only_root is True:
        if alias in node.root.implicit_aliases:
            tmp_node = node.root.implicit_aliases[alias]
        else:
            tmp_node = None
    else:
        if alias in node.explicit_aliases:
            tmp_node = node.explicit_aliases[alias]
        elif alias in node.implicit_aliases:
            tmp_node = node.implicit_aliases[alias]
        else:
            tmp_node = None

    return tmp_node


def process_values(values, tmp_node, dy_err, cmd_line_index):
    if values is not None:
        try:
            values = shlex.split(values)
        except ValueError as e:
            if "closing quotation" in str(e):
                raise EndUserError(dict(
                    attributes=dict(
                        values=values,
                    ),
                    cmd_line=dy_err["cmd_line"][:cmd_line_index],
                    error_type=ErrorTypes().ClosingQuotationError,
                    message="There is no closing quotation for value(s) '{values}'.",
                    node_usage=tmp_node,
                    show_usage=False,
                    stack_trace="".join(traceback.format_stack()),
                    show_stack=False,
                    prefix=dy_err["prefix"],
                ))
            else:
                raise (e)

        if len(values) > 0:
            if tmp_node.dy["values_authorized"] is True:
                cmd_line = dy_err["cmd_line"]
                for v, value in enumerate(values):
                    cmd_line_index += len(value)
                    while True:
                        if cmd_line_index >= len(cmd_line)-1:
                            cmd_line_index = len(cmd_line)+1
                            break
                        else:
                            cmd_line_index += 1
                            if cmd_line[cmd_line_index] == " ":
                                break
                    add_value(tmp_node.current_arg, value,
                              dy_err, cmd_line_index)
            else:
                raise EndUserError(dict(
                    attributes=dict(
                        arg_alias=tmp_node.current_arg._alias,
                        values=values,
                    ),
                    cmd_line=dy_err["cmd_line"][:cmd_line_index],
                    error_type=ErrorTypes().ValuesNotAllowed,
                    message="for argument '{arg_alias}' values are not allowed {values}.",
                    node_usage=tmp_node,
                    show_usage=True,
                    stack_trace="".join(traceback.format_stack()),
                    show_stack=False,
                    prefix=dy_err["prefix"],
                ))

def reset_branch(arg, parent_arg, branches, dy_chk=None, to_renew=False, is_renew=True):
    new_arg = None
    if to_renew is True and is_renew is True:
        branch_index = None
        node_dfn = arg._dfn
        try:
            branch_index = branches.index(arg)
        except:
            pass
        new_arg = CliArg(
            branches=branches,
            node_dfn=node_dfn,
            parent=parent_arg,
            branch_index=branch_index,
        )
        node_dfn.current_arg = new_arg

    for child_name in sorted(arg._):
        child_arg = arg._[child_name]
        tmp_is_renew = is_renew
        for branch in child_arg._branches.copy():
            reset_branch(
                branch,
                branches=[],
                parent_arg=new_arg,
                dy_chk=dy_chk,
                to_renew=to_renew,
                is_renew=tmp_is_renew,
            )
            tmp_is_renew = False

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
    dy_metadata,
    node_dfn,
    path_etc,
    pretty_msg,
    pretty_help,
    substitute,
    theme,
    get_documentation,
    reset_dfn_tree=False,
    _from_query=False,
    query_values=None,
    raise_exc=False,
):
    try:
        dy_err = dict(
            prefix="For '{}' at Nargs on the command-line".format(app_name),
        )

        is_query = False

        if query_values is None:
            query_values = []
        else:
            if isinstance(query_values, list):
                is_query = len(query_values) > 0
            else:
                raise EndUserError(dict(
                    attributes=dict(
                        match_type=list,
                    ),
                    cmd_line=None,
                    error_type=ErrorTypes().OptionQueryError,
                    message="option query values must be of type {match_type}.",
                    node_usage=node_dfn,
                    show_usage=False,
                    stack_trace="".join(traceback.format_stack()),
                    show_stack=False,
                    prefix=dy_err["prefix"],
                ))

        if node_dfn is None:
            return None

        if reset_dfn_tree is True:
            to_renew = True
            for branch in node_dfn.root.current_arg._branches.copy():
                tmp_node_dfn = reset_branch(branch, parent_arg=None, branches=[
                ], dy_chk=None, to_renew=to_renew)
                to_renew = False

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

        from_sys_argv = False

        if cmd is None:
            from_sys_argv = True
            cmd = copy.deepcopy(sys.argv)
            root_arg = os.path.basename(cmd.pop(0))
            cmd.insert(0, root_arg)
        else:
            if isinstance(cmd, list):
                tmp_cmd_line=[]
                for elem in cmd:
                    tmp_cmd_line.append(elem)
                    if not isinstance(elem, str):
                        raise EndUserError(dict(
                            attributes=dict(
                                element=elem,
                                match_type=str,
                            ),
                            cmd_line=" ".join(tmp_cmd_line),
                            error_type=ErrorTypes().CmdElementTypeError,
                            message="'cmd' list element '{element}' must be a of type {match_type}.",
                            node_usage=None,
                            show_usage=False,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=False,
                            prefix=dy_err["prefix"],
                        ))
            elif isinstance(cmd, str):
                try:
                    cmd = shlex.split(cmd)
                except ValueError as e:
                    if "closing quotation" in str(e):
                        raise EndUserError(dict(
                            attributes=dict(),
                            cmd_line=cmd,
                            error_type=ErrorTypes().OptionCmdError,
                            message="There is no closing quotation for command-line.",
                            node_usage=None,
                            show_usage=False,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=False,
                            prefix=dy_err["prefix"],
                        ))
                    else:
                        raise (e)
            else:
                raise EndUserError(dict(
                    attributes=dict(
                        cmd_type=type(cmd),
                        match_type=str,
                    ),
                    cmd_line=cmd,
                    error_type=ErrorTypes().OptionCmdError,
                    message="cmd type {cmd_type} must be of type {match_type}.",
                    node_usage=None,
                    show_usage=False,
                    stack_trace="".join(traceback.format_stack()),
                    show_stack=False,
                    prefix=dy_err["prefix"],
                ))

        if len(cmd) == 0:
            raise EndUserError(errors=dict(
                attributes=dict(),
                cmd_line=" ".join(cmd),
                error_type=ErrorTypes().RootArgumentNotFound,
                message="command must have at least the root argument set.",
                node_usage=None,
                show_usage=False,
                stack_trace="".join(traceback.format_stack()),
                show_stack=False,
                prefix=dy_err["prefix"],
            ))

        if substitute is True:
            tmp_cmd = []
            for elem in cmd:
                elem = re.sub(r"(?:__(?!:)(?P<input>input|hidden)?(?::)?(?P<label>[a-zA-Z][a-zA-Z0-9]*)?(?<!:)__)", lambda m: get_substitute_var(m), elem)
                tmp_cmd.append(elem)
            cmd=tmp_cmd

        cmd_line = None
        if is_query is True:
            tmp_cmd = []
            num_values = 0
            is_first_elem = True
            tmp_query_values = []

            for elem in cmd:
                if elem == "?":
                    if is_first_elem is True:
                        raise EndUserError(dict(
                            attributes=dict(),
                            cmd_line=None,
                            error_type=ErrorTypes().QuestionMarkError,
                            message="for query 'cmd' first list element can't be a question mark.",
                            node_usage=None,
                            show_usage=False,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=False,
                            prefix=dy_err["prefix"],
                        ))

                    num_values += 1

                    if num_values > len(query_values):
                        raise EndUserError(dict(
                            attributes=dict(),
                            cmd_line=" ".join(tmp_cmd),
                            error_type=ErrorTypes().CmdQueryValuesMisMatch,
                            message="there are less query values than the number of cmd question marks.",
                            node_usage=None,
                            show_usage=False,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=False,
                            prefix=dy_err["prefix"],
                        ))

                    query_value = query_values[num_values-1]

                    if isinstance(query_value, bool):
                        tmp_query_values.append(str(query_value))
                    elif type(query_value) in [float, int, str]:
                        tmp_query_values.append(query_value)
                    else:
                        raise EndUserError(dict(
                            attributes=dict(
                                authorized_types=[bool, float, int, str],
                                query_value=query_value,
                            ),
                            cmd_line=" ".join(tmp_cmd),
                            error_type=ErrorTypes().QueryValueTypeError,
                            message="query value '{query_value}' type not found in authorized types {authorized_types}.",
                            node_usage=None,
                            show_usage=False,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=False,
                            prefix=dy_err["prefix"],
                        ))

                    tmp_cmd.append(str(query_value))

                else:
                    tmp_cmd.append(elem)

                is_first_elem = False

            if num_values != len(query_values):
                raise EndUserError(dict(
                    attributes=dict(),
                    cmd_line=" ".join(cmd),
                    error_type=ErrorTypes().CmdQueryValuesMisMatch,
                    message="there are more query values than the number of cmd question marks.",
                    node_usage=None,
                    show_usage=False,
                    stack_trace="".join(traceback.format_stack()),
                    show_stack=False,
                    prefix=dy_err["prefix"],
                ))

            query_values = tmp_query_values

            cmd_line= " ".join(tmp_cmd)
        else:
            cmd_line= " ".join(cmd)

        at_start = True
        after_explicit = False
        builtin_dfn = None
        cmd_line_index = 0
        dy_err["cmd_line"]=cmd_line
        dy_chk = dict()
        elem = None
        query_index = 0
        search_only_root = False
        usage_dfn = None

        try:
            while len(cmd) > 0:
                is_only_value = False
                if elem is not None:
                    cmd_line_index += 1

                elem = None
                if is_query is True:
                    tmp_elem = cmd.pop(0)
                    if tmp_elem == "?":
                        is_only_value = True
                        elem = query_values[query_index]
                        query_index += 1
                    else:
                        elem = tmp_elem
                else:
                    elem = cmd.pop(0)

                cmd_line_index += len(elem)

                is_last_elem = len(cmd) == 0
                if at_start is True:
                    at_start = False
                    if from_sys_argv is True:
                        activate_arg(node_dfn.current_arg, elem,
                                    dy_err, cmd_line_index, dy_chk)
                        continue
                    else:
                        search_only_root = True
                elif after_explicit is False and is_only_value is False:
                    reg_explicit = re.match(get_regex_cli_explicit(), elem)
                    if reg_explicit:
                        if is_last_elem is True:
                            raise EndUserError(dict(
                                attributes=dict(
                                    element=elem,
                                ),
                                cmd_line=dy_err["cmd_line"][:cmd_line_index],
                                error_type=ErrorTypes().ExplicitNotationEndError,
                                message="command must finish with an argument or a value not an explicit notation '{element}'.",
                                node_usage=node_dfn,
                                show_usage=True,
                                stack_trace="".join(traceback.format_stack()),
                                show_stack=False,
                                prefix=dy_err["prefix"],
                            ))

                        if reg_explicit.group("plus") is None:
                            level_up = 0
                            if reg_explicit.group("equal") is not None:
                                level_up = 1
                            elif reg_explicit.group("minus_concat") is not None:
                                level_up = len(reg_explicit.group("minus_concat"))+1
                            else:
                                level_up = int(reg_explicit.group("minus_index"))+1

                            level_up = node_dfn.level - level_up
                            if level_up < 0:
                                raise EndUserError(dict(
                                    attributes=dict(
                                        cmd_element=elem,
                                        level_up=level_up,
                                    ),
                                    cmd_line=dy_err["cmd_line"][:cmd_line_index],
                                    error_type=ErrorTypes().ExplicitNotationOutOfBound,
                                    message="explicit level '{cmd_element}' out of bound. Level value '{level_up}' is lower than limit '0'.",
                                    node_usage=node_dfn,
                                    show_usage=False,
                                    stack_trace="".join(traceback.format_stack()),
                                    show_stack=False,
                                    prefix=dy_err["prefix"],
                                ))
                            elif level_up == 0:
                                node_dfn = node_dfn.root
                                search_only_root = True
                            else:
                                while node_dfn.level != level_up:
                                    node_dfn = node_dfn.parent

                        if search_only_root is False:
                            after_explicit = True
                        continue

                search_values = False
                if is_only_value is False:
                    search_flags = False
                    reg_alias = re.match(get_regex_cli("alias", node_dfn), elem)
                    if reg_alias:

                        alias = reg_alias.group("alias")
                        values_str = reg_alias.group("values_str")
                        tmp_values = reg_alias.group("values")
                        alias_cmd_line_index = cmd_line_index

                        if tmp_values is not None:
                            alias_cmd_line_index = cmd_line_index - len(values_str)

                        alias_values = tmp_values

                        node_from_alias = get_node_from_alias(
                            node_dfn,
                            alias,
                            after_explicit,
                            search_only_root,
                        )

                        if node_from_alias is None:
                            search_flags = True
                        else:
                            set_node(alias, node_from_alias, dy_err, alias_cmd_line_index, dy_chk)
                            process_values(alias_values, node_from_alias, dy_err, alias_cmd_line_index)

                            previous_dfn = node_dfn
                            node_dfn, builtin_dfn, usage_dfn = get_builtin_dfn(node_dfn, node_from_alias, builtin_dfn, usage_dfn)
                            if node_dfn.dy["is_usage"] is True:
                                node_dfn.current_arg._previous_dfn = previous_dfn

                            if after_explicit is True:
                                after_explicit = False
                            elif search_only_root is True:
                                search_only_root = False
                    else:
                        search_flags = True

                    if search_flags is True:
                        reg_flags = re.match(get_regex_cli("flags", node_dfn), elem)
                        if reg_flags:
                            alias = reg_flags.group("alias")
                            chars = reg_flags.group("chars")
                            values = reg_flags.group("values")
                            values_str = reg_flags.group("values_str")

                            tmp_cmd_line_index = cmd_line_index
                            if values is not None:
                                tmp_cmd_line_index -= len(values_str)

                            tmp_cmd_line_index = tmp_cmd_line_index-len(chars)

                            node_from_alias = get_node_from_alias(
                                node_dfn,
                                alias,
                                after_explicit,
                                search_only_root,
                            )

                            if node_from_alias is None:
                                search_values = True
                            else:
                                has_usage = False
                                if node_from_alias.dy["is_builtin"] and node_from_alias.name == "_usage_":
                                    has_usage = True

                                tmp_nodes = []
                                tmp_nodes.append(dict(
                                    alias=alias,
                                    cmd_line_index=tmp_cmd_line_index,
                                    node=node_from_alias,
                                ))

                                dy_flags = node_from_alias.get_dy_flags()

                                break_for_usage = False
                                for c in chars:
                                    if c in dy_flags:
                                        tmp_cmd_line_index += 1
                                        tmp_node = dy_flags[c]["node"]
                                        tmp_alias = dy_flags[c]["alias"]
                                        tmp_nodes.append(dict(
                                            alias=tmp_alias,
                                            cmd_line_index=tmp_cmd_line_index,
                                            node=tmp_node,
                                        ))
                                        dy_flags = tmp_node.get_dy_flags()
                                        if tmp_node.dy["is_builtin"] and tmp_node.name == "_usage_":
                                            has_usage = True
                                    else:
                                        if has_usage is True:
                                            break_for_usage = True
                                        else:
                                            search_values = True
                                        break

                                if search_values is False:
                                    index = 1
                                    for dy_tmp_node in tmp_nodes:
                                        tmp_node_dfn = dy_tmp_node["node"]
                                        tmp_alias = dy_tmp_node["alias"]
                                        tmp_cmd_line_index = dy_tmp_node["cmd_line_index"]

                                        set_node(tmp_alias, tmp_node_dfn,dy_err, tmp_cmd_line_index, dy_chk)
                                        if index == len(tmp_nodes):
                                            process_values(values, tmp_node_dfn, dy_err, tmp_cmd_line_index)

                                        previous_dfn = node_dfn
                                        node_dfn, builtin_dfn, usage_dfn = get_builtin_dfn(node_dfn, tmp_node_dfn, builtin_dfn, usage_dfn)
                                        if node_dfn.dy["is_usage"] is True:
                                            node_dfn.current_arg._previous_dfn = previous_dfn
                                        index += 1

                                    if after_explicit is True:
                                        after_explicit = False
                                    elif search_only_root is True:
                                        search_only_root = False

                                    if break_for_usage is True:
                                        break
                        else:
                            search_values = True

                if after_explicit is True or search_only_root is True:
                    raise EndUserError(dict(
                        attributes=dict(
                            cmd_element=elem,
                        ),
                        cmd_line=dy_err["cmd_line"][:cmd_line_index],
                        error_type=ErrorTypes().UnknownArgument,
                        message="unknown argument '{cmd_element}'.",
                        node_usage=node_dfn,
                        show_usage=True,
                        stack_trace="".join(traceback.format_stack()),
                        show_stack=False,
                        prefix=dy_err["prefix"],
                    ))

                if search_values is True or is_only_value is True:
                    if node_dfn.dy["values_authorized"] is True:
                        add_value(node_dfn.current_arg, elem,
                                dy_err, cmd_line_index)
                    else:
                        raise EndUserError(dict(
                            attributes=dict(
                                arg_alias=node_dfn.current_arg._alias,
                                cmd_element=elem,
                            ),
                            cmd_line=dy_err["cmd_line"][:cmd_line_index],
                            error_type=ErrorTypes().ArgumentNoValuesAllowed,
                            message="argument '{arg_alias}' does not accept value(s) '{cmd_element}'.",
                            node_usage=node_dfn,
                            show_usage=True,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=False,
                            prefix=dy_err["prefix"],
                        ))

            last_check(dy_chk, dy_err, usage_dfn)
        
        except EndUserError:
            if builtin_dfn is not None and builtin_dfn.name == "_usage_":
                pass
            else:
                raise

        if builtin_dfn is None:
            return node_dfn.root.current_arg._branches[0]
        else:
            builtin_arg = builtin_dfn.current_arg
            if builtin_arg._name == "_query_":
                if _from_query is True:
                    raise EndUserError(dict(
                        attributes=dict(
                            arg_alias=builtin_arg._alias,
                        ),
                        cmd_line=dy_err["cmd_line"][:builtin_arg._cmd_line_index],
                        error_type=ErrorTypes().QueryRecursionError,
                        message="Nargs built-in 'query' argument with alias '{arg_alias}' can't be provided more than once.",
                        node_usage=builtin_dfn,
                        show_usage=False,
                        stack_trace="".join(traceback.format_stack()),
                        show_stack=False,
                        prefix=dy_err["prefix"],
                    ))

                tmp_query_values=[]
                with open(builtin_arg._value, "r") as f:
                    try:
                        dy_query = json.load(f)
                        if "cmd" not in dy_query:
                            raise EndUserError(dict(
                                attributes=dict(
                                    value=builtin_arg._value,
                                ),
                                cmd_line=dy_err["cmd_line"][:builtin_arg._cmd_line_index],
                                error_type=ErrorTypes().QueryAttributeNotFound,
                                message="In Nargs built-in 'query' argument file '{value}' attribute 'cmd' not found.",
                                node_usage=builtin_dfn,
                                show_usage=False,
                                stack_trace="".join(traceback.format_stack()),
                                show_stack=False,
                                prefix=dy_err["prefix"],
                            ))
                
                        if "values" in dy_query:
                            tmp_query_values = dy_query["values"]

                    except JSONDecodeError as e:
                        raise EndUserError(dict(
                            attributes=dict(
                                value=builtin_arg._value,
                            ),
                            cmd_line=dy_err["cmd_line"][:builtin_arg._cmd_line_index],
                            error_type=ErrorTypes().JsonSyntaxError,
                            message="JSON syntax error in query file '{value}'.",
                            node_usage=builtin_dfn,
                            show_usage=False,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=True,
                            prefix=dy_err["prefix"],
                        ))

                return get_args(
                    app_name=app_name,
                    cmd=dy_query["cmd"],
                    dy_metadata=dy_metadata,
                    node_dfn=node_dfn.root,
                    path_etc=path_etc,
                    pretty_help=pretty_help,
                    pretty_msg=pretty_msg,
                    substitute=substitute,
                    theme=theme,
                    get_documentation=get_documentation,
                    _from_query=True,
                    reset_dfn_tree=True,
                    query_values=tmp_query_values,
                    raise_exc=raise_exc,
                )
            elif builtin_arg._name == "_help_":
                if builtin_arg.metadata._here is True:
                    get_values = builtin_arg.metadata.values._here is True
                    get_keys = builtin_arg.metadata.keys._here is True
                    to_json = builtin_arg.metadata.json._here

                    data = None
                    is_list = get_values is True or get_keys is True
                    if is_list is True:
                        data = []
                    else:
                        data = dict()

                    keys = None
                    has_user_keys = len(builtin_arg.metadata._values) > 0
                    if has_user_keys is True:
                        keys = builtin_arg.metadata._values
                    else:
                        keys = sorted(dy_metadata)

                    for key in keys:
                        if has_user_keys is True:
                            if key not in dy_metadata:
                                raise EndUserError(dict(
                                    attributes=dict(
                                        metadata_key=key,
                                        metadata_keys=sorted(dy_metadata),
                                    ),
                                    cmd_line=dy_err["cmd_line"][:builtin_arg.metadata._cmd_line_index],
                                    error_type=ErrorTypes().MetadataKeyNotFound,
                                    message="metadata key '{metadata_key}' not found in {metadata_keys}.",
                                    node_usage=builtin_arg.metadata._dfn,
                                    show_usage=False,
                                    stack_trace="".join(traceback.format_stack()),
                                    show_stack=False,
                                    prefix=dy_err["prefix"],
                                ))

                        if get_keys is True:
                            data.append(key)
                        else:
                            value = dy_metadata[key]

                            if get_values is True:
                                data.append(value)
                            else:
                                data[key] = value

                    if to_json is True:
                        print(json.dumps(data, sort_keys=True, indent=4))
                    else:
                        if is_list is True:
                            for value in data:
                                if isinstance(value, dict):
                                    value = json.dumps(value, sort_keys=True)
                                print(value)
                        else:
                            for key in sorted(data):
                                value = data[key]
                                if isinstance(value, dict):
                                    value = json.dumps(value, sort_keys=True)
                                print("{}: {}".format(key, value))
                        sys.exit(0)
                elif builtin_arg.examples._here is True:
                    print_examples(builtin_arg._root._dfn)
                    sys.exit(0)
                else:
                    output = "cmd_help"
                    if builtin_arg.export._here is True:
                        output = builtin_arg.export._value

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
                tmp_node = builtin_arg._previous_dfn
                from_ = builtin_arg._["from"]._value
                if from_ < -1:
                    raise EndUserError(dict(
                        attributes=dict(
                            value=from_,
                        ),
                        cmd_line=dy_err["cmd_line"][:builtin_arg._["from"]._cmd_line_index],
                        error_type=ErrorTypes().UsageFromValueError,
                        message="from LEVEL '{value}' must be greater or equal than '-1'.",
                        node_usage=builtin_arg._["from"]._dfn,
                        show_usage=False,
                        stack_trace="".join(traceback.format_stack()),
                        show_stack=False,
                        prefix=dy_err["prefix"],
                    ))

                if from_ == 0:
                    tmp_node = builtin_arg._previous_dfn
                else:
                    count = 0
                    while tmp_node.parent is not None:
                        tmp_node = tmp_node.parent
                        count += 1
                        if count == from_:
                            break

                depth = builtin_arg.depth._value
                if depth < -1:
                    raise EndUserError(dict(
                        attributes=dict(
                            value=builtin_arg.depth._value,
                        ),
                        cmd_line=dy_err["cmd_line"][:builtin_arg.depth._cmd_line_index],
                        error_type=ErrorTypes().UsageLevelValueError,
                        message="depth LEVEL '{value}' must be greater or equal than '-1'.",
                        node_usage=builtin_arg.depth._dfn,
                        show_usage=False,
                        stack_trace="".join(traceback.format_stack()),
                        show_stack=False,
                        prefix=dy_err["prefix"],
                    ))

                if depth == -1:
                    depth = None

                allproperties = None
                if builtin_arg.properties._here is True:
                    allproperties = sorted([prop for prop, dy in get_arg_properties().items() if dy["for_help"] is True])

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
                    raise EndUserError(dict(
                        attributes=dict(),
                        cmd_line=dy_err["cmd_line"][:builtin_arg._cmd_line_index],
                        error_type=ErrorTypes().BuiltinVersionNotProvided,
                        message="version not provided.",
                        node_usage=builtin_dfn,
                        show_usage=False,
                        stack_trace="".join(traceback.format_stack()),
                        show_stack=False,
                        prefix=dy_err["prefix"],
                    ))
    except EndUserError as e:
        if raise_exc is True:
            if _from_query:
                e.errors["node_usage"]=e.errors["node_usage"].location
                print(json.dumps(e.errors, indent=4, sort_keys=True, default=str), file=sys.stderr)
            raise
        else:
            msg.error(
                e.errors["message"],
                keys=e.errors["attributes"],
                prefix=e.errors["prefix"],
                pretty=pretty_msg,
            )

            if e.errors["show_usage"] is True:
                print_usage(e.errors["node_usage"])

            if e.errors["show_stack"] is True:
                print(e.errors["stack_trace"])

            sys.exit(1)

def last_check(
    dy_chk,
    dy_err,
    usage_dfn,
):
    for arg, props in dy_chk.items():
        process = False
        if usage_dfn is None:
            process = True
        else:
            if arg == usage_dfn:
                process = True
            else:
                tmp_arg = arg
                while True:
                    if tmp_arg._dfn == usage_dfn:
                        process = True
                        break
                    if tmp_arg._parent is None:
                        break
                    tmp_arg = tmp_arg._parent

        if process is True:
            if "chk_values_min" in props:
                values_final_check(arg, dy_err)

            if "chk_required_children" in props:
                process_required(arg, dy_err)

            if "chk_preset_children" in props:
                process_preset(arg, dy_err)

            if "chk_need_child" in props:
                if len(arg._args) == 0:
                    raise EndUserError(dict(
                        attributes=dict(
                            arg_alias=arg._alias,
                        ),
                        cmd_line=dy_err["cmd_line"][:arg._cmd_line_index],
                        error_type=ErrorTypes().ArgumentChildIsNeeded,
                        message="For argument '{arg_alias}' at least one child argument is needed.",
                        node_usage=arg._dfn,
                        show_usage=True,
                        stack_trace="".join(traceback.format_stack()),
                        show_stack=False,
                        prefix=dy_err["prefix"],
                    ))

def print_examples(node_dfn):
    if node_dfn.dy["examples"] is not None:
        for example in node_dfn.dy["examples"]:
            print(example)
    for node in node_dfn.nodes:
        print_examples(node)

def get_builtin_dfn(previous_node_dfn, node_dfn, builtin_dfn, usage_dfn):
    if node_dfn.dy["is_usage"] is True:
        usage_dfn = node_dfn
        if node_dfn.dy["is_builtin"] is True:
            builtin_dfn = node_dfn
    elif node_dfn.level == 2 and node_dfn.dy["is_builtin"] is True:
        if builtin_dfn is None:
            builtin_dfn = node_dfn
        else:
            ignore = (builtin_dfn.name ==
                      "_usage_" and builtin_dfn.dy["is_builtin"] is True)
            if ignore is False:
                builtin_dfn = node_dfn

    return node_dfn, builtin_dfn, usage_dfn

def get_prompted_value(input_type, label=None):
    if label is None:
        label = input_type
    if input_type == "input":
        return input(label+": ")
    elif input_type == "hidden":
        return getpass.getpass(label+": ")

def get_substitute_var(reg):
    dy = reg.groupdict()
    if dy["input"] is None:
        if dy["label"] is None:
            return reg.group()
        else:
            value = os.environ[dy["label"]].strip()
            return re.sub(r"^\"?(.*?)\"?$", r"\1", value)
    else:
        return get_prompted_value(dy["input"], dy["label"])

def process_required(parent_arg, dy_err, skip_preset=False, from_implicit=False):
    for child_name in parent_arg._dfn.dy["required_children"]:
        required_arg = parent_arg._[child_name]
        if required_arg._here is False:

            cmd_line_index = parent_arg._cmd_line_index
            if from_implicit is False:
                if required_arg._dfn.dy["values_required"] is True:
                    if required_arg._dfn.dy["default"] is None:
                        raise EndUserError(dict(
                            attributes=dict(
                                arg_alias=required_arg._default_alias
                            ),
                            cmd_line=dy_err["cmd_line"][:required_arg._parent._cmd_line_index],
                            error_type=ErrorTypes().RequiredArgumentMissing,
                            message="required argument '{arg_alias}' is missing.",
                            node_usage=parent_arg._dfn,
                            show_usage=True,
                            stack_trace="".join(traceback.format_stack()),
                            show_stack=False,
                            prefix=dy_err["prefix"],
                        ))

            activate_arg(required_arg, required_arg._dfn.dy["default_alias"],
                         dy_err, cmd_line_index, dy_chk=None, is_implicit=True)
            values_final_check(required_arg, dy_err)
            process_required(required_arg, dy_err,
                             skip_preset=False, from_implicit=True)

    if skip_preset is False:
        process_preset(parent_arg, dy_err, from_implicit=from_implicit)

def process_preset(parent_arg, dy_err, from_implicit=False):
    for child_name in parent_arg._dfn.dy["preset_children"]:
        preset_arg = parent_arg._[child_name]
        if preset_arg._here is False and parent_arg._has_explicit_nodes is False:
            cmd_line_index = parent_arg._cmd_line_index
            activate_arg(preset_arg, preset_arg._dfn.dy["default_alias"],
                         dy_err, cmd_line_index, dy_chk=None, is_implicit=True)
            values_final_check(preset_arg, dy_err)
            process_preset(preset_arg, dy_err)
    process_required(parent_arg, dy_err, skip_preset=True,
                     from_implicit=from_implicit)

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
