import base64
import logging
import re

from lark import Lark, Transformer, exceptions
from urllib.parse import unquote

logger = logging.getLogger(__name__)

grammar = '''
// log4j substition parser

start: subst

subst: "${" prefix? cstr default? "}"

cstr: (subst|/[^$]/|NAME)*

default: ":-" (LETTER|DIGIT|OTHER)+

prefix: (NAME)? ":"

NAME: LETTER (LETTER|DIGIT|"_"|"-"|".")*
OTHER: "/"|"."|"_"|":"

%import common (LETTER, DIGIT)
'''

class _TranslateTree(Transformer):
    def __init__(self):
        super().__init__()

    def start(self, arg):
        return '${' + arg[0] + '}'

    def subst(self, args):
        if len(args) == 3:
            if args[0] == 'jndi':
                return ':'.join(args)
            return args[2]
        if len(args) == 2:
            # interpret args[0] as context (e.g. base64)
            prefix = args[0]
            if prefix == 'base64':
                value = base64.b64decode(args[1]).decode('utf-8')
            elif prefix == 'lower':
                value = args[1].lower()
            elif args[0] == 'jndi':
                value = ':'.join(args)
            else:
                value = args[1]
            return value
        return args[0]

    def cstr(self, args):
        return ''.join(args)

    def default(self, args):
        if args:
            return ''.join(args)
        return ''

    def prefix(self, args):
        if args and args[0]:
            return args[0].value
        return ''

parser = Lark(grammar, parser='lalr', # debug=True,
              transformer=_TranslateTree())


def deobfuscate(data):
    try:
        result = parser.parse(data.lower())
    except exceptions.UnexpectedToken as e:
        logger.error('%s', e, exc_info=e)
        result = None
    return result


def check_string(s):
    for match in re.findall(r'(\$\{.*\})', s):
        deob = deobfuscate(match.lower())
        if deob and deob.find('${jndi:') > -1:
            return deob
    return None


def check_url(url):
    # We run unencode 3 times to handle all known in-the-wild in-log encodings
    return check_string(unquote(unquote(unquote(url))))


def check_payload(payload_bin):
    # Hopefully this is a log payload and not a packet payload!
    payload = base64.b64decode(payload_bin).decode('utf-8')
    # Use check_url here in case there's some URL-encoding
    return check_url(payload)
