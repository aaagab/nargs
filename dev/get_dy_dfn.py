#!/usr/bin/env python3
from pprint import pprint
import json
import os
import sys
import traceback

from ..gpkgs import message as msg

# def get_dy_dfn(direpa_caller, definition, pretty, app_name):
def get_dy_dfn(direpa_caller, filenpa_definition, dy_definition):
    prefix="At Nargs".format(app_name)
    pretty=False
    if not isinstance(dy_definition, dict):
        msg.error("argument dy_definition wrong type {}. It must be of type {}.".format(type(definition), dict), prefix=prefix, pretty=pretty, exit=1)


    sys.exit()

    prefix="For '{}' at Nargs".format(app_name)

    if definition is None:
        definition=dict()

    dy_definition=dict()

    if isinstance(definition, dict):
        dy_definition=definition
    elif isinstance(definition, str):
        filenpa_definition=definition
        if not os.path.isabs(filenpa_definition):
            filenpa_definition=os.path.join(direpa_caller, filenpa_definition)
        filenpa_definition=os.path.normpath(filenpa_definition)

        if not os.path.exists(filenpa_definition):
            msg.error("arguments definition path not found '{}'.".format(filenpa_definition), prefix=prefix, pretty=pretty, exit=1)
        if not os.path.isfile(filenpa_definition):
            msg.error("arguments definition path is not a file '{}'".format(filenpa_definition), prefix=prefix, pretty=pretty, exit=1)

        filen=os.path.basename(definition)
        filer, ext=os.path.splitext(filen)

        authorized_exts=[".json", ".yaml", ".yml"]
        if ext not in authorized_exts:
            msg.error("arguments definition file extension '{}' must be in {}".format(ext, authorized_exts), prefix=prefix, pretty=pretty, exit=1)

        if ext == ".json":
            with open(filenpa_definition, "r") as f:
                try:
                    dy_definition=json.load(f)
                except BaseException:
                    print(traceback.format_exc())
                    msg.error("JSON syntax error in arguments definition file '{}'.".format(filenpa_definition), prefix=prefix, pretty=pretty)
                    sys.exit(1)
        elif ext in [".yaml", ".yml"]:
            with open(filenpa_definition, "r") as f:
                try:
                    import yaml
                except:
                    msg.error(r"""
                        YAML module not found to import arguments definition file.
                        Do either:
                        - pip install pyyaml.
                        - use a JSON file for arguments definition.
                        - use a python dict for arguments definition.
                    """, heredoc=True, prefix=prefix, pretty=pretty, exit=1)
                try:
                    dy_definition=yaml.safe_load(f)
                except BaseException as e:
                    print(traceback.format_exc())
                    msg.error("YAML syntax error in definition file '{}'".format(filenpa_definition), prefix=prefix, pretty=pretty)
                    sys.exit(1)

        if dy_definition is None:
            dy_definition=dict()
        elif not isinstance(dy_definition, dict):
            msg.error("arguments definition must return a dict not a '{}'".format(type(dy_definition)), prefix=prefix, pretty=pretty, exit=2)

    else:
        msg.error("arguments definition must be either a YAML file, a JSON file, or a python dict not a '{}'.".format(type(definition)), prefix=prefix, pretty=pretty, exit=1)

    return dy_definition
