#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
import os
import re
import sys

from .aliases import set_explicit_aliases
from .nodes import NodeDfn
from .set_dfn import get_dfn_prefix
from .regexes import get_regex, get_regex_hints

from ..gpkgs import message as msg

def verify_name(name, is_builtin, location, verified_names, pretty, app_name):
    prefix="For '{}' at Nargs in definition for key '{}'".format(app_name, location)
    if name not in verified_names:
        if re.match(get_regex("def_arg_name")["rule"], name):
            verified_names.append(name)
        else:
            if is_builtin is False:
                msg.error([
                    "Argument name '{}' does not match regex:".format(name),
                    *get_regex_hints("def_arg_name"),
                ], prefix=prefix, pretty=pretty, exit=1)

def get_node_dfn(
    builtins=None,
    dy_metadata=None,
    dy_dfn=None,
    arg_name=None,
    pnode_dfn=None,
    verified_names=None,
    dy_replicate=None,
    pretty=False,
    app_name=None,
):
    if pnode_dfn is None:
        if builtins is None:
            builtins=[]
        if dy_metadata is None:
            dy_metadata=dict()
        if dy_dfn is None:
            dy_dfn=dict()
        if verified_names is None:
            verified_names=[]
        if dy_replicate is None:
            dy_replicate=dict()
        
        if len(dy_dfn) == 0:
            return None
        elif len(dy_dfn) != 1: 
            msg.error("definition accepts only one root key.", prefix=get_dfn_prefix(app_name), pretty=pretty, exit=1)
        else:
            arg_name=next(iter(dy_dfn))
            
    if arg_name == "@":
        if pnode_dfn is None:
            msg.error("'@' not allowed at root key.", prefix=get_dfn_prefix(app_name), pretty=pretty, exit=1)
        else:
            elems=[]
            if isinstance(dy_dfn[arg_name], str):
                elems.append(dy_dfn[arg_name])
            elif isinstance(dy_dfn[arg_name], list):
                for entry in dy_dfn[arg_name]:
                    if isinstance(entry, str):
                        if entry not in elems:
                            elems.append(entry)
                    else:
                        msg.error("Wrong value type {} in list. It must be {}.".format(type(entry), str), prefix=get_dfn_prefix(app_name, pnode_dfn.location, arg_name), pretty=pretty, exit=1)
            else:            
                msg.error("Wrong value type {}. It must be either {} or {}.".format(type(dy_dfn[arg_name]), str, list), prefix=get_dfn_prefix(app_name, pnode_dfn.location, arg_name), pretty=pretty, exit=1)

            set_dy_replicate(pnode_dfn, dy_replicate, elems)
    else:
        location=None
        siblings_level=None
        is_builtin=None

        if pnode_dfn is None:
            location=arg_name
            siblings_level=1
        else:
            location=pnode_dfn.location
            siblings_level=pnode_dfn.level+1

        if dy_dfn[arg_name] is None:
            dy_dfn[arg_name]=dict()
            is_builtin=False
        elif not isinstance(dy_dfn[arg_name], dict):
            msg.error("for nested argument '{}' value with type {} must be of type {}.".format(arg_name, type(dy_dfn[arg_name]), dict), prefix=get_dfn_prefix(app_name, location), pretty=pretty, exit=1)
        
        if siblings_level == 1:
            dy_dfn[arg_name]["_is_builtin"]=False
            is_builtin=False
        elif siblings_level == 2:
            # dy_dfn[arg_name]["_is_builtin"] builtin has been set with add_builtins
            is_builtin=dy_dfn[arg_name]["_is_builtin"]
        else:
            if pnode_dfn.dy["is_builtin"] is True:
                dy_dfn[arg_name]["_is_builtin"]=True
                is_builtin=True
            else:
                dy_dfn[arg_name]["_is_builtin"]=False
                is_builtin=False

        verify_name(arg_name, is_builtin, location, verified_names, pretty, app_name)

        node_dfn=NodeDfn(dy=dy_dfn[arg_name], name=arg_name, parent=pnode_dfn, pretty=pretty, app_name=app_name)

        if node_dfn.dy["enabled"] is True:
            if node_dfn.is_root is True:
                add_builtins(builtins, dy_dfn, arg_name, location, verified_names, pretty, app_name)

            for key in sorted(dy_dfn[arg_name]):
                get_node_dfn(
                    builtins=builtins,
                    dy_metadata=dy_metadata,
                    dy_dfn=dy_dfn[arg_name],
                    arg_name=key,
                    pnode_dfn=node_dfn,
                    verified_names=verified_names,
                    dy_replicate=dy_replicate,
                    pretty=pretty,
                    app_name=app_name,
                )
        else:
            if node_dfn.is_root is False:
                node_dfn.parent.nodes.remove(node_dfn)

        if node_dfn.is_root is True:
            if node_dfn.dy["enabled"] is True:
                process_at_addresses(node_dfn, dy_replicate, verified_names, pretty, app_name)
                process_aliases(node_dfn)
                return node_dfn
            else:
                return None

def set_dy_replicate(node_dfn, dy_replicate, addresses):
    at_address=".".join(node_dfn.location.split(" > "))
    dy_replicate[at_address]=dict(
        at_addresses=addresses,
        pnode=node_dfn,
    )

def add_builtins(builtins, dy_dfn, arg_name, location, verified_names, pretty, app_name):
    for key in dy_dfn[arg_name]:
        if key != "@":
            verify_name(key, False, location, verified_names, pretty, app_name)
            dy_dfn[arg_name][key]["_is_builtin"]=False

    dy_builtins={
        "_cmd_": {
            "_aliases": ":cmd,:c",
            "_hint": "Load program's arguments from a file.",
            "_info": "Arguments can be typed with indentation and new lines in the text file. Lines are then striped and new lines are joined with spaces and the whole text is split with shlex and fed again to the program. Root argument alias needs to be provided as first argument. Empty lines and lines starting with '#' are ignored.",
            "_type": "file",
            "_is_builtin": True,
        },
        "_help_": {
            "_aliases": ":help,:h",
            "_hint": "Print program help and exit.",
            "_is_builtin": True,
            "export": {
                "_hint": "Export help to selected format.",
                "_in": "asciidoc,html,markdown,text",
                "to": {
                    "_hint": "Export help to selected path.",
                    "_type": "vpath",
                },
            },
            "metadata" : {
                "_hint": "Print program metadata and exit.",
                "_info": "KEY can be provided to get only selected key(s) from metadata dictionary. If KEY is not provided then all keys from metadata dictionary are selected.",
                "_label": "KEY",
                "_values": "*",
                "get": {
                    "_aliases": "-v,--value,--values,-k,--key,--keys",
                    "_hint": "Filter metadata dictionary",
                    "_info": "Either -v, --value, or --values return only values from selected metadata. Either -k, --key, or --keys return only keys from selected metadata.",
                },
                "json": {
                    "_hint": "Selected metadata is returned as json dictionary",
                },
            },
            "syntax": {
                "_hint": "Print arguments Cheat Sheet syntax and exit.",
            },
        },
        "_usage_": {
            "_aliases": ":usage,:u",
            "_hint": "Print program usage and exit.",
            "_info": "LEVEL is an integer >= 0. LEVEL number describes the number of nested siblings levels to print. LEVEL number is relative to current argument siblings LEVEL. If LEVEL == 0 then all nested siblings levels are printed. If LEVEL == 1 then only current argument is printed. If LEVEL > 1 current argument's siblings levels are printed and LEVEL sets the depth of siblings levels nesting.",
            "_is_builtin": True,
            "examples": {
                "_hint": "Print argument(s) examples if any",
            },
            "depth": {
                "_default": -1,
                "_required": True,
                "_hint": "Provide the printing depth of nested arguments.",
                "_info": "If LEVEL == -1 then all nested arguments are printed. If LEVEL == 0 then only selected argument is printed. If LEVEL > 0 then the bigger the LEVEL number is, the bigger the children nesting level is if any children are available.",
                "_label": "LEVEL",
                "_type": "int",
                "_values": "1",
            },
            "from_": {
                "_aliases": "-f,--from",
                "_default": 0,
                "_required": True,
                "_hint": "This option allows to start printing usage from a parent.",
                "_info": "If LEVEL == -1 then selected argument is the root argument. If LEVEL == 0 then selected argument is the current argument. If LEVEL > 0 then one argument parent is selected and the bigger the LEVEL number is, the older the selected parent is unless parent's limit is reached. Argument's parent's limit is the oldest parent also called the root argument.",
                "_label": "LEVEL",
                "_type": "int",
                "_values": "1",
            },
            "hint": {
                "_hint": "Print argument(s) hint if any",
            },
            "info": {
                "_hint": "Print argument(s) info if any",
            },
            "path": {
                "_hint": "Print argument(s) path with values",
            }
        },
    }
    for builtin in builtins:
        tmp_name="_{}_".format(builtin)
        dy_dfn[arg_name][tmp_name]=dy_builtins[tmp_name]

def get_aliases_sort(node):
    aliases_sort=None
    if len(node.dy["aliases"]) > 0:
        tmp_aliases=[]
        dy_aliases=dict()
        for alias in node.dy["aliases"]:
            tmp_alias=re.sub(r"^(-+|:)", "", alias)
            if tmp_alias not in dy_aliases:
                dy_aliases[tmp_alias]=[]
            dy_aliases[tmp_alias].append(alias)

        aliases_sort=[]
        for tmp_alias in sorted(dy_aliases):
            aliases_sort.append(tmp_alias)
            dy_length=dict()
            for alias in sorted(dy_aliases[tmp_alias]):
                length=len(alias.replace(tmp_alias, ""))
                if length not in dy_length:
                    dy_length[length]=[]
                dy_length[length].append(alias)

            for l in sorted(dy_length):
                for alias in sorted(dy_length[l]):
                    tmp_aliases.append(alias)

        node.dy["aliases"]=tmp_aliases
        aliases_sort=",".join(aliases_sort)

    return aliases_sort

def process_aliases(node_dfn):
    node_dfn.current_arg._default_alias=node_dfn.dy["default_alias"]
    node_dfn.current_arg._["_default_alias"]=node_dfn.dy["default_alias"]
    node_dfn.current_arg._aliases=node_dfn.dy["aliases"]
    node_dfn.current_arg._["_aliases"]=node_dfn.dy["aliases"]
    node_dfn.dy["aliases_sort"]=get_aliases_sort(node_dfn)
    del node_dfn.dy["dfn_aliases"]

    set_implicit_aliases(node_dfn)

    for node in node_dfn.nodes:
        process_aliases(node)

def get_node_to_copy(prefix, pretty, at_path, root_node, pnode=None):
    ref_nodes=[]
    level=None
    if pnode is None:
        pnode=root_node
        level=0
        at_path=at_path.split(".")
        ref_nodes=[root_node]
    else:
        level=pnode.level
        ref_nodes=pnode.nodes
    
    node_name=at_path[level]
    for ref_node in ref_nodes:
        if node_name == ref_node.name:
            if level == len(at_path) - 1:
                return ref_node
            else:
                return get_node_to_copy(prefix, pretty, at_path, root_node, ref_node) 

    msg.error("argument with name '{}' does not exist in arguments tree.".format(node_name), prefix=prefix, pretty=pretty, exit=1)

def duplicate_node(prefix, pnode_to_copy, pnode_at, pretty, app_name):
    if pnode_to_copy in pnode_at.parents:
        msg.error("Infinite recursion. Argument '{}' can't be added at '{}' because it is a already one of its parents.".format(pnode_to_copy.name, pnode_at.location), prefix=prefix, pretty=pretty, exit=1)

    node_at=NodeDfn(dy=deepcopy(pnode_to_copy.dy), name=pnode_to_copy.name, parent=pnode_at, is_dy_preset=True, pretty=pretty, app_name=app_name)
    if node_at.dy["enabled"] is True:
        set_explicit_aliases(node_at, pretty, app_name)
    for node_to_copy in pnode_to_copy.nodes:
        duplicate_node(
            prefix=prefix,
            pnode_to_copy=node_to_copy,
            pnode_at=node_at,
            pretty=pretty,
            app_name=app_name,
        )

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

def process_at_addresses(node_dfn, dy_replicate, verified_names, pretty, app_name):
    start_prefix="For '{}' at Nargs in definition".format(app_name)
    dy_unsolved=dict()
    ref_nodes=dict()
    ref_prefixes=dict()
    while True:
        element_deleted=False
        for at_address in sorted(dy_replicate):
            dy=dy_replicate[at_address]
            for nested_at_address in dy["at_addresses"].copy():
                prefix="{} for argument '{}' at key '@' with value '{}'".format(start_prefix, dy["pnode"].location, nested_at_address)
                if is_in_dy_replicate(dy_replicate, nested_at_address) is True:
                # if nested_at_address in dy_replicate:
                    if at_address not in dy_unsolved:
                        dy_unsolved[at_address]=[]
                        ref_nodes[at_address]=dy["pnode"]
                        ref_prefixes[at_address]=prefix

                    if nested_at_address not in dy_unsolved[at_address]:
                        dy_unsolved[at_address].append(nested_at_address)
                else:
                    node_to_copy=get_node_to_copy(prefix, pretty, nested_at_address, node_dfn.root)
                    node_dst_names=[node.name for node in dy["pnode"].nodes]
                    if node_to_copy.name in node_dst_names:
                        msg.error("argument '{}' can't be duplicated at location '{}' because one sibling argument has already the same name.".format(node_to_copy.name, dy["pnode"].location), prefix=prefix, pretty=pretty, exit=1)

                    duplicate_node(prefix, node_to_copy, dy["pnode"], pretty, app_name)        # input("ppokpok")
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
                        num_occurences=recursive_loop.count(addr)
                        for elem in recursive_loop:
                            if len(elem) < len(addr):
                                if addr[:len(elem)] == elem: 
                                    num_occurences+=1
                        if num_occurences > 1:
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
                tmp_prefix=start_prefix
                error_msg+=" not defined for key '@' in {}.".format(sorted(dy_unsolved));
            else:
                error_msg+=" at address {} with loop {}.".format(recursive_element, recursive_loop)
                tmp_prefix=ref_prefixes[recursive_addr]

            msg.error(error_msg, prefix=tmp_prefix, pretty=pretty)
            sys.exit(1)

def get_cached_node_dfn(dy_dfn, pretty, app_name, arg_name=None, pnode_dfn=None):
    tmp_dy_dfn=dict()
    if pnode_dfn is None:
        arg_name=next(iter(dy_dfn))
    
    for key, value in dy_dfn[arg_name].items():
        if key != "args":
            tmp_dy_dfn[key]=value

    node_dfn=NodeDfn(dy=tmp_dy_dfn, name=arg_name, parent=pnode_dfn, is_dy_preset=True, pretty=pretty, app_name=app_name)
    if node_dfn.is_root is False:
        for alias in node_dfn.dy["aliases"]:
            node_dfn.parent.dy_aliases[alias]=dict(explicit=node_dfn, implicit=[])
        
    node_dfn.current_arg._default_alias=tmp_dy_dfn["default_alias"]

    for key in dy_dfn[arg_name]["args"]:
        get_cached_node_dfn(
            dy_dfn=dy_dfn[arg_name]["args"],
            pretty=pretty,
            app_name=app_name,
            arg_name=key,
            pnode_dfn=node_dfn,
        )

    set_implicit_aliases(node_dfn)

    if node_dfn.is_root is True:
        return node_dfn

def set_implicit_aliases(node_dfn):
    if node_dfn.is_root is False:
        for alias in node_dfn.parent.dy_aliases:
            if alias not in node_dfn.dy_aliases:
                node_dfn.dy_aliases[alias]=dict(explicit=None, implicit=[])

            for imp_node in node_dfn.parent.dy_aliases[alias]["implicit"]:
                node_dfn.dy_aliases[alias]["implicit"].append(imp_node)

            if node_dfn.parent.dy_aliases[alias]["explicit"] is not None:
                node_dfn.dy_aliases[alias]["implicit"].append(node_dfn.parent.dy_aliases[alias]["explicit"])
