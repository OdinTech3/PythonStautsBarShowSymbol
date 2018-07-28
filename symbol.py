# -*- coding:utf-8 -*-
import sublime
import sublime_plugin
import re
import functools
import os


class BackgroundShowPythonIndentName(sublime_plugin.EventListener):
    """ Process Sublime Text events """

    def on_selection_modified(self, view):
        global posHistory, lastLine, prevHistory
        syntax = view.settings().get('syntax')
        if syntax.lower().find('python') == -1:
            return
        s = view.sel()
        if s[0].a != s[0].b:
            return
        cursorX = s[0].b

        symList = []
        symbols = view.get_symbols()
        lastIndex = len(symbols) - 1
        for i, symbol in enumerate(symbols):
            rng, line = symbol
            if rng.a > cursorX:
                lastIndex = i - 1
                break
        indent = -1
        for i in range(lastIndex, -1, -1):
            rng, line = symbols[i]
            if indent == -1:
                indent = self._getIndent(line)
            else:
                c = self._getIndent(line)
                if indent <= c:
                    continue
                indent = c
            symList.append(line)
            if indent == 0:
                break
        symList.reverse()
        rs = None
        if (sublime.version()[0] == '3'):
            rs = re.compile(r'\s*(\w*)')
        else:
            rs = re.compile(r'\s*(def|class)\s+(\w*)')
        strs = ["---------------------"]
        for s in symList:
            m = rs.match(s)
            if m:
                strs.append(m.group(0).strip())
        if len(strs) > 1:
            sublime.status_message('->'.join(strs))

    def _getIndent(self, line):
        c = 0
        for s in line:
            if s in (" ", "\t"):
                c += 1
            else:
                break
        return c
