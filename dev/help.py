#!/usr/bin/env python3
from copy import deepcopy
from datetime import datetime
from pprint import pprint
from subprocess import list2cmdline

import json
import os
import re
import shlex 
import shutil
import sys

from .get_types import get_type_str
from .nargs_syntax import get_nargs_syntax, get_joined_list
from .regexes import get_regex_dfn, get_regex_hints
from .style import Style

def get_values_notation(style, _in, in_labels, _type, default, label, values_min, values_max, values_required, values_authorized):
    if values_authorized is False:
        return None
    else:
        lt=style.get_symbol("<")
        gt=style.get_symbol(">")

        if _in is not None:
            value="{{{}:".format(get_type_str(_type))
            if len(in_labels) == 0:
                value+=", ".join(map(str, _in))
            else:
                tmp_values=[]
                for i, v in enumerate(_in):
                    tmp_values.append("{}({})".format(v, in_labels[i]))
                value+=", ".join(tmp_values)
            value+="}"
        elif label is not None:
            value="{}{}:{}{}".format(lt, get_type_str(_type), label, gt)
        else:
            value="{}{}{}".format(lt, get_type_str(_type), gt)

        if values_min == values_max:
            if values_min > 1:
                value+=" {}".format(values_min)
        elif values_max is None:
            value+=" "
            if values_min > 1:
                value+=str(values_min)
            value+="..."
        else:
            if values_min > 1:
                value+=" {}..{}".format(values_min, values_max)
            else:
                value+=" ...{}".format(values_max)

        if default is not None:
            value+=" (="
            if isinstance(default, dict):
                value+=json.dumps(default)
            elif isinstance(default, list):
                tmp_list=[]
                for tmp in default:
                    if isinstance(tmp, dict):
                        tmp_list.append(json.dumps(tmp))
                    else:
                        tmp_list.append(tmp)
                value+=", ".join(map(str, tmp_list))
            else:
                value+=str(default)
            value+=")"

        value=style.get_text(value, "values")

        if values_required is False:
            value="{}{}{}".format(
                style.get_text(style.get_symbol("["), "brackets"),
                value,
                style.get_text(style.get_symbol("]"), "brackets"),
            )

        return value

def get_flags_notation(dy_flags):
    flags=[flag for flag, dy in dy_flags.items() if dy["node"].dy["show"] is True]
    notation="".join(sorted(sorted(flags, reverse=True), key=str.lower))
    if notation == "":
        return None
    else:
        return notation

def get_help_usage(
    dy_metadata,
    node_ref,
    output,
    style,
    about=[],
    columns=None,
    examples=[],
    help=[],
    index=None,
    keep_default_alias=False,
    node_dfn=None,
    usage=[],
    max_sibling_level=None,
    user_options=None,
    allflags=False,
    allproperties=None,
    properties=None,
    wproperties=False,
    wexamples=False,
    whint=False,
    winfo=False,
    wpath=False,
    wsyntax=False,
    top_node=True,
    only_syntax=False,
    top_flags=False,
    
):
    if only_syntax is False:
        prefix="Nargs at Usage"
        dy_help=dict()
        if node_dfn is None:
            about=[]
            examples=[]
            help=[]
            usage=[]

            node_dfn=node_ref

            if output in ["cmd_help", "cmd_usage"]:
                columns=shutil.get_terminal_size((80, 20)).columns

            if output in ["asciidoc", "cmd_help", "html", "markdown", "text"]:
                about=get_about(output, dy_metadata, style)

                text=style.get_text("USAGE", "headers")
                if output == "cmd_help":
                    print(text)
                else:
                    if output == "html":
                        usage.append("\t\t<div id=\"usage\">")
                    usage.append(text)
        
        if node_dfn is not None and node_dfn.dy["show"] is True:
            str_alias_value=""
            node_dfn_aliases=deepcopy(node_dfn.dy["aliases"])
            aliases=style.get_text(", ".join(node_dfn_aliases), "aliases")
            if node_dfn.is_root is True:
                root_flags_notation=""
                if (allflags is True and output == "cmd_usage") or output in ["asciidoc", "cmd_help", "html", "markdown", "text"] or top_flags is True:
                    root_flags_notation=get_flags_notation(node_dfn._implicit_flags)
                    if root_flags_notation is None:
                        root_flags_notation=""
                    else:
                        root_flags_notation=" {},".format(style.get_text("{}".format(root_flags_notation), "flags"))


                executable=style.escape(".", dy_metadata["executable"])
                str_alias_value+="{}{} {}".format(
                    style.get_text(executable+":", "aliases"),
                    root_flags_notation,
                    aliases,
                )
            else:
                str_alias_value+=aliases

            value_notation=get_values_notation(
                style,
                node_dfn.dy["in"],
                node_dfn.dy["in_labels"],
                node_dfn.dy["type"],
                node_dfn.dy["default"],
                node_dfn.dy["label"],
                node_dfn.dy["values_min"],
                node_dfn.dy["values_max"],
                node_dfn.dy["values_required"],
                node_dfn.dy["values_authorized"],
            )

            if value_notation is not None:
                str_alias_value+=" {}".format(value_notation)

            process_children=False
            if max_sibling_level is None:
                process_children=True
            else:
                if node_dfn.level - node_ref.level < max_sibling_level:
                    process_children=True

            lelem=""
            relem=""
            if node_dfn.dy["required"] is False:
                lsbracket=style.get_symbol("[")
                rsbracket=style.get_symbol("]")
                lelem=style.get_text(lsbracket, "brackets")
                relem=style.get_text(rsbracket, "brackets")

            if top_node is True:
                if lelem == " ":
                    lelem=""
                    relem=""

            str_alias_value="{}{}{}".format(
                lelem,
                str_alias_value, 
                relem,
            )

            if (allflags is True and output == "cmd_usage") or output in ["asciidoc", "cmd_help", "html", "markdown", "text"] or (top_node is True and top_flags is True):
                flags_notation=get_flags_notation(node_dfn.get_dy_flags())
                if flags_notation is not None:
                    str_alias_value+=" {}".format(
                        style.get_text("{}".format(flags_notation), "flags"),
                    )



            indent=None
            indent_size=node_dfn.level-node_ref.level
            if output in ["cmd_help", "cmd_usage", "html", "text"]:
                indent=style.get_space(2)*indent_size
            elif output in ["asciidoc", "markdown"]:
                indent=style.get_space(4)*indent_size

            if wpath is True:
                print("{}{}".format(indent, node_dfn.current_arg._get_path(wvalues=False, keep_default_alias=keep_default_alias)))

            add_expand_symbol=False
            if top_node is False:
                if len(node_dfn.nodes) > 0:
                    if process_children is False:
                        add_expand_symbol=True

            if output in ["asciidoc", "cmd_help", "markdown", "text"]:
                dy_help["aliases"]=str_alias_value
            elif output == "html":
                dy_help["aliases"]=style.get_text(str_alias_value, "aliases_and_values")

            usage_alias_value="{}{}".format(indent, str_alias_value)
            if add_expand_symbol is True:
                usage_alias_value="{}{}{}".format(
                    indent[1:],
                    style.get_text("*", "emphasize"),
                    str_alias_value,
                )

            if output in ["cmd_help", "cmd_usage"]:
                print(usage_alias_value)
            elif output in ["html", "text", "markdown", "asciidoc"]:
                usage.append(usage_alias_value)

            if whint is True:
                if node_dfn.dy["hint"] is not None:
                    if output == "cmd_help":
                        dy_help["hint"]=style.get_text(get_wrap_text(columns, node_dfn.dy["hint"], "    "), "hint")
                    elif output == "cmd_usage":
                        print(style.get_text(get_wrap_text(columns, node_dfn.dy["hint"], indent+"     "), "hint"))
                    elif output in ["html", "text", "markdown", "asciidoc"]:
                        dy_help["hint"]=style.get_text(node_dfn.dy["hint"], "hint")

            if wproperties is True:
                selected_properties=[]
                if output == "cmd_usage":
                    if len(properties) == 0:
                        selected_properties=allproperties
                    else:
                        selected_properties=properties
                else:
                    selected_properties=allproperties

                props=[]
                for prop in selected_properties:
                    props.append("{}={}".format(prop, node_dfn.dy[prop]))
                proptxt="properties: "+", ".join(props)

                if output == "cmd_help":
                    dy_help["properties"]=style.get_text(get_wrap_text(columns, proptxt, "    "), "properties")
                elif output == "cmd_usage":
                    print(style.get_text(get_wrap_text(columns, proptxt, indent+"     "), "properties"))
                elif output in ["html", "text", "markdown", "asciidoc"]:
                    dy_help["properties"]=style.get_text(proptxt, "properties")

            if winfo is True:
                if node_dfn.dy["info"] is not None:
                    if output == "cmd_help":
                        dy_help["info"]=style.get_text(get_wrap_text(columns, node_dfn.dy["info"], "    "), "info")
                    elif output == "cmd_usage":
                        print(style.get_text(get_wrap_text(columns, node_dfn.dy["info"], indent+"     "), "info"))
                    elif output in ["html", "text", "markdown", "asciidoc"]:
                        dy_help["info"]=style.get_text(node_dfn.dy["info"], "info")

            if output in ["cmd_help", "html", "text", "markdown", "asciidoc"]:
                if index is None:
                    index=""

                node_dfn_path=shlex.split(node_dfn.current_arg._get_path())
                del node_dfn_path[0]
                node_dfn_path.insert(0, dy_metadata["executable"])
                tmp_path=[]
                for t in node_dfn_path:
                    tmp_path.append(shlex.quote(t))
                node_dfn_path=" ".join(tmp_path)

                tmp_index=""
                if index != "":
                    if output in ["markdown", "asciidoc"]:
                        tmp_index="{} ".format(style.get_text(index+":", "arg_index"))
                    else:
                        tmp_index="{}: ".format(index)

                if output == "cmd_help":
                    dy_help["path"]="{}{}".format(tmp_index, style.get_text(get_wrap_text(columns, node_dfn_path, ""), "arg_path"))
                elif output in ["html", "text"]:
                    dy_help["path"]=style.get_text(tmp_index+style.get_text(node_dfn_path, "arg_path"), "arg_index")
                elif output in ["markdown", "asciidoc"]:
                    dy_help["path"]="{} {}".format(
                        tmp_index,
                        style.get_text(node_dfn_path, "arg_path"),
                    )

            if wexamples is True:
                if node_dfn.dy["examples"] is not None:
                    dy_help["examples"]=[]
                    for example in node_dfn.dy["examples"]:
                        tmp_text=style.get_text("{} {}".format(style.get_text(">", "bullets"), example), "examples")
                        if output == "cmd_usage":
                            print("{}   {}".format(indent, tmp_text))
                        elif output in ["cmd_help", "html", "text"]:
                            dy_help["examples"].append(tmp_text)
                            if output in ["cmd_help", "text"]:
                                examples.append(tmp_text)
                            elif output == "html":
                                examples.append("\t\t\t\t<li>{}</li>".format(example))
                        elif output == "asciidoc":
                            tmp_text=style.get_text(example, "examples")
                            dy_help["examples"].append(tmp_text)
                            examples.append(tmp_text)
                        elif output == "markdown":
                            tmp_text=style.get_text(example, "examples")
                            dy_help["examples"].append(tmp_text)
                            examples.append("{}`{}`".format(style.get_list_bullet(), example))
                        
            help.append(dy_help)

            if process_children is True:
                _explicit_aliases_sort=get_explicit_aliases_sort(node_dfn)
                index_counter=0
                for aliases_sort in sorted(_explicit_aliases_sort):
                    for tmp_node in _explicit_aliases_sort[aliases_sort]:
                        if tmp_node.dy["show"] is True:
                            index_counter+=1
                            tmp_index=None
                            if index == "":
                                tmp_index="{}".format(index_counter)
                            else:
                                tmp_index="{}.{}".format(index, index_counter)

                            get_help_usage(
                                dy_metadata=dy_metadata,
                                node_ref=node_ref,
                                output=output,
                                style=style,
                                about=about,
                                columns=columns,
                                examples=examples,
                                help=help,
                                index=tmp_index,
                                keep_default_alias=keep_default_alias,
                                node_dfn=tmp_node,
                                usage=usage,
                                max_sibling_level=max_sibling_level,
                                user_options=user_options,
                                allflags=allflags,
                                allproperties=allproperties,
                                properties=properties,
                                wproperties=wproperties,
                                wexamples=wexamples,
                                whint=whint,
                                winfo=winfo,
                                wpath=wpath,
                                wsyntax=wsyntax,
                                top_node=False,
                                only_syntax=only_syntax,
                                top_flags=top_flags,
                            )

    if node_ref == node_dfn or only_syntax is True:
        only_syntax_title="NARGS END-USER DOCUMENTATION"

        if output in ["asciidoc", "cmd_help", "html", "markdown", "text"]:
            if only_syntax is False:

                if output == "cmd_help":
                    print()
                elif output == "text":
                    usage.append("")
                elif output == "html":
                    usage.append("\t\t</div>")

                tmp_help=[]
                if output == "html":
                    tmp_help.append("\t\t<div id=\"help\">")


                text=style.get_text("HELP", "headers")
                if output == "cmd_help":
                    print(text)
                else:
                    tmp_help.append(text)

                if output == "html":
                    tmp_help.append("\t\t\t<dl>")
                
                for d, dy in enumerate(help):
                    for elem in ["path", "aliases", "hint", "properties", "info", "examples"]:
                        if elem in dy:
                            if elem == "path":
                                if output == "cmd_help":
                                    print(dy[elem])
                                elif output == "html":
                                    tmp_help.append("\t\t\t\t<dt>{}</dt>".format("{}".format(dy[elem])))
                                    tmp_help.append("\t\t\t\t<dd>")
                                elif output == "text":
                                    tmp_help.append(dy[elem])
                                elif output in ["markdown", "asciidoc"]:
                                    tmp_help.append(dy[elem])
                            elif elem == "aliases":
                                if output == "cmd_help":
                                    print("  {}".format(dy[elem]))
                                elif output == "html":
                                    tmp_help.append("\t\t\t\t\t"+dy[elem])
                                elif output == "text":
                                    tmp_help.append("  {}".format(dy[elem]))
                                elif output in ["asciidoc", "markdown"]:
                                    tmp_help.append("{}{}".format(style.get_space(4), dy[elem]))
                            elif elem == "hint":
                                if output == "cmd_help":
                                    print(dy[elem])
                                elif output == "html":
                                    tmp_help.append("\t\t\t\t\t"+dy[elem])
                                elif output == "text":
                                    tmp_help.append("    "+dy[elem])
                                elif output in ["asciidoc", "markdown"]:
                                    tmp_help.append("{}{}".format(style.get_space(8), dy[elem]))
                            elif elem == "properties":
                                if output == "cmd_help":
                                    print(dy[elem])
                                elif output == "html":
                                    tmp_help.append("\t\t\t\t\t"+dy[elem])
                                elif output == "text":
                                    tmp_help.append("    "+dy[elem])
                                elif output in ["asciidoc", "markdown"]:
                                    tmp_help.append("{}{}".format(style.get_space(8), dy[elem]))
                            elif elem == "info":
                                if output == "cmd_help":
                                    print(dy[elem])
                                elif output == "html":
                                    tmp_help.append("\t\t\t\t\t"+dy[elem])
                                elif output == "text":
                                    tmp_help.append("    "+dy[elem])
                                elif output in ["asciidoc", "markdown"]:
                                    tmp_help.append("{}{}".format(style.get_space(8), dy[elem]))
                            elif elem == "examples":
                                for ex in dy[elem]:
                                    if output == "cmd_help":
                                        print("    {}".format(ex))
                                    elif output == "html":
                                        tmp_help.append("\t\t\t\t\t"+ex)
                                    elif output == "text":
                                        tmp_help.append("    "+ex)
                                    elif output in ["asciidoc", "markdown"]:
                                        tmp_help.append("{}{}".format(style.get_space(8), ex))
                    if output == "html":
                        tmp_help.append("\t\t\t\t</dd>")

                    if d + 1 < len(help):
                        if output == "cmd_help":
                            print()
                        elif output == "text":
                            tmp_help.append("")
                        elif output in ["asciidoc", "html", "markdown"]:
                            tmp_help.append(style.get_newline())

                if output == "cmd_help":
                    pass
                elif output == "html":
                    tmp_help.append("\t\t\t</dl>")
                    tmp_help.append("\t\t</div>")
                elif output in ["text"]:
                    tmp_help.append("")

                if len(examples) > 0:
                    examples.insert(0, style.get_text("EXAMPLES", "headers"))
                    if output == "html":

                        examples.insert(0, "\t\t<div id=\"examples\">")
                        examples.insert(2, "\t\t\t<ul class=\"no-bullets\">")
                        examples.append("\t\t\t</ul>")
                        examples.append("\t\t</div>")
                else:
                    examples=[]

            if output == "cmd_help":
                if only_syntax is True:
                    pass
                else:
                    has_example=len(examples) > 0

                    if has_example is True or wsyntax is True:
                        print()

                    if has_example is True:
                        print("\n".join(examples))
                        print()

                if wsyntax is True:
                    print("\n".join(get_nargs_syntax(style, user_options)))
                    print()
                
                if only_syntax is False:
                    if has_example is False and wsyntax is False:
                        print()
            elif output == "text":
                about.insert(0, "")
                if only_syntax is True:
                    about.insert(0, only_syntax_title)
                else:
                    about.insert(0, get_title(dy_metadata))

                if node_dfn is not None:
                    about.extend(usage)
                    about.extend(tmp_help)
                    if len(examples) > 0:
                        about.extend(examples)
                        about.append("")
                if wsyntax is True:
                    about.extend(get_nargs_syntax(style, user_options))
                    about.append("")
                return "\n".join(about)
            else:
                sections=[]
                if node_dfn is None:
                    sections=[about]
                else:
                    sections=[about, usage, tmp_help, examples]

                if wsyntax is True:
                    sections.append(get_nargs_syntax(style, user_options))

                if output == "html":
                    text=""
                    text+="<!DOCTYPE html>\n"
                    text+="<html lang=\"en\">\n"
                    text+="<head>\n"
                    title=None
                    if only_syntax is True:
                        title=only_syntax_title
                    else:
                        title=get_title(dy_metadata)
                    text+="<title>{}</title>\n".format(title)
                    text+="<meta charset=\"utf-8\">\n"
                    text+="<style>\n"
                    text+=style.get_css()
                    text+="</style>\n"
                    text+="</head>\n"
                    text+="<body>\n"
                    text+="\t<div id=\"nargs-documentation\">\n"
                    text+="\t\t<h1>{}</h1>\n".format(title)

                    for section in sections:
                        for line in section:
                            tmp_line=None
                            if re.match(r"(?:\s+)?<(?:/)?(?:p|h1|h2|h3|div|dt|dd|dl|ul|li).*?>$", line):
                                tmp_line="{}\n".format(line)
                            else:
                                tmp_line="{}<br>\n".format(line)

                            if re.match(r"^(?:<p|<span|&nbsp;).*$", line):
                                tmp_line="\t\t\t{}".format(tmp_line)
                            text+=tmp_line
                        text+="\n"
                    text+="\t</div>\n"
                    text+="<br>\n"
                    text+="</body>\n"
                    text+="</html>\n"
                    return text
                elif output == "markdown":
                    return get_md_text(
                        sections=sections,
                        title=get_title(dy_metadata),
                    )
                elif output == "asciidoc":
                    text=""
                    text+=":asterisk: *\n"
                    text+=":caret: ^\n"
                    text+=":plus: +\n"
                    text+=":toc: +\n"
                    text+=":sectnums: +\n"
                    if only_syntax is True:
                        text+="= {}\n\n".format(only_syntax_title)
                    else:
                        text+="= {}\n\n".format(get_title(dy_metadata))

                    for section in sections:
                        for line in section:
                            if len(line) > 0:
                                reg_space=re.match(r"^\s+(.*)$", line)
                                if reg_space:
                                    line=reg_space.group(1)
                                if line[-1] == "\n" :
                                    text+="{}\n".format(line)
                                elif line[0] == "=":
                                    text+="\n{}\n\n".format(line)
                                elif line[-2:] == "::" or line[-2:] == " +":
                                    text+="{}\n".format(line)
                                else:
                                    text+="{} +\n".format(line)
                        text+="\n"
                    return text

def get_aliases_sort(node):
    aliases_sort=None
    if len(node.dy["aliases"]) > 0:
        tmp_aliases=[]
        dy_aliases=dict()
        default_tmp_alias=None
        for alias in node.dy["aliases"]:
                tmp_alias=re.sub(get_regex_dfn("alias_sort_regstr")["rule"], "", alias)
                if alias == node.dy["default_alias"]:
                    default_tmp_alias=tmp_alias

                if tmp_alias not in dy_aliases:
                    dy_aliases[tmp_alias]=[]
                dy_aliases[tmp_alias].append(alias)

        aliases_sort=[]
        for tmp_alias in sorted(sorted(dy_aliases, reverse=True), key=str.lower):
            aliases_sort.append(tmp_alias)
            dy_length=dict()
            for alias in sorted(dy_aliases[tmp_alias]):
                length=len(alias.replace(tmp_alias, ""))
                if length not in dy_length:
                    dy_length[length]=[]
                dy_length[length].append(alias)

            for l in sorted(dy_length):
                for alias in sorted(dy_length[l]):
                    tmp_aliases.append(alias)

        if len(tmp_aliases) > 1:
            tmp_aliases.remove(node.dy["default_alias"])
            tmp_aliases.insert(0, node.dy["default_alias"])
            aliases_sort.remove(default_tmp_alias)
            aliases_sort.insert(0, default_tmp_alias)

        node.dy["aliases"]=tmp_aliases
        aliases_sort=",".join(aliases_sort).lower()

    return aliases_sort

def get_explicit_aliases_sort(node_dfn):
    if node_dfn._explicit_aliases_sort is None:
        node_dfn._explicit_aliases_sort=dict()
        for node in node_dfn.nodes:
            aliases_sort=get_aliases_sort(node)
            if aliases_sort not in node_dfn._explicit_aliases_sort:
                node_dfn._explicit_aliases_sort[aliases_sort]=[]
            node_dfn._explicit_aliases_sort[aliases_sort].append(node)
    return node_dfn._explicit_aliases_sort

def get_md_text(sections, title):
    text=""
    text+="# {}\n".format(title)
    for section in sections:
        for line in section:
            if len(line) > 0:
                if line[0] == "#":
                    text+="{}\n".format(line)
                elif line[0] == ">" or line[-4:] == "<br>": 
                    text+=line
                else:
                    reg=re.match(r"^\s*-.+$", line)
                    if reg:
                        text+="{}\n".format(line)
                    else:
                        reg=re.match(r"^\n#+.+$", line)
                        if reg:
                            text+="{}\n".format(line)
                        else:
                            text+="{}<br>\n".format(line)
        text+="\n"
    return text

def get_title(dy_metadata):
    return dy_metadata["name"]

def get_wrap_text(columns, text, indent):
    screen_width=columns
    max_width=screen_width-len(indent)

    data=""
    start_index=0
    lines=[]
    for c, char in enumerate(text):
        data+=char
        if len(indent) > (screen_width/2):
            indent=" "*int(screen_width/3)
            max_width=screen_width-len(indent)
            if len(data) == max_width:
                lines.append(get_formatted_text(indent, data))
                data=""
        else:    
            if len(data) == max_width:
                if c < len(text)-1:
                    if text[c+1] == " ":
                        lines.append(get_formatted_text(indent, data))
                        data=""
                    else:
                        if " " in data:
                            index=data.rfind(" ")
                            remain=data[index+1:c+1]
                            data=data[:index]
                            lines.append(get_formatted_text(indent, data))
                            data=remain
                        else:
                            lines.append(get_formatted_text(indent, data))
                            data=""

    if data:
        lines.append(get_formatted_text(indent, data))

    return "\n".join(lines)

def get_formatted_text(indent, text):
    return "{}{}".format(indent, text.strip())

        
def get_about(output, dy_metadata, style):
    lines=[]
    if output == "html":
        lines.append("\t\t<div id=\"about\">")

    text=style.get_text("ABOUT", "headers")

    if output == "cmd_help":
        print(text)
    else:
        lines.append(text)
        
    for field in sorted(dy_metadata):
        text=""
        value=dy_metadata[field]

        if field in ["executable", "filen_main"]:
            value=style.escape(".", value)

        if isinstance(value, list):
            value=get_joined_list(value)
        elif isinstance(value, dict):
            value=json.dumps(value, sort_keys=True)
        text="{} {}".format(style.get_text(field+":", "about_fields"), value)
        if output == "cmd_help":
            print(text)
        else:
            lines.append(text)

    if output == "cmd_help":
        print()
    elif output == "html":
        lines.append("\t\t</div>")
    elif output == "text":
        lines.append("")

    return lines

