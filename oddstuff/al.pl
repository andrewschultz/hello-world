use integer;

my %inStack;
@toggles = ( "off", "on" );

open(A, "scores.txt");

$wins = $losses = $wstreak = $lstreak = $lwstreak = $llstreak = 0;

if (!fileno(A)) { print "No scores.txt\n"; }
else
{
print "Reading scores...\n";
$stats = <A>; chomp($stats); @pcts = split(/,/, $stats);
$wins = @pcts[0];
$losses = @pcts[1];
$wstreak = @pcts[2];
$lstreak = @pcts[3];
$lwstreak = @pcts[4];
$llstreak = @pcts[5];
close(A);
}

init(); drawSix(); printdeck();

while (1)
{
  $q = <STDIN>;
  if ($q =~ /^debug/) { printdeckraw(); next; }
  if ($q =~ /^d/) { drawSix(); printdeck(); next; }
  if ($q =~ /^h/) { showhidden(); next; }
  if ($q =~ /^l=/i) { loadDeck($q); next; }
  if ($q =~ /^c/) { $collapse = !$collapse; print "Card collapsing @toggles[$collapse].\n"; next; }
  if ($q =~ /^s=/i) { saveDeck($q); next; }
  if ($q =~ /^t=/i) { loadDeck($q, "debug"); next; }
  if ($q =~ /^$/) { printdeck(); next; }
  if ($q =~ /^v/) { $vertical = !$vertical; print "Vertical view @toggles[$vertical].\n"; next; }
  if ($q =~ /^z/) { print "Time passes more slowly than if you actually played the game."; next; }
  if ($q =~ /^ry/) { if ($drawsLeft) { print "Forcing restart despite draws left.\n"; } doAnotherGame(); next; }
  if ($q =~ /^r/) { if ($drawsLeft) { print "Use RY to clear the board with draws left.\n"; next; } doAnotherGame(); next; }
  if ($q =~ /^%/) { stats(); next; }
  if ($q =~ /^[1-6] *[1-6]/) { tryMove($q); next; }
  if ($q =~ /^[1-6][1-6][^1-9]/) { $q = substr($q, 0, 2); tryMove($q); tryMove(reverse($q)); next; }
  if ($q =~ /^[1-6][1-6][1-6]/)
  { # detect 2 ways
    @x = split(//, $q);
	tryMove("@x[0]@x[1]");
	tryMove("@x[0]@x[2]");
	tryMove("@x[1]@x[2]");
	next;
  }
  if ($q =~ /^[qx]/) { last; }
  if ($q =~ /^\?/) { usage(); next; }
#cheats

  print "That wasn't recognized. Push ? for usage.\n";
}
exit;

sub doAnotherGame
{
if ($youWon) { $youWon = 0; $wins++; $wstreak++; $lstreak=0; if ($wstreak > $lwstreak) { $lwstreak = $wstreak; } }
elsif ($hidCards == 16) { }
else { $losses++; $wstreak = 0; $lstreak++; if ($lstreak > $llstreak) { $llstreak = $lstreak; } }

open(A, ">scores.txt");
print A "$wins,$losses,$wstreak,$lstreak,$lwstreak,$llstreak";
close(A);
init(); drawSix(); printdeck();
}

sub saveDeck
{
  chomp($_[0]);
  my $filename = "al.txt";
  
  open(A, "alt.txt");
  open(B, ">albak.txt");
  while ($a = <A>)
  {
	if ($a =~ /^;/) { last; }
    print B $a;
    if ($a =~ /^s=$_[0]/)
	{
	  $overwrite = 1;
	  for (1..6) { print B join(",", @{$stack[$_]}); print B "\n"; }
	  for (1..6) { <A>; }
	}
  }
  
  if (!$overwrite)
  {
    print B "$_[0]\n";
	  for (1..6) { print B join(",", @{$stack[$_]}); print B "\n"; }
	  for (1..6) { <A>; }
  }
  
  close(A);
  close(B);
  
  `copy albak.txt al.txt`;

  print "OK, saved.\n";
  printdeck();
}

sub loadDeck
{
  if ($_[1] =~ /debug/) { $filename = "alt.txt"; print "DEBUG test\n"; } else { $filename="al.txt"; }
  chomp($_[0]);
  my $search = $_[0]; $search =~ s/^[lt]/s/gi;
  open(A, "$filename");
  
  while ($a = <A>)
  {
    chomp($a);
    if ($a eq $search)
	{
	print "Found $search in $filename.\n";
    for (1..6) { $a = <A>; chomp($a); @{$stack[$_]} = split(/,/, $a); }
	printdeck();
	close(A);
	return;
	}
  }
  
  print "No $search found in $filename.\n";
}

sub setPushEmpty
{
@stack = (
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[-1, 10, 9, 5, 4],
[],
[],
[],
[],
);
}

sub init
{

$hidCards = 16;
$cardsInPlay = 16;
$drawsLeft = 6;

for (1..52) { $inStack{$_} = 1; }

@stack = (
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[-1, -1, -1],
[-1, -1, -1],
[-1, -1],
[-1, -1],
[-1, -1, -1],
[-1, -1, -1],
);

}

sub drawSix
{
if ($drawsLeft == 0) { print "Can't draw any more!\n"; return; }
for (1..6)
{
  push (@{$stack[$_]}, randcard());
}
$drawsLeft--;
$cardsInPlay += 6;
}

sub randcard
{
  $rand = (keys %inStack)[rand keys %inStack];
  delete $inStack{$rand};
  #print "Returning $rand\n";
  return $rand;
}

sub faceval
{
  if ($_[0] == -1) { return "**"; }
  my $x = $_[0] - 1;
  @sui = ("C", "D", "H", "S");
  @vals = ("A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K");
  my $suit = @sui[$x/13];
  return "$vals[$x%13]$suit";
  
}

sub printdeck
{
  if ($vertical)
  { printdeckvertical(); }
  else
  { printdeckhorizontal(); }
}

sub printdeckhorizontal
{
  $chains = 0; $order = 0;
  for $d (1..6)
  {
    $thisLine = "$d:";
    for $q (0..$#{$stack[$_]})
	{
	$t1 = $stack[$d][$q];
	if (!$t1) { last; }
	$t2 = $stack[$d][$q-1];
	if ($t1)
	{
	if (($q >= 1) && (($t1-1)/13 == ($t2-1)/13))
	{
	  if ($stack[$d][$q-1] -1 == $stack[$d][$q]) { $thisLine .= "-"; $chains++; $order++;}
	  elsif ($stack[$d][$q-1] -1 > $stack[$d][$q]) { $thisLine .= ":"; $order++; }
	  else { $thisLine .= " "; }
	}
	else #default
	{
	$thisLine .= " ";
	}
	}
	$thisLine .= faceval($stack[$d][$q]);
	}
	
	if ($collapse) { $thisLine =~ s/-[0-9AKQJCHDS-]+-/=/g; }
	print "$thisLine\n";
  }
  showLegalsAndStats();
}

sub printdeckraw
{
  for $d (1..6)
  {
    print "$d: ";
    for $q (0..$#{$stack[$_]}) { if ($stack[$d][$q]) { print $stack[$d][$q] . " "; } }
	print "\n";
  }
  showLegalsAndStats();
  print "Left: "; for $j (sort { $a <=> $b } keys %inStack) { print " $j"; } print "\n";
    print "$cardsInPlay cards in play, $drawsLeft draws left.\n";
}

sub printdeckvertical
{
  my @deckPos = (0, 0, 0, 0, 0, 0, 0);
  for (1..6) { print "   $_"; } print "\n";
  do
  {
  $foundCard = 0;
  for $row (1..6)
  {
    if ($stack[$row][@deckPos[$row]])
	{
	$foundCard = 1;
	if ($stack[$row][@deckPos[$row]] % 13 != 10) { print " "; }
	print " " . faceval($stack[$row][@deckPos[$row]]);
	@deckPos[$row]++;
	}
	else { print "    "; }
  }
  if ($foundCard) { print "\n"; }
  } while ($foundCard);
  showLegalsAndStats();
}

sub showLegalsAndStats
{
  my @idx;
  my @blank = (0,0,0,0,0,0);
  for $d(1..6)
  {
    $curEl = 0;
    while ($stack[$d][$curEl]) { $curEl++; }
	@idx[$d] = $curEl - 1;
	if (@idx[$d] < 0) { @blank [$d] = 1; @idx[$d] = 0; }
  }
  #for $thi (0..5) { print "Stack $thi (@idx[$thi]): $stack[$thi][@idx[$thi]]\n"; }
  print "Legal moves:";
  for $from (1..6)
  {
    for $to (1..6)
	{
	  if ($from == $to) {}
	  elsif (@blank[$to] == 1) { print " $from$to"; }
	  elsif (cromu($stack[$from][@idx[$from]], $stack[$to][@idx[$to]]))
	  {
	    print " ";
	    $thisEl = @idx[$from];
	    while ($thisEl > 0)
		{
		  if (($stack[$from][$thisEl-1] == $stack[$from][$thisEl] + 1) && ($stack[$from][$thisEl-1] % 13))
		  {
		    $thisEl--;
		  }
		  else { last; }
		}
		if ($thisEl > 0)
		{#print "- $thisEl:" . ($stack[$from][$thisEl-1] - 1) / 13 . ($stack[$from][$thisEl] - 1) / 13;
		if ((($stack[$from][$thisEl-1] - 1) / 13) != (($stack[$from][$thisEl] - 1) / 13))
		  {
		  print "*";
		  }
		elsif (($stack[$from][$thisEl-1] < $stack[$from][$thisEl]) && ($stack[$from][$thisEl-1] != -1))
		  {
		  print "<";
		  }
		}
		if ((($stack[$from][$thisEl-1] - 1) / 13) == (($stack[$from][$thisEl] - 1) / 13))
		{
		  if ((($stack[$from][$thisEl] - 1) / 13) == (($stack[$to][@idx[$to]] - 1) / 13))
		  {
		    if (($stack[$from][$thisEl] < $stack[$to][@idx[$to]]) && ($stack[$from][$thisEl] < $stack[$from][$thisEl-1]))
			{
			  print "C";
			}
		  }
		}
		print "$from$to";
		if (($stack[$from][$thisEl] == $stack[$to][@idx[$to]] - 1) && ($stack[$from][$thisEl] % 13)) { print "+"; }
	  }
	}
  }
  print "\n";
  print "$cardsInPlay cards in play, $drawsLeft draws left, $hidCards hidden cards, $chains chains, $order in order.\n";
}

sub cromu
{
  if ($_[0] > $_[1]) { return 0; }
  my $x = ($_[0] - 1) / 13;
  my $y = ($_[1] - 1) / 13;
  #print "$_[0] vs. $_[1]: $x =? $y\n";
  if ($x != $y) { return 0; }
  return 1;
}

sub tryMove
{
  my @q = split(/ */, $_[0]);
  my $from = @q[0];
  my $to = @q[1];
  
  #print "$_[0] becomes $from $to\n";
  
  if ($from==$to) { print "The numbers should be different.\n"; return; }
  
  if (!$stack[$from][0]) { print "Empty row/column."; return; }

  my $toEl = 0;
  my $fromEl = 0;
  while ($stack[$to][$toEl])
  {
    #print "Skipping $stack[$to][$toEl]\n";
	$toEl++;
  }
  $toEl--;
  #print "$toEl elts\n";

   while ($stack[$from][$fromEl]) { $fromEl++; }
  $fromEl--;
  #print "$fromEl elts\n";
  #print "From " . $stack[$from][$fromEl] . "\n";
  #print "To " . $stack[$to][$toEl] . "\n";
  if (($toEl > -1) && ($fromEl > -1))
  {
	if (!cromu($stack[$from][$fromEl], $stack[$to][$toEl]))
	{
	  print "Card needs to be placed on empty stack or a same-suit card of greater value (kings high).\n";
	  return;
	}
  }

  #print "Start at $fromEl\n";
  while ($fromEl > 0)
  {
    if (($stack[$from][$fromEl-1] != $stack[$from][$fromEl] + 1) || ($stack[$from][$fromEl] % 13 == 0)) { last; }
	$fromEl--;
  }
  #print "Going from $from-$fromEl to $to-$toEl\n";
  while ($stack[$from][$fromEl])
  {
  push (@{$stack[$to]}, $stack[$from][$fromEl]);
  splice (@{stack[$from]}, $fromEl, 1);
  }
  if ($stack[$from][0] == -1) #see about turning a card over
  {
    $fromLook = 0;
	while ($stack[$from][$fromLook] == -1) { $fromLook++; }
	if ($stack[$from][$fromLook] == 0)
	{
	$fromLook--;
	$stack[$from][$fromLook] = randcard; $hidCards--;
	}
  }
  printdeck();
  checkwin();
  
}

sub showhidden
{
  print "Still off the board: "; for $j (sort { $a <=> $b } keys %inStack) { print " " . faceval($j); } print "\n";
}

sub checkwin
{
  my $suitsDone = 0;
  
  OUTER:
  for $stax (1..6)
  {
    @x = @{$stack[$stax]};
	if (@x == 0) { next; }
	if (@x % 13) { next; }
	if ($#x != 12) { next; }
	$lasty = @x[0];
	for (1..$#x)
	{
	  if (@x[$_] != $lasty - 1)
	  {
	    #print "$stax failed at $_.\n";
        next OUTER;
	  }
	  $lasty--;
	}
	$suitsDone++;
  }
  if ($suitsDone == 4) { print "You win! Push enter to restart."; $x = <STDIN>; $youWon = 1; doAnotherGame(); return; }
  elsif ($suitsDone) { print "$suitsDone suits on their own row/column.\n"; }
}

sub stats
{
 print "$wins wins $losses losses\n";
 if ($wstreak) { print "current streak = $wstreak wins\n"; }
 elsif ($lstreak) { print "current streak = $lstreak losses\n"; }
 print "Longest streak $lwstreak wins $llstreak losses\n";
 printf("Win percentage = %d.%02d", ((100*$wins)/($wins+$losses)), ((10000*$wins)/($wins+$losses)) % 100);
}

sub usage
{
print<<EOT;
[1-6][1-6] moves stack a to stack b
[1-6][1-6]0 (or any character moves stack a to stack b and back
[1-6][1-6][1-6] moves from a to b, a to c, b to c.
v toggles vertical view (default is horizontal)
q/x quits
r restarts
(blank) prints the screen
d draws 6 cards (you get 5)
s=saves deck name
l=loads deck name
t=loads test
EOT
}