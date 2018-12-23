import pytest
from StatusBarSymbols import StatusSymbol, PythonSyntax
from dataclasses import dataclass
from typing import Tuple, Iterable


@dataclass
class Region:
    a: int = 0
    b: int = 0


class Selection(Region):
    """
    Represents the Region a mouse has clicked on the View
    """

    def __init__(self, x: int) -> None:
        self.a = self.b = x


Symbols = Iterable[Tuple[Region, str]]


class View():
    def __init__(self, sel_region: Region, symbols: Symbols) -> None:
        self._symbols = symbols
        self._sel_region = sel_region

    def sel(self):
        return [self._sel_region]

    def symbols(self):

        return self._symbols


@pytest.fixture
def status_symbol():
    '''Returns a instance of StatusSymbol class'''
    return StatusSymbol()


@pytest.fixture
def python_syntax():
    '''Returns a instance of PythonSyntax class'''
    return PythonSyntax()


def test_parse_symbols(status_symbol: StatusSymbol) -> None:
    symbols = [
        (Region(0, 1), 'Foo:'),
        (Region(2, 3), '    method1(…)'),
        (Region(3, 4), '    method2(…)'),
    ]

    view = View(Selection(4), symbols)

    desired_symbols = status_symbol.get_desired_symbols(view)
    parsed_symbol = status_symbol.parse_symbols(desired_symbols)

    assert parsed_symbol == (desired_symbols[0], desired_symbols[0][1], desired_symbols)


@pytest.mark.parametrize("test_input, expected", [
    ('    f()', 4),
    ('  using-tab', 2),
    ('      using-tab', 6),
    (' f()', 1),
    ('        f()', 8),
    ('            f()', 12),
    ('  f()', 2),
])
def test_get_indent(test_input, expected, status_symbol: StatusSymbol):
    """
    Test `get_index` counts the number of spaces used for indentation correctly
    """
    assert status_symbol.get_indent(test_input) == expected


class TestDesiredSymbols:
    def test_empty_desired_symbols(self, status_symbol) -> None:
        '''
            Test that an empty symbols list produces an empty list of desired symbols
        '''
        view = View(Selection(0), [])

        assert status_symbol.get_desired_symbols(view) == []

    def test_non_empty_desired_symbols(self, status_symbol) -> None:
        '''
            Test that an non empty symbols list produces the same symbol list but reveresed
        '''
        symbols = [
            (Region(0, 1), 'Foo:'),
            (Region(2, 3), '    method1(…)'),
            (Region(3, 4), '    method2(…)'),
        ]

        view = View(Selection(4), symbols)
        expected = list(reversed(symbols))

        assert status_symbol.get_desired_symbols(view) == expected

    def test_filtered_desired_symbols(self, status_symbol) -> None:
        '''
            Test that an non empty symbols list with a specific selected region
            produces a reversed symbol list with symbols which have a starting region
            above the selected region
        '''
        symbols = [
            (Region(0, 1), 'Foo:'),
            (Region(2, 3), '    method1(…)'),
            (Region(3, 4), '    method2(…)'),
            (Region(4, 5), '    method3(…)'),
        ]

        view = View(Selection(3), symbols)
        expected = list(reversed([
            (Region(0, 1), 'Foo:'),
            (Region(2, 3), '    method1(…)'),
        ]))

        assert status_symbol.get_desired_symbols(view) == expected


class TestPythonSyntax:
    @pytest.mark.parametrize("test_input, expected", [
        ('Foo:', 'Foo'),
        ('Foo:', 'Foo'),
        ('Foo(A, B)', 'Foo'),
        ('bar(…)', 'bar()'),
        ('bar(…)', 'bar()'),
        ('bar2(…)', 'bar2()'),
        ('_bar3(…)', '_bar3()'),
        ('Foo2(A, b, C, D, E)', 'Foo2'),
        pytest.param(
            '_bar_method(...)',
            '_bar_method()',
            marks=pytest.mark.xfail(reason='triple dots should be \u2026')),
    ])
    def test_get_symbolname(self, test_input, expected, python_syntax: PythonSyntax):
        assert python_syntax.get_symbolname(test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [
        ('Foo', 'Unknown'),
        ('Foo(', 'Unknown'),
        ('Foo)', 'Unknown'),
        ('asdasdsdas', 'Unknown'),
    ])
    def test_get_symbolname_on_invalid_inputs(self, test_input, expected, python_syntax: PythonSyntax):
        assert python_syntax.get_symbolname(test_input) == expected
