#!/usr/bin/env python3
from pprint import pprint
from datetime import datetime
import json
import os 
import sys

def get_joined_list(lst):
    tmp_list=[]
    for value in lst:
        # if len(value.split()) > 1 or "," in value:
            # tmp_list.append(repr(value))
        # else:
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

def get_nargs_syntax(style, user_options, print_options=True):
    lsbracket=style.get_text(style.get_symbol("["), "square_brackets")
    rsbracket=style.get_text(style.get_symbol("]"), "square_brackets")
    lt=style.get_symbol("<")
    gt=style.get_symbol(">")

    plus=style.get_plus_symbol()
    caret=style.get_caret_symbol()
    minus=style.get_text("-", "nargs_syntax_emphasize")
    equal=style.get_text("=", "nargs_syntax_emphasize")

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
    user_options["yaml_syntax"]=has_yaml_module

    if print_options is True:
        text.append("\n{}".format(style.get_text("Nargs Options State", "nargs_syntax_headers")))
        open_ul_html(style, text)

        for option in sorted(user_options):
            state="enabled"
            value=user_options[option]
            if value in [None, False]:
                state="disabled"

            text.append("{}{}: {}".format(
                style.get_list_bullet(),
                option,
                style.get_text(state, "nargs_syntax_emphasize"), 
            ))
            append_li_html(style, text)

        close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Nargs Options Explained", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for option in sorted(user_options):
        description=None
        value=user_options[option]
        if option == "pretty_help":
            description="When 'enabled' Nargs usage, and help are themed."
        elif option == "pretty_msg":
            description="When 'enabled' Nargs system messages are themed."
        elif option == "substitute":
            description="When 'enabled' strings on the command line with syntax {dul}input{dur}, {dul}hidden{dur}, {dul}input:label{dur}, {dul}hidden:label{dur} trigger user prompt and strings are substituted with user input. Label must start with a letter and can only have letters or numbers. If only labels are provided then strings are substituted with values of matching environment variable names if any. i.e. {dul}input{dur}, {dul}input:username{dur}, {dul}USER{dur}, {dul}Session1{dur} .".format(
                dul=dul,
                dur=dur,
            )
        elif option == "yaml_syntax":
            description="When 'enabled' means PyYAML is installed and yaml can be provided for arguments values types {} and {}.".format(
                style.get_text(".json", "nargs_syntax_emphasize"),
                style.get_text("json", "nargs_syntax_emphasize"),
            )

        text.append("{}{} {}".format(
            style.get_list_bullet(),
            style.get_text(option+":", "nargs_syntax_emphasize"),
            description,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("User Option Files", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "The following Nargs options can be modified with a user file: {}, {}, {}, {}.".format(
            style.get_text("pretty_help", "nargs_syntax_emphasize"),
            style.get_text("pretty_msg", "nargs_syntax_emphasize"),
            style.get_text("substitute", "nargs_syntax_emphasize"),
            style.get_text("theme", "nargs_syntax_emphasize"),
        ),
        "A '{}' or '{}' user file can be placed in either the application executable directory or the application configuration path as set by path_etc argument if any i.e. --path-etc.".format(
            style.get_text(".nargs-user.json", "nargs_syntax_emphasize"),
            style.get_text(".nargs-user.yaml", "nargs_syntax_emphasize"),
        ),
        "If both '{}' and '{}' are present then only '{}' is selected.".format(
            style.get_text(".nargs-user.json", "nargs_syntax_emphasize"),
            style.get_text(".nargs-user.yaml", "nargs_syntax_emphasize"),
            style.get_text(".nargs-user.yaml", "nargs_syntax_emphasize"),
        ),
        "If user option file is located at executable directory then user options overload matching program's options. If user option file is also located at application configuration then options overload any previously set matching options.",
        "{}, {}, and {} are boolean options. {} is a dictionary. In order to set {}'s keys and values, please read Nargs developer's documentation at section 'get_default_theme'.".format(
            style.get_text("pretty_help", "nargs_syntax_emphasize"),
            style.get_text("pretty_msg", "nargs_syntax_emphasize"),
            style.get_text("substitute", "nargs_syntax_emphasize"),
            style.get_text("theme", "nargs_syntax_emphasize"),
            style.get_text("theme", "nargs_syntax_emphasize"),
        ),
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Aliases Types", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "Arguments' aliases can have any prefixes from list {}. i.e. {}, {}, {}, {}, {}, {}, and {}.".format(
            style.get_text("['', '+', '-', '--', '/', ':', '_']", "nargs_syntax_emphasize"),
            style.get_text("arg", "nargs_syntax_emphasize"),
            style.get_text("+arg", "nargs_syntax_emphasize"),
            style.get_text("-arg", "nargs_syntax_emphasize"),
            style.get_text("--arg", "nargs_syntax_emphasize"),
            style.get_text("/arg", "nargs_syntax_emphasize"),
            style.get_text(":arg", "nargs_syntax_emphasize"),
            style.get_text("_arg", "nargs_syntax_emphasize"),
        ),
        "Arguments' aliases accept index notation and may accept value(s).",
        "Each argument has a default alias. Default alias notation is only shown for required arguments that have at least two aliases. Default alias notation surrounds alias with single-quotes i.e.: {}. Single quotes are not part of the alias. ".format(
            style.get_text("-a, '--arg'", "nargs_syntax_emphasize")
        ),
        "One char only aliases may be selected as flags. i.e. {}, {}, {}, {}, {}, {}, and {}.".format(
            style.get_text("a", "nargs_syntax_emphasize"),
            style.get_text("+a", "nargs_syntax_emphasize"),
            style.get_text("-a", "nargs_syntax_emphasize"),
            style.get_text("--a", "nargs_syntax_emphasize"),
            style.get_text("/a", "nargs_syntax_emphasize"),
            style.get_text(":a", "nargs_syntax_emphasize"),
            style.get_text("_a", "nargs_syntax_emphasize"),
        ),
        "A flag is an argument with at least a one char alias that is selected according to rules defined in Nargs developer's documentation at section 'Concatenated Flags Aliases'.",
        "A flags set is a group of flag related to a particular argument. Each argument may have a different flags set. Some arguments may not have a flags set depending on arguments definition.",
        "A flags set start with 'at symbol' and contains at least one char. i.e. {} where 'c' is cmd, 'h' is 'help', 'u' is 'usage' and 'v' is 'version'.".format(
            style.get_text("@chuv", "nargs_syntax_emphasize"),
        ),
        "A flag may be repeated in a flags set depending on argument's definition. Flags order does not matter.",
        "Only the latest flag of a flags set may accept a value and may have index notation.",
        "A flag does not accept explicit notation. A flags set does accept explicit notation.",
        "Flags set information details is only available through 'usage' argument.",
        "To see what flags set is available for an argument, user can type: '{}' or '{}' for information on each flag.".format(
            style.get_text("prog.py --arg --usage", "nargs_syntax_emphasize"),
            style.get_text("prog.py --arg --usage --flags", "nargs_syntax_emphasize"),
        ),
        "Only the the current argument's flags set information is available at a time.",
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Aliases States", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}Required: {}".format(
        style.get_list_bullet(),
        style.get_text("-m, '--mount'", "aliases_text")
    ))
    append_li_html(style, text)
    text.append("{}Optional: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("-m, --mount", "aliases_text"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}Asterisk symbol means that nested arguments are available: {} {}{}{} or {} {}".format(
        style.get_list_bullet(),
        style.get_text("*", "nargs_syntax_emphasize"),
        lsbracket,
        style.get_text("-m, --mount", "aliases_text"),
        rsbracket,
        style.get_text("*", "nargs_syntax_emphasize"),
        style.get_text("-m, '--mount'", "aliases_text")

    ))
    append_li_html(style, text)

    for tmp_text in [
        "When a required argument is omitted and argument accepts either no value(s), optional value(s), or required value(s) with default value(s) set then required argument is added implicitly and the selected alias set is the default alias.",
        "When a required argument with required value(s) is omitted and argument has not default value(s) set then an error is thrown.",
        "Omitted required argument process is repeated recursively on implicitly added argument's required children.",
        "An optional argument may still be required in-code by developer. Nargs only represents a small subset of arguments' logical rules.",
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Repeated Argument's options", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}({})ppend values: {}".format(
        style.get_list_bullet(),
        style.get_text("a", "nargs_syntax_emphasize"),
        style.get_text("-m, '--mount' &a", "aliases_text"),
    ))
    append_li_html(style, text)
    text.append("{}({})rror if repeated: {}".format(
        style.get_list_bullet(),
        style.get_text("e", "nargs_syntax_emphasize"),
        style.get_text("-m, '--mount' &e", "aliases_text"),
    ))
    append_li_html(style, text)
    text.append("{}({})ork new argument is created: {}".format(
        style.get_list_bullet(),
        style.get_text("f", "nargs_syntax_emphasize"),
        style.get_text("-m, '--mount' &f", "aliases_text"),
    ))    
    append_li_html(style, text)
    text.append("{}({})eplace previous argument and reset children (implicit): {}".format(
        style.get_list_bullet(),
        style.get_text("r", "nargs_syntax_emphasize"),
        style.get_text("-m, '--mount'", "aliases_text"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("XOR Group Notation", "nargs_syntax_headers")))
    open_ul_html(style, text)
    text.append("{}When argument has notation: {}".format(
        style.get_list_bullet(),
        style.get_text("-m, --mount {}1{}3".format(caret, caret), "aliases_text"),
    ))
    append_li_html(style, text)
    text.append("{}It means that argument is part of two '{}' groups: group 1 and group 3. An argument can belong to multiple XOR groups.".format(
        style.get_list_bullet(),
        style.get_text("exclusive either (XOR)", "nargs_syntax_emphasize"),
    ))
    append_li_html(style, text)
    text.append("{}XOR groups define siblings arguments' groups where any argument from a group can't be present at the same time on the command-line with any other siblings' arguments of the same group.".format(
        style.get_list_bullet(),
    ))
    append_li_html(style, text)
    text.append("{}i.e. sibling argument with notation '{}' can't be present at the same time with argument '{}'.".format(
        style.get_list_bullet(),
        style.get_text("-u, --unmount {}3".format(caret), "aliases_text"),
        style.get_text("-m, --mount {}1{}3".format(caret, caret), "aliases_text"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Arguments Tree Vocabulary", "nargs_syntax_headers")))
    open_ul_html(style, text)

    text.append("{}Arguments tree structure related to --self argument:".format(style.get_list_bullet()))
    append_li_html(style, text)
    
    space_width=2
    for tmp_str in [
        "{}{}".format(style.get_space(space_width*2), style.get_text("--root-arg", "aliases_text")),
        "{}{}".format(style.get_space(space_width*4), style.get_text("--ancestor", "aliases_text")),
        "{}{}".format(style.get_space(space_width*6), style.get_text("--grand-parent", "aliases_text")),
        "{}{}".format(style.get_space(space_width*8), style.get_text("--parent", "aliases_text")),
        "{}{}".format(style.get_space(space_width*10), style.get_text("--self", "nargs_syntax_emphasize")),
        "{}{}".format(style.get_space(space_width*12), style.get_text("--child", "aliases_text")),
        "{}{}".format(style.get_space(space_width*10), style.get_text("--sibling", "aliases_text")),
        "{}{}".format(style.get_space(space_width*8), style.get_text("--uncle", "aliases_text")),
        "{}{}".format(style.get_space(space_width*6), style.get_text("--grand-uncle", "aliases_text")),
        "{}{}".format(style.get_space(space_width*4), style.get_text("--ancestor-uncle", "aliases_text")),
    ]:
        text.append("{}".format(
            tmp_str,
        ))
        append_li_html(style, text)
    
    for tmp_str in [
        "{} is the current argument.".format(
            style.get_text("--self", "nargs_syntax_emphasize"),
        ),
        "All {}'s parents may be called ancestors. The oldest ancestor is the root argument.".format(
            style.get_text("--self", "nargs_syntax_emphasize"),
        ),
    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_str,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Arguments Navigation", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_str in [
        "Implicit navigation uses only aliases and values.",
        "Explicit navigation uses explicit notation with command-line symbols {}, {}, and {}.".format(
            style.get_text(plus, "nargs_syntax_emphasize"), 
            equal,
            minus
        ),
        "Explicit navigation searches for aliases only in children arguments.",
        "Explicit navigation can reaches any argument described in arguments tree vocabulary.",
        "Implicit navigation searches aliases in children' arguments, parents' arguments and parents' arguments' children.",
        "Command-line symbols {}, {}, and {} help to explicitly navigate arguments' tree.".format(
            style.get_text(plus, "nargs_syntax_emphasize"), 
            equal,
            minus
        ),
        "Explicit navigation with command-line symbols {}, {}, and {} may be omitted most of the time.".format(
            style.get_text(plus, "nargs_syntax_emphasize"), 
            equal,
            minus
        ),
        "Explicit navigation is required for an alias when selected alias is also present either in children's arguments, parents' arguments, or parents' children arguments.",
        "Command-line {} symbol may be concatenated {} or used with a multiplier {}.".format(
            style.get_text(plus, "nargs_syntax_emphasize"),
            style.get_text(plus*3,"nargs_syntax_emphasize"),
            style.get_text("{}3".format(plus),"nargs_syntax_emphasize"),
        ),
        "Explicit navigation allows faster arguments parsing.",
        "Argument's alias is always required after explicit notation.",
        "i.e.(implicit): {} 'prog --self --child --sibling --grand-parent --grand-uncle --ancestor-uncle'.".format(style.get_text(">", "examples_bullet"), style.get_text(plus, "nargs_syntax_emphasize"), minus),
        "i.e.(explicit): {} 'prog --self {} --child {} --sibling {} --grand-parent {} --grand-uncle {} --ancestor-uncle'.".format(
            style.get_text(">", "examples_bullet"),
            minus,
            style.get_text(plus, "nargs_syntax_emphasize"),
            style.get_text(plus*2, "nargs_syntax_emphasize"),
            equal,
            style.get_text(plus, "nargs_syntax_emphasize"),
        ),
        "'prog --self {} --child'.".format(minus),
        "'prog --self {} --sibling'.".format(equal),
        "'prog --self {} --parent'.".format(style.get_text(plus*1, "nargs_syntax_emphasize")),
        "'prog --self {} --uncle'.".format(style.get_text(plus*1, "nargs_syntax_emphasize")),
        "'prog --self {} --grand-parent'.".format(style.get_text(plus*2, "nargs_syntax_emphasize")),
        "'prog --self {} --grand-uncle'.".format(style.get_text(plus*2, "nargs_syntax_emphasize")),
        "'prog --self {} --ancestor'.".format(style.get_text(plus*3, "nargs_syntax_emphasize")),
        "'prog --self {} --ancestor-uncle'.".format(style.get_text(plus*3, "nargs_syntax_emphasize")),
        "'prog --self {} --root-arg'.".format(style.get_text(plus*4, "nargs_syntax_emphasize")),
        "'prog --self {} --root-arg'.".format(style.get_text(plus+"4", "nargs_syntax_emphasize")),
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
        "Argument with repeat option set to 'fork' allows to have an index greater than 1.",
        "Argument with repeat option set to either 'append', 'error', or 'replace' only allows to have the index equals to 1.",
        "Index notation examples: 'prog --help_1 --export_1' or 'prog --arg_1 --arg_2' or 'prog --arg_1 = --arg_2'.",
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
    text.append("{}Required value(s) are added implicitly when argument's default values are set and argument is either present or required.".format(
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
        ".json:.json/.yml/.yaml file or JSON/YAML string.",
    ]:
        _type, type_text=type_str.split(":")
        text.append("{}{}: {}".format(
            style.get_list_bullet(),
            style.get_text(_type, "values_text"),
            type_text,
        ))
        append_li_html(style, text)

    for tmp_text in [
        "Relative paths are resolved for types dir, file, path, vpath, and .json.",
        "JSON strings can be single quoted.",
    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_text,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Aliases Equal/Colon Values Notation", "nargs_syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "All arguments's aliases accept equal/colon values notation.",
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
        
        "i.e. {}:'{}'".format(
            style.get_text("--argument", "aliases_text"),
            style.get_text("value1 value2 \"this is value3\"", "values_text"),
        ),
        "i.e. {}:\"{}\"".format(
            style.get_text("--argument", "aliases_text"),
            style.get_text("value1 value2 'this is value3'", "values_text"),
        ),
        "i.e. {}:\"{}\"".format(
            style.get_text("-a", "aliases_text"),
            style.get_text("value1 value2 'this is value3'", "values_text"),
        ),
         "i.e. {}:\"{}\"".format(
            style.get_text("argument", "aliases_text"),
            style.get_text("value1 value2 'this is value3'", "values_text"),
        ),
           "i.e. {}:{}".format(
            style.get_text("argument", "aliases_text"),
            style.get_text("value1", "values_text"),
        ),
        "Values notation is useful to prevent values to be mistaken for aliases.",
        "Values notation allows faster command-line parsing.",
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
    text.append("{}required int value(s): {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} 5".format(lt, gt), "values_text")))
    append_li_html(style, text)
    text.append("{}optional int value(s): {}{}{}".format(
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
        style.get_text("-m, '--mount'", "aliases_text"),
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
        style.get_text("-m, '--mount'", "aliases_text"),
        style.get_text("{}str:{{option1,option2,option3}}{} 2 (=option1, option2)".format(lt, gt), "values_text"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    if style.output == "html":
        text.append("\t\t</div>")

    return text
