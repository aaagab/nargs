#!/usr/bin/env python3
from pprint import pprint
import hashlib
import json
import os
import pickle
import sys
import traceback

from .regexes import get_alias_prefixes
from .style import get_theme

from .. import __version__

from ..gpkgs import message as msg

def get_default_builtins():
    return dict(
        help=None,
        path_etc=None,
        query=None,
        usage=None,
        version=None,
    )

def get_cached_options(direpa_caller, cache_file, extension, md5_options, only_cache, dy_err):
    tmp_prefix="{} with cache_file option".format(dy_err["prefix"])
    if os.path.exists(cache_file):
        if not os.path.isfile(cache_file):
            msg.error("path is not a file '{}'".format(cache_file), prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        dy_cached_options=None
        if extension == ".json":
            with open(cache_file, "r") as f:
                try:
                    data=f.read().strip()
                    if data == "":
                        dy_cached_options=None
                    else:
                        dy_cached_options=json.loads(data)
                except BaseException as e:
                    msg.error("JSON syntax error for file '{}'.".format(cache_file), prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        elif extension == ".pickle":
            with open(cache_file, "rb") as f:
                try:
                    dy_cached_options=pickle.load(f)
                except BaseException as e:
                    msg.error("Pickle syntax error for file '{}'.".format(cache_file), prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        
        if dy_cached_options is None:
            return None
        else:
            if only_cache is True:
                return dy_cached_options
            else:
                if "md5_options" in dy_cached_options:
                    if md5_options == dy_cached_options["md5_options"]:
                        if "md5_files" in dy_cached_options:

                            dy_cached_files=dict()
                            for file_label in dy_cached_options["md5_files"]:
                                for key in ["filenpa", "md5"]:
                                    if key not in dy_cached_options["md5_files"][file_label]:
                                        return None

                                filenpa_option=dy_cached_options["md5_files"][file_label]["filenpa"]
                                if not os.path.exists(filenpa_option) or not os.path.isfile(filenpa_option):
                                    return None

                                file_md5=dy_cached_options["md5_files"][file_label]["md5"]
                                if file_md5 != hashlib.md5(open(filenpa_option,"rb").read()).hexdigest():
                                    return None

                                if "user" in file_label:
                                    dy_cached_files[file_label]=filenpa_option

                            user_files=get_user_files(direpa_caller, dy_cached_options)
                            for dy_user_file in user_files:
                                if dy_user_file["label"] in dy_cached_files:
                                    filenpa_cached=dy_cached_files[dy_user_file["label"]]
                                    filenpa_found=dy_user_file["filenpa"]
                                    if filenpa_cached != filenpa_found:
                                        return None
                                else:
                                    return None

                        return dy_cached_options
                    else:
                        return None
                else:
                    return None
    else:
        return None

def get_user_files(direpa_caller, dy_options):
    tmp_filenpas=[]
    filer_user=".nargs-user"

    for ext in [".yaml", ".json"]:
        filenpa_user_exe=os.path.join(direpa_caller, filer_user+ext)
        if os.path.exists(filenpa_user_exe):
            tmp_filenpas.append(dict(filenpa=filenpa_user_exe, label="user1"))
            break

    if "path_etc" in dy_options:
        if isinstance(dy_options["path_etc"], str):
            if not os.path.isabs(dy_options["path_etc"]):
                dy_options["path_etc"]=os.path.abspath(os.path.join(direpa_caller, dy_options["path_etc"]))
            dy_options["path_etc"]=os.path.normpath(dy_options["path_etc"])
            if os.path.exists(dy_options["path_etc"]):
                if os.path.isdir(dy_options["path_etc"]):
                    for ext in [".yaml", ".json"]:
                        filenpa_user_conf=os.path.join(dy_options["path_etc"], filer_user+ext)
                        if os.path.exists(filenpa_user_conf):
                            tmp_filenpas.append(dict(filenpa=filenpa_user_conf, label="user2"))
                            break
    else:
        dy_options["path_etc"]=None

    return tmp_filenpas

def dy_options_update(dy_filenpa_md5, dy_options, dy_err):
    filenpa_md5=dy_filenpa_md5["filenpa"]
    file_label=dy_filenpa_md5["label"]
    filen=os.path.basename(filenpa_md5)

    filer, ext=os.path.splitext(filen)

    authorized_exts=[".json", ".yaml"]
    if ext not in authorized_exts:
        msg.error("options file extension '{}' must be in {}".format(ext, authorized_exts), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    tmp_dy_options=dict()
    if ext == ".json":
        with open(filenpa_md5, "r") as f:
            try:
                data=f.read().strip()
                if data == "":
                    tmp_dy_options=None
                else:
                    tmp_dy_options=json.loads(data)
            except BaseException:
                msg.error("JSON syntax error in options file '{}'.".format(filenpa_md5), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"])
                print(traceback.format_exc())
                sys.exit(1)
    elif ext == ".yaml":
        with open(filenpa_md5, "r") as f:
            try:
                import yaml
            except:
                msg.error(r"""
                    YAML module not found to import options file.
                    Do either:
                    - pip install pyyaml.
                    - use a JSON file for options file.
                    - use a python dict for options file.
                """, heredoc=True, prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
            try:
                tmp_dy_options=yaml.safe_load(f)
            except BaseException as e:
                msg.error("YAML syntax error in options file '{}'".format(filenpa_md5), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"])
                print(traceback.format_exc())
                sys.exit(1)

    if "user" in file_label:
        if tmp_dy_options is not None:
            for key in sorted(tmp_dy_options):
                if key not in [
                    "pretty_help",
                    "pretty_msg",
                    "substitute",
                    "theme",
                ]:
                    del tmp_dy_options[key]

    if tmp_dy_options is not None:
        dy_options.update(tmp_dy_options)

    dy_options["md5_files"][file_label]=dict(
        filenpa=filenpa_md5,
        md5=hashlib.md5(open(filenpa_md5,"rb").read()).hexdigest(),
    )

def set_options(direpa_caller, dy_options, md5_options, dy_default_theme, main, dy_err):
    dy_options["md5_options"]=md5_options
    dy_options["nargs_version"]=__version__
    dy_options["md5_files"]=dict()
    filenpas_md5=[]

    if "options_file" in dy_options:
        options_file=dy_options["options_file"]
        if options_file is not None:
            if isinstance(options_file, str) is False:
                msg.error("options file path type {} must be either type {} or type {}.".format(
                    type(options_file),
                    str,
                    type(None),
                ), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                
            if not os.path.isabs(options_file):
                options_file=os.path.abspath(os.path.join(direpa_caller, options_file))
            options_file=os.path.normpath(options_file)
            
            if not os.path.exists(options_file):
                msg.error("options file path not found '{}'.".format(options_file), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            if not os.path.isfile(options_file):
                msg.error("options file path is not a file '{}'".format(options_file), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            dy_filenpa_md5=dict(filenpa=options_file, label="options_file")
            dy_options_update(dy_filenpa_md5, dy_options, dy_err)
            filenpas_md5.append(dy_filenpa_md5)

    for dy_filenpa_md5 in get_user_files(direpa_caller, dy_options):
        dy_options_update(dy_filenpa_md5, dy_options, dy_err)
        filenpas_md5.append(dy_filenpa_md5)

    for field in ["pretty_help", "pretty_msg"]:
        if field in dy_options:
            if not isinstance(dy_options[field], bool):
                msg.error("argument dy_options at key '{}' wrong type {}. It must be of type {}.".format(field, type(dy_options[field]), bool), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
        else:
            dy_options[field]=True

    dy_err["pretty"]=dy_options["pretty_msg"]


    filenpa_nargs=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "gpm.json")
    dy_options["md5_files"]["nargs"]=dict(
        filenpa=filenpa_nargs,
        md5=hashlib.md5(open(filenpa_nargs,"rb").read()).hexdigest(),
    )

    if "metadata" in dy_options:
        if not isinstance(dy_options["metadata"], dict):
            msg.error("argument dy_options at key 'metadata' wrong type {}. It must be of type {}.".format(type(dy_options["metadata"]), dict), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
    else:
        dy_options["metadata"]=dict()

    set_dy_metadata(direpa_caller, dy_options, main, dy_err)
    app_name=dy_options["metadata"]["name"]
    prefix="For '{}' At Nargs when setting options".format(app_name)

    data=dict(
        args=[dict, type(None)],
        auto_alias_style=[str],
        auto_alias_prefix=[str],
        builtins=[dict, type(None)],
        substitute=[bool],
        theme=[dict, type(None)],
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

    alias_prefixes=get_alias_prefixes()
    builtins=sorted(get_default_builtins())

    for option in sorted(data):
        if option in dy_options:
            matched=False
            for _type in data[option]:
                if isinstance(dy_options[option], _type) is True:
                    matched=True
                    break

            if matched is False:
                msg.error("option '{}' has wrong type {}. Type can be any type from {}.".format(option, type(dy_options[option]), data[option]), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            value=dy_options[option]
            if option == "auto_alias_style":
                if value not in styles:
                    msg.error("option '{}' value '{}' is not in {}.".format(option, value, styles), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
            elif option == "auto_alias_prefix":
                if value not in alias_prefixes:
                    msg.error("option '{}' value '{}' is not in {}.".format(option, value, alias_prefixes), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
            elif option == "builtins":
                if value is None:
                    dy_options[option]=dict()
                else:
                    tmp_keys=[]
                    for key in value:
                        if key not in builtins:
                            msg.error("option '{}' key '{}' is not in {}.".format(option, key, builtins), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

                        aliases=value[key]
                        if type(aliases) in [type(None), str, list]:
                            if type(aliases) == str:
                                tmp_aliases=[]
                                for alias in aliases.split(","):
                                    tmp_aliases.append(alias.strip())
                                value[key]=tmp_aliases
                            elif type(aliases) == list:
                                for alias in aliases:
                                    if not isinstance(alias, str):
                                        msg.error("option '{}' at key '{}' for values '{}' with value '{}' wrong type {} it must be {} for alias.".format(option, key, aliases, alias, type(alias), str), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                        else:
                            msg.error("option '{}' for key '{}' value '{}' type {} is not in {}.".format(option, key, aliases, type(aliases), [type(None), str, list]), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

            elif option == "substitute":
                pass
            elif option == "theme":
                if dy_options["pretty_help"] is True:
                    dy_options[option]=get_theme(default_theme=dy_default_theme, user_theme=dy_options[option], dy_err=dy_err)
            elif option == "args":
                pass
        else:
            if option == "auto_alias_style":
                dy_options[option]="lowercase-hyphen"
            elif option == "auto_alias_prefix":
                dy_options[option]="--"
            elif option == "builtins":
                dy_options[option]=builtins
            elif option == "substitute":
                if dy_options["pretty_help"] is True:
                    dy_options[option]=False
            elif option == "theme":
                dy_options[option]=dy_default_theme
            elif option == "args":
                dy_options[option]=None
        
    

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

def set_dy_metadata(direpa_caller, dy_options, main, dy_err):
    tmp_prefix="{} at option 'metadata'".format(dy_err["prefix"])
    dy_metadata=dy_options["metadata"]
    filenpa_gpm=os.path.join(direpa_caller, "gpm.json")
    dy_tmp_metadata=dict()
    if os.path.exists(filenpa_gpm):
        with open(filenpa_gpm, "r") as f:
            try:
                dy_tmp_metadata=json.load(f)
            except BaseException:
                msg.error("JSON syntax error in gpm file '{}'.".format(filenpa_gpm), prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"])
                print(traceback.format_exc())
                sys.exit(1)

        dy_options["md5_files"]["filenpa_metadata"]=dict(
            filenpa=filenpa_gpm,
            md5=hashlib.md5(open(filenpa_gpm,"rb").read()).hexdigest(),
        )

    dy_tmp_metadata.update(dy_metadata)
    dy_options["metadata"]=dy_tmp_metadata
    dy_metadata=dy_options["metadata"]

    if "name" not in dy_metadata:
        msg.error("key 'name' not set.", prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    if "executable" not in dy_metadata:
        if "alias" in dy_metadata:
            dy_metadata["executable"]=dy_metadata["alias"]
        else:
            msg.error("key 'executable' not set.", prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    for name in ["name", "executable"]:
        if not isinstance(dy_metadata[name], str):
            msg.error("key '{}' value type {} must be of type {}.".format(name, type(dy_metadata[name]), str), prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        dy_metadata[name]=dy_metadata[name].strip()
        if len(dy_metadata[name]) == 0:
            msg.error("key '{}' value can't be empty.".format(name), prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

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
                    msg.error("key '{}' value type {} must be of type {}.".format(default_key, type(dy_metadata[default_key]), defaut_value_type), prefix=tmp_prefix, pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
