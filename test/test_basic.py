#!/usr/bin/env python

import textwrap
import unittest

from code_writer import (
    CodeWriter,
    fmt_camel,
    fmt_dashes,
    fmt_pascal,
    fmt_underscores,
)


class TestBasic(unittest.TestCase):

    def test_emit(self):
        # Test empty output
        cw = CodeWriter()
        assert cw.render() == ''

        cw = CodeWriter()
        cw.emit('hello, world.')
        assert cw.render() == 'hello, world.\n'

        cw = CodeWriter()
        cw.emit_raw('hello,\nworld.\n')
        assert cw.render() == textwrap.dedent("""\
            hello,
            world.
        """)

        cw = CodeWriter()
        with self.assertRaises(AssertionError) as ctx:
            cw.emit_raw('hello,\nworld.')
        assert ctx.exception.args[0] == \
            'Input string to emit_raw must end with a newline.'

        # Test blank lines
        cw = CodeWriter()
        cw.emit()
        cw.emit()
        cw.emit()
        assert cw.render() == '\n\n\n'

        cw = CodeWriter()
        cw.emit_raw('\n\n\n')
        assert cw.render() == '\n\n\n'

    def test_indent(self):
        # Test spaces
        cw = CodeWriter()
        cw.emit('if:')
        with cw.indent():
            cw.emit('level 1')
            with cw.indent():
                cw.emit('level 2')
        assert cw.render() == textwrap.dedent("""\
            if:
                level 1
                    level 2
        """)

        # Test two spaces per indent
        cw = CodeWriter(default_dent=2)
        cw.emit('if:')
        with cw.indent():
            cw.emit('level 1')
            with cw.indent():
                cw.emit('level 2')
        assert cw.render() == textwrap.dedent("""\
            if:
              level 1
                level 2
        """)

        # Test tabs
        cw = CodeWriter(use_tabs=True)
        cw.emit('if:')
        with cw.indent():
            cw.emit('level 1')
            with cw.indent():
                cw.emit('level 2')
        assert cw.render() == textwrap.dedent("""\
            if:
            \tlevel 1
            \t\tlevel 2
        """)

        # Test two-tabs per indent
        cw = CodeWriter(use_tabs=True, default_dent=2)
        cw.emit('if:')
        with cw.indent():
            cw.emit('level 1')
            with cw.indent():
                cw.emit('level 2')
        assert cw.render() == textwrap.dedent("""\
            if:
            \t\tlevel 1
            \t\t\t\tlevel 2
        """)

    def test_block(self):
        cw = CodeWriter()
        with cw.block('if {', '}'):
            cw.emit('level 1')
        assert cw.render() == textwrap.dedent("""\
            if {
                level 1
            }
        """)

        cw = CodeWriter(default_delim=('{', '}'))
        with cw.block('if'):
            cw.emit('level 1')
        assert cw.render() == textwrap.dedent("""\
            if {
                level 1
            }
        """)

        cw = CodeWriter()
        with cw.block('if:'):
            cw.emit('level 1')
        assert cw.render() == textwrap.dedent("""\
            if:
                level 1
        """)

        # Test allman
        cw = CodeWriter(default_delim=('{', '}'))
        with cw.block('if', allman=True):
            cw.emit('level 1')
        assert cw.render() == textwrap.dedent("""\
            if
            {
                level 1
            }
        """)

        # Test tabs
        cw = CodeWriter(default_delim=('{', '}'), use_tabs=True)
        with cw.block('if', allman=True):
            cw.emit('level 1')
        assert cw.render() == textwrap.dedent("""\
            if
            {
            \tlevel 1
            }
        """)

    def test_trim(self):
        # Test trimming of the trailing newline that's in the final iteration.
        cw = CodeWriter()
        with cw.block('if:'):
            for i in range(3):
                cw.emit(str(i))
                cw.emit()
        cw.trim_last_line_if_empty()
        cw.emit('end')
        assert cw.render() == textwrap.dedent("""\
            if:
                0
                
                1
                
                2
            end
        """)

        # Test that trim isn't overzealous
        cw = CodeWriter()
        cw.emit()
        cw.emit()
        cw.emit()
        cw.trim_last_line_if_empty()
        assert cw.render() == '\n\n'

        # Test mass trimming
        cw = CodeWriter()
        cw.emit()
        cw.emit('a')
        cw.emit()
        cw.emit()
        cw.emit()
        cw.trim_trailing_empty_lines()
        assert cw.render() == '\na\n'

        cw = CodeWriter()
        cw.emit()
        cw.emit()
        cw.emit()
        cw.trim_trailing_empty_lines()
        assert cw.render() == ''

    def test_wrapped_text(self):
        cw = CodeWriter()
        cw.emit_wrapped_text('this is a test')
        assert cw.render() == 'this is a test\n'

        cw = CodeWriter()
        cw.emit_wrapped_text('this is a test', width=12)
        assert cw.render() == 'this is a\ntest\n'

        # Test break_long_words
        cw = CodeWriter()
        cw.emit_wrapped_text('thisisalongword', width=12)
        assert cw.render() == 'thisisalongword\n'

        cw = CodeWriter()
        cw.emit_wrapped_text('thisisalongword', width=12, break_long_words=True)
        assert cw.render() == 'thisisalongw\nord\n'

        # Test break_on_hyphens
        cw = CodeWriter()
        cw.emit_wrapped_text('thisisalong-word', width=10)
        assert cw.render() == 'thisisalong-word\n'

        cw = CodeWriter()
        cw.emit_wrapped_text('thisisalong-word', width=10, break_on_hyphens=True)
        assert cw.render() == 'thisisalong-\nword\n'

        # Test indent
        cw = CodeWriter(default_width=12)
        with cw.indent():
            cw.emit_wrapped_text('this is a test')
        assert cw.render() == '    this is\n    a test\n'

        # Test prefix
        cw = CodeWriter()
        with cw.indent():
            cw.emit_wrapped_text('this is a test', width=12, prefix='# ')
        assert cw.render() == '    # this\n    # is a\n    # test\n'

        # Test prefixes for Python-like comment
        cw = CodeWriter(default_dent=2)
        cw.emit('hello')
        with cw.indent():
            cw.emit_wrapped_text(
                'this is a test',
                width=12,
                prefix='# ',
                initial_prefix='FIELD ID: ',
                indent_after_first=True)
        assert cw.render() == textwrap.dedent("""\
            hello
              # FIELD ID: this
              #   is a
              #   test
        """)

        # Test subsequent prefix
        cw = CodeWriter(default_dent=2, default_width=12)
        cw.emit('hello')
        with cw.indent():
            cw.emit_wrapped_text(
                'this is a test',
                prefix='# ',
                initial_prefix='FIELD ID: ',
                subsequent_prefix='- ',
                indent_after_first=True)
        assert cw.render() == textwrap.dedent("""\
            hello
              # FIELD ID: this
              #   - is a
              #   - test
        """)

    def test_list(self):
        bracket = ('[', ']')

        cw = CodeWriter()
        cw.emit_list([], bracket)
        assert cw.render() == '[]\n'

        cw = CodeWriter()
        cw.emit_list([], bracket, compact=True)
        assert cw.render() == '[]\n'

        cw = CodeWriter()
        cw.emit_list(['test'], bracket)
        assert cw.render() == '[test]\n'

        cw = CodeWriter()
        cw.emit_list(['test'], bracket, compact=True)
        assert cw.render() == '[test]\n'

        cw = CodeWriter()
        cw.emit_list(['a', 'b'], bracket, compact=True)
        assert cw.render() == textwrap.dedent("""\
            [a,
             b]
        """)

        cw = CodeWriter()
        cw.emit_list(
            ['a', 'b'],
            bracket,
            before='let val = ',
            after=';',
            compact=True,
        )
        assert cw.render() == textwrap.dedent("""\
            let val = [a,
                       b];
        """)

        cw = CodeWriter()
        cw.emit_list(
            ['a', 'b'],
            bracket,
            before='let val = ',
            after=';')
        assert cw.render() == textwrap.dedent("""\
            let val = [
                a,
                b,
            ];
        """)

        cw = CodeWriter()
        cw.emit_list(
            ['a', 'b'],
            bracket,
            before='let val = ',
            after=';',
            sep='|',
            skip_last_sep=True)
        assert cw.render() == textwrap.dedent("""\
            let val = [
                a|
                b
            ];
        """)

        # Try compact mode with tabs
        cw = CodeWriter(use_tabs=True)
        with self.assertRaises(AssertionError) as ctx:
            cw.emit_list(['a', 'b'], bracket, compact=True)
        assert ctx.exception.args[0] ==\
            'Cannot use compact mode with tabs for indents.'

    def test_fmt(self):
        text = 'a-B-HiHo-merryOh_yes_no_XYZ'
        assert fmt_camel(text) == 'aBHiHoMerryOhYesNoXyz'
        assert fmt_dashes(text) == 'a-b-hi-ho-merry-oh-yes-no-xyz'
        assert fmt_pascal(text) == 'ABHiHoMerryOhYesNoXyz'
        assert fmt_underscores(text) == 'a_b_hi_ho_merry_oh_yes_no_xyz'


if __name__ == '__main__':
    unittest.main()
