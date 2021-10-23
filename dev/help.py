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
from .regexes import get_regex, get_regex_hints
from .style import Style

def get_values_notation(style, _in, _in_labels, _type, default, label, value_min, value_max, value_required):
    if value_required is None:
        return None
    else:
        lt=style.get_symbol("<")
        gt=style.get_symbol(">")

        if _in is not None:
            value="{{{}:".format(get_type_str(_type))
            if len(_in_labels)> 0:
                tmp_values=[]
                for i, v in enumerate(_in):
                    tmp_values.append("{}({})".format(v, _in_labels[i]))
                value+=", ".join(tmp_values)
            else:
                value+=", ".join(_in)
            value+="}"
        elif label is not None:
            value="{}{}:{}{}".format(lt, get_type_str(_type), label, gt)
        else:
            value="{}{}{}".format(lt, get_type_str(_type), gt)

        if value_min == value_max:
            if value_min > 1:
                value+=" {}".format(value_min)
        elif value_max is None:
            value+=" "
            if value_min > 1:
                value+=str(value_min)
            value+="..."
        else:
            if value_min > 1:
                value+=" {}..{}".format(value_min, value_max)
            else:
                value+=" ...{}".format(value_max)

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

        value=style.get_text(value, "values_text")

        if value_required is False:
            value="{}{}{}".format(
                style.get_text(style.get_symbol("["), "square_brackets"),
                value,
                style.get_text(style.get_symbol("]"), "square_brackets"),
            )

        return value

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
    
):

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
        # if len(node_dfn_aliases) > 1:
        #     if node_dfn.dy["required"] is True:
        #         index_default=node_dfn_aliases.index(node_dfn.dy["default_alias"])
        #         default_alias="'{}'".format(node_dfn.dy["default_alias"])
        #         node_dfn_aliases.insert(index_default, default_alias)
        #         node_dfn_aliases.remove(node_dfn.dy["default_alias"])
        aliases=style.get_text(", ".join(node_dfn_aliases), "aliases_text")
        if node_dfn.is_root is True:
            str_alias_value+="{} {}".format(
                style.get_text(dy_metadata["executable"]+":", "aliases_text"),
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
            node_dfn.dy["value_min"],
            node_dfn.dy["value_max"],
            node_dfn.dy["value_required"],
        )

        if value_notation is not None:
            str_alias_value+=" {}".format(value_notation)

        # tmp_txt=""
        # if node_dfn.dy["repeat"] != "replace":
        #     tmp_txt="&{}".format(node_dfn.dy["repeat"][0])

        # if node_dfn.dy["xor_notation"] is not None:
            # tmp_txt+=node_dfn.dy["xor_notation"].replace("^", style.get_caret_symbol())

        # if tmp_txt != "":
        #     str_alias_value+=" "+style.get_text(tmp_txt, "aliases_text")


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
            lelem=style.get_text(lsbracket, "square_brackets")
            relem=style.get_text(rsbracket, "square_brackets")

        if top_node is True:
            if lelem == " ":
                lelem=""
                relem=""

        str_alias_value="{}{}{}".format(
            lelem,
            str_alias_value, 
            relem,
        )

        if (top_node is True and output == "cmd_usage") or output in ["asciidoc", "cmd_help", "html", "markdown", "text"] or allflags is True:
            if node_dfn.dy["flags_notation"] is not None:
                str_alias_value+=" {}".format(
                    style.get_text("@{}".format(node_dfn.dy["flags_notation"]), "flags"),
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
        # usage_alias_value="{}".format(str_alias_value)
        if add_expand_symbol is True:
            usage_alias_value="{}{}{}".format(
                indent[1:],
                style.get_text("*", "nargs_syntax_emphasize"),
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
                dy_help["properties"]=get_wrap_text(columns, proptxt, "    ")
            elif output == "cmd_usage":
                print(get_wrap_text(columns, proptxt, indent+"     "))
            elif output in ["html", "text", "markdown", "asciidoc"]:
                dy_help["properties"]=proptxt

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
                # input(dy_help["path"])
                # dy_help["path"]="{}{}".format(style.get_text(tmp_index, "arg_index"), style.get_text(node_dfn_path, "arg_path"))

        if wexamples is True:
            if node_dfn.dy["examples"] is not None:
                dy_help["examples"]=[]
                for example in node_dfn.dy["examples"]:
                    tmp_text=style.get_text("{} {}".format(style.get_text(">", "examples_bullet"), example), "examples")
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
            explicit_aliases_sort=get_explicit_aliases_sort(node_dfn)
            index_counter=0
            for aliases_sort in sorted(explicit_aliases_sort):
                for tmp_node in explicit_aliases_sort[aliases_sort]:
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
                        )

    if node_ref == node_dfn:
        if output in ["asciidoc", "cmd_help", "html", "markdown", "text"]:
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
                # print()
                pass
            elif output == "html":
                tmp_help.append("\t\t\t</dl>")
                tmp_help.append("\t\t</div>")
            elif output in ["text"]:
                tmp_help.append("")

            if len(examples) > 0:
                examples.insert(0, style.get_text("EXAMPLES", "headers"))
                # examples.insert(0, "")
                if output == "html":

                    examples.insert(0, "\t\t<div id=\"examples\">")
                    examples.insert(2, "\t\t\t<ul class=\"no-bullets\">")
                    examples.append("\t\t\t</ul>")
                    examples.append("\t\t</div>")
            else:
                examples=[]

            if output == "cmd_help":
                has_example=len(examples) > 0

                if has_example is True or wsyntax is True:
                    print()

                if has_example is True:
                    print("\n".join(examples))
                    print()

                if wsyntax is True:
                    print("\n".join(get_nargs_syntax(style, user_options)))
                    print()
                
                if has_example is False and wsyntax is False:
                    print()
            elif output == "text":
                about.insert(0, "")
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
                    text+=":plus: +\n"
                    text+=":caret: ^\n"
                    text+=":toc: +\n"
                    text+=":sectnums: +\n"
                    text+="= {}\n\n".format(get_title(dy_metadata))
                    for section in sections:
                        for line in section:
                            # print(repr(line))
                            if len(line) > 0:
                                reg_space=re.match(r"^\s+(.*)$", line)
                                if reg_space:
                                    line=reg_space.group(1)
                                if line[-1] == "\n" :
                                    # or line[0] == "=" or line[0:2] == "\n="
                                    text+="{}\n".format(line)
                                elif line[0] == "=":
                                    text+="\n{}\n\n".format(line)
                                elif line[-2:] == "::" or line[-2:] == " +":
                                    text+="{}\n".format(line)
                                else:
                                    text+="{} +\n".format(line)
                        text+="\n"
                    return text

def get_explicit_aliases_sort(node_dfn):
    if node_dfn.explicit_aliases_sort is None:
        node_dfn.explicit_aliases_sort=dict()
        for node in node_dfn.nodes:
            aliases_sort=node.dy["aliases_sort"]
            if aliases_sort not in node_dfn.explicit_aliases_sort:
                node_dfn.explicit_aliases_sort[aliases_sort]=[]
            node_dfn.explicit_aliases_sort[aliases_sort].append(node)

    return node_dfn.explicit_aliases_sort

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

