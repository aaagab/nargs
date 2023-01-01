#!/usr/bin/env python3
from pprint import pprint
from datetime import datetime
import json
import os 
import sys

def get_joined_list(lst):
    tmp_list=[]
    for value in lst:
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
    lsbracket=style.get_text(style.get_symbol("["), "brackets")
    rsbracket=style.get_text(style.get_symbol("]"), "brackets")
    lt=style.get_symbol("<")
    gt=style.get_symbol(">")

    asterisk=style.get_asterisk_symbol()
    plus=style.get_plus_symbol()
    caret=style.get_caret_symbol()
    minus="-"
    equal=style.get_text("=", "emphasize")

    dul="__"
    dur="__"
    if style.output == "asciidoc":
        dul="+__"
        dur="__+"
    elif style.output == "markdown":
        dul="\_\_"
        dur="\_\_"

    text=[]
    if style.output == "html":
        text.append("\t\t<div id=\"nargs-sheet\">")

    text.append(style.get_text("NARGS ARGUMENTS SYNTAX", "headers"))

    text.append("{}".format(style.get_text("About Nargs", "syntax_headers")))
    open_ul_html(style, text)
    dy_nargs=get_nargs_metadata()

    for key in sorted(dy_nargs):
        value=dy_nargs[key]
        if key in ["executable", "filen_main"]:
            value=style.escape(".", value)
        if isinstance(value, list):
            value=get_joined_list(value)
        elif isinstance(value, dict):
            value=json.dumps(value, sort_keys=True)
        text.append("{} {}".format(style.get_text(key+":", "emphasize"), value))
        append_li_html(style, text)

    close_ul_html(style, text)

    has_yaml_module=True
    try:
        import yaml
    except:
        has_yaml_module=False
    user_options["yaml_syntax"]=has_yaml_module

    if print_options is True:
        text.append("\n{}".format(style.get_text("Nargs Options State", "syntax_headers")))
        open_ul_html(style, text)

        for option in sorted(user_options):
            state="enabled"
            value=user_options[option]
            if value in [None, False]:
                state="disabled"

            text.append("{}{}: {}".format(
                style.get_list_bullet(),
                option,
                style.get_text(state, "emphasize"), 
            ))
            append_li_html(style, text)

        close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Nargs Options Explained", "syntax_headers")))
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
            description="When 'enabled' means PyYAML is installed and YAML can be provided for arguments values types {} and {}.".format(
                style.get_text(".json", "emphasize"),
                style.get_text("json", "emphasize"),
            )

        text.append("{}{} {}".format(
            style.get_list_bullet(),
            style.get_text(option+":", "emphasize"),
            description,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("User Option Files", "syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "The following Nargs options can be modified with a user file: {}, {}, {}, {}.".format(
            style.get_text("pretty_help", "emphasize"),
            style.get_text("pretty_msg", "emphasize"),
            style.get_text("substitute", "emphasize"),
            style.get_text("theme", "emphasize"),
        ),
        "A '{}' or '{}' user file can be placed in either the application executable directory or the application configuration path as set by path_etc argument if any i.e. --path-etc.".format(
            style.get_text(".nargs-user.json", "emphasize"),
            style.get_text(".nargs-user.yaml", "emphasize"),
        ),
        "If both '{}' and '{}' are present then only '{}' is selected.".format(
            style.get_text(".nargs-user.json", "emphasize"),
            style.get_text(".nargs-user.yaml", "emphasize"),
            style.get_text(".nargs-user.yaml", "emphasize"),
        ),
        "If user option file is located at executable directory then user options overload matching program's options. If user option file is also located at application configuration path then options overload any previously set matching options.",
        "{}, {}, and {} are Boolean options. {} is a dictionary. In order to set {}'s keys and values, please read Nargs developer's documentation at section 'get_default_theme'.".format(
            style.get_text("pretty_help", "emphasize"),
            style.get_text("pretty_msg", "emphasize"),
            style.get_text("substitute", "emphasize"),
            style.get_text("theme", "emphasize"),
            style.get_text("theme", "emphasize"),
        ),
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Aliases Types", "syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "Arguments' aliases can have any prefixes from list {}. i.e. {}.".format(
            style.get_text("['', '+', '-', '--', '/', ':', '_']", "emphasize"),
            style.get_text("arg, +arg, -arg, --arg, /arg, :arg, _arg", "emphasize"),
        ),
        "Arguments' aliases accept branch index notation and may accept value(s).",
        "Each argument has a default alias. Default alias is the first alias on the argument's aliases list as shown in help or in usage.",
        "One char only aliases may be selected as flags. i.e. {}.".format(
            style.get_text("a, +a, -a, --a, /a, :a, _a", "emphasize"),
        ),
        "A flag is an argument with at least a one char alias that is selected according to rules defined in Nargs developer's documentation at section 'Concatenated Flag Aliases'.",
        "In order to see available flag sets end-user can provide command-line '{}'".format(
            style.get_text("prog.py --usage --flags", "emphasize"),
        ),
        "A flag set is a group of flags related to a particular argument. Each argument may have a different flag set. Some arguments may not have a flag set depending on arguments definition.",
        "A flag set starts with a one char alias and its prefix if any and it contains at least another char. i.e. '{}' where '{}' is 'help', '{}' is 'usage' and '{}' is 'version'.".format(
            style.get_text("-huv", "flags"),
            style.get_text("h", "flags"),
            style.get_text("u", "flags"),
            style.get_text("v", "flags"),

        ),
        "Root argument aliases may start with a flag set. In that case this flag set is the one available on first command-line argument or when explicit notation reaches level 0.",
        "A flag may be repeated in a flag set depending on argument's definition. Flags order may not matter.",
        "Only the latest flag of a flag set may accept a value and may have branch index notation.",
        "'at symbol' may be repeated to nest multiple flag sets. i.e.: '{} {}' is the same as '{}'.".format(
            style.get_text("prog.py", "emphasize"),
            style.get_text("-uhip", "flags"),
            style.get_text("prog.py --usage --hint --info --path", "emphasize"),
        ),
        "A flag does not accept explicit notation. Explicit notation can only be applied to first flag of the set. Then all other flags are selected are part of the flags set of the previous flag.",
        "End-user can rely on usage argument to get flag information i.e.: '{} {}', or '{} {}', or '{} {}'.".format(
            style.get_text("prog.py", "emphasize"),
            style.get_text("-u?", "flags"),
            style.get_text("prog.py", "emphasize"),
            style.get_text("-uh?", "flags"),
            style.get_text("prog.py", "emphasize"),
            style.get_text("-uhiu", "flags"),
        ),
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Aliases States", "syntax_headers")))
    open_ul_html(style, text)
    text.append("{}Required: {}".format(
        style.get_list_bullet(),
        style.get_text("--mount, -m", "emphasize")
    ))
    append_li_html(style, text)
    text.append("{}Optional: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("--mount, -m", "emphasize"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}Asterisk symbol means that nested arguments are available: {} {}{}{} or {} {}".format(
        style.get_list_bullet(),
        style.get_text(asterisk, "emphasize"),
        lsbracket,
        style.get_text("--mount, -m", "aliases"),
        rsbracket,
        style.get_text(asterisk, "emphasize"),
        style.get_text("--mount, -m", "aliases")

    ))
    append_li_html(style, text)


    for tmp_text in [
        "When a required argument is omitted and argument accepts either no value(s), optional value(s), or required value(s) with default value(s) set then required argument is added implicitly and the selected alias set is the default alias.",
        "When a required argument with required value(s) is omitted and argument has not default value(s) set then an error is thrown.",
        "Omitted required argument process is repeated recursively and argument's required children may be added implicitly.",
        "An optional argument may still be required in-code by developer. Nargs only represents a small subset of arguments' logical rules.",
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Arguments Tree Vocabulary", "syntax_headers")))
    open_ul_html(style, text)

    text.append("{}Arguments tree structure related to --self argument:{}".format(style.get_list_bullet(), style.start_newline()))
    append_li_html(style, text)
    space_width=2
    for tmp_str in [
        "{}{}".format(style.get_space(space_width*2), style.get_text("--root", "aliases")),
        "{}{}".format(style.get_space(space_width*4), style.get_text("--ancestor", "aliases")),
        "{}{}".format(style.get_space(space_width*6), style.get_text("--gd-parent", "aliases")),
        "{}{}".format(style.get_space(space_width*8), style.get_text("--parent", "aliases")),
        "{}{}".format(style.get_space(space_width*10), style.get_text("--self", "emphasize")),
        "{}{}".format(style.get_space(space_width*12), style.get_text("--child", "aliases")),
        "{}{}".format(style.get_space(space_width*10), style.get_text("--sibling", "aliases")),
        "{}{}".format(style.get_space(space_width*8), style.get_text("--uncle", "aliases")),
        "{}{}".format(style.get_space(space_width*6), style.get_text("--gd-uncle", "aliases")),
        "{}{}".format(style.get_space(space_width*4), style.get_text("--ancestor-uncle", "aliases")),
    ]:
        text.append("{}".format(
            tmp_str,
        ))
        append_li_html(style, text)
    
    for tmp_str in [
        "{} is the current argument.".format(
            style.get_text("--self", "emphasize"),
        ),
        "All {}'s parents may be called ancestors. The oldest ancestor is the root argument.".format(
            style.get_text("--self", "emphasize"),
        ),
        "Arguments may be duplicated in multiple branches.",
        "Each argument's branch has its own subset of child arguments.",
        "Arguments may have multiple occurrences per branch.",
        "Arguments branches and occurrences described for command-line '{}':{}".format(
            style.get_text("--parent --self --child --self --child --self --child --sibling", "aliases"),
            style.start_newline(),
        ),
    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_str,
        ))
        append_li_html(style, text)

    for tmp_str in [
        "{}{}".format(style.get_space(space_width*2), style.get_text("--parent", "aliases")),
        "{}{}".format(style.get_space(space_width*4), style.get_text("--self (branch 1)", "emphasize")),
        "{}{}".format(style.get_space(space_width*6), style.get_text("--child (relates only to branch 1)", "aliases")),
        "{}{}".format(style.get_space(space_width*4), style.get_text("--self (branch 2)", "emphasize")),
        "{}{}".format(style.get_space(space_width*6), style.get_text("--child (relates only to branch 2)", "aliases")),
        "{}{}".format(style.get_space(space_width*4), style.get_text("--self (branch 3)", "emphasize")),
        "{}{}".format(style.get_space(space_width*6), style.get_text("--child (relates only to branch 3)", "aliases")),
        "{}{}".format(style.get_space(space_width*4), style.get_text("--sibling", "aliases")),
    ]:
        text.append("{}".format(
            tmp_str,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Arguments Navigation", "syntax_headers")))
    open_ul_html(style, text)
    for tmp_str in [
        "Implicit navigation uses only aliases and values.",
        "Explicit navigation uses explicit notation with command-line symbols {}, {}, and {}.".format(
            style.get_text(minus, "emphasize"), 
            equal,
            style.get_text(plus, "emphasize"), 
        ),
        "Explicit navigation searches for aliases only in children arguments.",
        "Explicit navigation can reach any argument described in arguments tree vocabulary.",
        "Implicit navigation searches aliases in children' arguments, parents' arguments and parents' children.",
        "Command-line symbols {}, {}, and {} help to explicitly navigate arguments' tree.".format(
            style.get_text(minus, "emphasize"),
            equal,
            style.get_text(plus, "emphasize"), 
        ),
        "Explicit navigation with command-line symbols {}, {}, and {} may be omitted most of the time.".format(
            style.get_text(minus, "emphasize"),
            equal,
            style.get_text(plus, "emphasize"), 
        ),
        "Explicit navigation is needed for an alias when selected alias is also present either in children's arguments, parents' arguments, or parents' children arguments and is not available implicit navigation.",
        "For similar aliases implicit notation will search first in the children and if not found it will stop at the younger ancestor child alias that matches.",
        "Explicit navigation can reach ancestors with {}, siblings with {}, and children with {}.".format(
            style.get_text(minus, "emphasize"),
            equal,
            style.get_text(plus, "emphasize"), 
        ),
        "Command-line {} symbol may be concatenated {} or used with a multiplier {}.".format(
            style.get_text(minus, "emphasize"),
            style.get_text(minus*3,"emphasize"),
            style.get_text("{}3".format(minus),"emphasize"),
        ),
        "Explicit navigation allows faster arguments parsing.",
        "Argument's alias or flag set is always required after explicit notation.",
        "i.e.(implicit): {} '{}'.".format(
            style.get_text(">", "bullets"),
            style.get_text("prog --ancestor --gd-parent --parent --self --child --sibling --gd-parent --gd-uncle --ancestor-uncle", "aliases"),
        ),
        "i.e.(explicit): {} '{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}'.".format(
            style.get_text(">", "bullets"),
            style.get_text("prog", "aliases"),
            style.get_text(plus, "emphasize"), 
            style.get_text("--ancestor", "aliases"),
            style.get_text(plus, "emphasize"), 
            style.get_text("--gd-parent", "aliases"),
            style.get_text(plus, "emphasize"), 
            style.get_text("--parent", "aliases"),
            style.get_text(plus, "emphasize"), 
            style.get_text("--self", "aliases"),
            style.get_text(plus, "emphasize"), 
            style.get_text("--child", "aliases"),
            style.get_text(minus, "emphasize"),
            style.get_text("--sibling", "aliases"),
            style.get_text(minus*2, "emphasize"),
            style.get_text("--gd-parent", "aliases"),
            equal,
            style.get_text("--gd-uncle", "aliases"),
            style.get_text(minus, "emphasize"),
            style.get_text("--ancestor-uncle", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            style.get_text(plus, "emphasize"),
            style.get_text("--child", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            equal,
            style.get_text("--sibling", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            style.get_text(minus*1, "emphasize"),
            style.get_text("--parent", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            style.get_text(minus*1, "emphasize"),
            style.get_text("--uncle", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            style.get_text(minus*2, "emphasize"),
            style.get_text("--gd-parent", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            style.get_text(minus*2, "emphasize"),
            style.get_text("--gd-uncle", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            style.get_text(minus*3, "emphasize"),
            style.get_text("--ancestor", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            style.get_text(minus*3, "emphasize"),
            style.get_text("--ancestor-uncle", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            style.get_text(minus*4, "emphasize"),
            style.get_text("--root", "aliases"),
        ),
        "'{} {} {}'.".format(
            style.get_text("prog --ancestor --gd-parent --parent --self", "aliases"),
            style.get_text(minus+"4", "emphasize"),
            style.get_text("--root", "aliases"),
        ),
        "Explicit navigation allows end-user to go back and forth to selected arguments in order to add values or nested arguments.",
    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_str,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Arguments' Logical Properties", "syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "An argument logical properties can be shown with usage argument. i.e.: '{}'".format(
            style.get_text("prog.py --arg --usage --properties", "emphasize"),
        ),
        "'{}' property is a bool that describes if argument's parent may have fork(s) when argument is present.".format(
            style.get_text("allow_parent_fork", "emphasize"),
        ),
        "'{}' property is a bool that describes if argument's siblings may be present when argument is present.".format(
            style.get_text("allow_siblings", "emphasize"),
        ),
        "'{}' property is a bool that describes if at least one argument's child must be provided when argument is present.".format(
            style.get_text("need_child", "emphasize"),
        ),
        "'{}' property is a bool that defines if an argument is a preset argument. A preset argument is added implicitly if only its parent is present with no children.".format(
            style.get_text("preset", "emphasize"),
        ),
        "'{}' property is a string set with one option from '{}'. Property defines multiple argument's occurrences behavior.".format(
            style.get_text("repeat", "emphasize"),
            style.get_text("append, error, fork, replace", "emphasize"),
        ),
        "'{}' means multiple argument's occurrences are allowed and for each occurrence the same argument is kept but argument's '{}' internal property is incremented and new argument's values are appended to argument's values list.".format(
            style.get_text("repeat=append", "emphasize"),
            style.get_text("_count", "emphasize"),
        ),
        "'{}' means only one argument's occurrence is allowed otherwise Nargs throws an error.".format(
            style.get_text("repeat=error", "emphasize"),
        ),
        "'{}' means that argument's forks are allowed. To fork means to divide into two or more branches.".format(
            style.get_text("repeat=fork", "emphasize"),
        ),
        "'{}' means multiple argument's occurrences are allowed and for each occurrence a new argument is created, and the previous argument is replaced, and all the previous argument's children are removed. Argument's '{}' internal property is not incremented and new argument's values start a new argument's values list.".format(
            style.get_text("repeat=replace", "emphasize"),
            style.get_text("_count", "emphasize"),
        ),
        "'{}' property is a bool that describes if argument's must be present when argument's parent is present. '{}' property has also been described in 'Argument Aliases States'.".format(
            style.get_text("required", "emphasize"),
            style.get_text("required", "emphasize"),
        ),
        "'{}' property is a list of integers where each integer represents a group. Argument's siblings arguments with the same '{}' group can't be present at the same time on the command-line with any other argument from that group. It is the definition of '{}' which means '{}'. Siblings arguments have the same parent argument. Group scope is at the node level on argument's branch, it means that the same group name is not related if it is located on argument's parents or argument's children or if on same argument but on a different branch.".format(
            style.get_text("xor_groups", "emphasize"),
            style.get_text("xor", "emphasize"),
            style.get_text("xor", "emphasize"),
            style.get_text("exclusive or", "emphasize"),
        ),
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Values", "syntax_headers")))
    open_ul_html(style, text)
    text.append("{}required: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{}".format(lt, gt), "values")))
    append_li_html(style, text)
    text.append("{}optional: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{}".format(lt, gt), "values"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}default: {} or {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} (=default_value)".format(lt, gt), "values"),
        style.get_text("{}int{} (=1, 3, 4, 5)".format(lt, gt), "values"),
    ))
    append_li_html(style, text)
    text.append("{}preset: {}".format(
        style.get_list_bullet(),
        style.get_text("{str:1, 2, 3}", "values")))
    append_li_html(style, text)
    text.append("{}preset with label: {}".format(
        style.get_list_bullet(),
        style.get_text("{str:1(value1),2(value2),3(value3)}", "values")))
    append_li_html(style, text)
    text.append("{}label: {} i.e. {}".format(
        style.get_list_bullet(),
        style.get_text("{}type:label{}".format(lt, gt), "values"),
        style.get_text("{}str:PATH{}".format(lt, gt), "values"),
    ))
    append_li_html(style, text)
    text.append("{}standard types: {}, {}, {}, and {}".format(
        style.get_list_bullet(),
        style.get_text("str", "values"),
        style.get_text("bool", "values"),
        style.get_text("int", "values"),
        style.get_text("float", "values"),
    ))
    append_li_html(style, text)
    text.append("{}Boolean argument's value(s) can be either case-insensitive string {}, case-insensitive string {}, {}, or {} where {} is False and {} is True. i.e. {}".format(
        style.get_list_bullet(),
        style.get_text("true", "values"),
        style.get_text("false", "values"),
        style.get_text("0", "values"),
        style.get_text("1", "values"),
        style.get_text("0", "values"),
        style.get_text("1", "values"),
        style.get_text("prog.py true True 1 0 False falsE", "values"),
    ))
    append_li_html(style, text)
    text.append("{}Required value(s) are added implicitly when argument's default values are set, and argument is either present with no given values or required and added implicitly.".format(
        style.get_list_bullet(),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Special Values Types", "syntax_headers")))
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
            style.get_text(_type, "values"),
            type_text,
        ))
        append_li_html(style, text)

    for tmp_text in [
        "Relative paths are resolved according to terminal current path for types dir, file, path, vpath, and .json.",
        "JSON strings can be single quoted.",
    ]:
        text.append("{}{}".format(
            style.get_list_bullet(),
            tmp_text,
        ))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Aliases Equal/Colon Values Notation", "syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "All arguments' aliases accept equal/colon values notation. (Warning: external single quotes trigger error on Windows CMD terminal)",
        "i.e. {}{}".format(
            style.get_text("--argument", "aliases"),
            style.get_text("='value1 value2 \"this is value3\"'", "emphasize"),
        ),
        "i.e. {}{}".format(
            style.get_text("--argument", "aliases"),
            style.get_text("=\"value1 value2 'this is value3'\"", "emphasize"),
        ),
        "i.e. {}{}".format(
            style.get_text("-a", "aliases"),
            style.get_text("=\"value1 value2 'this is value3'\"", "emphasize"),
        ),
         "i.e. {}{}".format(
            style.get_text("argument", "aliases"),
            style.get_text("=\"value1 value2 'this is value3'\"", "emphasize"),
        ),
           "i.e. {}{}".format(
            style.get_text("argument", "aliases"),
            style.get_text("=value1", "emphasize"),
        ),
        
        "i.e. {}{}".format(
            style.get_text("--argument", "aliases"),
            style.get_text(":'value1 value2 \"this is value3\"'", "emphasize"),
        ),
        "i.e. {}{}".format(
            style.get_text("--argument", "aliases"),
            style.get_text(":\"value1 value2 'this is value3'\"", "emphasize"),
        ),
        "i.e. {}{}".format(
            style.get_text("-a", "aliases"),
            style.get_text(":\"value1 value2 'this is value3'\"", "emphasize"),
        ),
         "i.e. {}{}".format(
            style.get_text("argument", "aliases"),
            style.get_text(":\"value1 value2 'this is value3'\"", "emphasize"),
        ),
           "i.e. {}{}".format(
            style.get_text("argument", "aliases"),
            style.get_text(":value1", "emphasize"),
        ),
        "Values notation is useful to prevent values to be mistaken for aliases.",
        "Values notation allows faster command-line parsing.",
        "Last flag on a flag set can also accepts values i.e. {}".format(
            style.get_text("-chu:value", "emphasize"),
        )
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Number of Values", "syntax_headers")))
    open_ul_html(style, text)
    text.append("{}required 1 value: {} ".format(
        style.get_list_bullet(),
        style.get_text("{}str{}".format(lt, gt), "values")))
    append_li_html(style, text)
    text.append("{}optional 1 value: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{}".format(lt, gt), "values"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required int value(s): {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} 5".format(lt, gt), "values")))
    append_li_html(style, text)
    text.append("{}optional int value(s): {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{} 3".format(lt, gt), "values"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required min int to max int: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} 2..3".format(lt, gt), "values")))
    append_li_html(style, text)
    text.append("{}optional min int to max int: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{} 4..5".format(lt, gt), "values"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required min 1 to max infinite: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} ...".format(lt, gt), "values")))
    append_li_html(style, text)
    text.append("{}optional min 1 to max infinite: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{} ...".format(lt, gt), "values"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required min int to max infinite: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} 7...".format(lt, gt), "values"),
    ))
    append_li_html(style, text)
    text.append("{}optional min int to max infinite: {}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("{}str{} 8...".format(lt, gt), "values"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}required min 1 to int: {}".format(
        style.get_list_bullet(),
        style.get_text("{}str{} ...3".format(lt, gt), "values"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Argument Usage Full Syntax Examples", "syntax_headers")))
    open_ul_html(style, text)
    text.append("{}{}{}{}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("--mount, -m", "aliases"),
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}{} {}".format(
        style.get_list_bullet(),
        style.get_text("--mount, -m", "aliases"),
        style.get_text("{}str:PATH{} 1... (=mycustompath)".format(lt, gt), "values"),
    ))
    append_li_html(style, text)
    text.append("{}{}{} {}{}{} {}".format(
        style.get_list_bullet(),
        lsbracket,
        style.get_text("--mount, -m", "aliases"),
        lsbracket,
        style.get_text("{}str:PATH{} ...5 (=mycustompath)".format(lt, gt), "values"),
        rsbracket,
        rsbracket,
    ))
    append_li_html(style, text)
    text.append("{}{} {}".format(
        style.get_list_bullet(),
        style.get_text("--mount, -m", "aliases"),
        style.get_text("{}str:{{option1,option2,option3}}{} 2 (=option1, option2)".format(lt, gt), "values"),
    ))
    append_li_html(style, text)
    close_ul_html(style, text)

    text.append("\n{}".format(style.get_text("Arguments Syntax Pitfalls", "syntax_headers")))
    open_ul_html(style, text)
    for tmp_text in [
        "If an alias or flags notation is mistyped on the command-line, it may be use as a value if previous argument accept values.",
        "If a flags notation turns-out to be the same as a reachable alias, then the alias is going to be selected instead of the flags notation.",
        "If multiple same aliases are present and user uses implicit notation on the command-line, the argument selected may be different than what the argument expected.", 
        "Question mark alias '{}' from usage may be misinterpreted by Bash as wildcard operator. If that happens end-user may want to use any other aliases provided for usage argument.".format(
            style.get_text("?", "emphasize"),
        ),
        "For values notation on Windows CMD terminal emulator, command-line {} single quotes trigger shlex {}. Instead end-user must type {} or {}.".format(
            style.get_text("prog.py --arg='value value value'", "emphasize"),
            style.get_text("ValueError: No closing quotation", "emphasize"),
            style.get_text("prog.py --arg=\"value value value\"", "emphasize"),
            style.get_text("prog.py --arg=\"value1 value2 'value 3'\"", "emphasize"),
        ),
        "Note: Basic overview of Nargs arguments parsing sequence: 'explicit notation' else 'alias notation' else 'flags notation' else 'value' else 'unknown input'. If 'alias notation' then 'known alias' else 'flags notation' else 'value' else 'unknown input'. If 'flags notation' then flag set chars are tested as arguments (see Nargs /dev/get_args.py for detailed implementation).",
    ]:
        text.append("{}{}".format(style.get_list_bullet(), tmp_text))
        append_li_html(style, text)
    close_ul_html(style, text)

    if style.output == "html":
        text.append("\t\t</div>")

    return text
