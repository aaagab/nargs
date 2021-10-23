#!/usr/bin/env python3
from pprint import pprint
from copy import deepcopy
import atexit
import hashlib
import inspect
import json
import os
import pickle
import re
import sys
import shlex
import traceback

from .get_args import get_args, delete_branch, create_branch
from .set_options import get_cached_options, set_options
from .get_node_dfn import get_node_dfn, get_cached_node_dfn
from .get_types import get_type_str
from .help import get_help_usage, get_md_text
from .nargs_syntax import get_nargs_syntax

from .regexes import get_regex
from .style import get_theme, get_default_props, Style

from ..gpkgs import message as msg

debug=False
cache=True

def get_dump(node, dump=None):
    if node is None:
        return None

    if node.is_root is True:
        dump=dict()

    dump[node.name]=deepcopy(node.dy)
    dump[node.name]["type"]=get_type_str(node.dy["type"])
    dump[node.name]["args"]=dict()

    for tmp_node in node.nodes:
        get_dump(tmp_node, dump[node.name]["args"])

    if node.is_root is True:
        return dump

class Nargs():
    def __init__(self,
        args=None,
        auto_alias_prefix="--",
        auto_alias_style="lowercase-hyphen",
        builtins=None,
        cache_file="nargs-cache.json",
        metadata=None,
        options_file=None,
        only_cache=False,
        path_etc=None,
        pretty_help=True,
        pretty_msg=True,
        substitute=False,
        theme=None,
        need_=True,
    ):
        self._reset_dfn_tree=False
        prefix="At Nargs"

        self._debug=debug

        if builtins is None:
            builtins=["cmd", "help", "usage", "version"]
        if metadata is None:
            metadata=dict()
        if theme is None:
            theme=dict()
        dy_options=locals()

        del dy_options["self"]

        md5_options=hashlib.md5(json.dumps(dy_options, sort_keys=True).encode()).hexdigest()

        filenpa_caller=inspect.stack()[1].filename
        if not os.path.isabs(filenpa_caller):
            filenpa_caller=os.path.abspath(filenpa_caller)

        if os.path.islink(filenpa_caller):
            filenpa_caller=os.path.realpath(filenpa_caller)
        direpa_caller=os.path.normpath(os.path.dirname(filenpa_caller))

        if isinstance(only_cache, bool) is False:
            msg.error("only_cache option wrong type {}. It must be of type {}.".format(type(only_cache), bool), prefix=prefix, pretty=False, exit=1)

        dy_cached_options=None
        cache_extension=None
        if isinstance(cache_file, str) is True:
            filer, cache_extension = os.path.splitext(cache_file)
            auth_exts=[".json", ".pickle"]
            if cache_extension in auth_exts:
                if not os.path.isabs(cache_file):
                    cache_file=os.path.normpath(os.path.abspath(os.path.join(direpa_caller, cache_file)))
                dy_cached_options=get_cached_options(direpa_caller, cache_file, cache_extension, md5_options, only_cache)
            else:
                msg.error("cache_file option file extension '{}' not found in '{}'.".format(cache_extension, auth_exts), prefix=prefix, pretty=False, exit=1)
        else:
            msg.error("cache_file option wrong type {}. It must be of type {}.".format(type(cache_file), str), prefix=prefix, pretty=False, exit=1)

        if cache is False:
            dy_cached_options=None
        if dy_cached_options is None:
            if self._debug is True:
                print("not cached")
            if only_cache is True:
                msg.error("option 'only_cache' is set to True but Nargs was unable to retrieve cache from cache_file '{}'.".format(cache_file), prefix=prefix, pretty=False, exit=1)
            set_options(direpa_caller, dy_options, md5_options, self.get_default_theme(), sys.argv[0])
            self._set_basic_vars(dy_options)
            if dy_options["path_etc"] is not None:
                dy_options["builtins"].append("path_etc")

            if dy_options["args"] is None:
                self._node_dfn=None
            else:
                self._node_dfn=get_node_dfn(
                    builtins=dy_options["builtins"],
                    dy_metadata=dy_options["metadata"],
                    dy_args=dy_options["args"],
                    pretty=self._pretty_msg,
                    app_name=self._app_name,
                    dy_attr_aliases=self._dy_attr_aliases,
                )

            del dy_options["args"]

            os.makedirs(os.path.dirname(cache_file), exist_ok=True)

            if cache_extension == ".json":
                dy_dump=get_dump(self._node_dfn)
                dy_options["dump"]=dy_dump
                with open(cache_file, "w") as f:
                    f.write(json.dumps(dy_options, sort_keys=True, separators=(',', ':')))
            elif cache_extension == ".pickle":
                dy_options["dump"]=self._node_dfn
                with open(cache_file, "wb") as f:
                    pickle.dump(dy_options, f)
        else:
            if self._debug is True:
                print("cached")
            dy_options=dy_cached_options
            self._set_basic_vars(dy_options)

            if cache_extension == ".json":
                self._node_dfn=self._get_node_dfn_cached_trigger_error_if(
                    dy_options["dump"],
                    cache_file,
                )
            elif cache_extension == ".pickle":
                self._node_dfn=dy_options["dump"]
        try:
            self._dy_metadata=dy_options["metadata"]
            self._substitute=dy_options["substitute"]
            self._theme=dy_options["theme"]

            self._user_options=dict(
                pretty_help=self._pretty_help,
                pretty_msg=self._pretty_msg,
                substitute=self._substitute,
            )
        except KeyError as e:
            if dy_cached_options is None:
                msg.error(
                    "For '{}' at Nargs with definition data, key {} not found. It is a bug please contact developer.".format(
                        self._app_name,
                        e,
                    ), pretty=self._pretty_msg)
                sys.exit(1)
            else:
                msg.error(
                    "For '{}' at Nargs with cached data, key {} not found. Cache must be reset please delete file '{}'.".format(
                        self._app_name,
                        e,
                        cache_file,
                    ), pretty=self._pretty_msg)
                sys.exit(1)

        # pprint(get_dump(self._node_dfn))
        # pprint(vars(self._node_dfn))

    def _set_basic_vars(self, dy_options):
        self._pretty_msg=dy_options["pretty_msg"]
        self._pretty_help=dy_options["pretty_help"]
        self._app_name=dy_options["metadata"]["name"]
        self._path_etc=dy_options["path_etc"]
        self._dy_attr_aliases=dict(
            auto_alias_prefix=dy_options["auto_alias_prefix"],
            auto_alias_style=dy_options["auto_alias_style"],
        )

    def _get_node_dfn_cached_trigger_error_if(self, dy_args_dump, filenpa_cache):
        try:
            if dy_args_dump is None:
                return None
            else:
                return get_cached_node_dfn(
                    dy_args=dy_args_dump,
                    pretty=self._pretty_msg,
                    app_name=self._app_name,
                )
        except Exception as e:
            msg.error([
                "For '{}' at Nargs with cached definition, unexpected error occured when loading definition from dumped data.".format(self._app_name),
                "Dumped data is obtained from file '{}'.".format(filenpa_cache),
                "File should be deleted and program re-executed to regenerate the cache. It may solve the issue.",
            ], pretty=self._pretty_msg)
            raise Exception(e)
            sys.exit(1)

    def get_default_theme(self):
        black="#2b2b2b"
        bgreen="#95e454"
        bred="#ff2026"
        blue="#88b8f6"
        gray="#9c998e"
        green="#cae982"
        purple="#d787ff"
        red="#e5786d"
        yellow="#eae788"

        styles=dict(
            about_fields=dict(
                foreground=green,
            ),
            aliases_text=dict(
                foreground=blue,
            ),
            arg_index=dict(
                bold=True,
            ),
            arg_path=dict(
                foreground=green,
            ),
            examples=dict(
            ),
            examples_bullet=dict(
                foreground=gray,
            ),
            flags=dict(
                italic=True,
                foreground=bgreen,
            ),
            headers=dict(
                bold=True,
                foreground=yellow,
            ),
            hint=dict(
                italic=True,
            ),
            info=dict(
            ),
            nargs_syntax_emphasize=dict(
                foreground=red,
            ),
            nargs_syntax_headers=dict(
                foreground=green,
            ),
            square_brackets=dict(
                bold=True,
                foreground=green,
            ),
            values_text=dict(
                italic=True,
                foreground=purple,
            ),
        )

        default_props=get_default_props()
        for elem in sorted(styles):
            for prop in sorted(default_props):
                if prop in styles[elem]:
                    if prop in ["background", "foreground"]:
                        value=styles[elem][prop]
                        reg_hexa=re.match(get_regex("def_theme_hexa")["rule"], value)
                        if reg_hexa:
                            tmp_colors=[]
                            for color in reg_hexa.groups():
                                tmp_colors.append(str(int(color, 16)))
                            styles[elem][prop]=";".join(tmp_colors)
                else:
                    styles[elem][prop]=default_props[prop]
        return styles

    def get_args(self, 
        cmd=None, 
    ):
        args=get_args(
            app_name=self._app_name,
            cmd=cmd,
            debug=self._debug,
            dy_metadata=self._dy_metadata,
            node_dfn=self._node_dfn,
            path_etc=self._path_etc,
            pretty_help=self._pretty_help,
            pretty_msg=self._pretty_msg,
            substitute=self._substitute,
            theme=self._theme,
            get_documentation=self.get_documentation,
            reset_dfn_tree=self._reset_dfn_tree,
        )
        self._reset_dfn_tree=True
        return args

    def _update_nargs_syntax(self):
        filenpa=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "end-user.md")
        nargs_syntax=get_md_text(
            title="NARGS END-USER DOCUMENTATION", 
            sections=[get_nargs_syntax(
                    Style(pretty_help=self._pretty_help, pretty_msg=self._pretty_msg, output="markdown", theme=self._theme, prefix="For '{}' at Nargs update syntax".format(self._app_name)), 
                    self._user_options,
                    print_options=False,

                )
            ],
        )
        with open(filenpa, "w") as f:
            f.write("{}".format(nargs_syntax))
            
    def get_documentation(self, output, filenpa=None, wsyntax=False, overwrite=False):
        prefix="For '{}' at Nargs get_documentation".format(self._app_name)

        props_node=self._node_dfn.dy_nodes["_usage_"].dy_nodes["properties"]
        allproperties=props_node.dy["in"]

        documentation=get_help_usage(
            dy_metadata=self._dy_metadata,
            node_ref=self._node_dfn,
            output=output,
            style=Style(pretty_help=self._pretty_help, pretty_msg=self._pretty_msg, output=output, theme=self._theme, prefix=prefix),
            user_options=self._user_options,
            allproperties=allproperties,
            properties=allproperties,
            wproperties=True,
            wexamples=True,
            whint=True,
            winfo=True,
            wsyntax=wsyntax,
        )

        if output not in ["cmd_usage", "cmd_help"]:
            if filenpa is not None:
                if not isinstance(filenpa, str):
                    msg.error("filenpa type {} is not type {}".format(type(filenpa), str), prefix=prefix, pretty=self._pretty_msg, exit=1)

                if not os.path.isabs(filenpa):
                    filenpa=os.path.abspath(filenpa)
                filenpa=os.path.normpath(filenpa)
                if overwrite is False:
                    if os.path.exists(filenpa):
                        msg.error("file already exists '{}'".format(filenpa), prefix=prefix, pretty=self._pretty_msg, exit=1)
                with open(filenpa, "w") as f:
                    f.write("{}".format(documentation))

            return documentation

    def get_metadata_template(self):
        return get_metadata_template()
