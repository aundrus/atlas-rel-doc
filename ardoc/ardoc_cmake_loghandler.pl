#!/usr/bin/env perl
#                                                                             
# ARDOC - ATLAS RELEASE DOC
# Author Alex Undrus <undrus@bnl.gov>
#
# ----------------------------------------------------------
# ardoc_cmake_loghandler
# ----------------------------------------------------------
#
use Env;
use Cwd;
use File::Basename;
use Time::HiRes qw(stat);

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
sub compar9{
    my $strg=shift;
    my $mtm=(stat($strg))[9];
#    print "compar9: $strg $mtm\n";
    return $mtm; 
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

my $prevdir = cwd;
my $file_suffix="";
my $infile="";
my $testhandling=0;

if ($#ARGV>=0) {
    $_ = $ARGV[0];
    /^-[quflt]+$/ && /f/ && do { shift; $file_suffix="$ARGV[0]"; };
    /^-[quflt]+$/ && /l/ && do { shift; $infile="$ARGV[0]"; };
    /^-[quflt]+$/ && /t/ && do { $testhandling=1; };
    /^-[quflt]+$/ && shift;
    }

print "ardoc_cmake_loghandler.pl: TESTHANDLING KEY: $testhandling\n";
my $ARDOC_WORK_AREA="$ARDOC_WORK_AREA";
my $ARDOC_PROJECT_NAME="$ARDOC_PROJECT_NAME";
my $ARDOC_PROJECT_RELNAME="$ARDOC_PROJECT_RELNAME";
my $ARDOC_WEBPAGE="$ARDOC_WEBPAGE";
my $ARDOC_BUILDLOG="$ARDOC_BUILDLOG";
my $ARDOC_DBFILE = "$ARDOC_DBFILE";
my $ARDOC_HOSTNAME = "$ARDOC_HOSTNAME";
my $ARDOC_RELHOME="$ARDOC_RELHOME";
my $ARDOC_ARCH="$ARDOC_ARCH";
my $ARDOC_LOG="$ARDOC_LOG";
if ( $testhandling == 1 ) { $ARDOC_LOG="$ARDOC_TESTLOG"; }
my $ARDOC_LOGDIR = dirname(${ARDOC_LOG});
my $ARDOC_NINJALOG="$ARDOC_NINJALOG";

my $MAKELOG = "${ARDOC_BUILDLOG}";
if ( $infile ne "" )
{ $MAKELOG = "$infile" };

my $LOGDIR = dirname($MAKELOG);
my $LOGHANDLER_REPORT="$ARDOC_WORK_AREA/ardoc_loghandler_report";
if ( $testhandling == 1) { $LOGHANDLER_REPORT="$ARDOC_WORK_AREA/ardoc_testloghandler_report";}
my $file_unassigned_lines = "$LOGDIR/REMNANTS.log${file_suffix}";

if ( -f $file_unassigned_lines && $testhandling != 1 ){
    system("rm -f $file_unassigned_lines");
    system("touch $file_unassigned_lines"); 
}

my $cntr=0;
my $cntr_abs=0;
my $stat=0; 
my $dbfile = basename($ARDOC_DBFILE);
if ( $testhandling == 1) { $dbfile = basename(${ARDOC_TEST_DBFILE} . "_res");}
my $dbfilegen = "${ARDOC_WORK_AREA}/${dbfile}";
my $separator = "";
my $pkg = "";
$went_to_file=0;
warn "ardoc_cmake_loghandler: files/dirs $dbfilegen $ARDOC_LOG $ARDOC_LOGDIR\n";

open(DBF,"$dbfilegen");
chomp(my @dbc1=<DBF>);
close(DBF);

@dbc2 = sort { compar($a) <=> compar($b) } @dbc1;
@dbc = reverse (@dbc2);
#foreach (@dbc)
#{print "DDDD $_\n"};
@dbc1=(); @dbc2=();

##open(REP,">$LOGHANDLER_REPORT");
##open(RMNT,">$file_unassigned_lines");

#warn "FFFFF @dbc\n";
$typel="Build";$typelow="build";
if ( $testhandling == 1 ) { $typel="Test"; $typelow="test";}

foreach (@dbc)
{
#       Ignore comments
    next if ($_ =~ /^#/ );
#       remove trailing leading stretches whitespaces
    $lll = join(' ', split(' ', $_));
    @fields = split(" ", $lll);
    $pkg = $fields[0];
    $pkg_base = basename($fields[0]);
    warn "ardoc_cmake_loghandler.pl: package: $pkg , base $pkg_base\n";
#    $dirlog="${ARDOC_RELHOME}/build.${ARDOC_ARCH}/${pkg}";
    $dirlog="${ARDOC_RELHOME}/build.${ARDOC_ARCH}/${typel}Logs";
    if ( ! -d $dirlog && -d "${ARDOC_RELHOME}/${typel}Logs" ) { $dirlog="${ARDOC_RELHOME}/${typel}Logs";}
#    warn "ardoc_cmake_loghandler.pl: dirlog: $dirlog\n"; 
    opendir(DD, ${dirlog});
    @listlog = grep /^${pkg_base}\.log$/, readdir(DD);
    closedir DD;
    warn "ardoc_cmake_loghandler.pl:logs:@listlog\n"; 
    $file_vers="${ARDOC_RELHOME}/${pkg}/version.cmake";
#    warn "ardoc_cmake_loghandler.pl: version file: $file_vers \n";
    $linev="N/A";
    if ( -f $file_vers ){
        open (FVR, "$file_vers");
	$linev = readline(FVR);
	$linev =~ s/\n//gs;
        close (FVR);
    }  
    ($pkgn = $pkg) =~ s/\//_/g;
    if ($pkgn eq "") { $pkgn = $pkg; }
    $file = "$ARDOC_LOGDIR/${pkgn}.loglog";
    if ( $testhandling == 1 ) { $file = "$ARDOC_LOGDIR/${pkgn}___${pkg_base}Conf__${pkg_base}Test__m.loglog";}
    if ($#listlog < 0){
        open(OUT, "> $file");
        print OUT "===========================================================================\n";
        print OUT "[ATLAS ARDOC]: no ${typelow} logfiles for ${pkg_base} are found in ${dirlog}\n";
        if ( $testhandling != 1 ) {  
          print OUT "[ATLAS ARDOC]: absence of ${typelow} logfile alone is not a problem sign\n"; 
          print OUT "[ATLAS ARDOC]: but it is a WARNING sign\n";
        }
	print OUT "===========================================================================\n";
        close(OUT); 
    } else {
#	@listordered = sort { -M "$dirlog/$b" <=> -M "$dirlog/$a" } @listlog;
#        print "LLLL1111111111: @listlog\n";
	@listordered = sort{ compar9("${dirlog}/$a") <=> compar9("${dirlog}/$b")} @listlog;
#        print "LLLL2222222222: @listordered\n";
        open(OUT, "> $file");
##        print OUT "===========================================================================\n";
##        print OUT "[ATLAS ARDOC]: logfile ${dirlog}/${pkg_base}.log\n";
##        print OUT "===========================================================================\n"; 	
        if ( $ARDOC_NINJALOG ne "" ){
          if ( -f $ARDOC_NINJALOG ) {
	    $nninja=`cat $ARDOC_NINJALOG | wc -l`;
            if ($?) {
		warn "ardoc_cmake_loghandler: failed to count lines in ninja logfile $ARDOC_LOGDIR\n";
	    } else {
                chomp($nninja); 
                $nninja=int($nninja);
#                warn "ardoc_cmake_loghandler: line count $nninja in ninja logfile $ARDOC_LOGDIR\n";
                if ( $nninja > 1 ){
                    $release="${ARDOC_PROJECT_RELNAME}";
		    $WLogdir="ARDOC_Log_${release}";
                    $ARDOC_NINJALOGBASE = basename(${ARDOC_NINJALOG});
		    $ARDOC_NINJAURL="${ARDOC_WEBPAGE}/${WLogdir}/${ARDOC_NINJALOGBASE}";
##                   print OUT "===========================================================================\n";
##                   print OUT "[ATLAS ARDOC]: Ninja logfile can be accessed at <a href=\"$ARDOC_NINJAURL\">this address</a>\n";
##                   print OUT "[ATLAS ARDOC]: Ninja logfile can be accessed at $ARDOC_NINJAURL\n";
##                   print OUT "===========================================================================\n";		    
		}
            }
          } 
	}
#        print OUT "\# Version: ${linev}\n";
        foreach $ff (@listordered) {
	    $ffbase = (split('\.', $ff))[0];
            $infile="$dirlog/$ff";
            $line_cnt=0;
            open(IN, "<$infile")
                or die "Couldn't open $ff for reading: $!\n";
            1 while <IN>;
            $count = $.;
#            warn "FFFFF $count $infile\n";
            seek IN, 0, 0;
            while (<IN>) {
                chomp;
                $line_cnt++;
#                if ( $line_cnt == 1 ){ print OUT "# start $ffbase $_\n";}
#                elsif ( $line_cnt == $count ) { print OUT "# end $ffbase $_\n";}
#                else {print OUT "$_\n";}
                print OUT "$_\n";
                if ( $testhandling != 1 && $line_cnt == $count && $_ !~ /^.*Package\s+${typelow}\s+succeeded.*$/ && $_ !~ /^.*pseudo\s+package.*$/ && "$ARDOC_PROJECT_NAME" ne "GAUDI" ) { print OUT "Warning: the last line does not indicate that the package ${typelow} is successful\n";}
                if ( $testhandling != 1 && $line_cnt == $count && "$ARDOC_PROJECT_NAME" eq "GAUDI" ) { print OUT "Info: CMake does not print messages \'Package ${typelow} succeeded\' for ${ARDOC_PROJECT_NAME} project \n";}
            } 
            close(IN);
        } 
        close(OUT);
    }
}

chdir "$prevdir" or die "Can not cd to $previr: $!\n";
#end of Log maker
