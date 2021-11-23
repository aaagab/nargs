#!/usr/bin/env python3

if __name__ == "__main__":
    from pprint import pprint
    import importlib
    import json
    import os
    import sys
    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(direpa_script)
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    import tempfile

    filenpa_metadata=os.path.join(direpa_script, "gpm.json")
    dy_metadata=dict()
    with open(filenpa_metadata, "r") as f:
        dy_metadata=json.load(f)


    args=sys.argv[1:]

    manual="--manual" in args

    class Chk():
        def __init__(self):
            self.func=None

        def exc(self, func, *args):
            self.func=func
            func(*args)
            pkg.msg.success("passed '{}'".format(self.func.__name__))

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            pass


    direpa_tmp=os.path.join(tempfile.gettempdir(), "nargs")
    os.makedirs(direpa_tmp, exist_ok=True)
    filenpa_cache_json=os.path.join(direpa_tmp, "nargs-cache.json")
    filenpa_cache_pickle=os.path.join(direpa_tmp, "nargs-cache.pickle")

    with Chk() as chk:
        chk.exc(pkg.test_aliases, dy_metadata)
        chk.exc(pkg.test_get_json, dy_metadata)
        chk.exc(pkg.test_get_args, dy_metadata, filenpa_cache_json)
        chk.exc(pkg.test_get_node_dfn, dy_metadata)
        chk.exc(pkg.test_get_path, dy_metadata)
        chk.exc(pkg.test_nargs, dy_metadata, filenpa_cache_json, filenpa_cache_pickle)
        chk.exc(pkg.test_set_dfn, dy_metadata)
        chk.exc(pkg.test_set_options, dy_metadata)
        chk.exc(pkg.test_style, dy_metadata)
        chk.exc(pkg.test_implementation, dy_metadata, filenpa_cache_json, filenpa_cache_pickle, manual)
        # chk.exc(pkg.single_test, dy_metadata)

        # chk.exc(pkg.test_performance, dy_metadata, direpa_tmp, filenpa_cache_json)

    direpa_tests=os.path.join(os.path.dirname(os.path.realpath(__file__)), "tests")
    filenpa_tmp_cache=os.path.join(direpa_tests, "nargs-cache.json")
    filenpa_src_cache=os.path.join(os.path.dirname(direpa_tests), "nargs-cache.json")
    for filenpa in [
        filenpa_tmp_cache,
        filenpa_src_cache,
    ]:
        try:
            os.remove(filenpa)
        except:
            pass



    