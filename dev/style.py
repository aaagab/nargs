#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
import platform
import os 
import sys
import re

from .regexes import get_regex_dfn, get_regex_hints

from ..gpkgs import message as msg

class Style():
    def __init__(self,
        pretty_help=False,
        output=None,
        theme=None,
    ):
        self.pretty_help=pretty_help
        self.theme=theme
        self.output=output
        if platform.system() == "linux":
            self.is_tty="/dev/tty" in os.ttyname(1)
        else:
            self.is_tty=False


    def get_adoc_elem(self, text, elem):
        # white, silver, gray, black, red, maroon, yellow, olive, lime, green, aqua, teal, blue, navy, fuchsia, purple,
        indent=""
        if not hasattr(self, "dy_adoc_elem"):
            self.dy_adoc_elem=dict(
                about_fields=" *{}* ",
                aliases=" *{}* ",
                arg_index=" *{}* ",
                arg_path=" *{}* ",
                examples=" ++{}++ ",
                bullets="{}",
                flags=" _{}_ ",
                headers="== {}",
                hint=" _{}_ ",
                info="{}",
                properties="{}",
                emphasize=" **{}** ",
                syntax_headers="=== {}",
                brackets="{}",
                values=" __{}__ ",
            )
        
        return deepcopy(self.dy_adoc_elem[elem]).format(text)

    def escape(self, char, text):
        chars={
            ".": dict(
                markdown=".&#65279;",
            )
        }

        if char in chars:
            if self.output in chars[char]:
                return text.replace(char, chars[char][self.output])
            else:
                return text
        else:
            return text

    def get_cmd_elem(self, text, elem):
        if self.pretty_help is True:
            for prop in sorted(self.theme[elem]):
                ignore= self.is_tty and prop == "italic"
                if ignore is False:
                    value=self.theme[elem][prop]
                    if value is True:
                        text=self.get_cmd_style(text, prop)
                    elif isinstance(value, str):
                        text=self.get_cmd_style(text, prop, value)
        return text
    
    def get_len_text(self, text):
        tmp_text=text
        for pattern in [
            r"\x1b\[48;2;.+?m",
            r"\x1b\[49m",
            r"\x1b\[1m",
            r"\x1b\[22m",
            r"\x1b\[38;2;.+?m",
            r"\x1b\[39m",
            r"\x1b\[3m",
            r"\x1b\[23m",
            r"\x1b\[4m",
            r"\x1b\[24m",
        ]:
            tmp_text=re.sub(pattern, "", tmp_text)
        return len(tmp_text)

    def get_cmd_style(self, text, style, color=None):
        if not hasattr(self, "dy_cmd_styles"):
            self.dy_cmd_styles=dict(
                background=dict(
                    start="\x1b[48;2;{}m",
                    end="\x1b[49m",
                ),
                bold=dict(
                    start="\x1b[1m",
                    end="\x1b[22m",
                ),
                foreground=dict(
                    start="\x1b[38;2;{}m",
                    end="\x1b[39m",
                ),
                italic=dict(
                    start="\x1b[3m",
                    end="\x1b[23m",
                ),
                underline=dict(
                    start="\x1b[4m",
                    end="\x1b[24m",
                ),
            )

        return "{}{}{}".format(
            self.dy_cmd_styles[style]["start"].format(color),
            text,
            self.dy_cmd_styles[style]["end"].format(color),
        )

    def get_css(self):
        text=get_heredoc_lines("""
        body {
            background-color: #2b2b2b;
            color: white;
            font-family: "Lucida Console", "Courier New", monospace;
        }
        #nargs-documentation {
            width: 90%;
            margin: auto;
        }
        #nargs-documentation h1 {
            text-align: center;
        }
        #nargs-documentation h3 {
            margin-bottom: 5px;
        }
        #nargs-documentation p {
            margin-bottom: 0px;
            margin-top: 0px;
        }
        #nargs-documentation dd {
            margin-left: 20px;
        }
        #nargs-documentation #nargs-sheet ul,
        #nargs-documentation #examples ul {
            margin-top: 0px;
            list-style-type: none;
            padding-left: 1em;
        }
        #nargs-documentation .hint,
        #nargs-documentation .info,
        #nargs-documentation .properties,
        #nargs-documentation .examples {
            margin-left: 20px;
        }
        #nargs-documentation #nargs-sheet ul > li:before,
        #nargs-documentation #examples ul > li:before {
            content: "- ";
            position: absolute;
            text-indent: -1em;
        }

        #nargs-documentation #examples ul > li:before {
            content: "\u00BB ";
        }
        """, indent="\t")

        for _class in sorted(self.theme):
            class_name=_class.replace("_", "-")
            is_set=False
            for prop in sorted(self.theme[_class]):
                value=self.theme[_class][prop]
                if value not in [None, False]:
                    if is_set is False:
                        text+="\t#nargs-documentation .{} {{\n".format(class_name)
                    is_set=True
                    if prop == "background":
                        text+="\t\tbackground-color: rgb({});\n".format(", ".join(value.split(";")))
                    elif prop == "bold":
                        text+="\t\tfont-weight: bold;\n"
                    elif prop == "foreground":
                        text+="\t\tcolor: rgb({});\n".format(", ".join(value.split(";")))
                    elif prop == "italic":
                        text+="\t\tfont-style: italic;\n"
                    elif prop == "underline":
                        text+="\t\ttext-decoration: underline;\n"

            if is_set is True:
                text+=("\t}\n")

        return text

    def get_html_elem(self, text, elem):
        indent=""
        if not hasattr(self, "dy_html_elem"):
            self.dy_html_elem=dict(
                aliases="span",
                aliases_and_values="p",
                arg_index="span",
                arg_path="span",
                brackets="span",
                hint="p",
                examples="p",
                flags="span",
                info="p",
                bullets="span",
                headers="h2",
                about_fields="span",
                properties="p",
                syntax_headers="h3",
                emphasize="span",
                values="span",
            )
        tag=self.dy_html_elem[elem]
        if tag in ["h2", "h3"]:
            indent="\t\t\t"

        return "{}<{} class=\"{}\">{}</{}>".format(
            indent,
            tag,
            elem.replace("_", "-"),
            text,
            tag,
        )

    def get_space(self, num_occurrences=1):
        space=None
        if self.output in ["cmd_help", "cmd_usage", "text"]:
            space=" "
        elif self.output in ["html", "markdown"]:
            space="&nbsp;"
        elif self.output == "asciidoc":
            space="{nbsp}"
        return space*num_occurrences

    def start_newline(self):
        if self.output in ["markdown", "asciidoc"]:
            return self.get_newline()
        else:
            return ""

    def get_newline(self, num_occurrences=1):
        newline=None
        if self.output in ["cmd_help", "cmd_usage", "text"]:
            newline="\n"
        elif self.output in ["html", "markdown"]:
            newline="<br>"
        elif self.output == "asciidoc":
            newline="{empty} +"
        return newline*num_occurrences

    def get_list_bullet(self):
        if self.output in ["cmd_help", "cmd_usage", "text", "markdown"]:
            return "- "
        elif self.output == "html":
            return ""
        elif self.output == "asciidoc":
            return "* "

    def get_plus_symbol(self):
        if self.output in ["cmd_help", "cmd_usage", "text", "markdown", "html"]:
            return "+"
        elif self.output == "asciidoc":
            return "{plus}"

    def get_asterisk_symbol(self):
        if self.output in ["cmd_help", "cmd_usage", "text", "markdown", "html"]:
            return "*"
        elif self.output == "asciidoc":
            return "{asterisk}"

    def get_caret_symbol(self):
        if self.output in ["cmd_help", "cmd_usage", "text", "markdown", "html"]:
            return "^"
        elif self.output == "asciidoc":
            return "{caret}"

    def get_md_elem(self, text, elem):
        indent=""
        if not hasattr(self, "dy_md_elem"):
            self.dy_md_elem=dict(
                about_fields=" **{}**",
                aliases="{}",
                arg_index="**{}**",
                arg_path=" **`{}`**",
                brackets=" **{}**",
                hint="*{}*",
                examples=" `{}`",
                flags="`{}`",
                info="{}",
                properties="{}",
                bullets="{}",
                headers="## {}",
                syntax_headers="### {}",
                emphasize="`{}`",
                values="*`{}`*",
            )

        return deepcopy(self.dy_md_elem[elem]).format(text)

    def get_symbol(self, symbol):
        if not hasattr(self, "dy_symbols"):
            self.dy_symbols={
                "<": dict(
                    html="&lt;",
                ),
                ">": dict (
                    html="&gt;",
                ),
                "[": dict(
                    asciidoc="{startsb}",
                ),
                "]": dict(
                    asciidoc="{endsb}",
                )
            }

        if self.output in self.dy_symbols[symbol]:
            return self.dy_symbols[symbol][self.output]
        else:
            return symbol

    def get_text(self,
        text,
        element,
    ):
        if self.output in ["cmd_help", "cmd_usage"]:
            if element in ["headers", "syntax_headers"]:
                text="{}:".format(text)
            return self.get_cmd_elem(text, element)            
        elif self.output == "text":
            if element in ["headers", "syntax_headers"]:
                text="{}:".format(text)
            return text
        elif self.output == "html":
            return self.get_html_elem(text, element)
        elif self.output == "markdown":
            return self.get_md_elem(text, element)
        elif self.output == "asciidoc":
            return self.get_adoc_elem(text, element)

def get_heredoc_lines(heredoc, indent=None):
    if indent is None:
        indent=""
    lines=heredoc.split("\n")
    tmp_indent=None
    tmp_lines=[]
    for l, line in enumerate(lines):
        ignore= l == 0 or l == len(lines) -1
        if ignore is False:
            if tmp_indent is None:
                tmp_indent=len(re.match(r"^(\s+)", line).group(1))
            tmp_lines.append("{}{}".format(indent, line[tmp_indent:]))
    return "{}\n".format("\n".join(tmp_lines))

def get_default_props():
    return  dict(
        background=None,
        bold=False,
        foreground=None,
        italic=False,
        underline=False,
    )

def get_prop_type(prop):
    if prop in ["bold", "italic", "underline" ]:
        return [bool]
    elif prop in ["background", "foreground"]:
        return [str, type(None)]

def get_theme(default_theme, user_theme, dy_err):
    if user_theme is not None:
        for elem in sorted(user_theme):
            if elem in default_theme:
                default_theme[elem]=deepcopy(get_default_props())
                if isinstance(user_theme[elem], dict):
                    for prop in sorted(user_theme[elem]):
                        if prop in default_theme[elem]:
                            prop_value=user_theme[elem][prop]
                            if type(prop_value) in get_prop_type(prop):
                                if isinstance(prop_value, str):
                                    reg_rgb=re.match(get_regex_dfn("def_theme_rgb")["rule"], prop_value)
                                    if reg_rgb:
                                        for value in prop_value.split(";"):
                                            if int(value) > 255:
                                                msg.error("Theme element '{}' property '{}' all integer values from {} must be less or equal than 255.".format(elem, prop, prop_value), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                                    else:
                                        reg_hexa=re.match(get_regex_dfn("def_theme_hexa")["rule"], prop_value)
                                        if reg_hexa:
                                            tmp_colors=[]
                                            for color in reg_hexa.groups():
                                                tmp_colors.append(str(int(color, 16)))
                                            prop_value=";".join(tmp_colors)
                                        else:
                                            msg.error([
                                                "Theme element '{}' property '{}' with value '{}' does not match any regexes from:".format(elem, prop, prop_value),
                                                *get_regex_hints("def_theme_rgb"),
                                                *get_regex_hints("def_theme_hexa"),
                                            ], prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

                                default_theme[elem][prop]=prop_value
                            else:
                                msg.error("Theme element '{}' property '{}' value type {} unknown in {}.".format(elem, prop, type(prop_value), get_prop_type(prop)), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                        else:
                            msg.error("Theme element '{}' property '{}' unknown in {}.".format(elem, prop, sorted(default_theme[elem])), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
                else:
                    msg.error("Theme element '{}' type '{}' must be of type '{}'.".format(elem, type(user_theme[elem]), dict), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)
            else:
                msg.error("Theme element '{}' unknown in {}.".format(elem, sorted(default_theme)), prefix=dy_err["prefix"], pretty=dy_err["pretty"], exc=dy_err["exc"], exit=1)

    return default_theme
