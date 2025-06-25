#!/usr/bin/env perl
#
# ARDOC - NIghtly COntrol System
# Author Alex Undrus <undrus@bnl.gov>
# 
# ----------------------------------------------------------
# ardoc_cachescan.pl 
# ----------------------------------------------------------
use Env;
use locale;

if ($#ARGV < 1) {
warn "ardoc_cachescan.pl: error: at least two arguments required\n";  
exit 1;
}

my $ARDOC_HOME="$ARDOC_HOME";
my $ARDOC_WORK_AREA="$ARDOC_WORK_AREA";

$opt="";
$section="";
$output="${ARDOC_WORK_AREA}/cache_scan_result";
@conf_array=();

while ($#ARGV>=0) {
    $_ = $ARGV[0];
    /^-[cd]+$/ && /d/ && do { $opt="def"; $section=$ARGV[1]; shift; };
    /^-[cd]+$/ && /c/ && do { $opt="com"; $section=$ARGV[1]; shift; };
    /^-[o]+$/ && /o/ && do { $output=$ARGV[1]; shift; };
    /^-[f]+$/ && /f/ && do { push(@conf_array,$ARGV[1]); shift; };
    shift;
}

if ( $opt eq "" || $section eq "" ){
    warn "ardoc_cachescan.pl: error: options -c <section> or -d <section> required\n";
    exit 1;
}

if ($#conf_array < 0){
    warn "ardoc_cachescan.pl: error: ardoc_cache files are not provided\n";
    exit 1; 
}

($sect = $section) =~ s/\s+/ /g;

system("touch $output");
open(TF, ">$output");

foreach $file (@conf_array){
@lines=();
if ( -f $file ){
  open(FR, "$file"); 
  chomp(@lines=<FR>);
  close(FR)
}

$label=0;
$label_bypass=0;
foreach $line (@lines){
    $line =~ s/\s+/ /g;
    $line =~ s/^\s+//g;
    $line =~ s/\s+$//g;
    $line_low = lc($line);
    $line_low =~ s/ //g;
    if ( $opt eq "com" ){
	$stt=1; $sbp=1; $sbpend=1;
        if ( $line_low =~ /^</ && $line_low !~ /^<bypass/ && $line_low !~ /^<\/bypass/ ) {$stt=0;}
        if ( $line_low =~ /^<bypass/ ){$sbp=0;} 
	if ( $line_low =~ /^<\/bypass/ ){$sbpend=0;}
        if ( $label == 1 && $stt == 0 ){
	  if ( $label_bypass == 1 ){
	    $label_bypass=0;
            print TF "fi\n";
	  }
       last;
        } # if ( $label == 1 && $stt == 0 ){
        if ( $label == 1 ){
#	    print "LLLL $line\n";
        if ( $line_low !~ /source/ && $line !~ /cmt/ && $line_low !~ /echo/ && $line_low !~ /broadcast/ && $line_low !~ /^if/ && $line_low !~ /^:/ && $line_low !~ /^make/ && $line_low !~ /fi[^a-zA-Z0-9]/ && $line_low !~ /stat=/ && $line_low !~ /^#/ && $line_low =~ /=/ ){
	     print TF "export ${line}\n";
        }
        elsif ( $line_low =~ /^cmtprojectpath=/ || $line_low =~ /^cmtroot=/ || $line_low =~ /^cmtpath=/ ){
	    print TF "export ${line}\n";
        }
        elsif ( $sbp == 0 ){ # if ( $line
          $label_bypass=1;
          print TF "if [ \"\${ARDOC_BYPASS}\" != \"yes\" ]; then :;\n"; 
        }
        elsif ( $sbpend == 0 ){ # if ( $line
	    $label_bypass=0;
            print TF "fi\n";
        } 
        else { # if ( $line
            if ( $line_low ne "" ){
            print TF "${line}\n";
	    }
	} # if ( $line
        } # if ( $label == 1       
	if ( $line =~ /^<${sect}/ ) { $label=1;}
    }
    if ( $opt eq "def" ){
      if ( $line =~ /^<${sect}/ ) {
      ($lin = $line) =~ s/[<>]//gs;
      ($li = $lin) =~ s/${sect}//gs;
      @varr = split(" ", $li);
	for $var (@varr){
#            print "VPPSST $var\n";
	    print TF "$var\n";
	}
      }
    }
}
}
close(TF);  



