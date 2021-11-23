#!/usr/bin/env python3
from pprint import pprint
import ast
import json
import os
import getpass
import re
import sys
import traceback

from ..gpkgs import message as msg

from .regexes import get_regex

has_yaml_module=True
try:
    import yaml
except:
    has_yaml_module=False

def get_arg_prefix(dy_err, cmd_line_index):
    return "{} '{}'".format(dy_err["prefix"], dy_err["cmd_line"][:cmd_line_index])

def get_json(
    value,
    node,
    dy_err,
    cmd_line_index,
    search_file=False, 
):
    dy=dict()
   
    if isinstance(value, dict):
        dy=value
    else:
        json_set=False
        if search_file is True:
            reg_file=re.match(r"^.+\.(?P<ext>json|yml|yaml)$", value)
            if reg_file:
                json_set=True
                ext=reg_file.group("ext")
                filenpa=value
                if not os.path.isabs(filenpa):
                    filenpa=os.path.abspath(filenpa)
                filenpa=os.path.normpath(filenpa)

                if os.path.exists(filenpa):
                    if ext == "json":
                        try:
                            with open(filenpa, "r") as f:
                                dy=json.load(f)
                        except BaseException:
                            msg.error("json syntax error in file '{}'".format(filenpa), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                    elif ext in ["yml", "yaml"]:
                        if has_yaml_module is True:
                            try:
                                with open(filenpa, "r") as f:
                                    dy=yaml.safe_load(f)
                            except BaseException:
                                msg.error("yaml syntax error in file '{}'".format(filenpa), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                        else:
                            msg.error(r"""
                                yaml module not found to import file '{}'.
                                Either do:
                                - pip install pyyaml
                                - use a json file or a json string as argument
                            """.format(filenpa), heredoc=True, prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                else:
                    msg.error("File not found '{}'".format(filenpa), prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

        if json_set is False:
            failed=False
            errors=[]
            try:
                dy=json.loads(value)
            except BaseException as e:
                errors.append(repr(e))

                yaml_parsed=False
                if has_yaml_module is True:
                    try:
                        dy=yaml.safe_load(value)
                        yaml_parsed=True
                    except BaseException as e:
                        errors.append(repr(e))

                if yaml_parsed is False:
                    # for single-quoted json string
                    if len(value) < 100000:
                        reg_str=r"(\'.+?\'\s*:\s*){}(\s*(?:,|\}})?)"
                        syntax=dict(true=True, false=False, null=None)
                        for old, new in syntax.items():
                            value = re.sub(reg_str.format(old), r"\1{}\2".format(new), value)
                        try:
                            dy=ast.literal_eval(value)
                        except BaseException as e:
                            failed=True
                            errors.append(repr(e))
                    else:
                        failed=True
                        errors.append("value length is >= than '100000'.")


            if failed is True:
                msg.error([
                    "Error when trying to load dict from '{}'.".format(value[:50]),
                    *errors,
                ], prefix=get_arg_prefix(dy_err, cmd_line_index), pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    return dy