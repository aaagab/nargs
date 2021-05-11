#!/usr/bin/env python3
from pprint import pprint
from datetime import datetime
import json
import os 
import sys

def open_ul_html(style, text):
    if style.output == "html":
        text.append("\t\t\t<ul>")

def close_ul_html(style, text):
    if style.output == "html":
        text.append("\t\t\t</ul>")

def append_li_html(style, text):
    if style.output == "html":
        previous=text[-1]
        del text[-1]
        text.append("\t\t\t\t<li>{}</li>".format(previous))

def get_nargs_metadata():
    filenpa_metadata=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "gpm.json")
    dy=None
    with open(filenpa_metadata, "r") as f:
        dy=json.load(f)
    return dy

def get_nargs_syntax(style, modes, print_modes=True):
    lsbracket=style.get_text(style.get_symbol("["), "square_brackets")
    rsbracket=style.get_text(style.get_symbol("]"), "square_brackets")
    lt=style.get_symbol("<")
    gt=style.get_symbol(">")

    plus=style.get_text(style.get_plus_symbol(), "nargs_syntax_emphasize")
    minus=style.get_text("-", "nargs_syntax_emphasize")
    dul="__"
    dur="__"
    if style.output == "asciidoc":
        dul="+__"
        dur="__+"
    elif style.output == "markdown":
        dul="\_\_"
        dur="\_\_"
        # plus=style.get_text("\+", "nargs_syntax_emphasize")
        # minus=style.get_text("-", "nargs_syntax_emphasize")

    text=[]
    if style.output == "html":
        text.append("\t\t<div id=\"nargs-sheet\">")

    text.append(style.get_text("NARGS ARGUMENTS SYNTAX", "headers"))

    text.append("{}".format(style.get_text("About Nargs", "nargs_syntax_headers")))
    open_ul_html(style, text)
    dy_nargs=get_nargs_metadata()
    text.append("{} {}".format(style.get_text("Name:", "nargs_syntax_emphasize"), dy_nargs["Name".lower()].title()))
    append_li_html(style, text)
    text.append("{} {}".format(style.get_text("UUID4:", "nargs_syntax_emphasize"), dy_nargs["UUID4".lower()]))
    append_li_html(style, text)
    text.append("{} {}".format(style.get_text("Version:", "nargs_syntax_emphasize"), dy_nargs["Version".lower()]))
    append_li_html(style, text)
    text.append("{} {}".format(style.get_text("Date:", "nargs_syntax_emphasize"), datetime.fromtimestamp(dy_nargs["timestamp"]).strftime('%m/%d/%Y %H:%M:%S')))
    append_li_html(style, text)
    text.append("{} {}".format(style.get_text("Authors:", "nargs_syntax_emphasize"), ", ".join(dy_nargs["Authors".lower()])))
    append_li_html(style, text)
    text.append("{} {}".format(style.get_text("Licenses:", "nargs_syntax_emphasize"), ", ".join(dy_nargs["Licenses".lower()])))
    append_li_html(style, text)
    text.append("{} {}".format(style.get_text("Description:", "nargs_syntax_emphasize"), dy_nargs["Description".lower()]))
    append_li_html(style, text)
    close_ul_html(style, text)

    has_yaml_module=True
    try:
        import yaml
    except:
        has_yaml_module=False
    modes["yaml_syntax"]=has_yaml_module

    if print_modes is True:
        text.append("\n{}".format(style.get_text("Nargs Modes State", "nargs_syntax_headers")))
        open_ul_html(style, text)

        for mode in sorted(modes):
            state="enabled"
            value=modes[mode]
            if value in [None, False]:
                state="disabled"

            text.append("{}{}: '{}'".format(
                style.get_list_bullet(),
                mode,
                style.get_text(state, "nargs_syntax_emphasize"), 
            ))
            append_li_html(style, text)

        close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Nargs Modes Explained", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for mode in sorted(modes):
        description=None
        value=modes[mode]
        if mode == "cached_dfn":
            description="When 'enabled' arguments definition is cached to enable faster arguments parsing."
        elif mode == "usage_on_root":
            description="When 'enabled' Nargs throws usage when only root argument is provided."
        elif mode == "explicit":
            description="When 'enabled' argument navigation needs to be explicit only."
        elif mode == "substitute":
            description="When 'enabled' string in the command-line with syntax {}name{} are substituted with same 'name' environment variable if any.".format(dul, dur)
        elif mode == "yaml_syntax":
            description="When 'enabled' means PyYAML is installed and yaml can be provided for arguments values types {} and {}.".format(
                style.get_text(".json", "nargs_syntax_emphasize"),
                style.get_text("json", "nargs_syntax_emphasize"),
            )

        text.append("{}{} {}".format(
            style.get_list_bullet(),
            style.get_text(mode+":", "nargs_syntax_emphasize"),
            description,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Aliases Types", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "{} i.e. {}. They may accept value(s).".format(style.get_text("long aliases", "nargs_syntax_emphasize"), style.get_text("--argument", "aliases_text")),
        "{} i.e. {}. They may accept value(s) and may be concatenated.".format(style.get_text("short aliases", "nargs_syntax_emphasize"), style.get_text("-a", "aliases_text")),
        "{} i.e. {}. Each char represents one short alias argument. Values can't be provided with this notation. All arguments must have the same parent.".format(style.get_text("concatenated aliases", "nargs_syntax_emphasize"), style.get_text("-abcd", "aliases_text")),
        "{} i.e. {}. They may accept value(s).".format(style.get_text("dashless aliases", "nargs_syntax_emphasize"), style.get_text("argument", "aliases_text")),
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Aliases State", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}required: {}".format(
        style.get_list_bullet(),
        style.get_text("-m, --mount", "aliases_text")
    ))
    append_li_html(style, text)
    text.append("{}optional: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("-m, --mount", "aliases_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}available nested arguments: {} {}{}{} or {} {}".format(
        style.get_list_bullet(),
        style.get_text(chr(187), "nargs_syntax_emphasize"),
        lsbracket,
        style.get_text("-m, --mount", "aliases_text"),
        rsbracket,
        style.get_text(chr(187), "nargs_syntax_emphasize"),
        style.get_text("-m, --mount", "aliases_text")

    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Arguments Navigation", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_str in [
        "Implicit navigation uses only aliases and values.",
        "Explicit navigation uses command-line symbols {} and {}.".format(plus, minus),
        "Explicit navigation searches for aliases only in children arguments.",
        "Implicit navigation searches first aliases in children arguments and if not found it searches aliases in parent arguments until root argument is reached.",
        "Command-line symbols {} and {} help to explicitly navigate arguments' tree.".format(plus, minus),
        "Explicit navigation with command-line symbols {} and {} may be omitted.".format(plus, minus),
        "Command-line {} symbol may be concatenated {} or used with a multiplier {}.".format(
            plus,
            style.get_text(style.get_plus_symbol()*3,"nargs_syntax_emphasize"),
            style.get_text("{}3".format(style.get_plus_symbol()),"nargs_syntax_emphasize"),
        ),
        "Explicit navigation is needed to select one alias that is both in parent and children arguments.",
        "Explicit navigation allows faster arguments parsing.",
        "Alias is needed after explicit navigation.",
        "i.e.(implicit): {} prog --help --export html --to file.html.".format(style.get_text(chr(187), "examples_bullet"), plus, minus),
        "i.e.(explicit): {} prog {} --help {} --export html {} --to file.html.".format(style.get_text(chr(187), "examples_bullet"), minus, minus, plus),
    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_str,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Values", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}required: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{}".format(lt, gt), "values_text")))
    append_li_html(style, text)
    text.append("{}optional: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{}".format(lt, gt), "values_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}default: {} or {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} (=default_value)".format(lt, gt), "values_text"),
        style.get_text("{}int:VALUE{} (=1, 3, 4, 5)".format(lt, gt), "values_text"),
    ))
    append_li_html(style, text)
    text.append("{}preset: {}".format(
        style.get_list_bullet(),
        style.get_text("{str:value1, value2, value3}", "values_text")))
    append_li_html(style, text)
    text.append("{}preset return values: {}".format(
        style.get_list_bullet(),
        style.get_text("{str:value1 (1), value2 (2), value3 (3)}", "values_text")))
    append_li_html(style, text)
    text.append("{}label: {} i.e. {}".format(
        style.get_list_bullet(),
        style.get_text("{}type:label{}".format(lt, gt), "values_text"),
        style.get_text("{}str:PATH{}".format(lt, gt), "values_text"),
    ))
    append_li_html(style, text)
    text.append("{}standard types: {}, {}, {}, and {}".format(
        style.get_list_bullet(),
        style.get_text("str", "values_text"),
        style.get_text("bool", "values_text"),
        style.get_text("int", "values_text"),
        style.get_text("float", "values_text"),
    ))
    append_li_html(style, text)
    text.append("{}Boolean argument's value(s) can be either case-insensitive string {}, case-insensitive string {}, {}, or {} where {} is False and {} is True. i.e. {}".format(
        style.get_list_bullet(),
        style.get_text("true", "values_text"),
        style.get_text("false", "values_text"),
        style.get_text("0", "values_text"),
        style.get_text("1", "values_text"),
        style.get_text("0", "values_text"),
        style.get_text("1", "values_text"),
        style.get_text("prog.py true True 1 0 False falsE", "values_text"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Special Values Types", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for type_str in [
        "dir:existing directory.",
        "file:existing file.",
        "path:existing directory or file.",
        "vpath:existing or non-existing directory or file.",
        "json:JSON/YAML string.",
        ".json:.json/.yaml/.yml file or JSON/YAML string.",
    ]:
        _type, type_text=type_str.split(":")
        text.append("{}{}: {}".format(
            style.get_list_bullet(),
            style.get_text(_type, "values_text"),
            type_text,
        ))
        append_li_html(style, text)

    for tmp_text in [
        "Relative paths are resolved in types dir, file, path, vpath, and .json.",
        "JSON strings can be single quoted.",
    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_text,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Aliases Equals Values Notation", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "{}, {}, and {} arguments accept equals values notation.".format(
            style.get_text("long aliases", "nargs_syntax_emphasize"),
            style.get_text("short aliases", "nargs_syntax_emphasize"),
            style.get_text("dashless aliases", "nargs_syntax_emphasize"),
        ),
        "i.e. {}='{}'".format(
            style.get_text("--argument", "aliases_text"),
            style.get_text("value1, value2, \"this is value3\"", "values_text"),
        ),
        "i.e. {}=\"{}\"".format(
            style.get_text("--argument", "aliases_text"),
            style.get_text("value1, value2, 'this is value3'", "values_text"),
        ),
        "i.e. {}=\"{}\"".format(
            style.get_text("-a", "aliases_text"),
            style.get_text("value1, value2, 'this is value3'", "values_text"),
        ),
         "i.e. {}=\"{}\"".format(
            style.get_text("argument", "aliases_text"),
            style.get_text("value1, value2, 'this is value3'", "values_text"),
        ),
        "This values notation is mainly use when a value is mistaken for an alias and end-user wants to explicitly add it as a value.",
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Number of Values", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}required 1 value: {} ".format(
        style.get_list_bullet(),
        style.get_text("{}str{}".format(lt, gt), "values_text")))
    append_li_html(style, text)
    text.append("{}optional 1 value: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{}".format(lt, gt), "values_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required int value: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} 5".format(lt, gt), "values_text")))
    append_li_html(style, text)
    text.append("{}optional int value: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{} 3".format(lt, gt), "values_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required min int to max int: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} 2..3".format(lt, gt), "values_text")))
    append_li_html(style, text)
    text.append("{}optional min int to max int: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{} 4..5".format(lt, gt), "values_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required min 1 to max infinite: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} ...".format(lt, gt), "values_text")))
    append_li_html(style, text)
    text.append("{}optional min 1 to max infinite: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{} ...".format(lt, gt), "values_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required min int to max infinite: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} 7...".format(lt, gt), "values_text"),
    ))
    append_li_html(style, text)
    text.append("{}optional min int to max infinite: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{} 8...".format(lt, gt), "values_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required min 1 to int: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} ...3".format(lt, gt), "values_text"),
    ))
    append_li_html(style, text)
    text.append("{}optional min 1 to int: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{} ...2".format(lt, gt), "values_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Repeated Argument", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}({})ppend values: {}".format(
        style.get_list_bullet(),
        style.get_text("a", "nargs_syntax_emphasize"),
        style.get_text("-m, --mount :a", "aliases_text"),
    ))
    append_li_html(style, text)
    text.append("{}({})reate new argument fork: {}".format(
        style.get_list_bullet(),
        style.get_text("c", "nargs_syntax_emphasize"),
        style.get_text("-m, --mount :c", "aliases_text"),
    ))
    append_li_html(style, text)
    text.append("{}({})xit if repeated: {}".format(
        style.get_list_bullet(),
        style.get_text("e", "nargs_syntax_emphasize"),
        style.get_text("-m, --mount :e", "aliases_text"),
    ))
    append_li_html(style, text)
    text.append("{}({})eplace previous argument and reset children (implicit): {}".format(
        style.get_list_bullet(),
        style.get_text("r", "nargs_syntax_emphasize"),
        style.get_text("-m, --mount", "aliases_text"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Examples", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}{}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("-m, --mount :e", "aliases_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}{} {}".format(
        style.get_list_bullet(),
        style.get_text("-m, --mount", "aliases_text"),
        style.get_text("{}str:PATH{} 1... (=mycustompath)".format(lt, gt), "values_text"),
    ))
    append_li_html(style, text)
    text.append("{}{}{} {}{}{} {}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("-m, --mount", "aliases_text"),
        lsbracket,
        style.get_text("{}str:PATH{} ...5 (=mycustompath)".format(lt, gt), "values_text"),
        rsbracket,
        style.get_text(":a", "aliases_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}{} {}".format(
        style.get_list_bullet(),
        style.get_text("-m, --mount", "aliases_text"),
        style.get_text("{}str:{{option1, option2, option3}}{} 2 (=option2)".format(lt, gt), "values_text"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Either Arguments", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "Either Arguments belong to one or multiple either groups.",
        "Either groups are noted with a vertical bar and an index.",
        "i.e. one group {}".format(style.get_text("-m, --mount |1", "aliases_text")),
        "i.e. two groups {}".format(style.get_text("-m, --mount |1|2", "aliases_text")),
        "Each either group argument can't be selected on the command-line if another argument from the same either group is present already.",
        "Either exclusion scope is per arguments siblings' level.",

    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_text
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Single Arguments", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "Single Arguments are singleton at their siblings' level.",
        "Any other arguments at the same siblings' level throw an error.",
        "Single arguments are noted with a dot.",
        "i.e. {}".format(style.get_text("-m, --mount \u2022", "aliases_text")),
        "i.e. {}{}{}".format(
            lsbracket,
            style.get_text("-m, --mount \u2022", "aliases_text"),
            rsbracket,
        ),
    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_text
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Special Commands", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}Special commands are related to current command-line argument.".format(
        style.get_list_bullet(),
    ))
    append_li_html(style, text)
    text.append("{}Special commands start with either '{}' for usage or '{}' for path.".format(
        style.get_list_bullet(),
        style.get_text(":", "nargs_syntax_emphasize"),
        style.get_text("@", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}Both '{}' and '{}' can be used at the same time.".format(
        style.get_list_bullet(),
        style.get_text(":", "nargs_syntax_emphasize"),
        style.get_text("@", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}'{}' and '{}' can be repeated three times each for verbosity.".format(
        style.get_list_bullet(),
        style.get_text(":", "nargs_syntax_emphasize"),
        style.get_text("@", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}'{}': Print argument's usage, and first nested arguments.".format(
        style.get_list_bullet(),
        style.get_text(":", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}'{}': Print argument's usage, nested arguments and sub-nested arguments.".format(
        style.get_list_bullet(),
        style.get_text("::", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}'{}': Print argument's usage, and all nested arguments.".format(
        style.get_list_bullet(),
        style.get_text(":::", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}'{}': Print argument's path.".format(
        style.get_list_bullet(),
        style.get_text("@", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}'{}': Print argument's path with values.".format(
        style.get_list_bullet(),
        style.get_text("@@", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}'{}': Print argument's path with values and explicit notation.".format(
        style.get_list_bullet(),
        style.get_text("@@@", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}Parameters can be added: '{}' for examples, '{}' for hint, '{}' for info.".format(
        style.get_list_bullet(),
        style.get_text("e", "nargs_syntax_emphasize"),
        style.get_text("h", "nargs_syntax_emphasize"),
        style.get_text("i", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}Examples: '{}', '{}', '{}', '{}', '{}'".format(
        style.get_list_bullet(),
        style.get_text("@:ehi", "nargs_syntax_emphasize"),
        style.get_text("::@h", "nargs_syntax_emphasize"),
        style.get_text("@@@:eh", "nargs_syntax_emphasize"),
        style.get_text(":::@@@he", "nargs_syntax_emphasize"),
        style.get_text(":i", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    if style.output == "html":
        text.append("\t\t</div>")

    return text
