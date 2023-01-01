#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys
import traceback

from .exceptions import EndUserError, ErrorTypes

def get_path(node_dfn, path_elem, path_type, dy_err, cmd_line_index):
    exit_not_found=None
    if path_type in ["path", "file", "dir"]:
        exit_not_found=True
    elif path_type == "vpath":
        exit_not_found=False

    if not os.path.isabs(path_elem):
        path_elem=os.path.abspath(path_elem)
    path_elem=os.path.normpath(path_elem)
    if exit_not_found is True:
        if not os.path.exists(path_elem):
            raise EndUserError(dict(
                attributes=dict(
                    path_elem=path_elem,
                ),
                cmd_line=dy_err["cmd_line"][:cmd_line_index],
                error_type=ErrorTypes().PathNotFound,
                message="Path not found '{path_elem}'.",
                node_usage=node_dfn,
                show_usage=False,
                stack_trace=traceback.format_exc(),
                show_stack=False,
                prefix=dy_err["prefix"],
            ))

        if path_type == "dir":
            if not os.path.isdir(path_elem):
                raise EndUserError(dict(
                    attributes=dict(
                        path_elem=path_elem,
                    ),
                    cmd_line=dy_err["cmd_line"][:cmd_line_index],
                    error_type=ErrorTypes().PathNotADirectory,
                    message="Path is not a directory '{path_elem}'.",
                    node_usage=node_dfn,
                    show_usage=False,
                    stack_trace=traceback.format_exc(),
                    show_stack=False,
                    prefix=dy_err["prefix"],
                ))
        elif path_type == "file":
            if not os.path.isfile(path_elem):
                raise EndUserError(dict(
                    attributes=dict(
                        path_elem=path_elem,
                    ),
                    cmd_line=dy_err["cmd_line"][:cmd_line_index],
                    error_type=ErrorTypes().PathNotAFile,
                    message="Path is not a file '{path_elem}'.",
                    node_usage=node_dfn,
                    show_usage=False,
                    stack_trace=traceback.format_exc(),
                    show_stack=False,
                    prefix=dy_err["prefix"],
                ))

    return path_elem