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

    # def seed(pkg_major, direpas_configuration=dict(), fun_auto_migrate=None):
        # fun_auto_migrate()
    # etconf=pkg.Etconf(enable_dev_conf=False, tree=dict( files=dict({ "settings.json": dict() })), seed=seed)
    # args, dy_app=pkg.Options(
    #     direpa_configuration=etconf.direpa_configuration,
    #     examples=None, 
    #     filenpa_app="gpm.json", 
    #     filenpa_args="config/options.json"
    # ).get_argsns_dy_app()

    # args=dict(
    #     __main__=dict(
    #         arg_one=dict(
    #             nested_arg_one=dict(
    #                 nested_nested_arg_one=dict()
    #             )
    #         ),
    #         arg_two=dict(
    #             nested_arg_two=dict()
    #         ),
    #         _values=[]
    #     )
    # )

    # pprint(args)
    # from yaml import C
    import yaml
    # yaml_str="""
        # # marc:
    # """
    # definition=yaml.safe_load(yaml_str)

    # class Hello():
    #     def __init__(fself, state):
    #         self.state=state

    #     def __call__(self, otherstate):
    #         self.otherstate=otherstate
    #         print("in call")

    #     def __enter__(self):
    #         print("in enter")
    #         return self

    #     def __exit__(self, exc_type, exc_val, exc_tb):
    #         print("in exit")

    # # hello=
    # with Hello("marc") as hello:
    #     hello("tom")
    #     print(hello.state)
    #     print(hello.otherstate)
    #     pass

    # sys.exit()

    # # /home/gabaaa/fty/wrk/n/nargs/89d8676a6b0243fa8694e97de5680cd0/test
    # # /home/gabaaa/fty/wrk/n/nargs/89d8676a6b0243fa8694e97de5680cd0/test


    definition="../test/config/options.json"
    definition="../test/config/small.json"
    definition="../test/config/small.yaml"
    # definition="../test/config/options.yaml"
    direpa_dump="../test/config"
    # dump="../test/config/nargs-dump.json"
    # definition=dict()
    # definition="../test/config/options.yaml"
    narg=pkg.Nargs(
        # builtins=1,
        # builtins=None,
        # cached_dfn="../test/config/nargs-dump.json",
        # cached_dfn="../test/config/nargs-dump-test.pickle",
        options_file=definition,
        auto_alias_prefix="--",
        # path_etc="../test",
        # definition=my_dump,
        # cached=True,
        # metadata=dict(executable="dummy"),
        # pretty=True,
        # prompt=True,
        # substitute=True,
        # theme=dict(aliases_text=dict(foreground="178;24;124")),
        # theme=dict(aliases_text=dict(foreground="c62b2b")),
    )
    # print(narg.dump())
    # print(narg.dump(direpa=direpa_dump))
    # sys.exit()
    # narg.get(
    #     # cmd="prog.py __DISPLAY__ __OLDPWD__marc",
    #     # substitute=True,
    # )
    # sys.exit()

    # print(narg.get_documentation(output="text", filenpa="../output/output.txt", wsyntax=True, overwrite=True))
    # print(narg.get_documentation(output="html", filenpa="../output/output.html", wsyntax=True, overwrite=True))
    # print(narg.get_documentation(output="markdown", filenpa="../output/output.md", wsyntax=True, overwrite=True))
    # print(narg.get_documentation(output="asciidoc", filenpa="../output/output.adoc", wsyntax=True, overwrite=True))
    narg._update_nargs_syntax()
    root_arg=narg.get_args()

    # print()
    # print(root_arg.arg_one._here)
    # print("root_arg._args:", root_arg._args)
    # for arg in root_arg._args:
    #     print(arg._name)

    # cmd_line=root_arg._branches[0]._cmd_line
    # print(root_arg._["arg_one"])

    # for arg in root_arg._args:
    #     print()
    #     print("address:", arg)
    #     print("branch_num:", arg._branches.index(arg)+1)
    #     print("count:", arg._count)
    #     print("argument paths:")
    #     for index in sorted(arg._dy_indexes["aliases"]):
    #         print(cmd_line[:index])
    #     print("values paths:")
    #     for index in arg._dy_indexes["values"]:
    #         print(cmd_line[:index])

    #     print("values:", arg._values)

    # print("######################")
    # print(root_arg._["arg_one"])
    # print(root_arg._["arg_one"]._branches)
    # # sys.exit()
    # for arg in root_arg._["arg_one"]._branches:
    #     print()
    #     print("branch_num:", arg._branches.index(arg)+1)
    #     print("count:", arg._count)
    #     print("argument paths:")
    #     for index in sorted(arg._dy_indexes["aliases"]):
    #         print(cmd_line[:index])
    #     print("values paths:")
    #     for index in arg._dy_indexes["values"]:
    #         print(cmd_line[:index])

    #     print("values:", arg._values)


    # print(root_arg.arg_one.arg_two.snarg_two._here)

    
