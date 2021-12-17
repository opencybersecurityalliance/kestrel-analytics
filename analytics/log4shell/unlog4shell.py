import base64
import logging
import re

from lark import Lark, Transformer, exceptions
from urllib.parse import unquote

logger = logging.getLogger(__name__)


grammar = '''
// log4j substition parser

start: subst

subst: "${" prefix? default "}"

prefix: /[^:]*:/

default: "-"? (LETTER|DIGIT|OTHER)+

NAME: LETTER (LETTER|DIGIT|"_"|"-"|".")*

OTHER: "/"|"."|"_"|"-"|":"|" "|"="|"#"|"@"|"$"

%import common (LETTER, DIGIT)
'''

class _TranslateTree(Transformer):
    def __init__(self):
        super().__init__()

    def start(self, arg):
        return arg[0]

    def subst(self, args):
        if len(args) >= 2:
            # interpret args[0] as context (e.g. base64)
            prefix = args[0]
            if prefix == 'base64':
                value = base64.b64decode(args[1]).decode('utf-8')
            elif prefix == 'lower':
                if len(args) == 3 and args[1] == '' and args[2] == '':
                    # ${lower::} is probably not valid, but we should detect it anyway
                    value = ':'
                else:
                    value = args[1].lower()
            elif prefix == 'jndi':
                value = ':'.join(args)
            elif prefix == 'sys':
                value = '' # '${' + ':'.join(args) + '}'
            else:
                value = args[-1]
            return value
        return args[-1]

    def default(self, args):
        if args:
            #return ''.join(args).lstrip(':-')
            return ''.join(args).rpartition(':-')[2]
        return ''

    def prefix(self, args):
        if args and args[0]:
            return args[0].value.rstrip(':')
        return ''


parser = Lark(grammar, parser='lalr', # debug=True,
              transformer=_TranslateTree())


def deobfuscate(data):
    #print(Lark(grammar, parser='lalr').parse(data.lower()).pretty())
    try:
        result = parser.parse(data.lower())
    except exceptions.UnexpectedToken as e:
        #logger.error('%s', e, exc_info=e)
        result = data
    return result


def extract_innermost(data):
    stack = []
    match_lb = False
    start = 0
    stop = 0
    for pos, ch in enumerate(data):
        if match_lb and ch == '{':
            stack.append(pos - 1)
        elif match_lb and ch == '$':
            pass
        elif ch == '$':
            match_lb = True
        else:
            match_lb = False
        if ch == '}':
            if stack:
                start = stack.pop()
                stop = pos + 1
                break
    return start, stop


def check_string(s):
    # Check for a Java exception as a special case
    if re.match(r'.*Error looking up JNDI resource \[ldap:\/\/.+\/.*\].*', s):
        return s

    result = None
    while True:
        prev = s
        start, stop = extract_innermost(s)
        if start != stop:
            inner = s[start:stop]
            result = deobfuscate(inner)
            if result == inner:
                s = deobfuscate(s)
                return s
            if result.startswith('jndi:'):
                return result[5:]  # Remove jndi part
            if start and s[start - 1] == '$':
                # Trim double $
                start -= 1
            s = s[:start] + result + s[stop:]
            if prev == s:
                break
        else:
            break

    return None


def check_url(url):
    # We run unencode 3 times to handle all known in-the-wild in-log encodings
    return check_string(unquote(unquote(unquote(url))))


def check_payload(payload_bin):
    # Hopefully this is a log payload and not a packet payload!
    payload = base64.b64decode(payload_bin).decode('utf-8')
    # Use check_url here in case there's some URL-encoding
    return check_url(payload)
