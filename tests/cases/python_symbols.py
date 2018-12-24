from . import View, Selection, Region

PYTHON_SYNTAX_SYMBOLS = [
    (View(
        Selection(4), [
            (Region(0, 1), 'Foo:'),
            (Region(2, 3), '    method1(…)'),
            (Region(3, 4), '    method2(…)'),
        ]), ['Foo', 'method2()']),
    (View(
        Selection(4), [
            (Region(0, 1), 'Foo:'),
            (Region(2, 3), '    method1(…)'),
            (Region(3, 4), 'method2(…)'),
        ]), ['method2()']),
]
