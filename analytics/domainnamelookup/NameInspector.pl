#!/usr/bin/perl -w
#
# Copyright 2021 International Business Machines
# 
# License: Apache 2.0
#
#----------------------------------------------------------------------
#
# Version: 0.0.0, Release: 0
# Commit: 56570cc3bf1dc26373a4ecf9fce0956665e8327c
# Date: 2019/11/05 19:05:36
# schales@us.ibm.com

use strict;

use Time::Local;

sub Inspect($);

my $BASE='/opt/ibm/analytics';
my $WhoisCache='/tmp';

if(! -d $WhoisCache){
    system('/bin/mkdir', '-p', $WhoisCache);
}

my @WHOIS = ();
my %MAP = ();
my %RENAME = ();

my @tld=(
    ['\.com$', [-2,-1]],
    ['\.edu$', [-2,-1]],
    ['\...$', [-3,-1]]
    );

my $mapper = "/opt/analytics/WhoisMapper.cf";

if(! -f $mapper){
    die "$0: Missing Whois mapping file ($mapper).\n";
}

#my $DNSPTLD="/opt/analytics/dnspTLD";

open(FH, "<$mapper");
while(<FH>){
    chomp;
    next if(/^\s*$/);
    if(/^\#=/){
	s/^\#=//;
	my($k,$v) = split('=',$_);
	$MAP{$k} = $v;
    }
    elsif(/^\#\!/){
	s/^\#\!//;
	my($k,$v) = split('=',$_);
	$RENAME{$k} = $v;
    }
    next if(/^\#/);
    my($re,$id,$info,$flags) = split(',');
    push @WHOIS, [$re,$id,$info,$flags];
}
close(FH);

my %month = ('jan' => '01',
	     'feb' => '02',
	     'mar' => '03',
	     'apr' => '04',
	     'may' => '05',
	     'jun' => '06',
	     'jul' => '07',
	     'aug' => '08',
	     'sep' => '09',
	     'oct' => '10',
	     'nov' => '11',
	     'dec' => '12',
             'january' => '01',
	     'february' => '02',
	     'march' => '03',
	     'april' => '04',
	     'june' => '06',
	     'july' => '07',
	     'august' => '08',
	     'september' => '09',
	     'october' => '10',
	     'november' => '11',
	     'december' => '12'
);

my $cacheOnly = 0;
my $noWhoIs = 0;

if(scalar @ARGV != 0 && $ARGV[0] eq '--cached'){
    $cacheOnly = 1;
    shift @ARGV;
}

if(scalar @ARGV != 0 && $ARGV[0] eq '--nowhois'){
    $cacheOnly = 1;
    $noWhoIs = 1;
    shift @ARGV;
}

if(scalar @ARGV != 0){
    for my $name (@ARGV){
	Inspect($name);
    }
}
else {
    while(<STDIN>){
	chomp;
	my $name = $_;
	Inspect($name);
    }
}

sub whoisParse($)
{
    my($text) = @_;

    for my $x (@WHOIS){
	if($text =~ /$x->[0]/){
	    my @captured = ($1,$2,$3,$4,$5,$6,$7);
	    my $id = $x->[1];
	    my $info = $x->[2];
	    $info = '' if($info eq '%');
	    for my $f (0..$#captured){
		my $fn = $f+1;
		last if(!defined($captured[$f]));
		$id =~ s/%$fn/$captured[$f]/g;
		$info =~ s/%$fn/$captured[$f]/g;
	    }
	    if(defined($x->[3])){
		for my $c (split('',$x->[3])){
		    if($c eq 'U'){
			$info = uc $info;
		    }
		    elsif($c eq 'L'){
			$info = lc $info;
		    }
		    elsif($c eq 'M'){
			if(defined($MAP{$info})){
			    $info = $MAP{$info};
			}
		    }
		}
	    }
	    return ($id,$info,$x->[3]);
	}
    }
    return ();
}



sub fixDate($)
{
    my($date) = @_;

    $date =~ s/\s*\#[0-9]*\s*$//;
    $date =~ s/\s*$//;
    $date =~ s/^\s*$//;

    return undef if($date eq 'null');

    if($date =~ /^(\d\d\d\d)(\d\d)(\d\d)\s*/){
	if($1 > 1990 && $1 < 2040 &&
	   $2 >= 1 && $2 <= 12 &&
	   $3 >= 1 && $3 <= 31){
	    return timegm(0,0,0,$3,$2-1,$1);
	}
    }
    if($date =~ /^(\d\d\d\d)[\-\.\/]\s*(\d\d)[\-\.\/]\s*(\d\d)\s*/){
	return timegm(0,0,0,$3,$2-1,$1)
    }
    if($date =~ /^(\d\d\d\d)[\-\.\/]\s*(\d)[\-\.\/]\s*(\d\d)\s*/){
	return timegm(0,0,0,$3,$2-1,$1)
    }
    if($date =~ /^(\d\d)-([A-Za-z]+)-(\d\d\d\d)\s*/){
	if(defined($month{lc $2})){
	    return timegm(0,0,0,$1,$month{lc $2}-1,$3);
	}
    }
    if($date =~ /^[A-Z][a-z][a-z], ([A-Za-z]+) (\d+), (\d\d\d\d)$/){
	if(defined($month{lc $1})){
	    return timegm(0,0,0,$2,$month{lc $1}-1,$3);
	}
    }
    if($date =~ /^(\d*) ([A-Za-z]+) (\d\d\d\d)\s*/){
	if(defined($month{lc $2})){
	    return timegm(0,0,0,$1,$month{lc $2}-1,$3);
	}
    }
    if($date =~ /^[A-Z][a-z][a-z] ([A-Za-z]+) (\d+) \d\d:\d\d:\d\d \S+ (\d\d\d\d)$/){
	if(defined($month{lc $1})){
	    return timegm(0,0,0,$2,$month{lc $1}-1,$3);
	}
    }

    if($date =~ /^[A-Z][a-z][a-z] ([A-Za-z]+) (\d+) (\d\d\d\d)$/){
	if(defined($month{lc $1})){
	    return timegm(0,0,0,$2,$month{lc $1}-1,$3);
	}
    }


    if($date =~ /^(\d\d\d\d)[\-\.]([A-Za-z]+)[\-\.](\d+)\s*/){
	if(defined($month{lc $2})){
	    return timegm(0,0,0,$3,$month{lc $2}-1,$1);
	}
    }

    if($date =~ /^([0-9][0-9]?)-([A-Za-z]+)-(\d+)\s*/){
	if(defined($month{lc $2})){
	    return timegm(0,0,0,$1,$month{lc $2}-1,$3);
	}
    }

    if($date =~ /^(\d+)[\/\-\.](\d+)[\/\-\.](\d\d\d\d)\s*/){
	# Stupidly ambiguous format...
	if($2 > 12){
	    return timegm(0,0,0,$2,$1-1,$3);
	}
	if($1 > 12){
	    return timegm(0,0,0,$1,$2-1,$3);
	}
	return timegm(0,0,0,$2,$1-1,$3);
    }
    return 0 if($date eq 'None');
    print STDERR $date,"\n";
    return $date;
}

sub whois($)
{
    my($name) = @_;

    my $whoisDom = undef;
    my $domain = undef;

    if($name =~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/){
	$whoisDom = $name;
	$domain = $name;
    }
    else {
	my $n = $name;
	$n =~ s/\-\d+\.$//;

	#open(FH, "-|", $DNSPTLD, $n);
	#my $line = <FH>;
	#close(FH);
	#return undef if(!defined($line));
	#chomp($line);

	#$domain = (split(',', $line))[1];
	#return undef if(!defined($domain));

	$domain = $name;
	for my $r (@tld){
	    if($name =~ /$r->[0]/){
		my $s = $r->[1]->[0];
		my $e = $r->[1]->[1];
		$domain = join('.', (split(/\./, $name))[$s,$e]);
	    }
	}

	$whoisDom = $domain;
	$whoisDom =~ s/\.$//;
    }

    my @record = ();
    my %W = ();

    my $cached = 0;
    my $cacheName = $WhoisCache . '/' . $domain;

    my @INPUT = ();
    if(-s $cacheName){
	if($cacheOnly == 1 || -M $cacheName < 7){
	    open(FH, "<$cacheName");
	    @INPUT = <FH>;
	    close(FH);
	    $cached = 1;
	}
	else {
	    my $t = (stat($cacheName))[9];
	    my @x = gmtime($t);
	    my $d = sprintf("%04u%02u%02u", $x[5]+1900,$x[4]+1,$x[3]);
	    rename($cacheName, $cacheName . '-' . $d);
	    eval {
		$cached = 0;
		my $pid;
		alarm(15);
		$pid = open(FH, "-|", '/usr/bin/whois', $whoisDom);
		local $SIG{ALRM} = sub { kill(9, $pid); };
		my @t = <FH>;
		push @INPUT, @t;
		close(FH);
		alarm(0);
	    }
	}
    }
    elsif(!$noWhoIs){
	eval {
	    my $pid;
	    alarm(15);
	    $pid = open(FH, "-|", '/usr/bin/whois', $whoisDom);
	    local $SIG{ALRM} = sub { kill(9,$pid) };
	    $cached = 0;
	    @INPUT = <FH>;
	    close(FH);
	    alarm(0);
	}
    }
    
    my @whoisData;
    my $i = 0;
    while($i < scalar @INPUT){
	$_ = $INPUT[$i]; $i++;
	chomp;
	push @whoisData,$_;
	s/\s*$//;
	s/\.$//;
	push @record, $_;
	my $wrapped = 0;
      again:
	my ($id,$info,$flags) = whoisParse($_);
	if(defined($id)){
	    if($id eq 'ns'){
		push @{$W{$id}}, lc $info unless($info eq '');
	    }
	    elsif($id eq '@nslist'){
		my $exitIfBlank = 0;
		my $exitIfNotIndented = 0;
		if($info ne ''){
		    push @{$W{'ns'}}, lc $info;
		    $exitIfNotIndented = 1;
		}
		while($i < scalar @INPUT){
		    $_ = $INPUT[$i]; $i++;
		    push @whoisData,$_;
		    last if(/WHOIS lookup made/);
                    push @record, $_;
		    if(/^\s*$/){
			last if($exitIfBlank == 1);
			next;
		    }
		    elsif(/^\S+:/){
			goto again;
		    }
		    if(!/^\s+/ && $exitIfNotIndented == 1){
			last;
		    }
		    else {
			s/^\s*//;
			s/\s*$//;
			push @{$W{'ns'}}, (split(/\s+/))[0];
			$exitIfBlank = 1;
		    }
		}
	    }
	    elsif($wrapped == 0 && $id eq '+wrap'){
		my $d = $INPUT[$i]; $i++;
		push @record, $d;
		chomp($d);
		$_ .= ' ' . $d;
		$wrapped=1;
		goto again;
	    }
	    elsif($id eq '@join'){
		my $rest = $INPUT[$i]; $i++;
		chomp($rest);
		$_ = $_ . $rest;
		goto again;
	    }
	    else {
		if(defined($flags)){
		    if($flags =~ /1/){
			$W{$id} = $info if(defined($id) && $info ne '' && !defined($W{$id}));
		    }
		    elsif($flags =~ /X/){
			$W{$id} = $info if(defined($id) && $info ne '');
		    }
		    else {
			$W{$id} = $info if(defined($id) && $info ne '');
		    }
		}
		else {
		    $W{$id} = $info if(defined($id) && $info ne '' && !defined($W{$id}));
		}
	    }
	}
    }

    if($cached == 0 && $#whoisData != -1){
	open(FH, ">$cacheName");
	print FH join("\n", @whoisData),"\n";
	close(FH);
    }

    return %W;
}
    

sub Inspect($)
{
    my($name) = @_;

    #$name .= '.' if($name !~ /\.$/);

    my %whois = ();

    my @pieces = split(/\./, $name);

    while(1){
	%whois = ();
	my $lookupName = join('.', @pieces);
	%whois = whois($lookupName);

	if(scalar keys %whois != 0){
	    last if(!defined($whois{'error'}));
	    last if($whois{'error'} ne 'NXDOMAIN');
	}
	shift @pieces;
	last if(scalar @pieces < 2);
    }

    for my $key (sort keys %whois){
	my($kv,$v);

	$kv = $key;
	if(defined($RENAME{$key})){
	    if(!defined($whois{$RENAME{$key}})){
		$kv = $RENAME{$key};
	    }
	    else {
		next;
	    }
	}

	if($key eq 'ns'){
	    $v = join(',', @{$whois{$key}});
	}
	else {
	    $v = $whois{$key};
	    if($key eq 'created' || $key eq 'updated' ||
	       $key eq 'expires' || $key eq 'registered'){
		my $z = fixDate($v);
		next if(!defined($z));
		$v = $z . ' ' . $v;
	    }
	}
	printf("%s: %s\n", $kv, $v);
    }
}
