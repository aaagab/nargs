#!/usr/bin/env python3

if __name__ == "__main__":
    import importlib
    import os
    import sys
    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(direpa_script)
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    # def seed(pkg_major, direpas_configuration=dict(), fun_auto_migrate=None):
        # fun_auto_migrate()
    # etconf=pkg.Etconf(enable_dev_conf=False, tree=dict( files=dict({ "settings.json": dict() })), seed=seed)
    # args, dy_app=pkg.Options(
    #     direpa_configuration=etconf.direpa_configuration,
    #     examples=None, 
    #     filenpa_app="gpm.json", 
    #     filenpa_args="config/options.json"
    # ).get_argsns_dy_app()
