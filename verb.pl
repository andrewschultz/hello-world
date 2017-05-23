####################################
#verb.pl
#
#lets you write code for a verb
#

use strict;
use warnings;

use Win32::Clipboard;

my $clip = Win32::Clipboard::new();
my @verbs;

if (!defined($ARGV[0])) { usage(); }
if ($ARGV[0] =~ /\?/) { usage(); }
if ($ARGV[0] =~ /,/) { @verbs = split(/,/, $ARGV[0]); } else { @verbs = @ARGV; }

my $v;
my $code = "";
my $oow;

for $v (@verbs)
{

  my $vo = $v;
  $v =~ s/^[a-zA-Z0-9#]+-//g;
  $v =~ s/\./ /g;

  if ($vo =~ /w-/) { print "Defining out of world action $v.\n"; }
  elsif ($vo =~ /a-/) { print "Defining instead rule for $v.\n"; $code = sprintf("%sinstead of doing something with $v:\n\tif action is procedural:\n\t\tcontinue the action;\n\tsay \"[fill-in-here\]\";\n\n", $code); }
  elsif ($vo =~ /o-/) { print "Defining action applying to one thing $v.\n"; }
  elsif ($vo =~ /p-/) { print "Defining action applying to one person $v.\n"; }
  elsif ($vo =~ /#-/) { print "Defining action applying to one number $v.\n"; }
  else { print "Defining action applying to nothing $v.\n"; }

$oow = "applying to nothing";
if ($v =~ /w-/) { $oow = "out of world"; $v =~ s/w-//g;}

#print "$b from $v\n"; next;
if (($v =~ /^ts-/) || ($v =~ /^t-/))
{
  $code = sprintf("%s%s is a truth state that varies. %s is usually false.\n\n", $code, $v, $v);
  }
  elsif ($v =~ /^#-/)
  {
  $code = sprintf("%schapter %sing\n\n%sing is an action applying to one number.

understand the command \"%s\" as something new.

understand \"%s [number]\" as %sing.

carry out %sing:
	the rule succeeds.

", $code, $v, $v, $v, $v, $v, $v);
  }
  elsif ($v =~ /^o-/)
  {
  $code = sprintf("%schapter %sing\n\n%sing is an action applying to one thing.

understand the command \"%s\" as something new.

understand \"%s [something]\" as %sing.

carry out %sing:
	the rule succeeds.

", $code, $v, $v, $v, $v, $v, $v);
  }
  elsif ($v =~ /^p-/)
  {
  $code = sprintf("%schapter %sing\n\n%sing is an action applying to one person.

understand the command \"%s\" as something new.

understand \"%s [person]\" as %sing.

carry out %sing:
	the rule succeeds.

", $code, $v, $v, $v, $v, $v, $v);
  }
  elsif ($v =~ /^n-/)
  {
  print "Defining number $v.\n";
  $code = sprintf("%s%s is a number that varies. %s is usually 0.\n\n", $code, $v, $v);
  }
  elsif ($v =~ /^rm-/)
  {
  print "Defining blocked room $v.\n";
  $code = sprintf("%schapter %s\n\n%s is a room. \"DESCRIPTION PLEASE\".\n\ncheck going in %s:\n\tcontinue the action;\n\n", $code, $v, $v, $v);
  }
  elsif ($v =~ /^r-/)
  {
  print "Defining room $v.\n";
  $code = sprintf("%schapter %s\n\n%s is a room. %s is DIR of ??.\n\n %s is in region ??.\n\n", $code, $v, $v, $v, $v);
  }
  else
  {

$code = sprintf("%schapter %sing\n\n%sing is an action $oow.

understand the command \"%s\" as something new.

understand \"%s\" as %sing.

carry out %sing:
	the rule succeeds;

", $code, $v, $v, $v, $v, $v, $v);
}

}

$clip->Set($code);

##########################################
#subroutines

sub usage
{
  exit()
}