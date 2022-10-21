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
from tokenize import tokenize, DEDENT, ENCODING, INDENT, NAME, NUMBER, OP, STRING

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

    prev = None
    prevtype = None

    # (ab)use the Python built-in tokenizer (which is for Python, not PowerShell)
    for toktype, tokval, _, _, _ in tokenize(BytesIO(input_script.encode("utf-8")).readline):
        val = tokval
        if toktype == ENCODING:
            continue
        if toktype in (INDENT, DEDENT):
            val = ''
        elif tokval == '}':
            indent = 0 if indent <= 0 else indent - 1  # De-indent a level
            val = newline() + tokval + newline()
        elif tokval == '{':
            indent += 1
            if check_last(' '):
                val = ''
            else:
                val = ' '
            val += tokval + newline()
        elif tokval == ';':
            if check_last('\n'):
                val = ''
            else:
                val += newline()
        elif toktype == NAME:
            val = tokval.lower()
            if val in KEYWORDS and prev != '$':
                val = f'{val} '
            elif val in LITERALS:
                pass  # We already made it lower case
            elif val in OPERATORS:
                if prev == '-':
                    val = f'{val} '
                    # HACK: ensure a space in output *before* the dash:
                    output_script = output_script[:-1] + ' -'
            elif prev == '$':
                val = tokval.upper()  # Should we instead preserve case for var names?
            elif prevtype == NAME:
                val = f' {val}'
        elif toktype == STRING:
            if tokval[0] == '"':
                # Process nonsense escapes
                val = re.sub(r'`([^abefnrtuv0])', r'\1', tokval)
                if check_last('.'):  # For things like blah."GetField"(...)
                    val = val.strip('"').lower()
                elif not check_last(' '):
                    val = f' {val}'
        elif toktype == OP:
            # Add spaces around operators
            if val in ['+', '/', '*', '%', '=', '!=', '|']:
                # Add space before if necessary
                if check_last(' '):
                    pre = ''
                else:
                    pre = ' '
                val = f'{pre}{val} '
            elif val == ',':
                # Only want a space after, not before
                val = f'{val} '
            elif val == '-':
                # Tricky, since it's used for operators like -ge
                if prevtype == NUMBER:
                    val = f' {val} '
                #else:
                #    val = f' {val}'

        prev = tokval  # Save previous token
        prevtype = toktype
        output_script += val

    ### Post-processing substitions

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
