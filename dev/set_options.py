#!/usr/bin/env python3
from pprint import pprint
import hashlib
import json
import os
import pickle
import sys
import traceback

from .style import get_theme

from ..gpkgs import message as msg

def get_cached_options(direpa_caller, cache_file, extension, md5_options):
    prefix="At Nargs with cache_file option"

    if os.path.exists(cache_file):
        if not os.path.isfile(cache_file):
            msg.error("path is not a file '{}'".format(cache_file), prefix=prefix, pretty=False, exit=1)

        dy_cached_options=None
        if extension == ".json":
            with open(cache_file, "r") as f:
                try:
                    dy_cached_options=json.load(f)
                except BaseException as e:
                    msg.warning("JSON syntax error for file '{}'.".format(cache_file), prefix=prefix, pretty=False)
        elif extension == ".pickle":
            with open(cache_file, "rb") as f:
                try:
                    dy_cached_options=pickle.load(f)
                except BaseException as e:
                    msg.warning("Pickle file error for file '{}'.".format(cache_file), prefix=prefix, pretty=False)
        
        if dy_cached_options is None:
            return None
        else:
            if "md5_options" in dy_cached_options:
                if md5_options == dy_cached_options["md5_options"]:
                    for file_option in ["filenpa_metadata", "filenpa_options"]:
                        if file_option in dy_cached_options:
                            for key in ["filenpa", "md5"]:
                                if key not in dy_cached_options[file_option]:
                                    dy_cached_options=None
                                    break

                            filenpa_option=dy_cached_options[file_option]["filenpa"]
                            if not os.path.exists(filenpa_option) or not os.path.isfile(filenpa_option):
                                dy_cached_options=None
                                break

                            file_md5=dy_cached_options[file_option]["md5"]
                            if file_md5 != hashlib.md5(open(filenpa_option,"rb").read()).hexdigest():
                                dy_cached_options=None
                                break
                    return dy_cached_options
                else:
                    return None
            else:
                return None
    else:
        return None

def set_options(direpa_caller, dy_options, md5_options, dy_default_theme, main):
    prefix="At Nargs when settings options"
    pretty=False
    if not isinstance(dy_options, dict):
        msg.error("argument dy_options wrong type {}. It must be of type {}.".format(type(dy_options), dict), prefix=prefix, pretty=pretty, exit=1)

    dy_options["md5_options"]=md5_options

    if "options_file" in dy_options:
        options_file=dy_options["options_file"]
        if options_file is not None:
            if isinstance(options_file, str) is False:
                msg.error("options file path type {} must be either type {} or type {}.".format(
                    type(options_file),
                    str,
                    type(None),
                ), prefix=prefix, pretty=pretty, exit=1)
                
            if not os.path.isabs(options_file):
                options_file=os.path.normpath(os.path.abspath(os.path.join(direpa_caller, options_file)))
            
            if not os.path.exists(options_file):
                msg.error("options file path not found '{}'.".format(options_file), prefix=prefix, pretty=pretty, exit=1)
            if not os.path.isfile(options_file):
                msg.error("options file path is not a file '{}'".format(options_file), prefix=prefix, pretty=pretty, exit=1)

            filen=os.path.basename(options_file)
            filer, ext=os.path.splitext(filen)

            authorized_exts=[".json", ".yaml", ".yml"]
            if ext not in authorized_exts:
                msg.error("options file extension '{}' must be in {}".format(ext, authorized_exts), prefix=prefix, pretty=pretty, exit=1)

            if ext == ".json":
                with open(options_file, "r") as f:
                    try:
                        dy_options.update(json.load(f))
                    except BaseException:
                        print(traceback.format_exc())
                        msg.error("JSON syntax error in options file '{}'.".format(options_file), prefix=prefix, pretty=pretty)
                        sys.exit(1)
            elif ext in [".yaml", ".yml"]:
                with open(options_file, "r") as f:
                    try:
                        import yaml
                    except:
                        msg.error(r"""
                            YAML module not found to import options file.
                            Do either:
                            - pip install pyyaml.
                            - use a JSON file for options file.
                            - use a python dict for options file.
                        """, heredoc=True, prefix=prefix, pretty=pretty, exit=1)
                    try:
                        dy_options.update(yaml.safe_load(f))
                    except BaseException as e:
                        print(traceback.format_exc())
                        msg.error("YAML syntax error in definition file '{}'".format(options_file), prefix=prefix, pretty=pretty)
                        sys.exit(1)

            dy_options["filenpa_options"]=dict(
                filenpa=options_file,
                md5=hashlib.md5(open(options_file,"rb").read()).hexdigest(),
            )

    for field in ["pretty_help", "pretty_msg"]:
        if field in dy_options:
            if not isinstance(dy_options[field], bool):
                msg.error("argument dy_options at key '{}' wrong type {}. It must be of type {}.".format(field, type(dy_options[field]), dict), prefix=prefix, pretty=pretty, exit=1)
        else:
            dy_options[field]=True

    pretty=dy_options["pretty_msg"]

    if "metadata" in dy_options:
        if not isinstance(dy_options["metadata"], dict):
            msg.error("argument dy_options at key 'metadata' wrong type {}. It must be of type {}.".format(type(dy_options["metadata"]), dict), prefix=prefix, pretty=pretty, exit=1)
    else:
        dy_options["metadata"]=dict()

    set_dy_metadata(direpa_caller, dy_options, pretty, main)
    app_name=dy_options["metadata"]["name"]
    prefix="For '{}' At Nargs when settings options".format(app_name)

    data=dict(
        args=[dict],
        auto_alias_style=[str],
        auto_alias_prefix=[str],
        builtins=[list, type(None)],
        char_prefix=[str],
        path_etc=[str, type(None)],
        substitute=[bool],
        theme=[dict],
        usage_on_root=[bool],
    )

    styles=[
        "camelcase",
        "camelcase-hyphen",
        "lowercase",
        "lowercase-hyphen",
        "pascalcase",
        "pascalcase-hyphen",
        "uppercase",
        "uppercase-hyphen",
    ]

    alias_prefixes=["", "+", "-", "--", "/", ":", "_"]
    builtins=["cmd", "help", "usage", "version"]
    concat_prefixes=["+", "-", "--", "/", ":", "_"]

    for option in sorted(data):
        if option in dy_options:
            matched=False
            for _type in data[option]:
                if isinstance(dy_options[option], _type) is True:
                    matched=True
                    break

            if matched is False:
                msg.error("option '{}' has wrong type {}. Type must be {}.".format(option, type(option), _type), prefix=prefix, pretty=pretty, exit=1)

            value=dy_options[option]
            if option == "auto_alias_style":
                if value not in styles:
                    msg.error("option '{}' value '{}' is not in {}.".format(option, value, styles), prefix=prefix, pretty=pretty, exit=1)
            elif option == "auto_alias_prefix":
                if value not in alias_prefixes:
                    msg.error("option '{}' value '{}' is not in {}.".format(option, value, alias_prefixes), prefix=prefix, pretty=pretty, exit=1)
            elif option == "builtins":
                if value is None:
                    dy_options[option]=[]
                else:
                    for v in value:
                        if v not in builtins:
                            msg.error("option '{}' value '{}' is not in {}.".format(option, v, builtins), prefix=prefix, pretty=pretty, exit=1)

                dy_options[option]=sorted(list(set(dy_options[option])))
            elif option == "char_prefix":
                if value == dy_options["auto_alias_prefix"]:
                    msg.error("option '{}' value '{}' can't be the same as option 'auto_alias_prefix'.".format(option, value), prefix=prefix, pretty=pretty, exit=1)
                elif value not in concat_prefixes:
                    msg.error("option '{}' value '{}' is not in {}.".format(option, value, concat_prefixes), prefix=prefix, pretty=pretty, exit=1)
            elif option == "path_etc":
                pass
            elif option == "substitute":
                pass
            elif option == "theme":
                dy_options[option]=get_theme(default_theme=dy_default_theme, user_theme=dy_options[option], pretty=pretty, app_name=app_name)
            elif option == "usage_on_root":
                pass
            elif option == "args":
                pass
        else:
            if option == "auto_alias_style":
                dy_options[option]="lowercase-hyphen"
            elif option == "auto_alias_prefix":
                dy_options[option]="--"
            elif option == "builtins":
                dy_options[option]=builtins
            elif option == "char_prefix":
                dy_options[option]="-"
            elif option == "path_etc":
                dy_options[option]=None
            elif option == "substitute":
                dy_options[option]=False
            elif option == "theme":
                dy_options[option]=dy_default_theme
            elif option == "usage_on_root":
                dy_options[option]=True
            elif option == "args":
                dy_options[option]=dict()

    alias_prefixes.remove(dy_options["char_prefix"])
    alias_prefixes.remove("")
    regstr="({})?".format("|".join(alias_prefixes)).replace("+", "\+")

    dy_options["alias_prefixes_regstr"]=regstr
    dy_options["alias_prefixes_reghint"]=alias_prefixes

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

def set_dy_metadata(direpa_caller, dy_options, pretty, main):
    prefix="At Nargs for dict metadata"
    dy_metadata=dy_options["metadata"]
    if not isinstance(dy_metadata, dict):
        msg.error("metadata type {} must be of type {}.".format(type(dy_metadata), dict), prefix=prefix, pretty=pretty, exit=1)

    filenpa_gpm=os.path.join(direpa_caller, "gpm.json")
    dy_tmp_metadata=dict()
    if os.path.exists(filenpa_gpm):
        with open(filenpa_gpm, "r") as f:
            try:
                dy_tmp_metadata=json.load(f)
            except BaseException:
                msg.error("JSON syntax error in gpm file '{}'.".format(filenpa_gpm), prefix=prefix, pretty=pretty)
                print(traceback.format_exc())
                sys.exit(1)

        dy_options["filenpa_metadata"]=dict(
            filenpa=filenpa_gpm,
            md5=hashlib.md5(open(filenpa_gpm,"rb").read()).hexdigest(),
        )

    dy_tmp_metadata.update(dy_metadata)
    dy_options["metadata"]=dy_tmp_metadata
    dy_metadata=dy_options["metadata"]

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
