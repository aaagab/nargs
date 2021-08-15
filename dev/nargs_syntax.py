#!/usr/bin/env python3
from pprint import pprint
from datetime import datetime
import json
import os 
import sys

def get_joined_list(lst):
    tmp_list=[]
    for value in lst:
        if len(value.split()) > 1 or "," in value:
            tmp_list.append(repr(value))
        else:
            tmp_list.append(value)
    return ", ".join(tmp_list)

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

    for key in sorted(dy_nargs):
        value=dy_nargs[key]
        if isinstance(value, list):
            value=get_joined_list(value)
        elif isinstance(value, dict):
            value=json.dumps(value, sort_keys=True)
        text.append("{} {}".format(style.get_text(key+":", "nargs_syntax_emphasize"), value))
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
        elif mode == "pretty":
            description="When 'enabled' Nargs messages, usage, and help are themed."
        elif mode == "usage_on_root":
            description="When 'enabled' Nargs throws usage when only root argument is provided."
        elif mode == "substitute":
            description="When 'enabled' strings on the command line with syntax {dul}input{dur}, {dul}hidden{dur}, {dul}input:label{dur}, {dul}hidden:label{dur} trigger user prompt and strings are substituted with user input. Label must start with a letter and can only have letters or numbers. If only labels are provided then strings are substituted with values of matching environment variable names if any. i.e. {dul}input{dur}, {dul}input:username{dur}, {dul}USER{dur}, {dul}Session1{dur} .".format(
                dul=dul,
                dur=dur,
            )
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
        "{} i.e. {}. Start with a colon, accept index notation and accept value(s).".format(style.get_text("built-in aliases", "nargs_syntax_emphasize"), style.get_text(":argument", "aliases_text")),
        "{} i.e. {}. Start with a dash, each char represents one short alias argument. They don't accept value(s) and they don't accept index notation. All arguments must have the same parent.".format(style.get_text("concatenated aliases", "nargs_syntax_emphasize"), style.get_text("-abcd", "aliases_text")),
        "{} i.e. {} . Each argument has a default alias. Default alias is the alias that ends with a dot when aliases are listed in help or usage. Dot symbol is not part of the alias. It is just to identify the default alias. Dot is not added for argument with only one alias.".format(style.get_text("default alias", "nargs_syntax_emphasize"), style.get_text("--info.", "aliases_text")),
        "{} i.e. {}. Start with a letter or a number, accept index notation and accept value(s).".format(style.get_text("dashless aliases", "nargs_syntax_emphasize"), style.get_text("argument", "aliases_text")),
        "{} i.e. {}. Start with double dashes, may have multiple chars, accept index notation and accept value(s).".format(style.get_text("long aliases", "nargs_syntax_emphasize"), style.get_text("--argument", "aliases_text")),
        "{} i.e. {}. Start with single dash, have only one char, accept index notation and accept value(s).".format(style.get_text("short aliases", "nargs_syntax_emphasize"), style.get_text("-a", "aliases_text")),
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Aliases State", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}required: {}".format(
        style.get_list_bullet(),
        style.get_text("-m, --mount.", "aliases_text")
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
        style.get_text("*", "nargs_syntax_emphasize"),
        lsbracket,
        style.get_text("-m, --mount", "aliases_text"),
        rsbracket,
        style.get_text("*", "nargs_syntax_emphasize"),
        style.get_text("-m, --mount.", "aliases_text")

    ))
    append_li_html(style, text)

    for tmp_text in [
        "When a required argument is omitted and argument accepts either no value(s), optional value(s), or required value(s) with default value(s) set then required argument is added implicitly and the selected alias set is the default alias.",
        "When a required argument with required value(s) is omitted and argument has not default value(s) set then an error is thrown.",
        "Omitted required argument process is repeated recursively on implicitly added argument's required children.",
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Repeated Argument's option", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}({})ppend values: {}".format(
        style.get_list_bullet(),
        style.get_text("a", "nargs_syntax_emphasize"),
        style.get_text("-m, --mount. &a", "aliases_text"),
    ))
    append_li_html(style, text)
    text.append("{}({})xit if repeated: {}".format(
        style.get_list_bullet(),
        style.get_text("e", "nargs_syntax_emphasize"),
        style.get_text("-m, --mount. &e", "aliases_text"),
    ))
    append_li_html(style, text)
    text.append("{}({})ork new argument is created: {}".format(
        style.get_list_bullet(),
        style.get_text("f", "nargs_syntax_emphasize"),
        style.get_text("-m, --mount. &f", "aliases_text"),
    ))    
    append_li_html(style, text)
    text.append("{}({})eplace previous argument and reset children (implicit): {}".format(
        style.get_list_bullet(),
        style.get_text("r", "nargs_syntax_emphasize"),
        style.get_text("-m, --mount.", "aliases_text"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Arguments Navigation", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_str in [
        "Implicit navigation uses only aliases and values.",
        "Explicit navigation uses explicit notation with command-line symbols {} and {}.".format(plus, minus),
        "Explicit navigation searches for aliases only in children arguments.",
        "Implicit navigation searches aliases in children' arguments, parents' arguments and parents' arguments' children.",
        "Command-line symbols {} and {} help to explicitly navigate arguments' tree.".format(plus, minus),
        "Explicit navigation with command-line symbols {} and {} may be omitted most of the time.".format(plus, minus),
        "Explicit navigation is required for an alias when selected alias is also present either in children's arguments, parents' arguments, or parents' children arguments.",
        "Command-line {} symbol may be concatenated {} or used with a multiplier {}.".format(
            plus,
            style.get_text(style.get_plus_symbol()*3,"nargs_syntax_emphasize"),
            style.get_text("{}3".format(style.get_plus_symbol()),"nargs_syntax_emphasize"),
        ),
        "Explicit navigation allows faster arguments parsing.",
        "Explicit notation only select an argument relative siblings level that is why an argument's alias is required after explicit notation.",
        "i.e.(implicit): {} prog :help --export html --to file.html.".format(style.get_text(">", "examples_bullet"), plus, minus),
        "i.e.(explicit): {} prog {} :help {} --export html {} --to file.html.".format(style.get_text(">", "examples_bullet"), minus, minus, plus),
        "Explicit navigation allows end-user to go back and forth to selected arguments in order to add values or nested arguments.",
    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_str,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Arguments Index Notation", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_str in [
        "Argument's index notation allows selecting a specific argument's occurence.",
        "Index notation consists in adding to argument's alias an underscore and an index number starting at one.",
        "Index notation's index is the argument occurence number.",
        "Argument with repeat option set to 'fork' allows to have an index greater than 1",
        "Argument with repeat option set to either 'append', 'exit', or 'replace' only allows to have the index equals to 1.",
        "Index notation examples: prog :help_1 --export_1 or prog --arg_1 + --arg_2",
        "Explicit notation and index notation allows to select accurately an argument's occurence in the arguments tree.",
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
        style.get_text("{str:1, 2, 3}", "values_text")))
    append_li_html(style, text)
    text.append("{}preset with label: {}".format(
        style.get_list_bullet(),
        style.get_text("{str:1(value1),2(value2),3(value3)}", "values_text")))
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
    text.append("{} Required value(s) are added implicitly when argument's default values are set and argument is either present or required.".format(
        style.get_list_bullet(),
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
            style.get_text("value1 value2 \"this is value3\"", "values_text"),
        ),
        "i.e. {}=\"{}\"".format(
            style.get_text("--argument", "aliases_text"),
            style.get_text("value1 value2 'this is value3'", "values_text"),
        ),
        "i.e. {}=\"{}\"".format(
            style.get_text("-a", "aliases_text"),
            style.get_text("value1 value2 'this is value3'", "values_text"),
        ),
         "i.e. {}=\"{}\"".format(
            style.get_text("argument", "aliases_text"),
            style.get_text("value1 value2 'this is value3'", "values_text"),
        ),
           "i.e. {}={}".format(
            style.get_text("argument", "aliases_text"),
            style.get_text("value1", "values_text"),
        ),
        "Values notation is useful to prevent values to be mistaken for aliases.",
        "Values notation also increases command-line parsing speed.",
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
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Help Syntax Examples", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}{}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("-m, --mount &e", "aliases_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}{} {}".format(
        style.get_list_bullet(),
        style.get_text("-m, --mount.", "aliases_text"),
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
        style.get_text("&a", "aliases_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}{} {}".format(
        style.get_list_bullet(),
        style.get_text("-m, --mount.", "aliases_text"),
        style.get_text("{}str:{{option1,option2,option3}}{} 2 (=option1, option2)".format(lt, gt), "values_text"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    if style.output == "html":
        text.append("\t\t</div>")

    return text
