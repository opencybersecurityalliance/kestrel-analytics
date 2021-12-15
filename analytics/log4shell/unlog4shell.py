import base64
import logging
import sys

from lark import Lark, Transformer, exceptions

logger = logging.getLogger(__name__)

grammar = '''
// log4j substition parser

start: subst

subst: "${" prefix? cstr default? "}"

cstr: (subst|/[^$]/)*

default: ":-" (LETTER|DIGIT|OTHER)+

prefix: (NAME)? ":"

NAME: LETTER (LETTER|DIGIT|"_")*
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
        result = parser.parse(data)
    except exceptions.UnexpectedToken as e:
        logger.error('%s', e, exc_info=e)
        result = None
    return result


if __name__ == '__main__':
    print(deobfuscate(sys.argv[1]))
