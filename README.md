# Code Writer [![Latest Version]][PyPI] [![Build Status]][Travis]

[Latest Version]: https://img.shields.io/pypi/v/code-writer.svg
[PyPI]: https://pypi.org/project/code-writer/
[Build Status]: https://api.travis-ci.com/braincore/code-writer.svg?branch=master
[Travis]: https://travis-ci.com/braincore/code-writer

A Python 3 library with convenience functions for generating code in any
language.

Based on the code generation backend in
[Stone](http://www.github.com/dropbox/stone) that's used to generate code in
many languages: C#, Java, Python, Ruby, Rust, Typescript, and more.

# Why?

You know all of the pains with code generation (coding, build process,
maintenance), but have decided you have no other choice. This library makes
generating code a little bit more manageable.

# Alternatives

If your code generation needs are simple, consider using a template language
such as [Jinja2](https://github.com/pallets/jinja).

# Install

```bash
pip3 install code-writer
```

# Usage

## Basics

You'll need to import `CodeWriter`:

```python
from code_writer import CodeWriter
```

## Examples

You probably want to write the output of `render()` to a file, but for
illustrative purposes we'll print them.

### Hello, world.

```python
cw = CodeWriter()
cw.emit('hello,')
with cw.indent():
    cw.emit('world.')
print(cw.render())
```

Output:
```
hello,
    world.
```

### Python if statement

```python
cw = CodeWriter()
cw.emit('if True:')
with cw.indent():
    cw.emit('print("hello, world.")')
print(cw.render())
```

Output:
```python
if True:
    print("hello, world.")
```

### Rust if statement

Use `block()` to create an indented block enclosed by curly braces.

```python
cw = CodeWriter()
with cw.block(before='if true', delim=('{', '}')):
    cw.emit('println!("hello, world.");')
print(cw.render())
```

Output:
```rust
if true {
    println!("hello, world.");
}
```

You can also set a default delimiter:

```python
cw = CodeWriter(default_delim=('{', '}'))
```
### Tabs

```python
cw = CodeWriter(use_tabs=True)
```

### Indent two spaces
```python
cw = CodeWriter(default_dent=2)
```

### Generate lists

```python
cw = CodeWriter()
cw.emit_list([], ('[', ']'), before='let li1 = ', after=';')
cw.emit_list(['1'], ('[', ']'), before='let li2 = ', after=';')
cw.emit_list(['1', '2', '3'], ('[', ']'), before='let li3 = ', after=';')
cw.emit_list(['1', '2', '3'], ('[', ']'), before='let li4 = ', after=';', compact=True)
print(cw.render())
```

Output:
```rust
let li1 = [];
let li2 = [1];
let li3 = [
    1,
    2,
    3,
];
let li4 = [1,
           2,
           3];
```

### Generate wrapped text

This is useful for documentation.

```python
# Artificially set col width low to show wrapped text
cw = CodeWriter(default_width=25)
cw.emit('/**')
cw.emit_wrapped_text(
    '@param param1 an explanation of what this argument does.',
    prefix=' * ',
    indent_after_first=True,
)
cw.emit('*/')
print(cw.render())
```

Output:
```java
/**
 * @param param1 an
 *     explanation of
 *     what this argument
 *     does.
*/
```

### Emit a preamble or header
```python
preamble = """\
This
is
a
preamble.
"""
cw = CodeWriter()
cw.emit_raw(preamble)
print(cw.render())
```

Output:
```
This
is
a
preamble.
```

### Trim trailing newlines

Sometimes you'll want a newline after every iteration of logic, but not for the
last iteration.

```python
cw = CodeWriter()
with cw.block(before='if true', delim=('{', '}')):
    for i in range(3):
        cw.emit('println!("{}");'.format(i))
        cw.emit()
print(cw.render())
```

Output:
```rust
if true {
    println!("0");

    println!("1");

    println!("2");

}
```

The gap after the last `println!()` is undesirable. To fix, do this:

```python
cw = CodeWriter()
with cw.block(before='if true', delim=('{', '}')):
    for i in range(3):
        cw.emit('println!("{}");'.format(i))
        cw.emit()
    cw.trim_last_line_if_empty()
print(cw.render())
```

Output:
```rust
if true {
    println!("0");

    println!("1");

    println!("2");
}
```

### Naming conventions

Depending on your target language, you may need to output names that are
PascalCase, camelCase, underscore_delimited, or dash-delimited.

```python
from code_writer import fmt_camel, fmt_dashes, fmt_pascal, fmt_underscores
# The input name can be a mix of formatting. These helpers will aggressively
# split the word and re-assemble as desired.
text = 'a-B-HiHo-merryOh_yes_no_XYZ'
assert fmt_camel(text) == 'aBHiHoMerryOhYesNoXyz'
assert fmt_dashes(text) == 'a-b-hi-ho-merry-oh-yes-no-xyz'
assert fmt_pascal(text) == 'ABHiHoMerryOhYesNoXyz'
assert fmt_underscores(text) == 'a_b_hi_ho_merry_oh_yes_no_xyz'
```
