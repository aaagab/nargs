#!/usr/bin/env python3
from json.decoder import JSONDecodeError
from pprint import pprint
import ast
import json
import os
import re
import sys
import traceback

from .exceptions import EndUserError, ErrorTypes

has_yaml_module=True
try:
    import yaml
except:
    has_yaml_module=False

def get_json(
    value,
    node_dfn,
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
                        except JSONDecodeError:
                            raise EndUserError(dict(
                                attributes=dict(
                                    filenpa=filenpa,
                                ),
                                cmd_line=dy_err["cmd_line"][:cmd_line_index],
                                error_type=ErrorTypes().JsonSyntaxError,
                                message="json syntax error in file '{filenpa}'",
                                node_usage=node_dfn,
                                show_usage=False,
                                stack_trace=traceback.format_exc(),
                                show_stack=True,
                                prefix=dy_err["prefix"],
                            ))

                    elif ext in ["yml", "yaml"]:
                        if has_yaml_module is True:
                            try:
                                with open(filenpa, "r") as f:
                                    dy=yaml.safe_load(f)
                            except BaseException:
                                raise EndUserError(dict(
                                    attributes=dict(
                                        filenpa=filenpa,
                                    ),
                                    cmd_line=dy_err["cmd_line"][:cmd_line_index],
                                    error_type=ErrorTypes().YamlSyntaxError,
                                    message="yaml syntax error in file '{filenpa}'",
                                    node_usage=node_dfn,
                                    show_usage=False,
                                    stack_trace=traceback.format_exc(),
                                    show_stack=True,
                                    prefix=dy_err["prefix"],
                                ))
                        else:
                            raise EndUserError(dict(
                                attributes=dict(
                                    filenpa=filenpa,
                                ),
                                cmd_line=dy_err["cmd_line"][:cmd_line_index],
                                error_type=ErrorTypes().YamlSyntaxError,
                                message=[
                                    "yaml module not found to import file '{filenpa}'.",
                                    "Either do:",
                                    "- pip install pyyaml",
                                    "- use a json file or a json string as argument",
                                ],
                                node_usage=node_dfn,
                                show_usage=False,
                                stack_trace=traceback.format_exc(),
                                show_stack=False,
                                prefix=dy_err["prefix"],
                            ))
                else:
                    raise EndUserError(dict(
                        attributes=dict(
                            filenpa=filenpa,
                        ),
                        cmd_line=dy_err["cmd_line"][:cmd_line_index],
                        error_type=ErrorTypes().FileNotFound,
                        message="File not found '{filenpa}'",
                        node_usage=node_dfn,
                        show_usage=False,
                        stack_trace=traceback.format_exc(),
                        show_stack=False,
                        prefix=dy_err["prefix"],
                    ))

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
                raise EndUserError(dict(
                    attributes=dict(
                        value=value[:50],
                    ),
                    cmd_line=dy_err["cmd_line"][:cmd_line_index],
                    error_type=ErrorTypes().LoadDictionaryError,
                    message=[
                        "Error when trying to load dict from '{value}'.",
                        *errors,
                    ],
                    node_usage=None,
                    show_usage=False,
                    stack_trace=traceback.format_exc(),
                    show_stack=False,
                    prefix=dy_err["prefix"],
                ))

    return dy