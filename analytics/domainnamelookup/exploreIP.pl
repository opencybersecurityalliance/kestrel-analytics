#!/bin/sh
#
# Copyright 2021 International Business Machines
# 
# License: Apache 2.0
#
#----------------------------------------------------------------------
#
# Doug Schales - schales@us.ibm.com
#
IP="$1"

#echo "Exploring <$IP>" 1>&2

rundig()
{
   TF=/tmp/dig.out.$$
   dig $* | sed -e '/^;/d' -e '/^$/d' |
   awk '$3 != "IN" || $4 != "SOA" {print}' > $TF
   N=`wc -l $TF | awk '{print $1}'`
   RC=0
   [ $N -eq 0 ] && RC=1
   cat $TF
   rm -f $TF
   return $RC
}

rundig_soa()
{
   TF=/tmp/dig.out.$$
   dig $* | sed -e '/^;/d' -e '/^$/d' > $TF
   N=`wc -l $TF | awk '{print $1}'`
   RC=0
   [ $N -eq 0 ] && RC=1
   cat $TF
   rm -f $TF
   return $RC
}

echo "ip: $IP"
(
  rundig_soa -x "$IP"
  case "$IP" in
  *:*) ;;
  *) 
     echo "$IP" | tr . ' ' |
     {
        read A B C D
	rundig $D.$C.$B.$A.in-addr.arpa. in ns ||
	rundig $C.$B.$A.in-addr.arpa. in ns ||
	rundig $B.$A.in-addr.arpa. in ns ||
	rundig $A.in-addr.arpa. in ns
     }
     ;;
  esac
) | 
awk '
  $3 == "IN" && $4 == "PTR" {RR["ptr"] = RR["ptr"] " " $5;}
  $3 == "IN" && $4 == "SOA" {RR["soa"] = RR["soa"] " " $5;}
  $3 == "IN" && $4 == "NS" {RR["ns"] = RR["ns"] " " $5;}
  END {
     for(rr in RR){
        printf("%s: %s\n", rr, RR[rr]);
     }
  }
' |
sed -e 's/\.$//' |
LANG=C sort -u

/opt/analytics/NameInspector.pl "$IP"

exit 0

