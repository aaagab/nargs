#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
import os
import re
import sys

from .nodes import NodeDfn
from .set_dfn import get_dfn_prefix
from .regexes import get_regex, get_regex_hints

from ..gpkgs import message as msg

def verify_name(name, location, verified_names):
    prefix="Nargs in definition for key '{}'".format(location)
    if name not in verified_names:
        if re.match(get_regex("def_arg_name")["rule"], name):
            verified_names.append(name)
        else:
            msg.error([
                "Argument name '{}' does not match regex:".format(name),
                *get_regex_hints("def_arg_name"),
            ], prefix=prefix, exit=1)

def get_node_dfn(
    dy_metadata=dict(),
    dy_dfn=dict(),
    arg_name=None,
    pnode_dfn=None,
    verified_names=[],
    dy_replicate=dict(),
):
    if pnode_dfn is None:
        if len(dy_dfn) == 0:
            return None
        elif len(dy_dfn) != 1: 
            msg.error("definition accepts only one root key.", prefix=get_dfn_prefix(), exit=1)
        else:
            arg_name=next(iter(dy_dfn))
            
    if arg_name == "@":
        if pnode_dfn is None:
            msg.error("'@' not allowed at root key.", prefix=get_dfn_prefix(), exit=1)
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
                        msg.error("Wrong value type {} in list. It must be {}.".format(type(entry), str), prefix=get_dfn_prefix(pnode_dfn.location, arg_name), exit=1)
            else:            
                msg.error("Wrong value type {}. It must be either {} or {}.".format(type(dy_dfn[arg_name]), str, list), prefix=get_dfn_prefix(pnode_dfn.location, arg_name), exit=1)

            at_address=".".join(pnode_dfn.location.split(" > "))
            dy_replicate[at_address]=dict(
                at_adresses=elems,
                pnode=pnode_dfn,
            )
    else:
        if pnode_dfn is not None:
            verify_name(arg_name, pnode_dfn.location, verified_names)

        node_dfn=NodeDfn(dy=dy_dfn[arg_name], name=arg_name, is_a_dump=False, is_dy_preset=False, parent=pnode_dfn)

        node_arg=None
        if node_dfn.dy["enabled"] is True:
            continue_process=True
            if node_dfn.is_root is True:
                add_builtins(node_dfn, dy_dfn, arg_name, dy_metadata)
            else:
                if node_dfn.dy["is_builtin"] is True:
                    if len(node_dfn.dy["aliases"]) == 0:
                        node_dfn.parent.nodes.remove(node_dfn)
                        continue_process=False

            if dy_dfn[arg_name] is not None and continue_process is True:
                for key in sorted(dy_dfn[arg_name]):
                    get_node_dfn(
                        dy_metadata=dy_metadata,
                        dy_dfn=dy_dfn[arg_name],
                        arg_name=key,
                        pnode_dfn=node_dfn,
                        verified_names=verified_names,
                        dy_replicate=dy_replicate,
                    )
        else:
            if node_dfn.is_root is False:
                node_dfn.parent.nodes.remove(node_dfn)

        if node_dfn.is_root is True:
            if node_dfn.dy["enabled"] is True:
                process_at_addresses(node_dfn, dy_replicate, verified_names)
                process_aliases(node_dfn)
                return node_dfn
            else:
                return None

def get_aliases_sort(node):
    aliases_sort=None
    if len(node.dy["aliases"]) > 0:
        tmp_aliases=[]
        dy_aliases=dict()
        for alias in node.dy["aliases"]:
            tmp_alias=re.sub(r"^-+", "", alias)
            if tmp_alias not in dy_aliases:
                dy_aliases[tmp_alias]=[]
            dy_aliases[tmp_alias].append(alias)

        aliases_sort=[]
        for tmp_alias in sorted(dy_aliases):
            aliases_sort.append(tmp_alias)
            for alias in sorted(dy_aliases[tmp_alias]):
                tmp_aliases.append(alias)

        node.dy["aliases"]=tmp_aliases
        
        aliases_sort=",".join(aliases_sort)

    return aliases_sort

def get_either(node):
    node_names={n.name: n for n in node.nodes}
    either_names=[]
    for lst_names in node.dy["either"]:
        for name in lst_names:
            if name not in either_names:
                either_names.append(name)

    _either=dict()
    for name in either_names:
        _either[name]=[]
        if name in node_names:
            if node_names[name].dy["required"] is True:
                msg.error("child argument '{}' can't be both with option '_required:True' and belonging in parent '_either' option.".format(name), prefix=get_dfn_prefix(node.location, "_either"), exit=1)
            if node_names[name].dy["single"] is True:
                msg.error("child argument '{}' can't be both with option '_single:True' and belonging in parent '_either' option.".format(name), prefix=get_dfn_prefix(node.location, "_either"), exit=1)
        else:
            msg.error("argument name '{}' does not exist in children names {}".format(name, node_names), prefix=get_dfn_prefix(node.location, "_either"), exit=1)

    for g, group in enumerate(node.dy["either"]):
        index=str(g+1)
        for name in group:
            if node_names[name].dy["either_notation"] is None:
                node_names[name].dy["either_notation"]=[]
            node_names[name].dy["either_notation"].append(index)
            for g in group:
                if g != name:
                    if g not in _either[name]:
                        _either[name].append(g)
    return _either

def process_aliases(node_dfn):
    if node_dfn.dy["either"] is not None:
        node.dy["either"]=get_either(node_dfn)
    node_dfn.get_arg().set_default_alias(node_dfn.dy["default_alias"])
    node_dfn.dy["aliases_sort"]=get_aliases_sort(node_dfn)
    for node in node_dfn.nodes:
        process_aliases(node)

def add_builtins(node_dfn, dy_dfn, arg_name, dy_metadata):
    if node_dfn.level == 1:
        if dy_dfn[arg_name] is None:
            dy_dfn[arg_name]=dict()
        
        for key in dy_dfn[arg_name]:
            if isinstance(dy_dfn[arg_name][key], dict):
                if "_is_builtin" in dy_dfn[arg_name][key]:
                    del dy_dfn[arg_name][key]["_is_builtin"]

        if "cmd" not in dy_dfn[arg_name]:
            dy_dfn[arg_name]["cmd"]=dict(
                _aliases="-c,--cmd",
                _hint="Load program's arguments from a file.",
                _info="Arguments can be typed with indentation and new lines in the text file. Lines are then striped and new lines are joined with spaces and the whole text is split with shlex and fed again to the program. Root argument alias needs to be provided as first argument. Empty lines and lines starting with '#' are ignored.",
                _single=True,
                _type="file",
                _is_builtin=True,
            )
        if "conf_path" in dy_metadata:
            if "conf_path" not in dy_dfn[arg_name]:
                dy_dfn[arg_name]["conf_path"]=dict(
                    _aliases="--conf_path",
                    _hint="Print program configuration path.",
                    _single=True,
                    _is_builtin=True,
                )
        if "examples" not in dy_dfn[arg_name]:
            dy_dfn[arg_name]["examples"]=dict(
                _aliases="--examples",
                _hint="Print program examples.",
                _single=True,
                _is_builtin=True,
            )
        if "help" not in dy_dfn[arg_name]:
            dy_dfn[arg_name]["help"]=dict(
                _aliases="-h,--help",
                _hint="Print program help.",
                _single=True,
                _is_builtin=True,
                syntax=dict(
                    _hint="Print arguments Cheat Sheet syntax."
                ),
                export=dict(
                    _hint="Export help to selected format.",
                    _in="asciidoc,html,markdown,text",
                    to=dict(
                        _hint="Export help to selected path.",
                        _type="vpath",
                    ),
                ),
            )
        if "uuid4" in dy_metadata:
            if "uuid4" not in dy_dfn[arg_name]:
                dy_dfn[arg_name]["uuid4"]=dict(
                    _aliases="--uuid4",
                    _hint="Print program UUID4.",
                    _single=True,
                    _is_builtin=True,
                )
        if "usage" not in dy_dfn[arg_name]:
            dy_dfn[arg_name]["usage"]=dict(
                _aliases="--usage",
                _hint="Print program usage.",
                _single=True,
                _is_builtin=True,
            )
        if "version" in dy_metadata:
            if "version" not in dy_dfn[arg_name]:
                dy_dfn[arg_name]["version"]=dict(
                    _aliases="-v,--version",
                    _hint="Print program version.",
                    _single=True,
                    _is_builtin=True,
                )

def process_at_addresses(node_dfn, dy_replicate, verified_names):
    while True:
        found_one=False
        recursives=set()
        not_founds=set()
        for at_address in sorted(dy_replicate):
            dy=dy_replicate[at_address]
            for nested_at_address in dy["at_adresses"].copy():
                if nested_at_address in dy_replicate:
                    recursives.add(nested_at_address)
                else:
                    if set_at_address(node_dfn, dy["pnode"], nested_at_address, verified_names) is True:
                        found_one=True
                        dy["at_adresses"].remove(nested_at_address)
                    else:
                        not_founds.add(nested_at_address)
            if len(dy["at_adresses"]) == 0:
                del dy_replicate[at_address]

        if len(dy_replicate) == 0:
            break
        else:
            if found_one is False:
                error=[
                    "Nargs in definition: Couldn't resolve @ addresses",
                ]
                if len(not_founds) > 0:
                    error.append("Address(es) not found:")
                    if len(recursives) > 0:
                        error.append("Probably comes from recursive address(es):")
                    for not_found in not_founds:
                        error.append("- {}".format(not_found))
                if len(recursives) > 0:
                    if len(not_founds) > 0:
                        error.append("Potential recursive address(es):")
                    else:
                        error.append("Recursive address(es):")
                    for recursive in recursives:
                        error.append("- {}".format(recursive))
                msg.error(error, exit=1)

def set_at_address(node_root, node_dst, at_address, verified_names):
    prefix="Nargs in definition at key '{}' for @:{}".format(node_dst.location, at_address)
    node_src=node_root
    for n, name in enumerate(at_address.split(".")):
        if n == 0:
            if name != node_root.name:
                msg.error("@ adresses are absolute, first name must be equal to '{}' not '{}'".format(node_root.name, name), prefix=prefix, exit=1)
        else:
            verify_name(name, "{} for @:{}".format(node_dst.location, at_address), verified_names)
            found=False
            for node in node_src.nodes:
                if node.name == name:
                    found=True
                    node_src=node
                    break
            if found is False:
                return False

    duplicate_node(node_src, node_dst)
    return True

def duplicate_node(pnode_src, pnode_dst):
    node_dst=NodeDfn(dy=deepcopy(pnode_src.dy), name=pnode_src.name, is_a_dump=False, is_dy_preset=True, parent=pnode_dst)
    for node_src in pnode_src.nodes:
        duplicate_node(
            pnode_src=node_src,
            pnode_dst=node_dst,
        )

def get_cached_node_dfn(dy_dfn, arg_name=None, pnode_dfn=None):
    tmp_dy_dfn=dict()
    if pnode_dfn is None:
        arg_name=next(iter(dy_dfn))
    
    for key, value in dy_dfn[arg_name].items():
        if key != "args":
            tmp_dy_dfn[key]=value
    
    node_dfn=NodeDfn(dy=tmp_dy_dfn, name=arg_name, is_a_dump=True, is_dy_preset=False, parent=pnode_dfn)
    node_dfn.get_arg()._default_alias=dy["_default_alias"]

    for key in dy_dfn[arg_name]["args"]:
        get_cached_node_dfn(
            dy_dfn=dy_dfn[arg_name]["args"],
            arg_name=key,
            pnode_dfn=node_dfn,
        )

    if node_dfn.is_root is True:
        return node_dfn
