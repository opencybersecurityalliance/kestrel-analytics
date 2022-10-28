import re

from tokenize import ENDMARKER

import pytest

from deobfuscator import PS_ENC_RE, decode, pstokenize, reformat

@pytest.mark.parametrize(
    "data, tokvals",
    [
        ('MaJOr -Ge', ['MaJOr', '-Ge']),
        ('New-ObjECT', ['New-ObjECT']),
        (';-join', [';', '-join']),
        ('if(foo){}', ['if', '(', 'foo', ')', '{', '}']),
        ('$8foo=1', ['$8foo', '=', '1']),
        ('$_-bxor', ['$_', '-bxor']),
        ('Clear-Variable -Name MyVariable', ['Clear-Variable', '-Name', 'MyVariable']),
        ('$MyVariable=$null', ['$MyVariable', '=', '$null']),
        ('$i,$j,$k = 10, "red", $true', ['$i', ',', '$j', ',', '$k', '=', '10', ',', '"red"', ',', '$true']),
    ]
)
def test_pstokenize(data, tokvals):
    for tok in pstokenize(data):
        if tok.type == ENDMARKER:
            break
        print(tok)
    results = [t.string for t in list(pstokenize(data)) if t.string]
    assert results == tokvals


@pytest.mark.parametrize(
    "cmdline, encoded, decoded",
    [
        ("powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc 'VwByAGkAdABlAC0ATwB1AHQAcAB1AHQAIAAiAFQAcgB5ACAASABhAHIAZABlAHIAIgAgAA=='",
         'VwByAGkAdABlAC0ATwB1AHQAcAB1AHQAIAAiAFQAcgB5ACAASABhAHIAZABlAHIAIgAgAA==',
         'write-output "Try Harder"'),
    ]
)
def test_deobfuscate(cmdline, encoded, decoded):
    match = re.search(PS_ENC_RE, cmdline, flags=re.IGNORECASE)
    enc = match.group(2) if match else None
    assert enc == encoded
    dec = reformat(decode(enc))
    assert dec == decoded
