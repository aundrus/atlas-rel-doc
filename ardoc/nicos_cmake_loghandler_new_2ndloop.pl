#!/usr/bin/env perl
#                                                                             
# NICOS - NIghtly COntrol System
# Author Alex Undrus <undrus@bnl.gov>
#
# ----------------------------------------------------------
# nicos_cmake_loghandler_2ndloop
# ----------------------------------------------------------
#
sub compar{
    my $strg=shift;
    ( $lin1 = $strg ) =~ s/ //g;
    if (length($lin1) != 0){
#       remove trailing leading stretches whitespaces
                 $lll = join(' ', split(' ', $strg));
                 @fields = split(" ", $lll);
                 $package1 = $fields[0];
                 return length($package1);
	     }
    else{
	return 0;
             }
}

sub maxstring {
my @list = @_;
my $lengthmax=0;
my $i=0;

for (@list)
{ 
if ( length > $lengthmax )
{$lengthmax=length; $pick=$i;}
}
$i++;
}

use Env;
use Cwd;
use File::Basename;
use File::Copy qw(copy);

my $prevdir = cwd;

my $file_suffix="";
my $infile="";

if ($#ARGV>=0) {
    $_ = $ARGV[0];
    /^-[qufl]+$/ && /f/ && do { shift; $file_suffix="$ARGV[0]"; };
    /^-[qufl]+$/ && /l/ && do { shift; $infile="$ARGV[0]"; };
    /^-[qufl]+$/ && shift;
    }

my $NICOS_PROJECT_NAME="$NICOS_PROJECT_NAME";
my $NICOS_WORK_AREA="$NICOS_WORK_AREA";
my $NICOS_BUILDLOG="$NICOS_BUILDLOG";
my $NICOS_DBFILE = "$NICOS_DBFILE";
my $NICOS_DBFILE_GEN = "$NICOS_DBFILE_GEN";
my $NICOS_HOSTNAME = "$NICOS_HOSTNAME";
my $NICOS_CREATE_LOGFILES = "$NICOS_CREATE_LOGFILES";

my $MAKELOG = "${NICOS_BUILDLOG}";
if ( $infile ne "" )
{ $MAKELOG = "$infile" };

my $LOGDIR = dirname($MAKELOG);
my $LOGHANDLER_REPORT="$NICOS_WORK_AREA/nicos_loghandler_2ndloop_report";
my $file_unassigned_lines = "$LOGDIR/REMNANTS_2ndloop.log${file_suffix}";

if ( -f $file_unassigned_lines ){
    system("rm -f $file_unassigned_lines");
    system("touch $file_unassigned_lines"); 
}

my $cntr=0;
my $cntr_abs=0;
my $stat=0; 
my $dbfile = basename($NICOS_DBFILE_GEN);
my $dbfilegen = "${NICOS_WORK_AREA}/${dbfile}_res";
my $separator = "";
my $pkg = "";
$went_to_file=0;

open(DBF,"$dbfilegen");
chomp(my @dbc1=<DBF>);
close(DBF);

@dbc2 = sort { compar($a) <=> compar($b) } @dbc1;
@dbc = reverse (@dbc2);
#foreach (@dbc)
#{print "DDDD $_\n"};
@dbc1=(); @dbc2=();

open(REP,">$LOGHANDLER_REPORT");
open(RMNT,">$file_unassigned_lines");
print RMNT "===========================================================================================\n";
print RMNT "[ATLAS Nightly System]: cmake build output that can not be assigned to a specific package\n";
print RMNT "===========================================================================================\n";
#warn "FFFFF @dbc\n";

open(IN,"<$MAKELOG")
    or die "Couldn't open $MAKELOG for reading: $!\n";
while (<IN>) {
    chomp;
    $cntr_abs++;
    $stat = 1; 
    $rec = $_;  
    ( $line = $rec ) =~ s/ //g;
    if ( length($line) != 0 ){  
    if ( $line =~ /[A-Za-z0-9_]/ ) {$stat = 0;}

        if ( $stat eq 0 ){ 
	$label_p=0;
        $cntr=0;
        $pkg="";
#        print "SSSS $line\n";
        foreach (@dbc)
        {
#       Ignore comments 
        next if ($_ =~ /^#/ );
#       remove trailing leading stretches whitespaces 
		 $lll = join(' ', split(' ', $_));
                 @fields = split(" ", $lll);
                 $package1 = $fields[0]; 
                 next until ($rec =~ /${package1}/);
	         $pkg=$package1;
                 $label_p=1;
                 last; 
        }
        } # if ($stat 

        $signat = 0;
        if ($pkg ne "") {$signat=1;}

        if ( $stat eq 0 && $signat ne 0 )
        {
        if ( $cntr eq 0 ) {$cntr=1;}
        if ( $cntr >= 2 ) {$cntr=1;}  
        }  
        $went_to_file=0;
        if ( $cntr eq 1 && $stat eq 0 && $label_p eq 1 )
          {
          ($pkgn = $pkg) =~ s/\//_/g; 
          if ($pkgn eq "") { $pkgn = $pkg; }
          $pkgbase=basename($pkg); 
          $file = "$LOGDIR/${pkgn}.loglog${file_suffix}";
          $pkg_prev=$pkg;
          print "nicos_cmake_loghandler_2ndloop: found separator for package $pkg\n";
          $foc=1;
          foreach $fo (@file_occurence){
          if ($fo eq $pkgn) {$foc=0;}  
          }
#          if ($NICOS_CREATE_LOGFILES ne "no"){
          if ($foc eq 0 ){
	      $do_nothing=0;
#              open(OUT, ">> $file");
          } 
          else { 
#              if ( -f $file )
#                   { unlink ($file) or die "Can not delete ${file}: $!\n"; }
#          open(OUT, "> $file"); 
	  open(OUT, ">> $file");
          push(@file_occurence, $pkgn);
          print OUT "===========================================================================\n";
          print OUT
"[ATLAS Nightly System]: build output for package $pkg extracted from cmake logfile\n";
	  print OUT "===========================================================================\n";
          close(OUT);#
#          } # if ($NICOS_CREATE_LOGFILES ne "no")
          print REP "$pkg \n";
	  }
          } # if [ "$cntr" eq 1 

        if ($cntr >= 1) # && $NICOS_CREATE_LOGFILES ne "no") 
        { 
	$file = "$LOGDIR/${pkgn}.loglog${file_suffix}";
        open(OUT, ">> $file"); 
        print OUT "$cntr_abs -- ${rec}\n";
        $went_to_file=1;
        close(OUT);
        }
        
        if ($went_to_file == 0)
        {
	    print RMNT "$cntr_abs -- ${rec}\n";
        }  

        if ($cntr ne 0) { $cntr++; }
     } # if length
} # while
close IN;
close RMNT;
close REP;

$file = "$LOGDIR/${NICOS_PROJECT_NAME}Release.loglog${file_suffix}";
print "nicos_cmake_loghandler_2ndloop: adding unassigned output lines to $file\n";
open(OUT, ">> $file");
open(RMNT,"<$file_unassigned_lines");
print OUT while <RMNT>; 
close OUT;
close RMNT;
print "nicos_cmake_loghandler_2ndloop: completed addition of unassigned output lines to $file\n";

chdir "$prevdir" or die "Can not cd to $previr: $!\n";
#end of Log maker
