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
    import yaml

    # args=yaml.safe_load("""
    #     _aliases: "--args,-a"
    #     connect:
    #         assemble:
    #             exchange:
    #         move:
    #         repair:
    #     computer:
    #         _fork: true
    #         _label: USER
    #         print:
    #             _hint: Only one document at a time can be printed
    #             _values: 1
    #         manage:
    #             _aliases: --power-off,--power-on,--sleep
    #     storage:
    #         _hint: access data through storage
    #         _xor: close,open,remove
    #         close:
    #         open:
    #         remove:
    # """)

    args=yaml.safe_load("""
        _aliases: "--args,r"
        _examples: "samples.py"
        output:
            _aliases: "--output,o"
            _examples: "samples.py --output html"
            _in: "asciidoc, html, markdown, text"
            _hint: "Export documentation in multiple formats."
            _info: "If values is not provided then documentation is exported in all formats. Files are exported into system temporary directory with filename 'output.[adoc|html|md|txt]'"
            _values: "?"
            only_syntax:
                _hint: "only help syntax is exported"
    """)

    nargs=pkg.Nargs(
        args=args,
        metadata=dict(
            executable="samples.py",
            name="Samples",
        ),
    )

    args=nargs.get_args()
    if args.output._here:
        values=args.output._values
        if len(values) == 0:
            values=args.output._dfn.dy["in"]

        exts=dict(
            asciidoc="adoc",
            html="html",
            markdown="md",
            text="txt",
        )
        direpa_tmp=os.path.join(tempfile.gettempdir(), "nargs")
        os.makedirs(direpa_tmp, exist_ok=True)

        for output in args.output._dfn.dy["in"]:
            if output in values:
                nargs.get_documentation(output, filenpa=os.path.join(direpa_tmp, "output."+exts[output]), overwrite=True, wsyntax=True, only_syntax=args.output.only_syntax._here)
