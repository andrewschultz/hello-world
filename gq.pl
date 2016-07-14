#gq.pl: stands for "grep quick"
#this shows where certain text I may've already used pops up in Roiling or Shuffling. It pegs them both as Shuffling << Roiling.
#-tb1 = table random, start with that word
#-tb = table random
#-t = table only
#usage
#gq.pl -tb rosco coors (matches both)
#gq.pl -tb rosco (matches one)
#gq.pl -tb1 rosco (matches starting with rosco)
#gq.pl -m 10 yes (matches 1st 10 yes's)
#
#

use POSIX;

my $gqfile = "c:/writing/scripts/gq.txt";

$count = 0;

$printTabbed = 1;
$printUntabbed = 1;

$pwd = getcwd();

if ($pwd =~ /oafs/) { @runs = ("oafs"); }
elsif ($pwd =~ /(threed|fourd)/) { @runs = ("opo"); }
elsif ($pwd =~ /Compound/i) { @runs = ("as"); }
elsif ($pwd =~ /slicker/i) { @runs = ("as"); }

while ($count <= $#ARGV)
{
  $a = @ARGV[$count];
  
  for ($a)
  {
  /^0$/ && do { processNameConditionals(); exit; };
  /^-?e$/ && do { `$gqfile`; exit; };
  /^\// && do { @thisAry[0] =~ s/^\///g; $onlyTables = 1; $onlyRand = 1; $firstStart = 1; $count++; next; };
  /^-?a$/ && do { $runAll = 1; $count++; next; }; # run all
  /^-o$/ && do { @runs = ("oafs"); $count++; next; }; # oafs?
  /,/ && do { @runs = split(/,/, $a); $count++; next; };
  /^-?n$/ && do { @runs = ("names"); $count++; next; }; # names
  /^-?(3d|3|4d|4)$/i && do { @runs = ("opo"); $count++; next; }; # 3dop try
  /^-?(c|as|sc|pc)$/i && do { @runs = ("as"); $count++; next; }; # Alec Smart?
  /^-?(r|roi|s|sa)$/i && do { @runs = ("sts"); $count++; next; }; # roiling original? (default)
  /^-sr$/ && do { $showRules = 1; $count++; next; }; # show the rules text is in
  /^-h$/ && do { $showHeaders = 1; $count++; next; };
  /^-p$/ && do { $headersToo = 1; $count++; next; };
  /^-nt$/ && do { $printTabbed = 0; $count++; next; };
  /^-x/ && do { $dontWant = 1; $count++; next; };
  /^-nd$/ && do { newDefault(@ARGV[$count+1]); $count++; next; };
  /^-ft$/ && do { $printUntabbed = 0; $count++; next; };
  /^-m$/ && do { $maxFind = @thisAry[1]; @thisAry = @thisAry[2..$#thisAry]; $count+= 2; next; };
  /^-t$/ && do { $onlyTables = 1; $count++; next; }; #not perfect, -h + -t = conflict
  /^-tb$/ && do { $onlyTables = 1; $onlyRand = 1; $count++; next; }; #not perfect, -h + -t = conflict
  /^-tb1$/ && do { $onlyTables = 1; $onlyRand = 1; $firstStart = 1; $count++; next; }; #not perfect, -h + -t = conflict
  /,/ && do { @runs = split(/,/, $a); $count++; next; };
  /^[\\0-9a-z]/ && do { if ($map{$a}) { print "$a -> $map{$a}, use upper case to avoid\n"; push(@thisAry, $map{$a}); } else { push(@thisAry, $a); } $count++; next; }; # if we want to use AS as a word, it would be in upper case
  print "Argument $a failed.\n"; usage();
  }

}
if (!@thisAry[0]) { die ("Need a process-able word for an argument."); }

processListFile();

if ($runAll)
{
  foreach $myrun (@availRuns)
  {
    processFiles($myrun);
  }
}
else
{
  foreach $myrun (@runs)
  {
    processFiles($myrun);
  }
}

sub processListFile
{
  open(A, $gqfile) || die ("Can't find $gqfile.");
  while ($a = <A>)
  {
    if ($a =~ /^#/) { next; }
    if ($a =~ /^;/) { last; }
	if ($a =~ /^MAP=/)
	{
	  chomp($a); $a =~ s/^MAP=//;
	  @b = split(/:/, $a);
	  @c = split(/,/, @b);
	  for (@c) { $map{$_} = @b[1]; }
	}
	if ($a =~ /^DEFAULT=/)
	{
	  $defaultString = $a; chomp($defaultString); $defaultString =~ s/DEFAULT=//;
	}
    if ($a =~ /^run=/)
	{
      chomp($a);
	  $a =~ s/.*=//g;
	  $currentLedger = $a;
	  push(@availRuns, $a);
	  next;
	}
	if ($a !~ /[a-z]/i) { $currentLedger = ""; next; }
	if ($currentLedger)
	{
	$cmds{$currentLedger} .= $a;
	}
	
  }
  close(A);
  if ($#runs == -1)
  {
    if ($defaultString) { @runs = ($defaultString); }
    else
    {
      die("No default string specified in $gqfile, and no project specified in the command line. Bailing.\n");
    }
  }
}

sub processFiles
{
  @x = split(/\n/, $cmds{$_[0]});
  foreach $cmd (@x)
  {
	@fileAndMarkers = split(/\t/, $cmd);
	processOneFile(@fileAndMarkers);
  }
  if ($#blanks > -1) { print "EMPTY FILES: " . join(", ", @blanks) . "\n"; }
  if (@errStuff[0]) { print "TEST RESULTS: $_[0],0," . $#errStuff+1 . ",0," . join("<br />", @errStuff) . "\n"; }
}

sub processOneFile
{
  my $inImportant = 1;
  my $alwaysImportant = 1;
  my $inTable = 0;
  my $line = 0;
  my $currentTable = "";
  my $foundOne = 0;
  my $latestRule;

  if ($_[1])
  {
    $inImportant = 0;
	$alwaysImportant = 0;
	@importants = split(/,/, $_[1]);
  }
  my $modFile = $_[0];
  if ($modFile =~ /story.ni/)
  {
    $modFile =~ s/\.inform.*/ MAIN/;
	$modFile =~ s/.*[\\\/]//;
  }
  if ($modFile =~ /(trizbort|i7x)/) { $modFile =~ s/.*[\\\/]//g; }
  open(A, "$_[0]") || die ("No $_[0]");
  while ($a = <A>)
  {
    if (($a =~ /^[a-z]/) && ($a !~ /\t/)) { $latestRule = "$a"; }
    if ($inImportant) { $idx++; }
    if ($a =~ /^\\/)
	{
      if ($_[1])
	  {
        for (@importants) { if ($a =~ /^\\$_[=\|]/) { $idx = 0; $inImportant = 1; $thisImportant = $a; chomp($thisImportant); $thisImportant =~ s/[\|=].*//g; } }
	  }
	  else { $thisImportant = $a; $thisImportant =~ s/^\\//g; $thisImportant =~ s/[=\\].*//g; chomp($thisImportant); }
	}
    $line++;
	if ($a =~ /^table/) { $idx = -1; $currentTable = $a; $currentTable =~ s/ *\[.*//g; chomp($currentTable); $inTable = 1; }
	if ($a !~ /[a-z]/i) { $currentTable = ""; $inTable = 0; if (!$alwaysImportant) { $inImportant = 0; $thisImportant = ""; } }
	my $crom = cromu($a);
    if ($inImportant && $crom)
	{
	  if ($dontWant) { push (@errStuff, "$modFile L$idx"); }
	  if (!$foundOne) { print "Results for $modFile:\n"; }
	  $foundOne++;
	  print "$modFile($line";
	  if ($currentTable) { print ",$currentTable"; }
	  if ($thisImportant) { print ",$thisImportant,L$idx"; }
	  chomp($a);
	  print "): $a";
	  if ($crom == 2) { print " **PLURAL**"; }
	  print "\n";
	  if ($showRules) { print "RULE=$latestRule"; }
	}
  }
  close(A);
  if (!$foundOne) { push (@blanks, $modFile); }
}

sub processNotes
{
  open(A, "c:/writing/$_[0]") || open(A, "c:/writing/dict/$_[0]") || open(A, "c:/games/inform/roiling.inform/source/$_[0]") || die ("Can't open $_[0] file.");
  print "In notes file $_[0]:\n"; $foundSomething = 0;
  $section = "";
  $lines = 0;
  while ($a = <A>)
  { # all headers for ARO?
    if ($readStuff) {
	  $lines++;
	}
    if ($a =~ /^\\ana/i) { $readStuff = 1; $header = $a; $header =~ s/.*=//g; chomp($header); $foundSomething = 0; }
    if ($a =~ /^\\ifupdate/i) { $readStuff = 1; $header = $a; $header =~ s/.*=//g; chomp($header); }
	if ($a !~ /[a-z\"]/i) { if ($readStuff && !$foundSomething) { print "NOTHING in $lines lines of $header.\n"; } $readStuff = 0; $lines=0; }
	if ($a =~ /^\\/) { $section = $a; chomp ($section); $section =~ s/.*=//g; }
    if ($a =~ /^#/) { next; }
    if ($readStuff)
    {
      if (cromu($a)) { print "In $section: $a"; $foundSomething = 1; }
    }
  }
}

sub cromu
{
  if ($firstStart)
  {
    if (($_[0] !~ /^\"@thisAry[0]/i) && ($_[0] !~ /'@thisAry[0]'/i)){ return 0; }
  }
  
    $a =~ s/\[one of\]/\[\]/g;
    $a =~ s/\[end if\]/\[\]/g;
  
  if ($_[0] =~ /^(test|volume|chapter|book|part|section)/) { return 0; }
  #lumped together
  if ($#thisAry)
  {
  if ($_[0] =~ /\b@thisAry[0]@thisAry[1]\b/i) { return 1; }
  if ($_[0] =~ /\b@thisAry[1]@thisAry[0]\b/i) { return 1; }
  if ($_[0] =~ /\b@thisAry[0]@thisAry[1]s\b/i) { return 2; }
  if ($_[0] =~ /\b@thisAry[1]@thisAry[0]s\b/i) { return 2; }
  if (($_[0] =~ /\b@thisAry[0]\b/i) && ($_[0] =~ /\b@thisAry[1]s\b/i)) { return 2; }
  if (($_[0] =~ /\b@thisAry[0]s\b/i) && ($_[0] =~ /\b@thisAry[1](s)?\b/i)) { return 2; }
  }
  elsif ($#thisAry == 0)
  {
  if ($_[0] =~ /\b@thisAry[0]s\b/i) { return 2; }
  if ($_[0] =~ /\b@thisAry[0]\b/i) { return 1; }
  }
  
  #words apart
  for $tomatch (@thisAry)
  {
    if ($_[0] !~ /\b$tomatch\b/i) { if (($headersToo) && ($myHeader =~ /\b$tomatch\b/i)) { next; } return 0; }
  }
  return 1;
}

sub processStory
{
  if ($_[0] =~ /trizbort/i)
  {
    $fileName = $_[0];
  }
  else
  {
  $shortName = $_[0];
  if ($_[1] == 1) { $fileName = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/$_[0] Random Text.i7x"; } else { $fileName = "c:/games/inform/$_[0].inform/Source/story.ni"; }
  }
  open(A, "$fileName") || die ("No $fileName.");
  $foundSomething = 0;
  $count = 0;
  while ($a = <A>)
  {
    chomp($a);
	if (($a =~ /^[a-z].*: *$/i) || ($a =~ /^table/)) { $myHeader = $a;  $tabrow = 0; $blurby = 0;}
	if ($a =~ /^blurb/) { $blurby = 1; }
    $count++; $tabrow++;
    if ($a =~ /`/) { print "WARNING: Line $count has back-quote!\n$a"; }
	if ($a =~ /^table of /i) { $a =~ s/ *\[[^\]]*\].*//g; $thisTable = "($a) "; } elsif ($a !~ /[a-z]/i) { $thisTable = ""; }
	my $tmp = cromu($a);
    if ($tmp)
    {
      if ($a =~ /list of text variable/i)
      { processList($a); }
      else
      {
	    if ($showHeaders)
		{
		  if ($myHeader ne $lastHeader)
		    { print "======================$myHeader\n"; $lastHeader = $myHeader; }
		}
		if (isPrintable())
		{ if (!$foundSomething) { print "In $fileName:\n"; }
		print "$shortName L$count ";
		$totalFind++;
		  if ($thisTable)
		  { $tr2 = $tabrow - 2; print "/$tr2"; }
		  if ($showHeaders) { print ": $a\n"; }
		  else
		  {
		  print ": $thisTable$a";
		  if ($tmp == 2) { print "****PLURAL****"; }
		  print "\n";
		  }
		if ($maxFind == $totalFind) { print "Hit the limit.\n"; }
		  $foundSomething = 1;
		}
	  }
    }
  }

  close(A);
  if (!$foundSomething) { print "Nothing in $fileName.\n"; }

}

sub isPrintable
{
  if (($maxFind) && ($maxFind <= $totalFind)) { return 0; }
  if (!$onlyTables) { return 1; }
  if (($onlyRand) && ($thisTable) && ($blurby) && tabCheck($a)) { return 1; }
  if (tabCheck($a) && ($thisTable) && (!$onlyRand)) { return 1; }
  return 0;
}
sub tabCheck
{
  if (($_[0] =~ /^\t/) && ($printUntabbed)) { return 1; }
  if (($_[0] !~ /^\t/) && ($printTabbed)) { return 1; }
  return 0;
}

sub processList
{
  $listName = $a; $listName =~ s/.is a list of.*//gi;
  $yep = 0;
  if ($a =~ /\{/)
  {
    $a =~ s/^[^\"]*.//g; $a =~ s/\" *\}.*//g;
    @b = split(/\", \"/, $a);
    for (@b)
    {
	  my $temp = cromu($_);
      if ($temp)
      { $yep = 1; $foundSomething = 1; print "$listName (L$count): $_"; if ($temp == 2) { print " (PLURAL)"; } print "\n"; }
    }
    return;
  }
  print "$a\n";
  if (!$yep) { print "$shortName had @ARGV[0]/@ARGV[1] but not in same entry.\n"; }
}

sub newDefault
{
open(A, "$gqfile");
my $newDefLine = "DEFAULT=$_[1]";
while ($a = <A>)
{
  if ($a =~ /^DEFAULT/)
  {
    push (@array, $newDefLine);
  }
  else
  {
    push(@array, $a);
  }
}
close(A);
open(A, ">$gqfile");
print A join("\n", @array);

}

sub processNameConditionals
{
open(A, "C:/games/inform/roiling.inform/Source/story.ni") || die ("Can't open Roiling source.");

while ($a = <A>)
{
  if ($a =~ /section gender specific stubs/) { print "List of gender-says:\n"; $processTo = 1; next; }
  if ($processTo)
  {
    if ($a =~ /^section/) { last; }
	if ($a =~ /^to /)
	{
	  $b = $a; chomp($b); $b =~ s/to say //g; $b =~ s/:.*//g;
	  $c = <A>;
	  if ($c =~ /\[one of\]/)
	  {
	    $c =~ s/.*one of\]//g;
		$c =~ s/\[in random.*//g;
		$c =~ s/\[or\]/\//g;
	  }
	  else
	  {
	    $c =~ s/\[end if.*//g; $c =~ s/.*if [^\]]*\]//g; $c =~ s/\[else\]/\//g;
	  }
	  print "$b = $c";
	}
  }

}
close(A);

}

sub usage
{
print<<EOT;
0 = process Roiling name conditionals
-h = show headers
-p = headers too
-nt = print tabbed
-ft = print untabbed
-t = only in tables
EOT
exit;
}