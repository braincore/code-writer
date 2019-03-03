from contextlib import contextmanager
import re
import textwrap
from typing import Generator, List, Optional, Tuple


_split_words_capitalization_re = re.compile(
    '^[a-z0-9]+|[A-Z][a-z0-9]+|[A-Z]+(?=[A-Z][a-z0-9])|[A-Z]+$'
)
_split_words_dashes_re = re.compile('[-_/]+')


def split_words(name: str) -> List[str]:
    """
    Splits name based on capitalization, dashes, and underscores.
        Example: 'GetFile' -> ['Get', 'File']
        Example: 'get_file' -> ['get', 'file']
    """
    all_words = []
    for word in re.split(_split_words_dashes_re, name):
        vals = _split_words_capitalization_re.findall(word)
        if vals:
            all_words.extend(vals)
        else:
            all_words.append(word)
    return all_words


def fmt_camel(name: str) -> str:
    """
    Converts name to lower camel case. Words are identified by capitalization,
    dashes, and underscores.
    """
    words = split_words(name)
    assert len(words) > 0
    first = words.pop(0).lower()
    return first + ''.join([word.capitalize() for word in words])


def fmt_dashes(name: str) -> str:
    """
    Converts name to words separated by dashes. Words are identified by
    capitalization, dashes, and underscores.
    """
    return '-'.join([word.lower() for word in split_words(name)])


def fmt_pascal(name: str) -> str:
    """
    Converts name to pascal case. Words are identified by capitalization,
    dashes, and underscores.
    """
    return ''.join([word.capitalize() for word in split_words(name)])


def fmt_underscores(name: str) -> str:
    """
    Converts name to words separated by underscores. Words are identified by
    capitalization, dashes, and underscores.
    """
    return '_'.join([word.lower() for word in split_words(name)])


TDelim = Tuple[Optional[str], Optional[str]]


class CodeWriter:

    def __init__(
            self,
            use_tabs: bool = False,
            default_dent: Optional[int] = None,
            default_delim: TDelim = (None, None),
            default_width: int = 80,
            ) -> None:
        assert isinstance(use_tabs, bool),\
            'Expected bool, got %r' % type(use_tabs)
        self.use_tabs = use_tabs
        if default_dent is None:
            self.default_dent = 1 if use_tabs else 4
        else:
            self.default_dent = default_dent
        self.default_delim = default_delim
        self.default_width = default_width
        self.cur_indent = 0
        self._buffer: List[str] = []

    def render(self) -> str:
        if self._buffer:
            return '\n'.join(self._buffer) + '\n'
        else:
            return ''

    @contextmanager
    def indent(self, dent: Optional[int] = None) -> Generator[None, None, None]:
        """
        For the duration of the context manager, indentation will be increased
        by the value of dent.
        """
        assert dent is None or dent >= 0, 'dent must None or >= 0.'
        delta = self.default_dent if dent is None else dent
        self.cur_indent += delta
        yield
        self.cur_indent -= delta

    def emit(self, s: str = '') -> None:
        """
        Adds indentation, then the input string, and lastly a newline to the
        output buffer. If s is an empty string (default) then an empty line is
        created with no indentation.
        """
        assert '\n' not in s, \
            'String to emit cannot contain newline strings.'
        if s:
            self.emit_raw('%s%s\n' % (self.mk_indent(), s))
        else:
            self.emit_raw('\n')

    def mk_indent(self) -> str:
        return ('\t' if self.use_tabs else ' ') * self.cur_indent

    def mk_one_indent(self) -> str:
        return ('\t' if self.use_tabs else ' ') * self.default_dent

    def emit_raw(self, s: str) -> None:
        """
        Adds the input string to the output buffer. The string must end in a
        newline. It may contain any number of newline characters. No
        indentation is generated.
        """
        if len(s) > 0 and s[-1] != '\n':
            raise AssertionError(
                'Input string to emit_raw must end with a newline.')
        self._buffer.extend(s.splitlines())

    @contextmanager
    def block(
        self,
        before: str = '',
        after: str = '',
        delim: Optional[TDelim] = None,
        dent: Optional[int] = None,
        allman: bool = False
    ) -> Generator[None, None, None]:
        """
        A context manager that emits configurable lines before and after an
        indented block of text.

        This is convenient for class and function definitions in some
        languages.

        Args:
            before: The string to be output in the first line (unindented).
            after: The string to be output in the final unindented line.
            delim: Override default delim. The first element is added
                immediately following `before` and a space. The second element
                is added prior to a space and then `after`.
            dent: Override default amount to indent the block.
            allman: Indicates whether to use `Allman` style indentation,
                or the default `K&R` style. If there is no `before` string this
                is ignored. For more details about indent styles see
                http://en.wikipedia.org/wiki/Indent_style
        """
        if delim is None:
            delim = self.default_delim
        if dent is None:
            dent = self.default_dent
        if before and not allman:
            if delim[0] is not None:
                self.emit('{} {}'.format(before, delim[0]))
            else:
                self.emit(before)
        else:
            if before:
                self.emit(before)
            if delim[0] is not None:
                self.emit(delim[0])

        with self.indent(dent):
            yield

        if delim[1] is not None:
            self.emit(delim[1] + after)
        else:
            if after:
                self.emit(after)

    def trim_last_line_if_empty(self) -> None:
        """
        If the last emit call was an empty line, undo it.
        """
        if self._buffer and self._buffer[-1] == '':
            self._buffer.pop()

    def trim_trailing_empty_lines(self) -> None:
        """
        Removes all empty lines at the end of the current buffer.
        """
        while self._buffer and self._buffer[-1] == '':
            self._buffer.pop()

    def emit_wrapped_text(
        self,
        s: str,
        prefix: str = '',
        initial_prefix: str = '',
        subsequent_prefix: str = '',
        indent_after_first: bool = False,
        width: Optional[int] = None,
        break_long_words: bool = False,
        break_on_hyphens: bool = False,
    ) -> None:
        """
        Adds the input string to the output buffer with indentation and
        wrapping. The wrapping is performed by the :func:`textwrap.fill` Python
        library function.

        Args:
            s: The input string to wrap.
            prefix: The string to prepend to *every* line.
            initial_prefix: The string to prepend to the first line of the
                wrapped string. Note that the current indentation is already
                added to each line.
            subsequent_prefix: The string to prepend to every line after the
                first. Note that the current indentation is already added to
                each line.
            indent_after_first: Whether to indent lines after the first line.
            width: Override the target width of each line including prefixes,
                indentation, and text.
            break_long_words: Break words longer than width.  If false, those
                words will not be broken, and some lines might be longer than
                width.
            break_on_hyphens: Allow breaking hyphenated words. If true,
                wrapping will occur preferably on whitespaces and right after
                hyphens part of compound words.
        """
        if width is None:
            width = self.default_width
        prefix = self.mk_indent() + prefix
        if indent_after_first:
            subsequent_prefix = self.mk_one_indent() + subsequent_prefix
        self.emit_raw(
            textwrap.fill(
                s,
                initial_indent=prefix + initial_prefix,
                subsequent_indent=prefix + subsequent_prefix,
                width=width,
                break_long_words=break_long_words,
                break_on_hyphens=break_on_hyphens,
            ) + '\n')

    def emit_list(
        self,
        items: List[str],
        bracket: Tuple[str, str],
        before: str = '',
        after: str = '',
        compact: bool = False,
        sep: str = ',',
        skip_last_sep: bool = False
    ) -> None:
        """
        Given a list of items, emits one item per line.

        This is convenient for function prototypes and invocations, as well as
        for instantiating arrays, sets, and maps in some languages.

        Args:
            items: Each element will be emitted as part of this list.
            bracket: The symbols that enclose the list such as curly, square,
                or angle brackets. The first element is added immediately
                following `before`. The second element is added prior to
                `after`.
            before: The string to come before the list of items.
            after: The string to follow the list of items.
            compact: In compact mode, the enclosing parentheses are on
                the same lines as the first and last list item.
            sep: The string that follows each list item when compact is true.
                If compact is false, the separator is omitted for the last
                item.
            skip_last_sep: When compact is false, whether the last line has a
                a trailing separator. Ignored when compact is true. Example:
                Use this to omit the last item's comma in JSON.
        """
        assert not compact or not self.use_tabs,\
            'Cannot use compact mode with tabs for indents.'
        if len(items) == 0:
            self.emit(before + bracket[0] + bracket[1] + after)
            return
        if len(items) == 1:
            self.emit(before + bracket[0] + items[0] + bracket[1] + after)
            return

        if compact:
            self.emit(before + bracket[0] + items[0] + sep)

            def emit_items(items: List[str]) -> None:
                for i, item in enumerate(items[1:]):
                    if i == len(items) - 2:
                        self.emit(item + bracket[1] + after)
                    else:
                        self.emit(item + sep)

            if before or bracket[0]:
                with self.indent(len(before) + len(bracket[0])):
                    emit_items(items)
            else:
                emit_items(items)
        else:
            if before or bracket[0]:
                self.emit(before + bracket[0])
            with self.indent():
                for (i, item) in enumerate(items):
                    if i == len(items) - 1 and skip_last_sep:
                        self.emit(item)
                    else:
                        self.emit(item + sep)
            if bracket[1] or after:
                self.emit(bracket[1] + after)
            elif bracket[1]:
                self.emit(bracket[1])
