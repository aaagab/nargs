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

    # pprint(definition)
    # my_dump=json.loads('{"prog": {"long_alias": "--prog", "short_alias": "-p", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": "this is my program", "type": "str", "in": null, "label": null, "repeat": "replace", "required": true, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "args": {"arg_one": {"long_alias": "--arg-one", "short_alias": "-a", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "args": {"a": {"long_alias": "--a", "short_alias": "-a", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "args": {"b": {"long_alias": "--b", "short_alias": "-b", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "default_alias": "--b", "args": {"c": {"long_alias": "--c", "short_alias": "-c", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "default_alias": "--c", "args": {}}}}}}, "b": {"long_alias": "--b", "short_alias": "-b", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "requ ired": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "args": {"c": {"long_alias": "--c", "short_alias": "-c", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "default_alias": "--c", "args": {}}}}, "c": {"long_alias": "--c", "short_alias": "-c", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "args": {}}, "nested_arg": {"long_alias": "--nested-arg", "short_alias": "-n", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "args": {"nested_nested_arg": {"long_alias": "--nested-nested-arg", "short_alias": "-n", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "args": {}}}}, "arg_two": {"long_alias": "--arg-two", "short_alias": "-a", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "args": {"nested_arg": {"long_alias": "--nested-arg", "short_alias": "-n", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "default_alias": "--nested-arg", "args": {"nested_nested_arg": {"long_alias": "--nested-nested-arg", "short_alias": "-n", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "default_alias": "--nested-nested-arg", "args": {}}}}, "c": {"long_alias": "--c", "short_alias": "-c", "auto_aliases": true, "default": null, "enabled": true, "examples": [], "hint": null, "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": false, "default_alias": "--c", "args": {}}}}}}, "examples": {"long_alias": "--examples", "short_alias": null, "auto_aliases": false, "default": null, "enabled": true, "examples": [], "hint": "Print program examples.", "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": true, "args": {}}, "help": {"long_alias": "--help", "short_alias": "-h", "auto_aliases": false, "default": null, "enabled": true, "examples": [], "hint": "Print program help.", "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": true, "args": {}}, "uuid4": {"long_alias": "--uuid4", "short_alias": null, "auto_aliases": false, "default": null, "enabled": true, "examples": [], "hint": "Print program UUID4.", "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": true, "args": {}}, "usage": {"long_alias": "--usage", "short_alias": null, "auto_aliases": false, "default": null, "enabled": true, "examples": [], "hint": "Print program usage.", "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": true, "args": {}}, "version": {"long_alias": "--version", "short_alias": "-v", "auto_aliases": false, "default": null, "enabled": true, "examples": [], "hint": "Print program version.", "type": "str", "in": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "is_builtin": true, "args": {}}}}}')

    # mydump='{"prog": {"long_alias": "--prog", "short_alias": "-p", "auto_aliases": true, "enabled": true, "examples": ["prog.py --arg-one -a -b -c"], "hint": "this is my program", "info": null, "type": "str", "label": null, "repeat": "replace", "required": true, "show": true, "value_min": 2, "value_max": null, "value_required": true, "default": null, "in": null, "is_builtin": false, "args": {"arg_one": {"long_alias": "--arg-one", "short_alias": "-a", "auto_aliases": true, "enabled": true, "examples": null, "hint": null, "info": null, "type": "str", "label": "VALUE", "repeat": "append", "required": false, "show": true, "value_min": 3, "value_max": 4, "value_required": false, "default": ["1", "3", "4"], "in": null, "is_builtin": false, "args": {"a": {"long_alias": "--a", "short_alias": "-a", "auto_aliases": true, "enabled": true, "examples": null, "hint": null, "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": false, "args": {"b": {"long_alias": "--b", "short_alias": "-b", "auto_aliases": true, "enabled": true, "examples": null, "hint": null, "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": false, "default_alias": "--b", "args": {"c": {"long_alias": "--c", "short_alias": "-c", "auto_aliases": true, "enabled": true, "examples": null, "hint": null, "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": false, "default_alias": "--c", "args": {}}}}}}, "b": {"long_alias": "--b", "short_alias": "-b", "auto_aliases": true, "enabled": true, "examples": null, "hint": null, "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": false, "args": {"c": {"long_alias": "--c", "short_alias": "-c", "auto_aliases": true, "enabled": true, "examples": null, "hint": null, "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": false, "default_alias": "--c", "args": {}}}}, "c": {"long_alias": "--c", "short_alias": "-c", "auto_aliases": true, "enabled": true, "examples": null, "hint": null, "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": false, "args": {}}, "nested_arg": {"long_alias": "--nested-arg", "short_alias": "-n", "auto_aliases": true, "enabled": true, "examples": null, "hint": null, "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": false, "args": {"nested_nested_arg": {"long_alias": "--nested-nested-arg", "short_alias": "-n", "auto_aliases": true, "enabled": true, "examples": null, "hint": null, "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": false, "args": {}}}}}}, "examples": {"long_alias": "--examples", "short_alias": null, "auto_aliases": false, "enabled": true, "examples": null, "hint": "Print program examples.", "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": true, "args": {}}, "help": {"long_alias": "--help", "short_alias": "-h", "auto_aliases": false, "enabled": true, "examples": null, "hint": "Print program help.", "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": true, "args": {}}, "usage": {"long_alias": "--usage", "short_alias": null, "auto_aliases": false, "enabled": true, "examples": null, "hint": "Print program usage.", "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": true, "args": {}}, "uuid4": {"long_alias": "--uuid4", "short_alias": null, "auto_aliases": false, "enabled": true, "examples": null, "hint": "Print program UUID4.", "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": true, "args": {}}, "version": {"long_alias": "--version", "short_alias": "-v", "auto_aliases": false, "enabled": true, "examples": null, "hint": "Print program version.", "info": null, "type": null, "label": null, "repeat": "replace", "required": false, "show": true, "value_min": null, "value_max": null, "value_required": null, "default": null, "in": null, "is_builtin": true, "args": {}}}}}'

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

    definition="../test/config/options.json"
    definition="../test/config/small.json"
    definition="../test/config/small.yaml"
    # definition="../test/config/options.yaml"
    direpa_dump="../test/config"
    dump="../test/config/nargs-dump.json"
    # definition=dict()
    # definition="../test/config/options.yaml"
    narg=pkg.Nargs(
        # builtins=1,
        # builtins=None,
        # cached_dfn="../test/config/nargs-dump.json",
        # cached_dfn="../test/config/nargs-dump-test.pickle",
        options_file=definition,
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

    # print(narg.get_documentation(output="text", filenpa="../output/output.txt", wsyntax=True))
    # print(narg.get_documentation(output="html", filenpa="../output/output.html", wsyntax=True))
    # print(narg.get_documentation(output="markdown", filenpa="../output/output.md", wsyntax=True))
    # print(narg.get_documentation(output="asciidoc", filenpa="../output/output.adoc", wsyntax=True))
    narg._update_nargs_syntax()

    # narg.dump()
    # pprint(narg.dump())

    root_arg=narg.get_args()

    # print(root_arg.arg_one)

    # print(root_arg.arg_one.a.b.get_path())
    # print(root_arg.arg_one.b.get_path())
    # print(root_arg.arg_one.get_path(wvalues=True))
    # pprint(root_arg.arg_one._args)
    # print(root_arg)
    # if root_arg.tom._here:
    #     print("sdfsdf")

    # print(arg)
    
