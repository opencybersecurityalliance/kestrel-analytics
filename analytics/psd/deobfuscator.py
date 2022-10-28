"""PowerShell De-obfuscator

Basic idea is to use Python's built-in tokenizer module, even though
Python != PowerShell.  There are still some issues here:

1. PowerShell Cmdlets use `-` in the name, e.g. `New-Object`
2. Some operators start with `-`, as do cmdlet options
3. Variable names can start with numbers?
4. Only handle some obfuscation techniques, but there are way more
5. probably a bunch more I can't think of right now

"""

import base64
import re
from io import BytesIO
from tokenize import tokenize, TokenInfo, DEDENT, ENCODING, ERRORTOKEN, INDENT, NAME, NUMBER, OP, STRING

# Use these to extract the encoded part
BASE64_RE = r"'?([A-Za-z\d/\+]+={0,2})'?"
PS_ENC_RE = r"-enc(odedcommand)? *" + BASE64_RE
PS_COM_RE = r"-[Cc][Oo][Mm][Mm][Aa][Nn][Dd] *'(.*)'"
PATH_RE = r"(/[A-Za-z0-9\._-]*)+"


KEYWORDS = [
    'begin',
    'break',
    'catch',
    'class',
    'continue',
    'data',
    'define',
    'do',
    'dynamicparam',
    'else',
    'elseif',
    'end',
    'enum',
    'exit',
    'filter',
    'finally',
    'for',
    'foreach',
    'from',
    'function',
    'hidden',
    'if',
    'in',
    'param',
    'process',
    'return',
    'static',
    'switch',
    'throw',
    'trap',
    'try',
    'until',
    'using',
    'var',
    'while',
]

LITERALS = [
    'null',
    'true',
    'false',
]


OPERATORS = [
    'eq', 'ieq', 'ceq',
    'ne', 'ine', 'cne',
    'gt', 'igt', 'cgt',
    'ge', 'ige', 'cge',
    'lt', 'ilt', 'clt',
    'le', 'ile', 'cle',
    'like', 'ilike', 'clike',
    'notlike', 'inotlike', 'cnotlike',
    'match', 'imatch', 'cmatch',
    'notmatch', 'inotmatch', 'cnotmatch',
    'replace', 'ireplace', 'creplace',
    'contains', 'icontains', 'ccontains',
    'notcontains', 'inotcontains', 'cnotcontains',
    'in',
    'notin',
    'is',
    'isnot',
    'join',
    'band', 'bnot', 'bor', 'bxor',
    'shl', 'shr',
]


def pstokenize(data: str):
    """
    A generator that's a wrapper around Python's tokenize, adapting it
    to handle PowerShell.

    """
    stack = []

    # (ab)use the Python built-in tokenizer (which is for Python, not PowerShell)
    for token in tokenize(BytesIO(data.encode("utf-8")).readline):
        if token.type in (ENCODING, INDENT, DEDENT):
            continue
        if token.type == NAME:
            if stack:
                prev = stack[-1]
                if prev.type == OP and prev.string == '-':
                    if len(stack) == 2:
                        # Found a CmdLet!
                        first = stack[0]
                        stack = []
                        value = ''.join([t.string for t in (first, prev, token)])
                        yield TokenInfo(OP, value, first.start, token.end, token.line)
                    else:
                        # Operator
                        stack.pop()
                        yield TokenInfo(OP, '-' + token.string, prev.start, token.end, token.line)
                elif prev.type == NAME or prev.string == '$':
                    # Merge
                    stack.pop()
                    stack.append(TokenInfo(NAME, prev.string + token.string, prev.start, token.end, token.line))
                else:
                    # Stash it and look ahead
                    stack.append(token)
            else:
                # Stash it and look ahead
                stack.append(token)
        elif token.type == NUMBER:
            if stack:
                prev = stack[-1]
                if prev.type == NAME or prev.string == '$':
                    # Merge
                    stack.pop()
                    stack.append(TokenInfo(NAME, prev.string + token.string, prev.start, token.end, token.line))
                else:
                    # Error?  Flush the stack.
                    for old in stack:
                        yield old
                    stack = []
                    yield token
            else:
                yield token
        elif token.type == OP and token.string == '-':
            # Check stack to see if it's a cmdlet
            if stack:
                prev = stack[-1]
                if token.start == prev.end and not prev.string.startswith('$'):
                    # it's cmdlet
                    stack.append(token)
                else:
                    # there was whitespace, so this must be an operator
                    # Pop previous and push this one
                    stack.pop()
                    stack.append(token)
                    yield prev
            else:
                # Need to save it
                stack.append(token)
        elif token.type == ERRORTOKEN and token.string == '$':
            # Starting a var?
            if stack:
                # Error?  Flush the stack.
                for old in stack:
                    yield old
                stack = []
            stack.append(token)
        elif token.type == ERRORTOKEN and token.string == ' ':
            pass  # Not sure what happened here
        else:
            for old in stack:
                yield old
            stack = []
            yield token


def itoa(match):
    i = int(match.group(1))
    c = chr(i)
    return f"'{c}'"


def reformat(input_script):
    """
    Try to format/pretty-print `input_script`, which should be PowerShell code.
    """

    if not isinstance(input_script, str):
        return input_script

    output_script = ''  # Our output
    indent = 0          # Indentation level
    TAB = '    '        # Use 4 spaces instead of \t

    def check_last(c):
        return output_script and output_script[-1] == c

    def newline():
        return f'\n{indent * TAB}'

    for toktype, tokval, _, _, _ in pstokenize(input_script):
        val = tokval
        pre = ''
        post = ''
        if toktype in (ENCODING, INDENT, DEDENT):
            continue
        if tokval == '}':
            indent = 0 if indent <= 0 else indent - 1  # De-indent a level
            pre = newline()
            post = newline()
        elif tokval == '{':
            indent += 1
            pre = ' '
            post = newline()
        elif tokval == ';':
            if check_last('\n'):
                val = ''
            else:
                post = newline()
        elif toktype == NAME:
            val = tokval.lower()
            if val in KEYWORDS:
                post = ' '
        elif toktype == STRING:
            if tokval[0] == '"':
                # Process nonsense escapes
                val = re.sub(r'`([^abefnrtuv0])', r'\1', tokval)
                if check_last('.'):  # For things like blah."GetField"(...)
                    val = val.strip('"').lower()
            pre = post = ''
        elif tokval in [',']:
            # Only want a space after, not before
            pre = ''
            post = ' '
        elif tokval in ['.', '(', ')', '[', ']', "'", ':']:
            # No spaces
            pre = post = ''
        elif toktype == OP:
            val = tokval.lower()  # For things like -ge
            pre = post = ' '

        if pre and (check_last(pre) or len(output_script) == 0):
            pre = ''
        output_script += pre
        output_script += val
        output_script += post

    ### Post-processing substitions

    # ASCII encoding
    output_script = re.sub(r'\[char\]([0-9]+)', itoa, output_script)

    # String concatention
    output_script = output_script.replace("' + '", '')

    result = []
    for line in output_script.split('\n'):
        match = re.search(r"\[convert\]::frombase64string\('" + BASE64_RE + r"'\)", line)
        if match:
            decoded = base64.b64decode(match.group(1)).decode('utf-16')
            line += f'  # {decoded}'  # Add base64-decoded string as comment
        result.append(line)

    return '\n'.join(result)


def decode(s):
    """
    Safely base64-decode `s`

    The encoded string is expected to be UTF-16 since it's Windows
    """
    if isinstance(s, str):
        if bool(re.match(BASE64_RE, s)):
            try:
                return base64.b64decode(s).decode('utf-16')
            except:
                pass
        return s
    return None
