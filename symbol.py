# -*- coding: utf-8 -*-
from collections import deque
import sublime
import sublime_plugin
import re
import sys
import os

if sys.version_info > (3, 4):
    from typing import Tuple, List, Deque


def is_python_syntax(view):
    # type: (sublime.View) -> bool
    syntax = view.settings().get('syntax')

    return 'python' in syntax.lower()


def get_syntax(view):  # type: (sublime.View) -> str
    syntax_path = view.settings().get('syntax')  # type: str
    path, *_ = syntax_path.rpartition('.')  # type: Tuple[str, str, str]
    syntax = os.path.basename(os.path.normpath(path))  # type: str

    return syntax


class StatusSymbol(sublime_plugin.EventListener):
    def __init__(self, *args, **kwargs):
        self.symbolname_regex_1 = re.compile(r'^(class\s*(\w+):?)')
        self.symbolname_regex_2 = re.compile(r'^((\w+)(\((\w*.?\w*)\))*:?)')

        super().__init__(*args, **kwargs)

    def on_selection_modified(self, view):

        if not is_python_syntax(view):
            return

        selection = view.sel()  # type: sublime.Selection[sublime.Region]
        sel_end_region = selection[0].b  # type: int
        symbols = view.symbols()  # type: [(sublime.Region, str)]
        desired_symbols = [
            symbol for symbol in symbols
            if self.in_region(symbol, sel_end_region)
        ]

        if not desired_symbols:
            return

        desired_symbols.reverse()

        target_symbol = desired_symbols.pop(0)
        symbol_path = deque()
        _, target_line = target_symbol

        if self.has_index(target_symbol):
            target_indent = self.get_indent(target_line)

            for region, line in desired_symbols:
                curr_indent = self.get_indent(line)

                if curr_indent == 0:
                    symbol_path.appendleft(line.strip())
                    break
                elif curr_indent < target_indent:
                    symbol_path.appendleft(line.strip())

                target_indent = curr_indent

            symbol_path.append(target_line.strip())

            symbol_names = [self._get_symbolname(line) for line in symbol_path]
            target_name = symbol_names.pop()

            symbol_names.append(self._highlight_target(target_name))

            sublime.status_message('[ {} ]'.format(self._format_symbolnames(symbol_names)))
        else:
            sublime.status_message('[ ( {} ) ]'.format(self._get_symbolname(target_line)))

    def in_region(self, symbol, end_region):
        region, _ = symbol
        start_region = region.a

        return end_region > start_region

    def get_indent(self, line_str):
        # type: (str) -> int
        return len(line_str) - len(line_str.lstrip())

    def has_index(self, symbol):
        # type: (tuple(sublime.Region, str)) -> bool
        _, line = symbol

        return self.get_indent(line) > 0

    def _get_symbolname(self, line):
        # type: (str) -> str
        if 'class' in line:
            match = self.symbolname_regex_1.match(line)
        else:
            match = self.symbolname_regex_2.match(line)

        return match.group(2) if match is not None else 'Unknown'

    def _highlight_target(self, symbol_name):
        return '( {} )'.format(symbol_name)

    def _format_symbolnames(self, symbol_path):
        # type: (List[str]) -> str
        return ' ↦ '.join(symbol_path)
