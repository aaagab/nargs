#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
import os
import re
import sys

from .aliases import check_aliases_conflict
from .nodes import NodeDfn
from .regexes import get_regex_dfn, get_regex_hints
from .set_dfn import get_auto_alias
from .set_dfn import get_filtered_dy
from .get_properties import get_arg_properties

from ..gpkgs import message as msg

def get_dfn_prefix(app_name, location, option=None):
    return "For '{}' at Nargs in definition for argument '{}'".format(app_name, location)

def get_location(pnode_dfn, arg_name):
    if pnode_dfn is None:
        return arg_name
    else:
        return "{}.{}".format(pnode_dfn.location, arg_name)

def verify_name(name, verified_names, dy_err):
    if isinstance(name, str):
        if name not in verified_names:
            if re.match(get_regex_dfn("def_arg_name")["rule"], name):
                verified_names.append(name)
            else:
                lst_errors=[
                    "name '{}' does not match argument regex:".format(name),
                    *get_regex_hints("def_arg_name"),
                ]
                if name[0] == "_":
                    properties=sorted(["_{}".format(prop) for prop, dy in get_arg_properties().items() if dy["for_definition"] is True])
                    lst_errors.append("Name '{}' not found in available properties: {}".format(name, properties))
                msg.error(lst_errors, prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        msg.error("Argument name '{}' wrong type {}. Type must match {}.".format(name, type(name), str), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)


def verify_type(dy_args, arg_name, dy_err):
    if dy_args[arg_name] is None:
        dy_args[arg_name]=dict()
    elif not isinstance(dy_args[arg_name], dict):
        msg.error("nested argument '{}' type {} must be of type {}.".format(arg_name, type(dy_args[arg_name]), dict), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

def get_node_dfn(
    builtins,
    dy_attr_aliases,
    pretty,
    app_name,
    dy_args,
    exc,
    arg_name=None,
    pnode_dfn=None,
    verified_names=None,
    dy_replicate=None,
    dy_chk=None,
    usage_node=None,
):
    if pnode_dfn is None:
        if dy_args is None:
            dy_args=dict()
        verified_names=[]
        dy_replicate=dict()
        dy_chk=dict()

        arg_name="args"
        dy_args=dict(args=dy_args)

    location=get_location(pnode_dfn, arg_name)
    dy_err=dict(
        exc=exc,
        location=location,
        prefix=get_dfn_prefix(app_name, location),
        pretty=pretty,
    )

    if arg_name == "@":
        elems=[]
        if isinstance(dy_args[arg_name], str):
            for elem in dy_args[arg_name].split(","):
                elem=elem.strip()
                if elem == "":
                    msg.error("'@' does not accept empty string.", prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                elems.append(elem)
        elif isinstance(dy_args[arg_name], list):
            for entry in dy_args[arg_name]:
                if isinstance(entry, str):
                    entry=entry.strip()
                    if entry == "":
                        msg.error("'@' does not accept empty string.", prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

                    if entry not in elems:
                        elems.append(entry)
                else:
                    msg.error("Wrong value type {} in list. It must be {}.".format(type(entry), str), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        else:            
            msg.error("Wrong value type {}. It must be either {} or {}.".format(type(dy_args[arg_name]), str, list), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        set_dy_replicate(pnode_dfn, dy_replicate, elems)
    else:
        node_level=None
        if pnode_dfn is None:
            node_level=1
        else:
            node_level=pnode_dfn.level+1

        if node_level != 2:
            verify_name(arg_name, verified_names, dy_err)
        verify_type(dy_args, arg_name, dy_err)

        filtered_dy=get_filtered_dy(
            pnode_dfn,
            arg_name,
            dy_args[arg_name],
            dy_attr_aliases,
            dy_err,
        )

        check_aliases_conflict(pnode_dfn, filtered_dy, dy_err)

        if filtered_dy["enabled"] is True:
            node_dfn=NodeDfn(
                dy=filtered_dy,
                location=location,
                name=arg_name,
                parent=pnode_dfn,
            )

            set_chk(dy_chk, node_dfn)

            if node_dfn.is_root is False:
                if node_dfn.dy["required"] is True:
                    node_dfn.parent.dy["required_children"].append(node_dfn.name)
                if node_dfn.dy["preset"] is True:
                    node_dfn.parent.dy["preset_children"].append(node_dfn.name)
                if node_dfn.name in node_dfn.parent.dy["xor"]:
                    group_nums=sorted([int(num) for num in node_dfn.parent.dy["xor"][node_dfn.name]])
                    node_dfn.dy["xor_groups"]=group_nums

            if node_dfn.is_root is True:
                node_dfn.dy["is_builtin"]=False
            elif node_dfn.parent.is_root is False:
                node_dfn.dy["is_builtin"]=node_dfn.parent.dy["is_builtin"]

            if node_dfn.is_root is True:
                add_builtins(builtins, dy_args, arg_name, verified_names, dy_attr_aliases, dy_err)

            for key in sorted(dy_args[arg_name]):
                get_node_dfn(
                    builtins=builtins,
                    dy_attr_aliases=dy_attr_aliases,
                    pretty=pretty,
                    app_name=app_name,
                    dy_args=dy_args[arg_name],
                    exc=exc,
                    arg_name=key,
                    pnode_dfn=node_dfn,
                    verified_names=verified_names,
                    dy_replicate=dy_replicate,
                    dy_chk=dy_chk,
                )

            if node_dfn.is_root is True:
                process_at_addresses(node_dfn, dy_replicate, verified_names, dy_attr_aliases, dy_chk, dy_err)
                final_check(dy_chk, dy_err, app_name)
                return node_dfn
        else:
            if pnode_dfn is None:
                return None

def final_check(dy_chk, dy_err, app_name):
    usage_nodes=[]
    builtin=None
    for node, chks in dy_chk.items():
        if "chk_xor" in chks:
            tmp_xor_groups=[]
            dy_xor_groups=dict()
            for name in sorted(node.dy["xor"]):
                if name in node.dy_nodes:
                    cnode=node.dy_nodes[name]
                    if cnode.dy["preset"] is True:
                        for group_num in cnode.dy["xor_groups"]:
                            if group_num not in tmp_xor_groups:
                                tmp_xor_groups.append(group_num)
                                dy_xor_groups[group_num]=name
                            else:
                                msg.error("at key '_xor' there is a xor conflict because child arguments '{}' and '{}' have both '_preset={}' and are part of the same xor group.".format(
                                    name, 
                                    dy_xor_groups[group_num],
                                    True,
                                ), prefix=get_dfn_prefix(app_name, node.location), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                else:
                    msg.error("at key '_xor' child argument name '{}' not found.".format(name), prefix=get_dfn_prefix(app_name, node.location), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)



        if "chk_need_child" in chks:
            if len(node.nodes) == 0:
                node.dy["need_child"]=False
            else:
                if node.level == 1:
                    node.dy["need_child"]=False
                    for cnode in node.nodes:
                        if cnode.dy["is_builtin"] is False and cnode.dy["is_custom_builtin"] is False and cnode.dy["is_usage"] is False:
                            node.dy["need_child"]=True
                            break

        if "chk_is_usage" in chks:
            if node.dy["is_builtin"] is True:
                builtin=node
            usage_nodes.append(node)

    if len(usage_nodes) > 1:
        error_msgs=[
            "property '_is_usage' can only be declared for one argument but it has been declared for multiple arguments:",
            *sorted([ "- {}".format(node.location) for node in usage_nodes]),
        ]

        if builtin is not None:
            error_msgs.append(
                "Built-in node '{}' may be disabled through Nargs 'builtins' option.".format(builtin.location),
            )


        msg.error(error_msgs
        , prefix=get_dfn_prefix(app_name, node.location), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    if len(usage_nodes) == 1:
        node_usage=usage_nodes[0]

        for key, value in dict(
            allow_parent_fork=True,
            allow_siblings=True,
            is_custom_builtin=True,
            preset=False,
            repeat="replace",
            required=False,
        ).items():
            if node_usage.dy[key] != value:
                ignore=node_usage.name == "_usage_" and key == "is_custom_builtin"
                if ignore is False:
                    msg.error("'_is_usage' node at key '{}' value '{}' must be '{}'.".format(key, node_usage.dy[key], value), prefix=get_dfn_prefix(app_name, node_usage.location), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        if node_usage in node_usage.parent.dy_xor:
            msg.error("'_is_usage' node can't be present in parent '{}' '_xor' groups.".format(node_usage.parent.location), prefix=get_dfn_prefix(app_name, node_usage.location), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

def set_chk(dy_chk, node_dfn):
    if len(node_dfn.dy["xor"]) > 0:
        dy_chk[node_dfn]=["chk_xor"]

    for prop in ["need_child", "is_usage"]:
        if node_dfn.dy[prop] is True:
            if node_dfn in dy_chk:
                dy_chk[node_dfn].append("chk_{}".format(prop))
            else:
                dy_chk[node_dfn]=["chk_{}".format(prop)]
    

def duplicate_node(tmp_prefix, dy_err, node_to_copy, pnode_at, dy_chk, first_node=True):
    if first_node is True:
        if node_to_copy.dy["is_builtin"] is True:
            msg.error("Built-in argument '{}' can't be duplicated.".format(node_to_copy.name, pnode_at.location), prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        check_aliases_conflict(pnode_at, node_to_copy.dy, dy_err)

    node_at=NodeDfn(
        dy=deepcopy(node_to_copy.dy),
        location=get_location(pnode_at, node_to_copy.name),
        name=node_to_copy.name,
        parent=pnode_at,
    )
    
    set_chk(dy_chk, node_at)

    for child_node_to_copy in node_to_copy.nodes:
        duplicate_node(
            tmp_prefix=tmp_prefix,
            dy_err=dy_err,
            node_to_copy=child_node_to_copy,
            pnode_at=node_at,
            dy_chk=dy_chk,
            first_node=False,
        )

def set_dy_replicate(node_dfn, dy_replicate, addresses):
    at_address=".".join(node_dfn.location.split("."))
    dy_replicate[at_address]=dict(
        at_addresses=addresses,
        pnode=node_dfn,
    )

def get_node_to_copy(tmp_prefix, dy_err, at_path, root_node, pnode=None):
    ref_nodes=[]
    at_path_index=None
    if pnode is None:
        pnode=root_node
        at_path_index=0
        at_path=at_path.split(".")
        ref_nodes=[root_node]
    else:
        at_path_index=pnode.level
        ref_nodes=pnode.nodes
    
    node_name=at_path[at_path_index]
    for ref_node in ref_nodes:
        if node_name == ref_node.name:
            if at_path_index == len(at_path) - 1:
                return ref_node
            else:
                return get_node_to_copy(tmp_prefix, dy_err, at_path, root_node, ref_node) 

    msg.error("argument path '{}' does not exist in arguments tree.".format(".".join(at_path)), prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

def get_recursive_loops(dy_unsolved, at_address, loops=None, loop=None, addresses_done=None):
    is_root=False
    if addresses_done is None:
        is_root=True
        addresses_done=[]
        loops=[]
        loop=[at_address]
        loops.append(loop)
    else:
        loop.append(at_address)

    if at_address in dy_unsolved:
        if at_address not in addresses_done:
            addresses_done.append(at_address)
            index=0
            for addr in dy_unsolved[at_address]:
                if at_address in dy_unsolved:
                    index+=1
                    tmp_loop=None
                    if index > 1:
                        tmp_loop=deepcopy(loop)
                        loops.append(tmp_loop)
                    else:
                        tmp_loop=loop
                    get_recursive_loops(dy_unsolved, addr, loops, tmp_loop, addresses_done)

    if is_root is True:
        return loops

def is_in_dy_replicate(dy_replicate, address):
    if address in dy_replicate:
        return True
    else:
        addresses=sorted(dy_replicate)
        for addr in addresses:
            if len(address) <= len(addr):
                if addr[:len(address)] == address:
                    return True
        return False

def process_at_addresses(node_dfn, dy_replicate, verified_names, dy_attr_aliases, dy_chk, dy_err):
    if len(dy_replicate) > 0:
        dy_unsolved=dict()
        ref_nodes=dict()
        ref_prefixes=dict()
    
        while True:
            element_deleted=False
            for at_address in sorted(dy_replicate):
                dy=dy_replicate[at_address]
                for nested_at_address in dy["at_addresses"].copy():
                    tmp_prefix="{} for argument '{}' at key '@' with value '{}'".format(dy_err["prefix"], dy["pnode"].location, nested_at_address)
                    if is_in_dy_replicate(dy_replicate, nested_at_address) is True:
                        if at_address not in dy_unsolved:
                            dy_unsolved[at_address]=[]
                            ref_nodes[at_address]=dy["pnode"]
                            ref_prefixes[at_address]=tmp_prefix

                        if nested_at_address not in dy_unsolved[at_address]:
                            dy_unsolved[at_address].append(nested_at_address)
                    else:
                        node_to_copy=get_node_to_copy(tmp_prefix, dy_err, nested_at_address, node_dfn.root)
                        
                        node_dst_names=[node.name for node in dy["pnode"].nodes]
                        if node_to_copy.name in node_dst_names:
                            msg.error("argument '{}' can't be duplicated at location '{}' because one sibling argument has already the same name.".format(node_to_copy.name, dy["pnode"].location), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

                        if node_to_copy.dy["enabled"] is True:
                            duplicate_node(
                                tmp_prefix,
                                dy_err,
                                node_to_copy,
                                dy["pnode"],
                                dy_chk,
                            )        
                        dy_replicate[at_address]["at_addresses"].remove(nested_at_address)
                        if at_address in dy_unsolved:
                            if nested_at_address in dy_unsolved[at_address]:
                                dy_unsolved[at_address].remove(nested_at_address)
                                if len(dy_unsolved[at_address]) == 0:
                                    del dy_unsolved[at_address]
                        element_deleted=True
                        if len(dy_replicate[at_address]["at_addresses"]) == 0:
                            del dy_replicate[at_address]

                        if len(dy_replicate) == 0:
                            break
            
            if element_deleted is True:
                if len(dy_replicate) == 0:
                    break
            else:
                recursive_loop=None
                recursive_addr=None
                recursive_element=None
                for at_address in sorted(dy_unsolved):
                    for recursive_loop in get_recursive_loops(dy_unsolved, at_address):
                        for addr in sorted(dy_unsolved):
                            num_occurrences=recursive_loop.count(addr)
                            for elem in recursive_loop:
                                if len(elem) < len(addr):
                                    if addr[:len(elem)] == elem: 
                                        num_occurrences+=1
                            if num_occurrences > 1:
                                recursive_addr=at_address
                                recursive_element=addr
                                break
                        if recursive_addr is not None:
                            break
                    if recursive_addr is not None:
                        break

                tmp_prefix=None
                error_msg="Infinite recursion"
                if recursive_addr is None:
                    tmp_prefix=dy_err["prefix"]
                    error_msg+=" not defined for key '@' in {}.".format(sorted(dy_unsolved));
                else:
                    tmp_prefix=ref_prefixes[recursive_addr]
                    error_msg+=" at address {} with loop {}.".format(recursive_element, recursive_loop)

                msg.error(error_msg, prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

def add_builtins(builtins, dy_args, arg_name, verified_names, dy_attr_aliases, dy_err):
    for key in dy_args[arg_name].copy():
        if key != "@":
            verify_name(key, verified_names, dy_err)
            verify_type(dy_args[arg_name], key, dy_err)
            dy_args[arg_name][key]["_is_builtin"]=False

    flag_prefix=dy_attr_aliases["auto_alias_prefix"]
    if flag_prefix == "--":
        flag_prefix="-"

    properties=sorted([prop for prop, dy in get_arg_properties().items() if dy["for_help"] is True])

    dy_builtins={
        "_help_": {
            "_aliases": "{},{}h".format(get_auto_alias(dy_attr_aliases, "help"), flag_prefix),
            "_allow_parent_fork": False,
            "_allow_siblings": False, 
            "_hint": "Print program help and exit.",
            "examples" : {
                "_aliases": "{},{}e".format(get_auto_alias(dy_attr_aliases, "examples"), flag_prefix),
                "_allow_siblings": False,
                "_hint": "Print program examples and exit.",
            },
            "export": {
                "_hint": "Export help to selected format.",
                "_in": "asciidoc,html,markdown,text",
                "overwrite": {
                    "_hint": "Implicitly overwrites exported documentation file if it exists already."
                },
                "to": {
                    "_hint": "Export help to selected path.",
                    "_type": "vpath",
                },
            },
            "metadata" : {
                "_aliases": "{},{}m".format(get_auto_alias(dy_attr_aliases, "metadata"), flag_prefix),
                "_allow_siblings": False,
                "_hint": "Print program metadata and exit.",
                "_info": "KEY can be provided to get only selected key(s) from metadata dictionary. If KEY is not provided then all keys from metadata dictionary are selected.",
                "_label": "KEY",
                "_values": "*",
                "_xor": "keys,values",
                "keys": {
                    "_aliases": "{},{}k".format(get_auto_alias(dy_attr_aliases, "keys"), flag_prefix),
                    "_hint": "Return only keys from metadata dictionary",
                },
                "values": {
                    "_aliases": "{},{}v".format(get_auto_alias(dy_attr_aliases, "values"), flag_prefix),
                    "_hint": "Return only values from metadata dictionary",
                },
                "json": {
                    "_aliases": "{},{}j".format(get_auto_alias(dy_attr_aliases, "json"), flag_prefix),
                    "_hint": "Selected metadata is returned as json dictionary",
                },
            },
            "syntax": {
                "_aliases": get_auto_alias(dy_attr_aliases, "syntax"),
                "_hint": "Print arguments Cheat Sheet syntax and exit.",
                "only": {
                    "_aliases": get_auto_alias(dy_attr_aliases, "only"),
                    "_hint": "Print only arguments Cheat Sheet syntax and exit.",
                },
            },
        },
        "_path_etc_": {
            "_aliases": get_auto_alias(dy_attr_aliases, "path_etc"),
            "_allow_parent_fork": False,
            "_allow_siblings": False, 
            "_hint": "Print program configuration path and exit.",
        },
        "_query_": {
            "_aliases": "{}".format(get_auto_alias(dy_attr_aliases, "query")),
            "_allow_parent_fork": False,
            "_allow_siblings": False, 
            "_hint": "Load program's arguments from a json file with optional parameterized values.",
            "_info": "query argument allows to execute safe command-line arguments query on the program. Command-line arguments are collected through a JSON file. The JSON file has two attributes 'command' and 'params'. 'command' accepts a list of command-line arguments with values where each value may be replaced with a question mark. 'params' accepts a list of values. The number of values in 'params' must match the number of question marks in 'command'. 'command' arguments are only parsed as arguments and 'params' are only parsed as argument values. It allows a safe way to pass values collected from a third party program like a web application to the command-line program. All errors are returned as a json dump for better communication with third party program.(see Nargs developer documentation)",
            "_type": "file",
        },
        "_usage_": {
            "_aliases": "{},{}u,?".format(get_auto_alias(dy_attr_aliases, "usage"), flag_prefix),
            "_hint": "Print program usage and exit.",
            "_info": "LEVEL is an integer >= 0. LEVEL number describes the number of nested node levels to print. LEVEL number is relative to current argument node level. If LEVEL == 0 then all nested node levels are printed. If LEVEL == 1 then only current argument is printed. If LEVEL > 1 current argument's node levels are printed and LEVEL sets the depth of node levels nesting.",
            "_is_usage": True,
            "examples": {
                "_aliases": "{},{}e".format(get_auto_alias(dy_attr_aliases, "examples"), flag_prefix),
                "_hint": "Print argument(s) examples if any",
            },
            "depth": {
                "_aliases": "{},{}d".format(get_auto_alias(dy_attr_aliases, "depth"), flag_prefix),
                "_default": 1,
                "_required": True,
                "_hint": "Provide the printing depth of nested arguments.",
                "_info": "If LEVEL == -1 then all nested arguments are printed. If LEVEL == 0 then only selected argument is printed. If LEVEL > 0 then the bigger the LEVEL number is, the bigger the children nesting level is if any children are available.",
                "_label": "LEVEL",
                "_type": "int",
                "_values": "1",
            },
            "from": {
                "_aliases": "{},{}f".format(get_auto_alias(dy_attr_aliases, "from"), flag_prefix),
                "_default": 0,
                "_required": True,
                "_hint": "This option allows to start printing usage from a parent.",
                "_info": "If LEVEL == -1 then selected argument is the root argument. If LEVEL == 0 then selected argument is the current argument. If LEVEL > 0 then one argument parent is selected and the bigger the LEVEL number is, the older the selected parent is unless parent's limit is reached. Argument's parent's limit is the oldest parent also called the root argument.",
                "_label": "LEVEL",
                "_type": "int",
                "_values": "1",
            },
            "flags": {
                "_aliases": "{},{}F".format(get_auto_alias(dy_attr_aliases, "flags"), flag_prefix),
                "_hint": "Print flag set if any for all arguments available on the terminal.",
            },
            "hint": {
                "_aliases": "{},{}h".format(get_auto_alias(dy_attr_aliases, "hint"), flag_prefix),
                "_hint": "Print argument(s) hint if any.",
            },
            "info": {
                "_aliases": "{},{}i".format(get_auto_alias(dy_attr_aliases, "info"), flag_prefix),
                "_hint": "Print argument(s) info if any.",
            },
            "path": {
                "_aliases": "{},{}p".format(get_auto_alias(dy_attr_aliases, "path"), flag_prefix),
                "_hint": "Print argument(s) path with values.",
            },
            "properties": {
                "_aliases": "{},{}r".format(get_auto_alias(dy_attr_aliases, "properties"), flag_prefix),
                "_hint": "Print argument(s) properties.",
                "_in": properties,
                "_values": "1-{}?".format(len(properties)),
            }

        },
        "_version_": {
            "_aliases": "{},{}v".format(get_auto_alias(dy_attr_aliases, "version"), flag_prefix),
            "_allow_parent_fork": False,
            "_allow_siblings": False, 
            "_hint": "Print program version and exit.",
        },
    }
    for builtin in builtins:
        tmp_name="_{}_".format(builtin)
        aliases=builtins[builtin]
        if aliases is not None:
            dy_builtins[tmp_name]["_aliases"]=aliases
        set_builtin_child(dy_builtins, tmp_name)
        dy_args[arg_name][tmp_name]=dy_builtins[tmp_name]

def set_builtin_child(dy, name):
    dy[name]["_is_builtin"]=True
    for prop in dy[name]:
        if prop[0] != "_":
            set_builtin_child(dy[name], prop)

