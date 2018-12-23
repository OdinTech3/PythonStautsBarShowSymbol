# -*- coding: utf-8 -*-
from collections import deque
import re
import sys
import os

try:
    from sublime_plugin import EventListener
    import sublime
except ModuleNotFoundError:
    EventListener = type('EventListener', (object, ), {})

if sys.version_info > (3, 4):
    from typing import Tuple, List, Deque, Iterable  # noqa: F401


def get_syntax(view):  # type: (sublime.View) -> str
    syntax_path = view.settings().get('syntax')  # type: str
    path = syntax_path.rpartition('.')[0]  # type: str
    syntax = os.path.basename(os.path.normpath(path))  # type: str

    return syntax


class StatusSymbol():
    SYNTAX_NAME = 'NA'

    def get_desired_symbols(self, view):  # type: (sublime.View) -> List[Tuple[sublime.Region, str]]
        selection = view.sel()  # type: sublime.Selection[sublime.Region]
        sel_end_region = selection[0].b  # type: int
        symbols = view.symbols()  # type: Iterable[Tuple[sublime.Region, str]]
        desired_symbols = [
            symbol for symbol in symbols
            if self.in_region(symbol, sel_end_region)
        ]

        if not desired_symbols:
            return []

        return list(reversed(desired_symbols))

    def parse_symbols(self, desired_symbols):  # type: (List[Tuple[sublime.Region, str]]) -> Tuple
        target_symbol = deque(desired_symbols).popleft()
        _, target_line = target_symbol
        return (target_symbol, target_line, desired_symbols)

    def build_symbols(self, target_line, symbol_list):  # type: (str, List[Tuple[sublime.Region, str]]) -> List
        symbol_path = deque()  # type: Deque
        target_indent = self.get_indent(target_line)

        for region, line in symbol_list:
            curr_indent = self.get_indent(line)

            # Break out of loop when we encounter a class
            if curr_indent == 0:
                symbol_path.appendleft(line.strip())
                break
            elif curr_indent < target_indent:
                symbol_path.appendleft(line.strip())

            target_indent = curr_indent

        symbol_path.append(target_line.strip())

        symbol_names = [self.get_symbolname(line) for line in symbol_path]
        target_name = symbol_names.pop()

        symbol_names.append(self.highlight_target(target_name))

        return symbol_names

    def in_region(self, symbol, end_region):  # type: (Tuple[sublime.Region, str], int) -> bool
        region, _ = symbol
        start_region = region.a

        return end_region > start_region

    def get_indent(self, line_str):  # type: (str) -> int
        return len(line_str) - len(line_str.lstrip())

    def has_index(self, symbol):  # type: (Tuple[sublime.Region, str]) -> bool
        _, line = symbol

        return self.get_indent(line) > 0

    def highlight_target(self, symbol_name):
        return '{}'.format(symbol_name)

    def format_symbolnames(self, symbol_path):  # type: (List[str]) -> str
        return ' ↦ '.join(symbol_path)

    def on_selection_helper(self, view):  # type: (sublime.View) -> None

        if not get_syntax(view) == self.SYNTAX_NAME:
            return

        desired_symbols = self.get_desired_symbols(view)

        if not desired_symbols:
            return

        target_symbol, target_line, symbol_list = self.parse_symbols(desired_symbols)

        if self.has_index(target_symbol):
            symbol_names = self.build_symbols(target_line, symbol_list)
            message = '[ {} ]'.format(self.format_symbolnames(symbol_names))
        else:
            message = '[ {} ]'.format(self.get_symbolname(target_line))

        sublime.status_message(message)

    def get_symbolname(self, line):  # type: (str) -> str
        raise NotImplementedError


class MagicPythonSyntax(StatusSymbol, EventListener):
    """docstring for MagicPythonSyntax"""

    SYNTAX_NAME = 'MagicPython'
    CLASS_REGEX = re.compile(r'^class\s*(?P<class_name>\w+)')
    METHOD_REGEX = re.compile(r'^(?P<method_name>\w+)(?P<parenthesis>\((\s*([^)]+?)\s*)?\))')

    def on_selection_modified(self, view):
        self.on_selection_helper(view)

    def get_symbolname(self, line):  # type: (str) -> str
        class_match = MagicPythonSyntax.CLASS_REGEX.match(line)
        method_match = MagicPythonSyntax.METHOD_REGEX.match(line)

        if class_match:
            return class_match.group('class_name')
        elif method_match:
            return '{}()'.format(method_match.group('method_name'))
        elif ':' in line:
            return line.replace(':', '')

        return 'Unknown'


class PythonSyntax(StatusSymbol, EventListener):
    """docstring for PythonSyntax"""

    SYNTAX_NAME = 'Python'
    CLASS_REGEX = re.compile(r'^(?P<class_name>\w+)(?P<parenthesis>\((\w,?\w*.\w*?,?)*\))')
    METHOD_REGEX = re.compile(r'^(?P<method_name>\w+)(?P<parenthesis>\(.\))')

    def on_selection_modified(self, view):
        self.on_selection_helper(view)

    def get_symbolname(self, line):  # type: (str) -> str
        class_match = PythonSyntax.CLASS_REGEX.match(line)
        method_match = PythonSyntax.METHOD_REGEX.match(line)

        if class_match:
            return class_match.group('class_name')
        elif method_match:
            return '{}()'.format(method_match.group('method_name'))
        elif ':' in line:
            return line.replace(':', '')

        return 'Unknown'
