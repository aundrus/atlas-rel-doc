#!/usr/bin/env perl
#
#-----------------------------------------------------------------------------
#
# ardoc_oracle_errortester.pl <file>
#
# Author:      A. Undrus
#-----------------------------------------------------------------------------
#
#   Define a grep command to avoid possible path problems when trying
#   to access gnu grep... (to be able to use -a flag...)
#
#
#   Get arguments:
#
use Env;
use File::Basename;

my $ARDOC_HOME="$ARDOC_HOME";
my $ARDOC_WORK_AREA="$ARDOC_WORK_AREA";
my $ARDOC_LOG = "$ARDOC_LOG";
my $ARDOC_WEBDIR = "$ARDOC_WEBDIR";
my $ARDOC_WEB_HOME = "$ARDOC_WEB_HOME";
$ARDOC_LOGDIR = dirname(${ARDOC_LOG});
$ARDOC_LOGDIRBASE = basename(${ARDOC_LOGDIR});
#
#-> check for correct number of arguments
#
    if ( "$#ARGV" < 0 || "$#ARGV" >= 1 ){
    print "ardoc_oracle_errortester:\n";
    print "One argument required: name of logfile\n";
    exit 2;
    }

$filename=$ARGV[0];
$option="oracle";

@e_patterns = ("ORA-", "permission denied", "Disk quota exceeded", ": Error:", "CVBFGG");
my @e_ignore = ("CVBFGH", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_correlators = ("", "", "", "ardoc","");
my @e_count = (0,0,0,0,0,0);

$lineT=0;
$lineE=0;
$lineW=0;
$eeee="";
if ( -f $filename ){
open(FL, "<$filename");
while (<FL>){ 
      chomp;
      $line=$_;
      $lineT++;
      for ($m=0; $m <= $#e_patterns; $m++){
        if ( $line =~ /\Q$e_patterns[$m]\E/ && $line !~ /\Q$e_ignore[$m]\E/ ){ 
          if ( $e_correlators[$m] ne "" ){
	    next if ( $line !~ /\Q$e_correlators[$m]\E/ );
          }    
        $e_count[$m]++; 
        if ( $lineE == 0 ) { 
        $lineE=$lineT;
        $eeee="$e_patterns[$m]";
        $problems=2;
        }
        }
      }
} # while
} else { # if ( -f $filename )
$eeee="logfile not found: $filename";
$problems=10;
}
print "$eeee";


