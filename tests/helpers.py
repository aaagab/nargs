#!/usr/bin/env python3
from pprint import pprint
import inspect
from inspect import currentframe, getframeinfo
import os
import sys
import time

from ..gpkgs import message as msg

class CatchEx():
    def __init__(self, ex):
        dy_err=dict(catched=False)
        self.ex=ex
        self.text=None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.text is None:
            direpa_script=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            frameinfo = getframeinfo(currentframe().f_back)
            filenpa=os.path.relpath(frameinfo.filename, direpa_script)
            text="At '{}' line '{}' text has not been set in CatchEx".format(filenpa, frameinfo.lineno)
            msg.error(text, trace=True, exit=1)

        if type is self.ex:
            if self.text in str(value):
                return True
            else:
                direpa_script=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                frameinfo = getframeinfo(currentframe().f_back)
                filenpa=os.path.relpath(frameinfo.filename, direpa_script)
                text="At '{}' line '{}' Error string not found in error message\nstring: {}\nmessage: {}".format(filenpa, frameinfo.lineno, self.text, str(value))
                msg.error(text, trace=True, exit=1)
        else:
            direpa_script=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            frameinfo = getframeinfo(currentframe().f_back)
            filenpa=os.path.relpath(frameinfo.filename, direpa_script)
            text="Uncaught Error at '{}' line '{}'".format(filenpa, frameinfo.lineno)
            msg.error(text, trace=True)
            if type is None:
                sys.exit(1)
            else:
                pass

def err():
    direpa_script=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    frameinfo = getframeinfo(currentframe().f_back)
    filenpa=os.path.relpath(frameinfo.filename, direpa_script)
    text="At '{}' line '{}' test failed.".format(filenpa, frameinfo.lineno)
    msg.error(text, trace=True, exit=1)

class Elapsed():
    def __init__(self):
        pass
        self._start=None

    def start(self):
        self._start=time.time()

    def show(self):
        return time.time()-self._start

def verify_tree(arg, cmd_line, is_root=True):
    if cmd_line is not None:
        print()
        print("# verify tree for: '{}'".format(cmd_line))

    print("{} -> {}\t{}".format((arg._dfn.level-1)*"    ", arg._name, arg))
    for attr in [
        "_",
        "_alias",
        "_aliases",
        "_args",
        "_branches",
        # "_cmd_line",
        "_cmd_line_index",
        "_count",
        "_default_alias",
        "_dy_indexes",
        "_here",
        "_implicit",
        "_is_root",
        "_name",
        "_dfn",
        "_parent",
        "_root",
        "_value",
        "_values",
    ]:
        if hasattr(arg, attr) is False:
            pprint(vars(arg))
            msg.error("attribute '{}' not found for arg ".format(attr, arg._name), exit=1, trace=True)

    if is_root is False:
        if arg._name == "narg":
            print("in verify:", arg)
        if arg._parent is None:
            msg.error("for arg '{}' parent is None.".format(arg._name), exit=1, trace=True)

    for child_name in sorted(arg._):
        child_arg=arg._[child_name]
        for branch in child_arg._branches.copy():
            verify_tree(
                branch,
                cmd_line=None,
                is_root=False,
            )
