##################################
#salf.pl
#section alphabetizer
#
# currently only for smart.otl but it can be expanded
#
# usage salf.pl
#
# recommended: salf.pl pc, salf.pl sc, salf.pl btp

#todo: test case
#got stuff!!!
#got stuff!!!!

#use Data::Dumper qw(Dumper);
#use List::MoreUtils qw(uniq);
use POSIX;

use strict;
use warnings;

my $didSomething = 0;
my $dupBytes = 0;
my %got = ();
my $noGlobals = 0;
my $dupes;

my @sects = ();
my $toSplit = "";

my $myd = getcwd();

my %list;
$list{"pc"} = "pc";
$list{"sc"} = "sc,sc1,sc2,sc3,sc4,scfarm,sce,scd,scc,scb,sca";
$list{"btp"} = "btp-rej,btp,btp-dis,btp-book,btp1,btp2,btp3,btp4,btp-farm,btp-e,btp-d,btp-c,btp-b,btp-a";

if ($myd eq "C:\\games\\inform\\compound.inform\\Source") { $toSplit = $list{"pc"}; }
if ($myd eq "C:\\games\\inform\\slicker-city.inform\\Source") { $toSplit = $list{"sc"}; }
if ($myd eq "C:\\games\\inform\\buck-the-past.inform\\Source") { $toSplit = $list{"btp"}; }

if (!defined($ARGV[0]))
{
  if (!$toSplit)
  {
  print ("Need alphabetical to sort, or -btp for all of BTP. PC and SC are largely redundant."); exit;
  }
}
else
{
  if ($ARGV[0] =~ /^-/) { $ARGV[0] =~ s/^-//; }
  if (defined($list{$ARGV[0]}))
  {
    $toSplit = $list{$ARGV[0]};
  }
  else
  {
    $toSplit = $ARGV[0];
  }
}

if (!$toSplit == -1) { print "Need a CSV of sections, or use -pc for ProbComp, -sc or BTP.\n"; exit; }

@sects = split(/,/, $toSplit);

my $infile = "c:\\writing\\smart.otl";
my $outfile = "c:\\writing\\temp\\smart.otl";

open(A, "$infile");
open(B, ">$outfile");

my $mysect;

while ($a = <A>)
{
  print B $a;
  if ($a =~ /^\\/)
  {
    for $mysect (@sects)
	{
	  if ($a =~ /^\\$mysect[=\|]/) { alfThis(); }
	}
  }
}

close(A);
close(B);

if (!$didSomething) { print "Didn't sort anything!\n"; exit; }

my $outDup = (-s $outfile) + $dupBytes;

if ((-s $infile) != $outDup)
{
  print "Uh oh, $infile and $outfile(+$dupBytes) didn't match sizes. Bailing.\n";
  print "" . (-s $infile) . " for $infile, " . (-s $outfile) . " for $outfile, total $outDup.\n";
  exit;
}

#die("$dupes duplicates $dupBytes bytes duplicated.");
my $cmd = "copy $outfile $infile";
print "$cmd\n";
`$cmd`;

sub alfThis
{
  $didSomething = 1;
  my @lines = ();
  my @uniq_no_case = ();
  if ($noGlobals) { %got = (); }


  while ($a = <A>)
  {
    chomp($a);
    if ($a !~ /[a-z0-9]/i)
    {
      #print "Last line $lines[-1]\n";
      last;
    }
    push(@lines, $a);
  }
  my @x = sort { comm($a) <=> comm($b) || "\L$a" cmp "\L$b" } @lines;
  #@x = @lines;

  for my $y (@x)
  {
    if (defined($got{simp($y)}) && ($got{simp($y)} == 1))
	{
	  print "Duplicate $y\n";
	  $dupBytes += length(lc($y))+2;
	  $dupes++;
	  #print "$dupBytes/$dupes total.\n";
	  next;
    }
	$got{simp($y)} = 1;
	push(@uniq_no_case, $y);
  }


  print B join("\n", @uniq_no_case);
  if ($#uniq_no_case > -1) { print B "\n"; }
  print B "$a\n";
  #print "$#lines ($#uniq_no_case unique) shuffled\n";
  return;
}

sub simp
{
  my $temp = $_[0];
  $temp = lc($_[0]);
  $temp =~ s/[\.!\/\?]//g;
  return $temp;
}

sub comm
{
  if ($_[0] =~ /^#/) { return 1; }
  return 0;
}