#!/usr/bin/env python3
from pprint import pprint
import os
import sys

def get_mapped_theme_props():
    return dict(
        foreground=dict(
            default=None,
            map="f",
        ),
        background=dict(
            default=None,
            map="b",
        ),
        bold=dict(
            default=False,
            map="o",
        ),
        italic=dict(
            default=False,
            map="i",
        ),
        underline=dict(
            default=False,
            map="u",
        ),
    )

def get_arg_properties():
    return dict(
        aliases=dict(
            default=None,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=False,
            map="a",
        ), 
        aliases_info=dict(
            default=None,
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=False,
            map="ai",
        ), 
        allow_parent_fork=dict(
            default=True,
            for_cache=True,
            for_definition=True,
            for_help=True,
            has_default=True,
            map="ap",
        ), 
        allow_siblings=dict(
            default=True,
            for_cache=True,
            for_definition=True,
            for_help=True,
            has_default=True,
            map="as",
        ), 
        args=dict(
            default=dict(),
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="ar",
        ), 
        default=dict(
            default=None,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="d",
        ), 
        default_alias=dict(
            default=None,
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=False,
            map="da",
        ), 
        enabled=dict(
            default=True,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="e",
        ), 
        examples=dict(
            default=None,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="ex",
        ),
        hint=dict(
            default=None,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="h",
        ), 
        **{"in":dict(
            default=None,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="i",
        )}, 
        in_labels=dict(
            default=[],
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="il",
        ), 
        info=dict(
            default=None,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="in",
        ), 
        is_auto_alias=dict(
            default=True,
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="is",
        ), 
        is_builtin=dict(
            default=False,
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="ib",
        ),
        is_custom_builtin=dict(
            default=False,
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="ic",
        ),
        is_usage=dict(
            default=False,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="iu",
        ), 
        label=dict(
            default=None,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="l",
        ), 
        need_child=dict(
            default=False,
            for_cache=True,
            for_definition=True,
            for_help=True,
            has_default=True,
            map="n",
        ),
        preset=dict(
            default=False,
            for_cache=True,
            for_definition=True,
            for_help=True,
            has_default=True,
            map="p",
        ),
        preset_children=dict(
            default=[],
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="pc",
        ),   
        repeat=dict(
            default="replace",
            for_cache=True,
            for_definition=True,
            for_help=True,
            has_default=True,
            map="r",
        ), 
        required=dict(
            default=False,
            for_cache=True,
            for_definition=True,
            for_help=True,
            has_default=True,
            map="re",
        ), 
        required_children=dict(
            default=[],
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="rc",
        ), 
        show=dict(
            default=True,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="s",
        ), 
        type=dict(
            default=None,
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="t",
        ), 
        values_authorized=dict(
            default=False,
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="v",
        ), 
        values_max=dict(
            default=None,
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="vm",
        ), 
        values_min=dict(
            default=None,
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="vi",
        ), 
        values_required=dict(
            default=False,
            for_cache=True,
            for_definition=False,
            for_help=False,
            has_default=True,
            map="vr",
        ), 
        values=dict(
            default=False,
            for_cache=False,
            for_definition=True,
            for_help=False,
            has_default=False,
            map=None,
        ), 
        xor=dict(
            default=dict(),
            for_cache=True,
            for_definition=True,
            for_help=False,
            has_default=True,
            map="x",
        ), 
        xor_groups=dict(
            default=None,
            for_cache=True,
            for_definition=False,
            for_help=True,
            has_default=True,
            map="xg",
        ), 
    )
