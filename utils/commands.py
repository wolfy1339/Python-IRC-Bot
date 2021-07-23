import re


def normalize_whitespace(s: str, remove_newline: bool=True):
    """Normalizes the whitespace in a string; \s+ becomes one space."""
    if not s:
        return str(s)  # not the same reference
    starts_with_space = (s[0] in ' \n\t\r')
    ends_with_space = (s[-1] in ' \n\t\r')
    if remove_newline:
        newline_re = re.compile('[\r\n]+')
        s = ' '.join([i for i in newline_re.split(s) if bool(i)])
    s = ' '.join([i for i in s.split('\t') if bool(i)])
    s = ' '.join([i for i in s.split(' ') if bool(i)])
    if starts_with_space:
        s = ' ' + s
    if ends_with_space:
        s += ' '
    return s


def format_cmd_docs(docs: str, name: str):
    doclines = docs.splitlines()
    s = '{0!s} {1!s}'.format(name, doclines.pop(0))
    if doclines:
        doc = ' '.join(doclines)
        s = f'(\x02{s}\x0F) -- {doc}'
    return normalize_whitespace(s)
