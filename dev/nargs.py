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
import time
import traceback

from .exceptions import EndUserError, DeveloperError
from .get_args import get_args
from .get_properties import get_arg_properties, get_mapped_theme_props
from .cached import get_args_dump, get_cached_node_dfn, get_cached_theme
from .set_options import get_cached_options, set_options, get_default_builtins, get_metadata_template
from .get_node_dfn import get_node_dfn
from .help import get_help_usage

from .regexes import get_regex_dfn
from .style import get_default_props, Style

from ..gpkgs import message as msg

class Nargs():
    def __init__(self,
        args=None,
        auto_alias_prefix="--",
        auto_alias_style="lowercase-hyphen",
        builtins=None,
        cache=True,
        cache_file=None,
        metadata=None,
        options_file=None,
        only_cache=False,
        path_etc=None,
        pretty_help=True,
        pretty_msg=True,
        raise_exc=False,
        substitute=False,
        theme=None,
    ):
        if builtins is None:
            builtins=get_default_builtins()
        if metadata is None:
            metadata=dict()
        if theme is None:
            theme=dict()
        if cache_file is None:
            cache_file="nargs-cache.json"

        
        dy_options=locals()

        self._from_cache=True
        self._reset_dfn_tree=None
        self._dy_err=dict(
            exc=None,
            prefix="At Nargs when setting options",
            pretty=False,
        )

        del dy_options["self"]

        md5_options=hashlib.md5(json.dumps(dy_options, sort_keys=True).encode()).hexdigest()


        filenpa_caller=inspect.stack()[1].filename
        if not os.path.isabs(filenpa_caller):
            filenpa_caller=os.path.abspath(filenpa_caller)

        if os.path.islink(filenpa_caller):
            filenpa_caller=os.path.realpath(filenpa_caller)
        direpa_caller=os.path.normpath(os.path.dirname(filenpa_caller))

        for option, var in dict(
            raise_exc=raise_exc,
            only_cache=only_cache,
            cache=cache,
        ).items():
            if isinstance(var, bool) is False:
                msg.error("'{}' option wrong type {}. It must be of type {}.".format(option, type(var), bool), prefix=self._dy_err["prefix"], pretty=self._dy_err["pretty"], exc=DeveloperError, exit=1)

        self._raise_exc=raise_exc
        if self._raise_exc is True:
            self._dy_err["exc"]=DeveloperError

        if only_cache is True and cache is False:
            msg.error("'only_cache' option must be set to '{}' when cache is '{}'.".format(False, False), prefix=self._dy_err["prefix"], pretty=self._dy_err["pretty"], exc=self._dy_err["exc"], exit=1)

        dy_cached_options=None

        cache_extension=None
        if cache is True:
            if isinstance(cache_file, str) is True:
                filer, cache_extension = os.path.splitext(cache_file)
                auth_exts=[".json", ".pickle"]
                if cache_extension.lower() in auth_exts:
                    if not os.path.isabs(cache_file):
                        cache_file=os.path.normpath(os.path.abspath(os.path.join(direpa_caller, cache_file)))
                    dy_cached_options=get_cached_options(direpa_caller, cache_file, cache_extension, md5_options, only_cache, self._dy_err)
                else:
                    msg.error("cache_file option file extension '{}' not found in '{}'.".format(cache_extension, auth_exts), prefix=self._dy_err["prefix"], pretty=self._dy_err["pretty"], exc=self._dy_err["exc"], exit=1)
            else:
                msg.error("cache_file option wrong type {}. It must be of type {}.".format(type(cache_file), str), prefix=self._dy_err["prefix"], pretty=self._dy_err["pretty"], exc=self._dy_err["exc"], exit=1)

        if dy_cached_options is None:
            self._from_cache=False
            if cache is True:
                if only_cache is True and os.path.exists(cache_file):
                    msg.error("option 'only_cache' is set to True but Nargs retrieved cache from cache_file '{}' is None. If arguments definition is provided then cache file may be manually deleted to regenerate the cache.".format(cache_file), prefix=self._dy_err["prefix"], pretty=self._dy_err["pretty"], exc=self._dy_err["exc"], exit=1)
            set_options(direpa_caller, dy_options, md5_options, self.get_default_theme(), sys.argv[0], self._dy_err)

            if cache is True:
                self._theme=deepcopy(dy_options["theme"])
            else:
                self._theme=dy_options["theme"]

            self._set_basic_vars(dy_options)
            if dy_options["path_etc"] is None:
                if "path_etc" in dy_options["builtins"]:
                    del dy_options["builtins"]["path_etc"]

            if dy_options["args"] is None and len(dy_options["builtins"]) == 0:
                self.dfn=None
            else:
                exc=None
                if self._raise_exc is True:
                    exc=DeveloperError

                self.dfn=get_node_dfn(
                    builtins=dy_options["builtins"],
                    dy_attr_aliases=self._dy_attr_aliases,
                    pretty=self._dy_err["pretty"],
                    app_name=self._app_name,
                    dy_args=dy_options["args"],
                    exc=exc,
                )

            del dy_options["args"]

            if cache is True:
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)

                theme_props=get_mapped_theme_props()
                dy_options["map"]=dict(
                    arg_props={dy["map"]:prop for prop, dy in get_arg_properties().items() if dy["for_cache"] is True},
                    arg_defaults={dy["map"]:dy["default"] for prop, dy in get_arg_properties().items() if dy["for_cache"] is True and dy["has_default"] is True},
                )

                if dy_options["pretty_help"] is True:
                    dy_options["map"]["theme_props"]={dy["map"]:prop for prop, dy in theme_props.items()}
                    dy_options["map"]["theme_defaults"]={dy["map"]:dy["default"] for prop, dy in theme_props.items()}

                dy_theme=dict()
                for name in dy_options["theme"]:
                    dy_theme[name]=dict()
                    for prop, value in dy_options["theme"][name].items():
                        if value != theme_props[prop]["default"]:
                            dy_theme[name][theme_props[prop]["map"]]=value

                dy_options["theme"]=dy_theme

                if cache_extension == ".json":
                    dy_dump=get_args_dump(self.dfn)
                    dy_options["dump"]=dy_dump
                    with open(cache_file, "w") as f:
                        f.write(json.dumps(dy_options, sort_keys=True, separators=(',', ':')))

                elif cache_extension == ".pickle":
                    dy_options["dump"]=self.dfn
                    with open(cache_file, "wb") as f:
                        try:
                            pickle.dump(dy_options, f)
                        except RecursionError as e:
                            msg.error("Pickle cache limit reached '{}'. Please switch cache_file option to '.json' extension to overcome Pickle file limit for arguments definition tree size.".format(str(e)), prefix=self._dy_err["prefix"], pretty=self._dy_err["pretty"], exc=self._dy_err["exc"], exit=1)
        else:
            self._from_cache=True
            dy_options=dy_cached_options
            self._set_basic_vars(dy_options)

            if dy_options["pretty_help"] is True:
                self._theme=get_cached_theme(dy_options)
            else:
                self._theme=None

            if dy_options["dump"] is None:
                self.dfn=None
            else:
                if cache_extension == ".json":
                    self.dfn=get_cached_node_dfn(
                        dy_args=dy_options["dump"],
                        arg_defaults=dy_options["map"]["arg_defaults"],
                        arg_props=dy_options["map"]["arg_props"],
                    )
                elif cache_extension == ".pickle":
                    self.dfn=dy_options["dump"]

        self.metadata=dy_options["metadata"]
        self._substitute=dy_options["substitute"]

        self._user_options=dict(
            pretty_help=self._pretty_help,
            pretty_msg=self._dy_err["pretty"],
            substitute=self._substitute,
        )

    def _set_basic_vars(self, dy_options):
        self._dy_err["pretty"]=dy_options["pretty_msg"]
        self._pretty_help=dy_options["pretty_help"]
        self._app_name=dy_options["metadata"]["name"]
        self._path_etc=dy_options["path_etc"]
        self._dy_attr_aliases=dict(
            auto_alias_prefix=dy_options["auto_alias_prefix"],
            auto_alias_style=dy_options["auto_alias_style"],
        )

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
            aliases=dict(
                foreground=blue,
            ),
            arg_index=dict(
                bold=True,
            ),
            arg_path=dict(
                foreground=green,
            ),
            brackets=dict(
                bold=True,
                foreground=green,
            ),
            bullets=dict(
                foreground=gray,
            ),
            emphasize=dict(
                foreground=red,
            ),
            examples=dict(
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

            properties=dict(
            ),
            syntax_headers=dict(
                foreground=green,
            ),
            values=dict(
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
                        reg_hexa=re.match(get_regex_dfn("def_theme_hexa")["rule"], value)
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
        exc=None
        if self._raise_exc is True:
            exc=EndUserError

        if self._reset_dfn_tree is None:
            self._reset_dfn_tree=False
        else:
            self._reset_dfn_tree=True

        args=get_args(
            app_name=self._app_name,
            cmd=cmd,
            exc=exc,
            dy_metadata=self.metadata,
            node_dfn=self.dfn,
            path_etc=self._path_etc,
            pretty_help=self._pretty_help,
            pretty_msg=self._dy_err["pretty"],
            substitute=self._substitute,
            theme=self._theme,
            get_documentation=self.get_documentation,
            reset_dfn_tree=self._reset_dfn_tree,
        )
        return args
            
    def get_documentation(self, output, filenpa=None, wsyntax=None, overwrite=False, only_syntax=False):

        prefix="For '{}' at Nargs get_documentation".format(self._app_name)

        outputs=["asciidoc", "cmd_help", "cmd_usage", "html", "markdown", "text"]
        if output not in outputs:
            msg.error("output '{}' not found in {}.".format(output, outputs), prefix=prefix, pretty=self._dy_err["pretty"], exc=self._dy_err["exc"], exit=1)

        if wsyntax is False and only_syntax is True:
            msg.error("option wsyntax must be 'True' when option only_syntax is 'True'.", prefix=prefix, pretty=self._dy_err["pretty"], exc=self._dy_err["exc"], exit=1)

        if wsyntax is None:
            wsyntax=False

        allproperties=sorted([prop for prop, dy in get_arg_properties().items() if dy["for_help"] is True])
        documentation=get_help_usage(
            dy_metadata=self.metadata,
            node_ref=self.dfn,
            output=output,
            style=Style(pretty_help=self._pretty_help, output=output, theme=self._theme),
            user_options=self._user_options,
            allproperties=allproperties,
            properties=allproperties,
            wproperties=True,
            wexamples=True,
            whint=True,
            winfo=True,
            wsyntax=wsyntax,
            only_syntax=only_syntax,
        )

        if output not in ["cmd_usage", "cmd_help"]:
            if filenpa is not None:
                if not isinstance(filenpa, str):
                    msg.error("filenpa type {} is not type {}".format(type(filenpa), str), prefix=prefix, pretty=self._dy_err["pretty"], exc=self._dy_err["exc"], exit=1)

                if not os.path.isabs(filenpa):
                    filenpa=os.path.abspath(filenpa)
                filenpa=os.path.normpath(filenpa)
                if overwrite is False:
                    if os.path.exists(filenpa):
                        msg.error("file already exists '{}'".format(filenpa), prefix=prefix, pretty=self._dy_err["pretty"], exc=self._dy_err["exc"], exit=1)
                with open(filenpa, "w") as f:
                    f.write("{}".format(documentation))

            return documentation

    def get_metadata_template(self):
        return get_metadata_template()
