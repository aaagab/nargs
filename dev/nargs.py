#!/usr/bin/env python3
from pprint import pprint
from copy import deepcopy
import inspect
import json
import os
import pickle
import re
import sys
import shlex
import traceback

from .get_args import get_args
from .get_dy_dfn import get_dy_dfn
from .get_node_dfn import get_node_dfn, get_cached_node_dfn
from .get_types import get_type_str
from .help import get_help_usage, get_md_text
from .nargs_syntax import get_nargs_syntax

from .regexes import get_regex
from .style import get_theme, get_default_props, Style

from ..gpkgs import message as msg

class Nargs():
    def __init__(self,
        filenpa_definition=None,
        dy_definition=dict(),
        # builtins=None,
        # # cached_dfn=None,
        # definition=None,
        # metadata=dict(),
        # # pretty=True,
        # substitute=False,
        # theme=None,
        # usage_on_root=True,
    ):
        # "how to add nargs_version to dict if not added by user. Some parameters won't be cached I guess."

        filenpa_caller=inspect.stack()[1].filename
        if os.path.islink(filenpa_caller):
            filenpa_caller=os.path.realpath(filenpa_caller)
        self._direpa_caller=os.path.normpath(os.path.dirname(filenpa_caller))

        self.tmp_dy_definition=dict()
        if filenpa_definition is not None:
        # dy_dfn=get_dy_dfn(direpa_caller)

            


        sys.exit()

        # bools=dict(
        #     pretty=pretty,
        #     substitute=substitute,
        #     usage_on_root=usage_on_root,
        # )

        # for key in sorted(bools):
        #     value=bools[key]
        #     if not isinstance(value, bool):
        #         msg.error("Nargs parameter '{}' type {} must be of type {}.".format(key, type(value), bool), pretty=False, exit=1)

        self._pretty=pretty
        self._dy_metadata=get_dy_metadata(self._direpa_caller, metadata, sys.argv[0], self._pretty)
        self._app_name=self._dy_metadata["name"]
        
        self._builtins=[]
        authorized_builtins=["cmd", "help", "usage"]
        if builtins is None:
            self._builtins=authorized_builtins
        else:
            if isinstance(builtins, list):
                for builtin in sorted(builtins):
                    if builtin not in authorized_builtins:
                        msg.error("For '{}' at Nargs parameter '{}' value '{}' not found in {}.".format(self._dy_metadata["name"] ,"builtins", builtin, authorized_builtins), pretty=self._pretty, exit=1)

                    if builtin not in self._builtins:
                        self._builtins.append(builtin)
            else:
                msg.error("For '{}' at Nargs parameter '{}' type {} must be either {} or of type {}.".format(self._dy_metadata["name"], "builtins", type(builtins), None, list), pretty=self._pretty, exit=1)

        self._substitute=substitute
        self._usage_on_root=usage_on_root
        self._user_theme=theme
        if self._pretty is True:
            self._theme=get_theme(default_theme=self.get_default_theme(), user_theme=self._user_theme, pretty=self._pretty, app_name=self._app_name)
        else:
            self._theme=None

        if cached_dfn is None:
            self._node_dfn=get_node_dfn(
                builtins=self._builtins,
                dy_metadata=self._dy_metadata,
                dy_dfn=get_dy_dfn(self._direpa_caller, definition, self._pretty, self._app_name),
                pretty=self._pretty,
                app_name=self._app_name,
            )
        else:
            self._manage_cached_dfn(cached_dfn, self._direpa_caller, definition)

        self._modes=dict(
            cached_dfn=cached_dfn,
            pretty=self._pretty,
            substitute=self._substitute,
            usage_on_root=self._usage_on_root,
        )

    def _manage_cached_dfn(self, cached_dfn, direpa_caller, definition):
        prefix="For '{}' at Nargs parameter cached_dfn".format(self._app_name)
        if isinstance(cached_dfn, dict):
            self._node_dfn=self.get_node_dfn_cached_trigger_error_if(dy_cached_dfn=cached_dfn)
        elif isinstance(cached_dfn, str):
            try:
                dy_cached_dfn=json.loads(cached_dfn)
                self._node_dfn=self.get_node_dfn_cached_trigger_error_if(dy_cached_dfn=dy_cached_dfn)
            except BaseException as e:
                if e.__class__.__name__ == "JSONDecodeError":
                    filerpa, ext=os.path.splitext(cached_dfn)
                    if ext in [".json", ".pickle"]:
                        if os.path.exists(cached_dfn):
                            if ext == ".json":
                                with open(cached_dfn, "r") as f:
                                    dy_cached_dfn=None
                                    try:
                                        dy_cached_dfn=json.load(f)
                                    except BaseException as e:
                                        print(str(e))
                                        msg.error("JSON syntax error in arguments definition file '{}'.".format(cached_dfn), prefix=prefix, pretty=self._pretty)
                                        sys.exit(2)
                                    
                                    self._node_dfn=self.get_node_dfn_cached_trigger_error_if(dy_cached_dfn=dy_cached_dfn)
                            elif ext == ".pickle":
                                with open(cached_dfn, "rb") as f:
                                    try:
                                        self._node_dfn=pickle.load(f)
                                    except BaseException as e:
                                        print(str(e))
                                        msg.error("Pickle file error in arguments definition file '{}'.".format(cached_dfn), prefix=prefix, pretty=self._pretty)
                                        sys.exit(2)
                        else:
                            self._node_dfn=get_node_dfn(
                                builtins=self._builtins,
                                dy_metadata=self._dy_metadata,
                                dy_dfn=get_dy_dfn(direpa_caller, definition, self._pretty, self._app_name),
                                pretty=self._pretty,
                                app_name=self._app_name,
                            )
                            self.dump(filenpa=cached_dfn)
                    else:
                        msg.error("cached_dfn value is not a json string, a .json file or a pickle file.", prefix=prefix, pretty=self._pretty, exit=1)
                elif e.code == 2:
                    sys.exit(1)
                else:
                    traceback.print_exc()
                    sys.exit(1)
        else:
            msg.error("wrong type {}, it must be {}.".format(type(cached_dfn), str), prefix=prefix, pretty=self._pretty, exit=1)

    def get_node_dfn_cached_trigger_error_if(self, dy_cached_dfn):
        try:
            return get_cached_node_dfn(dy_dfn=dy_cached_dfn, pretty=self._pretty, app_name=self._app_name)
        except Exception as e:
            msg.error([
                "For '{}' at Nargs cached_dfn, unexpected error occured when loading definition from dumped data.".format(self._app_name),
                "Dumped data is obtained with Nargs.dump() and/or cached_dfn.",
                "Please review cached_dfn data and delete it if corrupted to regenerate it.",
            ], pretty=self._pretty)
            traceback.print_exc()
            sys.exit(2)

    def dump(self, filenpa=None):
        from_cached_dfn=inspect.stack()[1].function == "_manage_cached_dfn"
        prefix="For '{}' at Nargs dump".format(self._app_name)
        if self._node_dfn is None:
            if from_cached_dfn is True:
                msg.error("cached_dfn can't be set when either definition is empty or root argument is not enabled.", prefix=prefix, pretty=self._pretty, exit=1)
            else:
                msg.error("definition can't be dumped when either definition is empty or root argument is not enabled.", prefix=prefix, pretty=self._pretty, exit=1)

        dy_dump=get_dump(self._node_dfn)

        if filenpa is None:
            return json.dumps(get_dump(self._node_dfn))
        else:
            if not isinstance(filenpa, str):
                msg.error("filenpa type {} is must be type {}".format(filenpa, str), prefix=prefix, pretty=self._pretty, exit=1)

            direpa_dump=os.path.dirname(filenpa)
            if direpa_dump == "":
                direpa_dump=self._direpa_caller

            if not os.path.isabs(direpa_dump):
                direpa_dump=os.path.normpath(os.path.join(self._direpa_caller, direpa_dump))

            if os.path.exists(direpa_dump):
                if not os.path.isdir(direpa_dump):
                    msg.error("path is not a directory '{}'".format(direpa_dump), prefix=prefix, pretty=self._pretty, exit=1)
            else:
                msg.error("directory not found '{}'".format(direpa_dump), prefix=prefix, pretty=self._pretty, exit=1)

            filenpa=os.path.join(direpa_dump, os.path.basename(filenpa))
            if os.path.exists(filenpa):
                msg.error("file already exists '{}'".format(filenpa), prefix=prefix, pretty=self._pretty, exit=1)

            filerpa, ext=os.path.splitext(filenpa)
            if ext == ".json":
                with open(filenpa, "w") as f:
                    f.write(json.dumps(dy_dump))
            elif ext == ".pickle":
                tmp_node_dfn=get_cached_node_dfn(dy_dfn=dy_dump, pretty=self._pretty, app_name=self._app_name)
                with open(filenpa, "wb") as f:
                    pickle.dump(tmp_node_dfn, f)
            else:
                msg.error("file extension '{}' not found in ['.json', '.pickle']".format(ext), prefix=prefix, pretty=self._pretty, exit=1)

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
        return get_args(
            app_name=self._app_name,
            cmd=cmd,
            dy_metadata=self._dy_metadata,
            node_dfn=self._node_dfn,
            pretty=self._pretty,
            substitute=self._substitute,
            theme=self._theme,
            usage_on_root=self._usage_on_root,
            get_documentation=self.get_documentation,
        )

    def _update_nargs_syntax(self):
        filenpa=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "nargs-syntax.md")
        nargs_syntax=get_md_text(
            title="NARGS END-USER DOCUMENTATION", 
            sections=[get_nargs_syntax(
                    Style(pretty=self._pretty, output="markdown", theme=self._theme, prefix="For '{}' at Nargs update syntax".format(self._app_name)), 
                    self._modes,
                    print_modes=False,

                )
            ],
        )
        with open(filenpa, "w") as f:
            f.write("{}".format(nargs_syntax))
            
    def get_documentation(self, output, filenpa=None, wsyntax=False):
        prefix="For '{}' at Nargs get_documentation".format(self._app_name)

        if self._theme is None:
            self._theme=get_theme(default_theme=self.get_default_theme(), user_theme=self._user_theme, pretty=self._pretty)

        documentation=get_help_usage(
            dy_metadata=self._dy_metadata,
            modes=self._modes,
            node_ref=self._node_dfn,
            output=output,
            style=Style(pretty=self._pretty, output=output, theme=self._theme, prefix=prefix),
            wexamples=True,
            whint=True,
            winfo=True,
            wsyntax=wsyntax,
        )

        if output not in ["cmd_usage", "cmd_help"]:
            if filenpa is not None:
                if not isinstance(filenpa, str):
                    msg.error("filenpa type {} is not type {}".format(type(filenpa), str), prefix=prefix, pretty=self._pretty, exit=1)

                if not os.path.isabs(filenpa):
                    filenpa=os.path.abspath(filenpa)
                filenpa=os.path.normpath(filenpa)
                if os.path.exists(filenpa):
                    msg.error("file already exists '{}'".format(filenpa), prefix=prefix, pretty=self._pretty, exit=1)
                with open(filenpa, "w") as f:
                    f.write("{}".format(documentation))

            return documentation

    def get_metadata_template(self):
        return get_metadata_template()

def get_dump(node, dump=None):
    if node.is_root is True:
        dump=dict()

    dump[node.name]=deepcopy(node.dy)
    dump[node.name]["type"]=get_type_str(node.dy["type"])
    dump[node.name]["args"]=dict()

    for tmp_node in node.nodes:
        get_dump(tmp_node, dump[node.name]["args"])

    if node.is_root is True:
        return dump

def get_metadata_template():
    return dict(
        authors=[],
        description="",
        executable="",
        licenses=[],
        name="",
        conf_path="",
        uuid4="",
        version="",
        timestamp=0.00,
    )

def get_dy_metadata(direpa_caller, dy, main, pretty):
    prefix="At Nargs for dict metadata"

    if not isinstance(dy, dict):
        msg.error("metadata type {} must be of type {}.".format(type(dy), dict), prefix=prefix, pretty=pretty, exit=1)

    filenpa_gpm=os.path.join(direpa_caller, "gpm.json")
    dy_metadata=dict()
    if os.path.exists(filenpa_gpm):
        with open(filenpa_gpm, "r") as f:
            try:
                dy_metadata=json.load(f)
            except BaseException:
                msg.error("JSON syntax error in gpm file '{}'.".format(filenpa_gpm), prefix=prefix, pretty=pretty)
                print(traceback.format_exc())
                sys.exit(1)

    dy_metadata.update(dy)

    if "name" not in dy_metadata:
        msg.error("at key 'name' not found.", prefix=prefix, pretty=pretty, exit=1)

    if "executable" not in dy_metadata:
        if "alias" in dy_metadata:
            dy_metadata["executable"]=dy_metadata["alias"]
        else:
            msg.error("at key 'executable' not found.", prefix=prefix, pretty=pretty, exit=1)

    for name in ["name", "executable"]:
        if not isinstance(dy_metadata[name], str):
            msg.error("at key '{}' value type {} must be of type {}.".format(name, type(dy_metadata[name]), str), prefix=prefix, pretty=pretty, exit=1)

        dy_metadata[name]=dy_metadata[name].strip()
        if len(dy_metadata[name]) == 0:
            msg.error("at key '{}' value can't be empty.".format(name), prefix=prefix, pretty=pretty, exit=1)

    del_keys=[]
    for key, value in dy_metadata.items():
        if isinstance(value, str):
            dy_metadata[key]=value.strip()
            if dy_metadata[key] == "" or dy_metadata[key] is None:
                del_keys.append(key)

    for key in del_keys:
        del dy_metadata[key]

    defaults=get_metadata_template()
    for default_key in sorted(defaults):
        if default_key not in ["name", "executable"]:
            defaut_value_type=type(defaults[default_key])
            if default_key in dy_metadata:
                if type(dy_metadata[default_key]) != defaut_value_type:
                    msg.error("at key '{}' value type {} must be of type {}.".format(default_key, type(dy_metadata[default_key]), defaut_value_type), prefix=prefix, pretty=pretty, exit=1)

    return dy_metadata