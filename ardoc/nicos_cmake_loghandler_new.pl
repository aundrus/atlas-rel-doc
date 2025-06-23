#!/usr/bin/env perl
#                                                                             
# ARDOC - ARtifact DOcumentation Control System
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

if ($#ARGV>=0) {
    $_ = $ARGV[0];
    /^-[qufl]+$/ && /f/ && do { shift; $file_suffix="$ARGV[0]"; };
    /^-[qufl]+$/ && /l/ && do { shift; $infile="$ARGV[0]"; };
    /^-[qufl]+$/ && shift;
    }

my $ARDOC_WORK_AREA="$ARDOC_WORK_AREA";
my $ARDOC_PROJECT_NAME="$ARDOC_PROJECT_NAME";
my $ARDOC_BUILDLOG="$ARDOC_BUILDLOG";
my $ARDOC_DBFILE = "$ARDOC_DBFILE";
my $ARDOC_DBFILE_GEN = "$ARDOC_DBFILE_GEN";
my $ARDOC_HOSTNAME = "$ARDOC_HOSTNAME";
my $ARDOC_RELHOME="$ARDOC_RELHOME";
my $ARDOC_DOCHOME="$ARDOC_DOCHOME";
my $ARDOC_ARCH="$ARDOC_ARCH";
my $ARDOC_LOG="$ARDOC_LOG";
my $ARDOC_LOGDIR = dirname(${ARDOC_LOG});

my $MAKELOG = "${ARDOC_BUILDLOG}";
if ( $infile ne "" )
{ $MAKELOG = "$infile" };

my $LOGDIR = dirname($MAKELOG);
my $LOGHANDLER_REPORT="$ARDOC_WORK_AREA/ardoc_loghandler_report";
my $file_unassigned_lines = "$LOGDIR/REMNANTS.log${file_suffix}";

if ( -f $file_unassigned_lines ){
    system("rm -f $file_unassigned_lines");
    system("touch $file_unassigned_lines"); 
}

my $cntr=0;
my $cntr_abs=0;
my $stat=0; 
my $dbfile = basename($ARDOC_DBFILE_GEN);
my $dbfilegen = "${ARDOC_WORK_AREA}/${dbfile}_res";
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

##open(REP,">$LOGHANDLER_REPORT");
##open(RMNT,">$file_unassigned_lines");

#warn "FFFFF @dbc\n";

foreach (@dbc)
{
#       Ignore comments
    next if ($_ =~ /^#/ );
#       remove trailing leading stretches whitespaces
    $lll = join(' ', split(' ', $_));
    @fields = split(" ", $lll);
    $pkg = $fields[0];
    $pkg_base = basename($fields[0]);
    warn "ardoc_cmake_loghandler_new.pl: package: $pkg , base $pkg_base\n";
#    $dirlog="${NICOS_RELHOME}/build.${NICOS_ARCH}/${pkg}";
    $dirlog="${NICOS_RELHOME}/build.${NICOS_ARCH}/BuildLogs";
    if ( ! -d $dirlog && -d "${NICOS_RELHOME}/BuildLogs" ) { $dirlog="${NICOS_RELHOME}/BuildLogs";}
    warn "ardoc_cmake_loghandler_new.pl: dirlog: $dirlog\n"; 
    opendir(DD, ${dirlog});
    @listlog = grep /^${pkg_base}\.log$/, readdir(DD);
    closedir DD;
    warn "ardoc_cmake_loghandler_new.pl:logs:@listlog\n"; 
    $file_vers="${NICOS_RELHOME}/${pkg}/version.cmake";
    warn "ardoc_cmake_loghandler_new.pl: version file: $file_vers \n";
    $linev="N/A";
    if ( -f $file_vers ){
        open (FVR, "$file_vers");
	$linev = readline(FVR);
	$linev =~ s/\n//gs;
        close (FVR);
    }  
    ($pkgn = $pkg) =~ s/\//_/g;
    if ($pkgn eq "") { $pkgn = $pkg; }
    $file = "$NICOS_LOGDIR/${pkgn}.loglog";
    if ($#listlog < 0){
        open(OUT, "> $file");
        print OUT "===========================================================================\n";
#        print OUT "[ATLAS Nightly System]: no build logfiles are found in build.${NICOS_ARCH}/${pkg}\n";
        print OUT "[ATLAS Nightly System]: no build logfiles for ${pkg_base} are found in build.${NICOS_ARCH}/BuildLogs\n";
	print OUT "===========================================================================\n";
        print OUT "[ATLAS Nightly System]: absence of build logfile alone is not a problem sign\n"; 
        print OUT "[ATLAS Nightly System]: but it is a WARNING sign\n";
        close(OUT); 
    } else {
#	@listordered = sort { -M "$dirlog/$b" <=> -M "$dirlog/$a" } @listlog;
#        print "LLLL1111111111: @listlog\n";
	@listordered = sort{ compar9("${dirlog}/$a") <=> compar9("${dirlog}/$b")} @listlog;
#        print "LLLL2222222222: @listordered\n";
        open(OUT, "> $file");
        print OUT "===========================================================================\n"; 
#        print OUT "[ATLAS Nightly System]: logfile from the build.${NICOS_ARCH}/${pkg}, added in the order of modification date\n";
        print OUT "[ATLAS Nightly System]: logfile build.${NICOS_ARCH}/BuildLogs/${pkg_base}.log\n";
        print OUT "===========================================================================\n";
        print OUT "\# Version: ${linev}\n";
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
                if ( $line_cnt == $count && $_ !~ /^.*Package\s+build\s+succeeded.*$/ && "$NICOS_PROJECT_NAME" ne "GAUDI" ) { print OUT "Warning: the last line does not indicate that the package build is successful\n";}
                if ( $line_cnt == $count && "$NICOS_PROJECT_NAME" eq "GAUDI" ) { print OUT "Info: CMake does not print messages \'Package build succeeded\' for ${NICOS_PROJECT_NAME} project \n";}
            } 
            close(IN);
        } 
        close(OUT);
    }
}

chdir "$prevdir" or die "Can not cd to $previr: $!\n";
#end of Log maker
