########################################
#
# 2dy.pl
#
# opens today's file or the one before that
#
# creates a new daily file if one hasn't been created for a week
#

use lib "c:\\writing\\scripts";
use i7;
use strict;
use warnings;

my $section = "";

my $absBack = 0;
my $maxBack = 7;

my $printInitSections = 0;    # -ps prints sections on file creation and dies

my $theMinus = 0;             # this is how many days precisely to go back

my $count     = 0;
my $filesBack = 1;
my $backSoFar = 0;

my $verbose = 0;

while ( $count <= $#ARGV ) {
  my $arg = lc( $ARGV[$count] );
  $arg =~ s/^-//;
  if    ( $arg =~ /ps/ )       { $printInitSections = 1; }
  elsif ( $arg =~ /^[0-9]+$/ ) { $filesBack         = $arg; $maxBack = 365 if ($maxBack == 7); }
  elsif ( $arg =~ /^-+[0-9]+$/ ) { $theMinus = $arg; $theMinus =~ s/^.//; }
  elsif ( $arg =~ /^m[0-9]+$/ ) { $maxBack = $arg; $maxBack =~ s/^.//; }
  elsif ( $arg =~ /^a[0-9]+$/ ) { $absBack = $arg; $absBack =~ s/^.//; }
  elsif ( $arg =~ /^[0-9]+v/) { $verbose = $arg; $verbose =~ s/v//g; }
  elsif ( $arg =~ /^[a-z]+$/ )  { $section = $arg; }
  else                          { print("Bad input $arg"); exit(); }
  $count++;
}

my $dailyToOpen = "";

if ($theMinus) {
  my $fileName = "c:/writing/daily/" . daysAgo($theMinus);
  if ( !-f $fileName ) {
    die("No file $fileName. We will not create it by force.");
  }
}
elsif ($filesBack) {
  my $lastDailyDone = "";
  for ( 0 .. $maxBack - 1 ) {
    print "back $_ " . daysAgo($_) . "\n" if $verbose >= 2;
    my $dailyCandidate = "c:/writing/daily/" . daysAgo($_);
    my $dailyDone      = "c:/writing/daily/done/" . daysAgo($_);
    if ( -f $dailyCandidate ) {
      $backSoFar++;
      if ( $backSoFar == $filesBack ) {
        $theMinus    = $_;
        $dailyToOpen = $dailyCandidate;
        print("Going back $theMinus days to get to $dailyCandidate.\n");
        openFileSection( $dailyToOpen, $section );
        last;
      }
	  print "Found daily file $backSoFar = $dailyCandidate" if $verbose >= 1;
    }
    $lastDailyDone = $dailyCandidate
      if ( -f $dailyDone ) && ( !$lastDailyDone );
  }
  if ($lastDailyDone) {
    print(
"Could not go $filesBack files back and could not create new file. Only went $backSoFar. Last done file was $lastDailyDone. Expand maxBack from $maxBack to see more.\n"
    );
    exit;
  }
  else {
    print("Found nothing. I'm going to create and open a new daily file.\n");
	exit();
  }
}
else {
  die("I couldn't find anything to do just now.");
}

my (
  $second,     $minute,    $hour,
  $dayOfMonth, $month,     $yearOffset,
  $dayOfWeek,  $dayOfYear, $daylightSavings
) = localtime( time - 86400 * $theMinus );

my $fileName = sprintf(
  "c:/writing/daily/%d%02d%02d.txt",
  $yearOffset + 1900,
  $month + 1, $dayOfMonth
);

my $fileDoneName = sprintf(
  "c:/writing/daily/done/%d%02d%02d.txt",
  $yearOffset + 1900,
  $month + 1, $dayOfMonth
);

print("Looking up $fileName.\n");
if ( -f $fileDoneName ) {
  print(
    "You already threw that file ($fileDoneName) in a Done folder. Exiting.");
  exit;
}

# here we create the file if it is not there
if ( ( !-f $fileName ) || ( -s $fileName == 0 ) || $printInitSections ) {
  open( A, "c:/writing/scripts/2dy.txt" );
  my @subjArray = ();
  while ( $a = <A> ) {
    next if $a =~ /^#/;
    chomp($a);
    ( my $modLine = $a ) =~ s/=[^,]*//g;
    @subjArray = split( /,/, $modLine );
    die( join( ", ", @subjArray ) ) if $printInitSections;
    ; # example of default = ( "qui", "spo", "aa", "btp", "sh", "sp", "nam" ) printed in order on separate lines from qui=quick,spo=spo,aa,btp,sh,sp,nam;
    last;
  }
  open( A, ">>$fileName" );
  for (@subjArray) { print A "\n\\$_\n"; }
  close(A);
  system($fileName);

  #`touch $fileName`;
}
else {
  print "$fileName is there. Opening (section $section) with Notepad++.\n";
  openFileSection( $fileName, $section );
}

# subroutines

sub openFileSection {
  my $fileName = $_[0];
  my $section  = $_[1];

  if ( !$section ) {
    `"$fileName"`;
    exit();
  }

  my $lineNum = 0;

  open( A, $fileName );

  while ( $a = <A> ) {
    if ( $a =~ /\\$section/ ) {
      $lineNum = $.;
      last;
    }
  }

  if ( !$lineNum ) {
    print("Warning no section $section found. Opening the start.");
  }
  else {
    print("Opening line $lineNum of $fileName.");
  }

  `$npo $fileName -n$lineNum`;

  exit;

}

sub daysAgo {
  (
    $second,     $minute,    $hour,
    $dayOfMonth, $month,     $yearOffset,
    $dayOfWeek,  $dayOfYear, $daylightSavings
  ) = localtime( time - 86400 * $_[0] );
  return
    sprintf( "%d%02d%02d.txt", $yearOffset + 1900, $month + 1, $dayOfMonth );
}
