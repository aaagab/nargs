#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
import os
import re
import sys

from .aliases import set_explicit_aliases
from .nodes import NodeDfn
from .regexes import get_regex, get_regex_hints, get_flags_precedence
from .set_dfn import get_dfn_prefix, get_auto_alias

from ..gpkgs import message as msg

def verify_name(name, is_builtin, location, verified_names, pretty, app_name):
    prefix="For '{}' at Nargs in definition for key '{}'".format(app_name, location)

    if isinstance(name, str):
        if name not in verified_names:
            if re.match(get_regex("def_arg_name")["rule"], name):
                verified_names.append(name)
            else:
                if is_builtin is False:
                    msg.error([
                        "Argument name '{}' does not match regex:".format(name),
                        *get_regex_hints("def_arg_name"),
                    ], prefix=prefix, pretty=pretty, exit=1)
    else:
        msg.error("Argument name '{}' wrong type {}. Type must match {}.".format(name, type(name), str), prefix=prefix, pretty=pretty, exit=1)


def verify_type(dy_args, arg_name, app_name, location, pretty):
    # pprint(dy_args)
    # print(arg_name)
    if dy_args[arg_name] is None:
        dy_args[arg_name]=dict()
        # is_builtin=False
    elif not isinstance(dy_args[arg_name], dict):
        msg.error("for nested argument '{}' value with type {} must be of type {}.".format(arg_name, type(dy_args[arg_name]), dict), prefix=get_dfn_prefix(app_name, location), pretty=pretty, exit=1)

def get_node_dfn(
    builtins=None,
    dy_metadata=None,
    dy_args=None,
    arg_name=None,
    pnode_dfn=None,
    verified_names=None,
    dy_replicate=None,
    pretty=False,
    app_name=None,
    dy_attr_aliases=dict(),
    xor_nodes=None,
):
    # I should set xor_nodes here so then I check if these names exist.
    # in a second I also have a function to populate dfn object instead of names so it can be restored from cache and also I can do a quick check with get_args on node_dfn that shouldn't be here'

    if pnode_dfn is None:
        if builtins is None:
            builtins=[]
        if dy_metadata is None:
            dy_metadata=dict()
        if dy_args is None:
            dy_args=dict()
        verified_names=[]
        dy_replicate=dict()
        xor_nodes=[]
        
        if len(dy_args) == 0:
            return None
        else:
            arg_name="args"
            dy_args=dict(args=dy_args)
            
    if arg_name == "@":
        elems=[]
        if isinstance(dy_args[arg_name], str):
            elems.append(dy_args[arg_name])
        elif isinstance(dy_args[arg_name], list):
            for entry in dy_args[arg_name]:
                if isinstance(entry, str):
                    if entry not in elems:
                        elems.append(entry)
                else:
                    msg.error("Wrong value type {} in list. It must be {}.".format(type(entry), str), prefix=get_dfn_prefix(app_name, pnode_dfn.location, arg_name), pretty=pretty, exit=1)
        else:            
            msg.error("Wrong value type {}. It must be either {} or {}.".format(type(dy_args[arg_name]), str, list), prefix=get_dfn_prefix(app_name, pnode_dfn.location, arg_name), pretty=pretty, exit=1)

        set_dy_replicate(pnode_dfn, dy_replicate, elems)
    else:
        location=None
        node_level=None

        if pnode_dfn is None:
            location=arg_name
            node_level=1
        else:
            location=pnode_dfn.location
            node_level=pnode_dfn.level+1

        if node_level != 2:
            is_builtin=False
            verify_name(arg_name, is_builtin, location, verified_names, pretty, app_name)
            verify_type(dy_args, arg_name, app_name, location, pretty)
            dy_args[arg_name]["_is_builtin"]=False

        node_dfn=NodeDfn(
            dy=dy_args[arg_name],
            is_dy_preset=False,
            name=arg_name,
            parent=pnode_dfn,
            pretty=pretty,
            app_name=app_name,
            dy_attr_aliases=dy_attr_aliases,
        )

        if node_dfn.dy["enabled"] is True:
            set_explicit_aliases(node_dfn, pretty, app_name)
            for alias in node_dfn.dy["aliases"]:
                set_explicit_nodes(node_dfn, alias)

            if len(node_dfn.dy["xor"]) > 0:
                xor_nodes.append(node_dfn)
            if node_dfn.is_root is True:
                add_builtins(builtins, dy_args, arg_name, location, verified_names, pretty, app_name, dy_attr_aliases)

            for key in sorted(dy_args[arg_name]):
                get_node_dfn(
                    builtins=builtins,
                    dy_metadata=dy_metadata,
                    dy_args=dy_args[arg_name],
                    arg_name=key,
                    pnode_dfn=node_dfn,
                    verified_names=verified_names,
                    dy_replicate=dy_replicate,
                    pretty=pretty,
                    app_name=app_name,
                    dy_attr_aliases=dy_attr_aliases,
                    xor_nodes=xor_nodes,
                )
        else:
            if node_dfn.is_root is False:
                node_dfn.parent.nodes.remove(node_dfn)

        if node_dfn.is_root is True:
            if node_dfn.dy["enabled"] is True:
                if len(dy_replicate) > 0:
                    process_at_addresses(node_dfn, dy_replicate, verified_names, pretty, app_name, dy_attr_aliases, xor_nodes)
                validate_xor_names(xor_nodes, pretty, app_name)
                process_aliases(node_dfn)
                return node_dfn
            else:
                return None

def validate_xor_names(xor_nodes, pretty, app_name):
    prefix="For '{}' at Nargs in definition".format(app_name)

    for xor_node in xor_nodes:
        xor_names=sorted(xor_node.dy["xor"])
        for child_node in xor_node.nodes:
            if child_node.name in xor_names:
                if child_node.dy["required"] is True:
                    msg.error("for argument '{}' at key '_xor' child argument name '{}' can't be both required and part of a xor group.".format(xor_node.location, xor_names[0]), prefix=prefix, pretty=pretty, exit=1)

                xor_names.remove(child_node.name)

        if len(xor_names) > 0:
            msg.error("for argument '{}' at key '_xor' child argument name '{}' not found.".format(xor_node.location, xor_names[0]), prefix=prefix, pretty=pretty, exit=1)

        set_xor_nodes(xor_node)

def set_xor_nodes(node_dfn):
    dy_refs={name: None for name in sorted(node_dfn.dy["xor"])}
    for node in node_dfn.nodes:
        if node.name in dy_refs:
            dy_refs[node.name]=node

    for name in node_dfn.dy["xor"]:
        node_dfn.dy_xor[dy_refs[name]]=dict()
        groups=node_dfn.dy["xor"][name]
        group_nums=sorted([int(num) for num in groups])
        for num in group_nums:
            node_dfn.dy_xor[dy_refs[name]][num]=[]
            for xor_name in groups[str(num)]:
                node_dfn.dy_xor[dy_refs[name]][num].append(dy_refs[xor_name])

def set_dy_replicate(node_dfn, dy_replicate, addresses):
    at_address=".".join(node_dfn.location.split(" > "))
    dy_replicate[at_address]=dict(
        at_addresses=addresses,
        pnode=node_dfn,
    )

def add_builtins(builtins, dy_args, arg_name, location, verified_names, pretty, app_name, dy_attr_aliases):
    for key in dy_args[arg_name].copy():
        if key != "@":
            is_builtin=False
            verify_name(key, is_builtin, location, verified_names, pretty, app_name)
            verify_type(dy_args[arg_name], key, app_name, location, pretty)
            dy_args[arg_name][key]["_is_builtin"]=False

    flag_prefix=dy_attr_aliases["auto_alias_prefix"]
    if flag_prefix == "--":
        flag_prefix="-"

    dy_builtins={
        "_cmd_": {
            "_aliases": "{},{}c".format(get_auto_alias(dy_attr_aliases, "cmd"), flag_prefix),
            "_hint": "Load program's arguments from a file.",
            "_info": "Arguments can be typed with indentation and new lines in the text file. Lines are then striped and new lines are joined with spaces and the whole text is split with shlex and fed again to the program. Root argument alias needs to be provided as first argument. Empty lines and lines starting with '#' are ignored.",
            "_type": "file",
        },
        "_help_": {
            "_aliases": "{},{}h".format(get_auto_alias(dy_attr_aliases, "help"), flag_prefix),
            "_hint": "Print program help and exit.",
            "export": {
                "_hint": "Export help to selected format.",
                "_in": "asciidoc,html,markdown,text",
                "to": {
                    "_hint": "Export help to selected path.",
                    "_type": "vpath",
                },
            },
            "metadata" : {
                "_aliases": "{},{}m".format(get_auto_alias(dy_attr_aliases, "metadata"), flag_prefix),
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
            },
        },
        "_path_etc_": {
            "_aliases": get_auto_alias(dy_attr_aliases, "path_etc"),
            "_hint": "Print program configuration path and exit.",
        },
        "_usage_": {
            "_aliases": "{},{}u".format(get_auto_alias(dy_attr_aliases, "usage"), flag_prefix),
            "_hint": "Print program usage and exit.",
            "_info": "LEVEL is an integer >= 0. LEVEL number describes the number of nested siblings levels to print. LEVEL number is relative to current argument siblings LEVEL. If LEVEL == 0 then all nested siblings levels are printed. If LEVEL == 1 then only current argument is printed. If LEVEL > 1 current argument's siblings levels are printed and LEVEL sets the depth of siblings levels nesting.",
            "examples": {
                "_aliases": "{},{}e".format(get_auto_alias(dy_attr_aliases, "examples"), flag_prefix),
                "_hint": "Print argument(s) examples if any",
            },
            "depth": {
                "_aliases": "{},{}d".format(get_auto_alias(dy_attr_aliases, "depth"), flag_prefix),
                "_default": -1,
                "_required": True,
                "_hint": "Provide the printing depth of nested arguments.",
                "_info": "If LEVEL == -1 then all nested arguments are printed. If LEVEL == 0 then only selected argument is printed. If LEVEL > 0 then the bigger the LEVEL number is, the bigger the children nesting level is if any children are available.",
                "_label": "LEVEL",
                "_type": "int",
                "_values": "1",
            },
            "flags": {
                "_aliases": "{},{}f".format(get_auto_alias(dy_attr_aliases, "flags"), flag_prefix),
                "_hint": "This option allows to print flags on separated line at the end of usage.",
                "_info": "Siblings options hint, info, and path modify flags output."
            },
            "from_": {
                "_aliases": "{}".format(get_auto_alias(dy_attr_aliases, "from")),
                "_default": 0,
                "_required": True,
                "_hint": "This option allows to start printing usage from a parent.",
                "_info": "If LEVEL == -1 then selected argument is the root argument. If LEVEL == 0 then selected argument is the current argument. If LEVEL > 0 then one argument parent is selected and the bigger the LEVEL number is, the older the selected parent is unless parent's limit is reached. Argument's parent's limit is the oldest parent also called the root argument.",
                "_label": "LEVEL",
                "_type": "int",
                "_values": "1",
            },
            "hint": {
                "_aliases": "{},{}h".format(get_auto_alias(dy_attr_aliases, "hint"), flag_prefix),
                "_hint": "Print argument(s) hint if any",
            },
            "info": {
                "_aliases": "{},{}i".format(get_auto_alias(dy_attr_aliases, "info"), flag_prefix),
                "_hint": "Print argument(s) info if any",
            },
            "path": {
                "_aliases": "{},{}p".format(get_auto_alias(dy_attr_aliases, "path"), flag_prefix),
                "_hint": "Print argument(s) path with values",
            }
        },
        "_version_": {
            "_aliases": "{},{}v".format(get_auto_alias(dy_attr_aliases, "version"), flag_prefix),
            "_hint": "Print program version and exit.",
        },
    }
    for builtin in builtins:
        tmp_name="_{}_".format(builtin)
        dy_builtins[tmp_name]["_is_builtin"]=True
        dy_args[arg_name][tmp_name]=dy_builtins[tmp_name]

def get_aliases_sort(node):
    aliases_sort=None
    if len(node.dy["aliases"]) > 0:
        tmp_aliases=[]
        dy_aliases=dict()
        for alias in node.dy["aliases"]:
            tmp_alias=re.sub(get_regex("alias_sort_regstr")["rule"], "", alias)
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
    # node_dfn.current_arg._["_default_alias"]=node_dfn.dy["default_alias"]
    node_dfn.current_arg._aliases=node_dfn.dy["aliases"]
    # node_dfn.current_arg._["_aliases"]=node_dfn.dy["aliases"]
    node_dfn.dy["aliases_sort"]=get_aliases_sort(node_dfn)
    # del node_dfn.dy["dfn_aliases"]

    set_implicit_nodes(node_dfn, from_cache=False)

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

def duplicate_node(prefix, pnode_to_copy, pnode_at, pretty, app_name, dy_attr_aliases, xor_nodes):
    if pnode_to_copy in pnode_at.parents:
        msg.error("Infinite recursion. Argument '{}' can't be added at '{}' because it is a already one of its parents.".format(pnode_to_copy.name, pnode_at.location), prefix=prefix, pretty=pretty, exit=1)

    node_at=NodeDfn(
        dy=deepcopy(pnode_to_copy.dy),
        name=pnode_to_copy.name,
        parent=pnode_at,
        is_dy_preset=True,
        pretty=pretty,
        app_name=app_name,
        dy_attr_aliases=dy_attr_aliases,
    )
    if node_at.dy["enabled"] is True:
        set_explicit_aliases(node_at, pretty, app_name)
    if len(node_at.dy["xor"]) > 0:
        xor_nodes.append(node_at)

    for node_to_copy in pnode_to_copy.nodes:
        duplicate_node(
            prefix=prefix,
            pnode_to_copy=node_to_copy,
            pnode_at=node_at,
            pretty=pretty,
            app_name=app_name,
            dy_attr_aliases=dy_attr_aliases,
            xor_nodes=xor_nodes,
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

def process_at_addresses(node_dfn, dy_replicate, verified_names, pretty, app_name, dy_attr_aliases, xor_nodes):
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

                    duplicate_node(
                        prefix,
                        node_to_copy,
                        dy["pnode"],
                        pretty,
                        app_name,
                        dy_attr_aliases,
                        xor_nodes,
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

def get_cached_node_dfn(dy_args, pretty, app_name, dy_attr_aliases, arg_name=None, pnode_dfn=None):
    tmp_dy_args=dict()
    if pnode_dfn is None:
        arg_name=next(iter(dy_args))
    
    for key, value in dy_args[arg_name].items():
        if key != "args":
            tmp_dy_args[key]=value

    node_dfn=NodeDfn(dy=tmp_dy_args,
        name=arg_name,
        parent=pnode_dfn,
        is_dy_preset=True,
        pretty=pretty,
        app_name=app_name,
        dy_attr_aliases=dy_attr_aliases,
    )
    
    for alias in node_dfn.dy["aliases"]:
        set_explicit_nodes(node_dfn, alias)
        
    node_dfn.current_arg._default_alias=tmp_dy_args["default_alias"]

    for key in dy_args[arg_name]["args"]:
        get_cached_node_dfn(
            dy_args=dy_args[arg_name]["args"],
            pretty=pretty,
            app_name=app_name,
            dy_attr_aliases=dy_attr_aliases,
            arg_name=key,
            pnode_dfn=node_dfn,
        )

    if len(node_dfn.dy["xor"]) > 0:
        set_xor_nodes(node_dfn)
    set_implicit_nodes(node_dfn, from_cache=True)

    if node_dfn.is_root is True:
        return node_dfn

def set_explicit_nodes(node_dfn, alias):
    if node_dfn.is_root is False:
        node_dfn.parent.dy_aliases[alias]=dict(explicit=node_dfn, implicit=[])
        set_flag(alias, node_dfn=node_dfn.parent, ref_node=node_dfn, from_cache=False)

def set_implicit_nodes(node_dfn, from_cache):
    if node_dfn.is_root is False:

        for alias in node_dfn.parent.dy_aliases:
            if alias not in node_dfn.dy_aliases:
                node_dfn.dy_aliases[alias]=dict(explicit=None, implicit=[])

            if node_dfn.parent.dy_aliases[alias]["explicit"] is not None:
                node_dfn.dy_aliases[alias]["implicit"].append(node_dfn.parent.dy_aliases[alias]["explicit"])
                set_flag(alias, node_dfn, node_dfn.parent.dy_aliases[alias]["explicit"], from_cache)

            for imp_node in node_dfn.parent.dy_aliases[alias]["implicit"]:
                node_dfn.dy_aliases[alias]["implicit"].append(imp_node)
                set_flag(alias, node_dfn, imp_node, from_cache)

    if from_cache is False:
        notation="".join(sorted(node_dfn.dy_flags))
        if notation == "":
            node_dfn.dy["flags_notation"]=None
        else:
            node_dfn.dy["flags_notation"]=notation

def set_flag(alias, node_dfn, ref_node, from_cache):
    flags_precedence=get_flags_precedence()
    if ref_node.dy["aliases_info"][alias]["is_flag"] is True:
        c=ref_node.dy["aliases_info"][alias]["text"]
        if from_cache is True:
            if c in node_dfn.dy["flags"]:
                if node_dfn.dy["flags"][c] == ref_node.location:
                    node_dfn.dy_flags[c]=ref_node
        else:
            to_set=False
            if c in node_dfn.dy["flags"]:
                if c in node_dfn.dy_flags:
                    flag_node=node_dfn.dy_flags[c]
                    if flag_node.level > ref_node.level:
                        pass
                    elif flag_node.level == ref_node.level:
                        flag_node_prefix=flag_node.dy["aliases_info"][alias]["prefix"]
                        ref_node_prefix=ref_node.dy["aliases_info"][alias]["prefix"]
                        if flags_precedence.index(ref_node_prefix) < flags_precedence.index(flag_node_prefix):
                            to_set=True
                    else: # flag_node.level < ref_node.level:
                            to_set=True
                else:
                    to_set=True
            else:
                to_set=True

            if to_set is True:
                node_dfn.dy["flags"][c]=ref_node.location
                node_dfn.dy_flags[c]=ref_node
                ref_node.dy["flags_aliases"][c]=alias