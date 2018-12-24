import pytest
from StatusBarSymbols import StatusSymbol, PythonSyntax
from StatusBarSymbols.tests.cases import View, Selection, Region
from StatusBarSymbols.tests.cases.python_symbols import PYTHON_SYNTAX_SYMBOLS


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
    target_symbol, *rest_symbols = desired_symbols

    assert parsed_symbol == (target_symbol, target_symbol[1], rest_symbols)


def test_empty_parse_symbols(status_symbol: StatusSymbol) -> None:
    view = View(Selection(4), [])

    desired_symbols = status_symbol.get_desired_symbols(view)
    parsed_symbol = status_symbol.parse_symbols(desired_symbols)

    assert parsed_symbol == ()


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

    def test_empty_symbols_build_symbols(self, python_syntax: PythonSyntax):
        '''
        Test that empty symbol list from the view, an empty parsed symbol tuple will raise an error.
        `build_symbols` can't execute becuse it needs the parsed symbols to not be empty
        '''
        view = View(Selection(4), [])
        desired_symbols = python_syntax.get_desired_symbols(view)

        with pytest.raises(ValueError):
            target_symbol, target_line, symbol_list = python_syntax.parse_symbols(desired_symbols)
            python_syntax.build_symbols(target_line, symbol_list)

    @pytest.mark.parametrize("test_input, expected", PYTHON_SYNTAX_SYMBOLS)
    def test_symbols_build_symbols(self, test_input, expected, python_syntax: PythonSyntax):
        desired_symbols = python_syntax.get_desired_symbols(test_input)
        target_symbol, target_line, symbol_list = python_syntax.parse_symbols(desired_symbols)

        assert python_syntax.build_symbols(target_line, symbol_list) == expected
