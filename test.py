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

    import yaml

    filenpa_metadata=os.path.join(direpa_script, "gpm.json")
    dy_metadata=dict()
    with open(filenpa_metadata, "r") as f:
        dy_metadata=json.load(f)

    pkg.run_tests(dy_metadata)
    # pkg.single_test(dy_metadata)





    