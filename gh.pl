#$procString="shu,roi,sts";

use File::Compare;

$ght = "c:/writing/scripts/gh.txt";

preProcessHashes();

$justPrint = 0;

$gh = "c:\\users\\andrew\\Documents\\github";

if (@ARGV[0] eq "-j") { shift(@ARGV); $justPrint = 1; }

if (@ARGV[0])
{
  if ($altHash{@ARGV[0]})
  { $procString = $altHash{@ARGV[0]}; }
  else
  { $procString = @ARGV[0]; }
}
else
{ print "Default string: $procString\n"; }

findTerms();

@procAry = split(/,/, $procString);

for (@procAry)
{
  if ($_ eq "-a")
  { $alph = 1; next; }
  if ($altHash{$_}) { $do{$altHash{$_}} = 1; print "$_ => $altHash{$_}\n"; }
  else
  {
  $do{$_} = 1;
  }
}

for $k (sort keys %poss) { if ($k =~ /,/) { print "$k is a valid key and maps to multiple others.\n"; } else { print "$k is a valid key.\n"; } }

processTerms();

sub processTerms
{
  $copies = 0; $unchanged = 0;
  open(A, $ght) || die ("No $ght");
  while ($a = <A>)
  {
    chomp($a);
    $b = $a;
    $b =~ s/=.*//g;
    if ($do{$b})
    {
	  $didOne = 1;
      $c = $a; $c =~ s/.*=//g; @d = split(/,/, $c);
	  $short = @d[0]; $short =~ s/.*[\\\/]//g;
	  if (compare(@d[0], "$gh\\@d[1]\\$short"))
	  {
	  #print "@d[0] $gh\\@d[1]\\$short\n";
      $cmd = "copy \"@d[0]\" $gh\\@d[1]";
	  $copies++;
	  if ($justPrint) { print "$cmd\n"; } else { `$cmd`; }
	  }
	  else
	  {
	  $unchanged++;
	  }
#      `$cmd`;
    }
  }
  if (!$didOne) { print "Didn't find anything for $procString."; }
  if ($copies > 0) { print "Copied $copies file(s), $unchanged unchanged.\n"; } elsif ($unchanged > 0) { print "All $unchanged file(s) were unchanged.\n"; }
}

##########################
# finds all valid terms

sub findTerms
{
open(A, $ght) || die ("Oops, couldn't open gh.txt.");

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /~/) { next; } #congruency
  if ($a =~ /^d:/) { next; } #default
  if ($a =~ /^;/) { last; }
  if ($a =~ /^#/) { next; }
  if ($a !~ /[a-z]/i) { next; }
  $a =~ s/=.*//g;
  $poss{$a} = 1;
}

close(A);
}

sub preProcessHashes
{
  open(A, "$ght") || die ("Can't open $ght.");
  while ($a = <A>)
  {
    chomp($a);
    if ($a =~ /^d:/)
	{
	  $procString = $a;
	  $procString =~ s/^d://gi;
	}
	if ($a =~ /~/)
	{
	  @b = split(/~/, $a);
	  $altHash{@b[0]} = @b[1];
	  #print "@b[0] -> @b[1]\n";
	}
  }
  close(A);
}