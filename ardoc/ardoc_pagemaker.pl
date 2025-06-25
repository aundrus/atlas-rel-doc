#!/usr/bin/env perl
#
# ARDOC - NIghtly COntrol System
# Author Alex Undrus <undrus@bnl.gov>
# 
# ----------------------------------------------------------
# ardoc_pagemaker.pl
# ----------------------------------------------------------
#

sub compartim {
    my $name = shift;
    my $tm = (stat("${ARDOC_WEBDIR}/$name"))[9];
    return $tm;
}

sub comparc{
    my $strg=shift;
    ( $lin1 = $strg ) =~ s/ //g;
    if (length($lin1) eq 0){
        return 0;}
    else{
        $res1 = (split(" ", $strg))[1];
        $res2 = (split(" ", $strg))[0];
        $res = "$res1" . "$res2";
        if ($res eq "" || $res eq "N/A"){ $res="AAAAAA";}  
        return $res;
    }
}
sub compar0{
    my $strg=shift;
    ( $lin1 = $strg ) =~ s/ //g;
    if (length($lin1) eq 0){
        return 0;}
    else{
        $res1 = (split(" ", $strg))[0];
        $probl = (split(" ", $strg))[3];
        $qprobl = (split(" ", $strg))[5];
        $tprobl = (split(" ", $strg))[8];
        $b_or = (split(" ", $strg))[10];
        $res=""; 
        if ($probl ge 0.5 || $tprobl ge 0.5 || $qprobl ge 0.5){
            $hilight="ZZ";
	    if ( $probl >= 2 ) { $hilight="RA"; }
	    elsif  ( $probl == 1 ) { $hilight="RB"; }
	    elsif  ( $probl == 0.5 ) { $hilight="RC"; }
	    elsif  ( $tprobl >= 2 ) { $hilight="SA"; }
	    elsif  ( $tprobl == 1 ) { $hilight="SB"; }
	    elsif  ( $tprobl == 0.5 ) { $hilight="SC"; }
	    elsif  ( $qprobl >= 2 ) { $hilight="YA"; }
	    elsif  ( $qprobl == 1 ) { $hilight="YB"; }
	    elsif  ( $qprobl == 0.5 ) { $hilight="YC"; }
#	    $probl_r=100 - int($probl*10);
#	    $tprobl_r=100 - int($tprobl*10);
#            $qprobl_r=100 - int($qprobl*10);
#            $probl_c=chr($probl_r);
#            $tprobl_c=chr($tprobl_r);            
#            $qprobl_c=chr($qprobl_r);
#            $probl_c = sprintf("%.3d",$probl_r);
#	    $tprobl_c = sprintf("%.3d",$tprobl_r);
#	    $qprobl_c = sprintf("%.3d",$qprobl_r);
            $b_or1 = sprintf("%.7d", $b_or);
##            print "ABC $probl_c  $tprobl_c  $qprobl_c\n";
##        $res = "AAAA" . "$probl_c" . "$tprobl_c" . "$qprobl_c" . "$res1";
	    $res = "AAAA" . "$hilight" . "$b_or1";
##	    print "BB $res1 BB $b_or1 BB XX${res}XX\n";
        }
        else
        {$res = "BBBB" . "$res1";}  
        return $res;
    }
}
sub compart{
    my $strg=shift;
    ( $lin1 = $strg ) =~ s/ //g;
    if (length($lin1) eq 0){
        return 0;}
    else{
        $res1 = (split(" ", $strg))[0];
        $tprobl = (split(" ", $strg))[3];
        $res="";
        if ($tprobl ge 2)
        {$res = "AAAA" . "$res1";}
        elsif ($tprobl eq 1) 
        {$res = "BBBB" . "$res1";}
        elsif ($tprobl eq 0.5)
        {$res = "BBCC" . "$res1";}
        else
        {$res = "CCCC" . "$res1";}
        return $res;
    }
}

use Env;
use Cwd;
use File::Basename;
#use ExtUtils::Command;                                                                               
print "------------------------------------------------------------\n";
print "   Starting creating ARDOC webpages (final step)\n";
print "------------------------------------------------------------\n";
my $ARDOC_WORK_AREA="$ARDOC_WORK_AREA";
my $ARDOC_RELHOME="$ARDOC_RELHOME";
my $ARDOC_WEBDIR="$ARDOC_WEBDIR";
my $ARDOC_HOME="$ARDOC_HOME";
my ${ARDOC_PROJECT_RELNAME}="${ARDOC_PROJECT_RELNAME_COPY}";
my ${ARDOC_PROJECT_RELNUMB_ORIG}="${ARDOC_PROJECT_RELNUMB}";
my ${ARDOC_PROJECT_RELNUMB}="${ARDOC_PROJECT_RELNUMB_COPY}";
my ${ARDOC_WEBDIR}="${ARDOC_WEBDIR}";
my ${ARDOC_INC_BUILD}="${ARDOC_INC_BUILD}";
my $ARDOC_TITLE_COMMENT="$ARDOC_TITLE_COMMENT";
my $prepage="ardoc_prepage";
my $testprepage="ardoc_testprepage";
my $qaprepage="ardoc_qaprepage";
my $release="${ARDOC_PROJECT_RELNAME}";
#my $project="${ARDOC_PROJECT_NAME}";
my $project="Nightly";
my $WLogdir="ARDOC_Log_${release}";
my $WTLogdir="ARDOC_TestLog_${release}";
my $WQLogdir="ARDOC_QALog_${release}";
my $WWW_DIR="${ARDOC_WEBDIR}";
my $WWW_WORK="${ARDOC_WORK_AREA}";
my $prevdir=cwd;
my $LOGHANDLER_REPORT="${ARDOC_WORK_AREA}/ardoc_loghandler_report";
my $suffix="_${ARDOC_PROJECT_RELNUMB}";
if ( ${ARDOC_PROJECT_RELNUMB} eq "" ) { $suffix=""; }
my $outfile_test_pass="${WWW_DIR}/status_test_pass${suffix}.js";
my $outfile_test_fail="${WWW_DIR}/status_test_fail${suffix}.js";
my $outfile_unit_pass="${WWW_DIR}/status_unit_pass${suffix}.js";
my $outfile_unit_fail="${WWW_DIR}/status_unit_fail${suffix}.js";
my $outfile_build_failures="${WWW_DIR}/build_failures${suffix}.js";
my $outfile_test_success="${WWW_DIR}/test_success${suffix}.js";
my $outfile_test_completed="${WWW_DIR}/test_completed${suffix}.js";
my $outfile_test_total="${WWW_DIR}/test_total${suffix}.js";
#
my $outfile_test_pass_f="${WWW_DIR}/status_test_pass_f${suffix}.js";
my $outfile_test_fail_f="${WWW_DIR}/status_test_fail_f${suffix}.js";
my $outfile_unit_pass_f="${WWW_DIR}/status_unit_pass_f${suffix}.js";
my $outfile_unit_fail_f="${WWW_DIR}/status_unit_fail_f${suffix}.js";
my $outfile_build_failures_f="${WWW_DIR}/build_failures_f${suffix}.js";
my $outfile_test_success_f="${WWW_DIR}/test_success_f${suffix}.js";
chdir "$WWW_WORK";
#-------------

@tprepx=();
@uprepx=();
@tprepy=();
@prepx=();
@logrep=();

$total_tests=0;
$filenmb="${ARDOC_WORK_AREA}/ardoc_testprepage_number";
if ( -f $filenmb ){
    open (FKM, "$filenmb");
    my $line1 = readline(FKM);
    $line1 =~ s/\n//gs;
( $line = $line1 ) =~ s/ //gs;
$total_tests=int($line);
close (FKM);
}

$ttp="${WWW_WORK}/${testprepage}";
open(TTT,"$ttp");
chomp(my @ttpp=<TTT>);
close(TTT);

$ttq="${WWW_WORK}/${qaprepage}";
open(TTT,"$ttq");
chomp(my @ttqq=<TTT>);
close(TTT);

$file = "$LOGHANDLER_REPORT";
open(REP,"<$file")
    or die "ardoc_pagemaker.pl: couldn't open $file for reading: $!\n";
while (<REP>) {
    chomp;
    next if ($_ =~ /^#/ );
             ( $lin1 = $_ ) =~ s/ //g;
next if (length($lin1) eq 0);
$lll = join(' ', split(' ', $_));
@fields = split(" ", $lll);
$entry = $fields[0];
$container=dirname($entry);
if($container eq "."){$container="N/A";} 
$package=basename($entry);
$l1="$package $container\n";
push(@logrep, $l1);
} # while (<REP>)
close(REP);

%seen=();
@uniq = grep { ! $seen{$_} ++ } @logrep;
@logrep=@uniq;
@uniq=();
$build_failures=0;
$build_failures_f=0;

$file = "${WWW_WORK}/${prepage}";
open(IN,"<$file")
    or die "ardoc_pagemaker.pl: couldn't open $file for reading: $!\n";
while (<IN>) {
    chomp;
    next if ($_ =~ /^#/ );
	     ( $lin1 = $_ ) =~ s/ //g;
	     next if (length($lin1) eq 0);
#   remove trailing leading stretches whitespaces
	     $lll = join(' ', split(' ', $_));
	     @fields9 = split(/ \"\"\" /, $lll);
	     @fields = split(" ", $fields9[0]);
	     $package = $fields[0];
	     $container = $fields[1];
             $recent_logfiles = $fields[2];
             $problems = $fields[3];
             @addresses=();
	     for ($m=6; $m <= $#fields; $m++){
                 $fields_elem=$fields[$m];
                 @fields_arr=split(',', $fields_elem);
                 if ( $#fields_arr != 0 ){
		     @fields_arr = sort @fields_arr;
                     $fields_elem=join(',',@fields_arr);
                 }
		 push(@addresses, $fields_elem);
	     }
             if ( $problems ge 2 ){$build_failures++;}
             if ( $problems ge 0.5 ){$build_failures_f++;}
	     $pkgn1="${container}_${package}";
             if ( $container eq "N/A" ) { $pkgn1 = ${package}; }
             $pkgn11="${pkgn1}_${package}"; 
             ( $pkgn = $pkgn11 ) =~ s/\//_/g;
             $comp11 = lc($pkgn);
             ( $pkgn = $pkgn1 ) =~ s/\//_/g;
             $comp1 = lc($pkgn);
my @xxxx=();
my $treclog="0";
my $tprob=0;
my $tcd=0;

foreach (@ttpp)
{
#       Ignore comments
        next if ($_ =~ /^#/);
                 ( $lin1 = $_ ) =~ s/ //g;
                 next if (length($lin1) eq 0);
#       remove trailing leading stretches whitespaces
                 $lll = join(' ', split(' ', $_));
                 @fields = split(" ", $lll);
                 $testname = $fields[0];
                 $testsuite = $fields[1];
                 $trecent_logfiles = $fields[2];
                 $tproblems = $fields[3];
                 $tecode = $fields[4];
                 $testdir = $fields[5];
                 $testname_base = $fields[6];
                 @xxxx=();
                    for ($m=7; $m <= $#fields; $m++){
                    push(@xxxx, $fields[$m]);
                    }
                 $comp2 = lc($testname);
                 @ftest = split("__", $comp2);
                 if ( $#ftest < 2 ){
                     $comp21=$comp2; }
                 else{
		     @xxxx1=();
                     push(@xxxx1, $ftest[0]);
                     push(@xxxx1, $ftest[1]);  
                     $comp21 = join('', @xxxx1);}
  if ( $comp11 eq $comp2 || $comp11 eq $comp21 ){
  $llll = "$testname $testsuite $trecent_logfiles $tproblems $tecode $testdir $testname_base @xxxx\n"; 
  push(@tprepx, $llll);
  $treclog = $trecent_logfiles;
  $tprob = $tproblems;
  $tcd=$tecode;
  last;
  }
  } #done

$qreclog="0";
$qprob=0;
$qcd=0;
foreach (@ttqq)
{
#       Ignore comments
        next if ($_ =~ /^#/);
                 ( $lin1 = $_ ) =~ s/ //g;
                 next if (length($lin1) eq 0);
#       remove trailing leading stretches whitespaces
                 $lll = join(' ', split(' ', $_));
                 @fields = split(" ", $lll);
                 $testname = $fields[0];
                 $testsuite = $fields[1];
                 $trecent_logfiles = $fields[2];
                 $tproblems = $fields[3];
                 $tecode = $fields[4];  
                 $testdir = $fields[5];
                 $testname_base = $fields[6];
                 @xxxx=();
		 for ($m=7; $m <= $#fields; $m++){
		     push(@xxxx, $fields[$m]);
		 }
                 $comp2 = lc($testname);
		 if ( $comp1 eq $comp2 ){
                     $qreclog = $trecent_logfiles;
                     $qprob = $tproblems;
                     $qcd = $tecode;
		     last;
          }
} #done

$b_order=0;
$bo=0;
foreach $item_yy (@logrep){
    next if ($item_yy =~ /^#/ );
    ( $lin1 = $item_yy ) =~ s/ //g;
    @fields_y = split(" ", $item_yy);
    $package_yy = $fields_y[0];
    $container_yy = $fields_y[1];
    $bo++;
    if( $package eq $package_yy && $container eq $container_yy ){
    $b_order=$bo;        
    last;    
    }
}

$llll = "$package $container $recent_logfiles $problems $qreclog $qprob $qcd $treclog $tprob $tcd $b_order @addresses\n";
push(@prepx, $llll);

#print "PPPP $package $b_order\n";
} #done

#######

foreach (@ttpp)
{
#       Ignore comments
        next if ($_ =~ /^#/);
                 ( $lin1 = $_ ) =~ s/ //g;
                 next if (length($lin1) eq 0);
                 $ardoc_pagemaker_data = 0;
#       remove trailing leading stretches whitespaces
                 $lll = join(' ', split(' ', $_));
                 @fields = split(" ", $lll);
                 $testname = $fields[0];
                 $testsuite = $fields[1];
                 $trecent_logfiles = $fields[2];
                 $tproblems = $fields[3];
                 $tecode = $fields[4];  
                 $testdir = $fields[5];
                 $testname_base = $fields[6];
                 @xxxx=();
                    for ($m=7; $m <= $#fields; $m++){
                    push(@xxxx, $fields[$m]);
                    }

		 foreach $item (@tprepx) {
                     next if ($item =~ /^#/ );
                     ( $lin1 = $item ) =~ s/ //g;
		     next if (length($lin1) eq 0);
                     @fields = split(" ", $item);
                     $ttestname = $fields[0];
#		     print "XXX $testname $ttestname\n";
                     if ($testname eq "$ttestname"){
                     $ardoc_pagemaker_data = 1;
                     last;
                     } 
		     }

if ( $ardoc_pagemaker_data eq 0 ){
$llll = "$testname $testsuite $trecent_logfiles $tproblems $tecode $testdir $testname_base @xxxx\n";
push(@tprepy,$llll);
}

} #done
close(IN);

#creating web page with test results
$inttestpage="${WWW_WORK}/ardoc_testsummary_${ARDOC_PROJECT_RELNUMB}.html";
if ( "${ARDOC_PROJECT_RELNUMB}" eq "" )
{
    $inttestpage="${WWW_WORK}/ardoc_testsummary.html";
}
open(WP,">$inttestpage");
$prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -h 22 ${project} ${release} ${ARDOC_RELHOME} ${WLogdir}";
$pid = open(RM, "${prg} |");
while (<RM>){ print WP "$_"; }
close (RM);
#@testprepage_01 = sort @tprepy;
@testprepage_01 =  sort { compart($a) cmp compart($b) } @tprepy;
@testprepage_u_01 =  sort { compart($a) cmp compart($b) } @tprepx;
my $test_pass=0;
my $test_fail=0;
my $unit_pass=0;
my $unit_fail=0;
my $test_pass_f=0;
my $test_fail_f=0;
my $unit_pass_f=0;
my $unit_fail_f=0;

foreach (@testprepage_01)
{
#       Ignore comments
        next if ($_ =~ /^#/);
                 ( $lin1 = $_ ) =~ s/ //g;
                 next if (length($lin1) eq 0);
                 $lin2=(split(/\s\"\"\"/, $_))[0]; 
                 @fields = split(" ", $lin2);
                 $testname = $fields[0];
                 $testsuite = $fields[1];
                 $recent_logfiles = $fields[2];
                 $problems = $fields[3];
                 $tecode = $fields[4];
                 $testdir = $fields[5];
                 $testname_base = $fields[6];
		 @ftest = split("__", $testname_base);
		 if ( $#ftest == 0 ){
		     $testname_base1=$testname_base; 
        	     $testname_base2=$testname_base;}
                 else{
                 if ( $ftest[-1] eq "" || $ftest[-1] eq "a" || $ftest[-1] eq "k" || $ftest[-1] eq "x" || $ftest[-1] eq "m" ){ pop @ftest; }
#                 print "BNBNBB $ftest[0]\n";
                 if ( $ftest[0] =~ /\d+/ || $ftest[0] eq "" ) { shift @ftest; }
#                 print "BNBNBA $ftest[0]\n";
                 $testname_base1 = join('#', @ftest);
                 $testname_base2 = $ftest[0];} 
                 @xxxx=();
		 for ($m=7; $m <= $#fields; $m++){
                     if ( $fields[$m] =~ /'/ ){
                     ( $fimod = $fields[$m] ) =~ s/'/\\'/g;
                     push(@xxxx, $fimod); 
                     } else {
		     push(@xxxx, $fields[$m]);
                     }
		 }
		 if ( $testname ne "" ){
		     if ( $recent_logfiles eq "" ){ $recent_logfiles="N/A"; }
		     if ( $problems le 1 ){$test_pass++;}
                     else {$test_fail++;} 
                     if ( $problems lt 0.5 ){$test_pass_f++;}
                     else {$test_fail_f++;}
#		     print "QQQQ $testname $testname_base $testname_base2 WWWW @xxxx\n";
    $prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -a ${testdir} ${testname_base1} ${testname_base2} ${testsuite} ${WTLogdir} ${recent_logfiles} ${problems} ${tecode} @xxxx";
    $pid = open(RM, "${prg} |");
    while (<RM>){ print WP "$_";}
    close (RM);
}
} #done

	$prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -u 0";
	$pid = open(RM, "${prg} |");
	while (<RM>){ print WP "$_";}
	close (RM);

foreach (@testprepage_u_01)
{
#       Ignore comments
        next if ($_ =~ /^#/);
                 ( $lin1 = $_ ) =~ s/ //g;
                 next if (length($lin1) eq 0);
                 $lin2=(split(/\s\"\"\"/, $_))[0];
                 @fields = split(" ", $lin2);
                 $testname = $fields[0];
                 $testsuite = $fields[1];
                 $recent_logfiles = $fields[2];
                 $problems = $fields[3];
                 $tecode = $fields[4];
                 $testdir = $fields[5];
                 $testname_base = $fields[6];
                 @ftest = split("__", $testname_base);
                 if ( $#ftest == 0 ){ 
                 $testname_base1=$testname_base; 
                 $testname_base2=$testname_base; }
                 else{
                 if ( $ftest[-1] eq "" || $ftest[-1] eq "a" || $ftest[-1] eq "k" || $ftest[-1] eq "x" || $ftest[-1] eq "m" ){ pop @ftest; }
                 if ( $ftest[0] =~ /\d+/ || $ftest[0] eq "" ) { shift @ftest; }
                 $testname_base1 = join('#', @ftest);  
                 $testname_base2 = $ftest[0];}
                 @xxxx=();
                 for ($m=7; $m <= $#fields; $m++){
		     if( $fields[$m] =~ /'/ ){
                     ( $fimod =$fields[$m] ) =~ s/'/\\'/g;
                     push(@xxxx, $fimod);
                     } else { 
                     push(@xxxx, $fields[$m]);
                     }
                 }
                 if ( $testname ne "" ){
                     if ( $recent_logfiles eq "" ){ $recent_logfiles="N/A"; }
                     if ( $problems le 1 ){$unit_pass++;}
                     else {$unit_fail++;}	
                     if ( $problems lt 0.5 ){$unit_pass_f++;}
                     else {$unit_fail_f++;}
    $prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -a ${testdir} ${testname_base1} ${testname_base2} ${testsuite} ${WTLogdir} ${recent_logfiles} ${problems} ${tecode} @xxxx";
    $pid = open(RM, "${prg} |");
    while (<RM>){ print WP "$_";}
    close (RM);
}
} #done

open(WRITEDATA,">$outfile_test_pass");
print WRITEDATA "function status_tp${suffix}(){return $test_pass}";
close(WRITEDATA);
open(WRITEDATA,">$outfile_test_pass_f");
print WRITEDATA "function status_tp_f${suffix}(){return $test_pass_f}";
close(WRITEDATA);
open(WRITEDATA,">$outfile_test_fail");
print WRITEDATA "function status_tf${suffix}(){return $test_fail}";
close(WRITEDATA);
open(WRITEDATA,">$outfile_test_fail_f");
print WRITEDATA "function status_tf_f${suffix}(){return $test_fail_f}";
close(WRITEDATA);
open(WRITEDATA,">$outfile_unit_pass");
print WRITEDATA "function status_up${suffix}(){return $unit_pass}";
close(WRITEDATA);
open(WRITEDATA,">$outfile_unit_pass_f");
print WRITEDATA "function status_up_f${suffix}(){return $unit_pass_f}";
close(WRITEDATA);
open(WRITEDATA,">$outfile_unit_fail");
print WRITEDATA "function status_uf${suffix}(){return $unit_fail}";
close(WRITEDATA);
open(WRITEDATA,">$outfile_unit_fail_f");
print WRITEDATA "function status_uf_f${suffix}(){return $unit_fail_f}";
close(WRITEDATA);

	$testsuccess="N/A";
        $testsuccess_f="N/A";
        $sum_all_tests=$test_pass+$test_fail+$unit_pass+$unit_fail;
        $sum_all_tests_f=$test_pass_f+$test_fail_f+$unit_pass_f+$unit_fail_f;
        $sum_ok_tests=$test_pass+$unit_pass;
        $sum_ok_tests_f=$test_pass_f+$unit_pass_f;
#	print "AAAAA $test_pass+$test_fail+$unit_pass+$unit_fail\n";
#	print "BBBB $test_pass $unit_pass\n";
	if ( $sum_all_tests == 0 ){
	    $testsuccess="N/A";
	}
	else{
	    $testsuccess=int(($sum_ok_tests/$sum_all_tests)*100);
	}
        if ( $sum_all_tests_f == 0 ){
            $testsuccess_f="N/A";
        }
        else{
            $testsuccess_f=int(($sum_ok_tests_f/$sum_all_tests_f)*100);
        }
open(WDATA,">$outfile_build_failures");
print WDATA "function failures${suffix}()\{return '";
my $ddd="$build_failures"."'\}";
print WDATA "$ddd";
close(WDATA);
open(WDATA,">$outfile_build_failures_f");
print WDATA "function failures_f${suffix}()\{return '";
my $ddd="$build_failures_f"."'\}";
print WDATA "$ddd";
close(WDATA);
open(WDATA,">$outfile_test_success");
print WDATA "function success${suffix}()\{return '";
my $ddd="$testsuccess"."'\}";
print WDATA "$ddd";
close(WDATA);
open(WDATA,">$outfile_test_success_f");
print WDATA "function success_f${suffix}()\{return '";
my $ddd="$testsuccess_f"."'\}";
print WDATA "$ddd";
close(WDATA);
open(WDATA,">$outfile_test_completed");
print WDATA "function t_completed${suffix}()\{return '";
my $ddd="$sum_all_tests"."'\}";
print WDATA "$ddd";
close(WDATA);
open(WDATA,">$outfile_test_total");
print WDATA "function t_total${suffix}()\{return '";
my $ddd="$total_tests"."'\}";
print WDATA "$ddd";
close(WDATA);

$prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -f";
$pid = open(RM, "${prg} |");
while (<RM>){ print WP "$_"; }
close (RM);

close(WP);

#loop produces web pages with different sorting  
my @sortind=("","1","2");
#		 my @sortind=("1");
#11------------

foreach $sortsuffix (@sortind){

$webpage="${WWW_WORK}/ardoc_buildsummary${sortsuffix}_${ARDOC_PROJECT_RELNUMB}.html";
if ( "${ARDOC_PROJECT_RELNUMB}" eq "" )
{
$webpage="${WWW_WORK}/ardoc_buildsummary${sortsuffix}.html";
}
open(WP,">$webpage");
$prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -h 11 ${project} ${release} ${ARDOC_RELHOME} ${WLogdir}";
   $pid = open(RM, "${prg} |");
   while (<RM>){ print WP "$_"; }
close (RM);

#114
if ($sortsuffix eq "1"){
$prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -i 1 ${release} ${WLogdir}";
}
elsif ($sortsuffix eq "2"){
$prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -i 2 ${release} ${WLogdir}";
}
else{
$prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -i 0 ${release} ${WLogdir}";
}
$pid = open(RM, "${prg} |");
while (<RM>){ print WP "$_"; }
close (RM);

#115
        @prep_01 = ();
	if ($sortsuffix eq ""){
            @prep_01 =  sort { compar0($a) cmp compar0($b) } @prepx;
	}
	elsif ($sortsuffix eq "2"){
	    @prep_01 =  sort { comparc($a) cmp comparc($b) } @prepx;
	}
        else{
	    @prep_01 = ();
               foreach $item_y (@logrep)
                {
                next if ($item_y =~ /^#/ );
	        ( $lin1 = $item_y ) =~ s/ //g;
		@fields = split(" ", $item_y);
		$package_y = $fields[0];
		$container_y = $fields[1];
                foreach $item_x (@prepx)
		     {
                     next if ($item_x =~ /^#/ );
		     ( $lin1 = $item_x ) =~ s/ //g;
		     @fields = split(" ", $item_x);
		     $package_x = $fields[0];
		     $container_x = $fields[1];
                     if( $package_x eq $package_y && $container_x eq $container_y )
	             {push(@prep_01,$item_x);}
		     }
               }

            my $rslt=0;
            foreach $item_x (@prepx)
            {
            next if ($item_x =~ /^#/ );
	    ( $lin1 = $item_x ) =~ s/ //g;
	    @fields = split(" ", $item_x);
            $package_x = $fields[0];
	    $container_x = $fields[1];
	    $rslt=0;
   	       foreach $item_y (@logrep)
               {
               next if ($item_y =~ /^#/ );
               ( $lin1 = $item_y ) =~ s/ //g;
               @fields = split(" ", $item_y);
               $package_y = $fields[0];
               $container_y = $fields[1];                  
               if( $package_x eq $package_y && $container_x eq $container_y )
			{
                	$rslt=1;
                        last;
                        }
               }              
            if($rslt eq 0)
            {push(@prep_01,$item_x);}
            } 
	}
     
foreach (@prep_01)
{    next if ($_ =~ /^#/ );
	      ( $lin1 = $_ ) =~ s/ //g;
	      next if (length($lin1) eq 0);
	      @fields = split(" ", $_);
	      $package = $fields[0];
	      $container = $fields[1];
	      $recent_logfiles = $fields[2];
	      $problems = $fields[3];
              $qrecent_logfiles = $fields[4];
              $qproblems = $fields[5];
              $qecode = $fields[6];
              $trecent_logfiles = $fields[7];
              $tproblems = $fields[8];
              $tecode = $fields[9]; 
              $b_order = $fields[10]; 
	      @addresses=();
	      for ($m=11; $m <= $#fields; $m++){
		  $fields_elem=$fields[$m];
                  @fields_arr=split(',', $fields_elem);
                  if ( $#fields_arr != 0 ){
		      @fields_arr = sort @fields_arr;
                      $fields_elem=join(',',@fields_arr);
                  }
                  push(@addresses, $fields_elem);
	      }
	      $pkgn1="${container}_${package}";
              if ( $container eq "N/A" ) { $pkgn1 = ${package}; }
              ( $pkgn = $pkgn1 ) =~ s/\//_/g;
 
if ( $package ne "" ){
if ( $recent_logfiles eq "" ){ $recent_logfiles="N/A"; }
if ( $recent_logfiles eq "0" ){ $recent_logfiles="N/A"; }
if ( $trecent_logfiles eq "" ){ $trecent_logfiles="N/A"; }
if ( $trecent_logfiles eq "0" ){ $trecent_logfiles="N/A"; }

if ( "$#addresses" < 0 ){ @addresses=("nobody"); }
for (@addresses) { s/'/\\'/g }

  $prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -g ${package} ${container} ${WLogdir} ${recent_logfiles} ${problems}  ${WQLogdir} ${qrecent_logfiles} ${qproblems} ${qecode} ${WTLogdir} ${trecent_logfiles} ${tproblems} ${tecode} @addresses";
  $pid = open(RM, "${prg} |");
  while (<RM>){ print WP "$_"; }
  close (RM);

}
} #done 
 
     $prg = "${ARDOC_HOME}/ardoc_wwwgen.pl -f";
     $pid = open(RM, "${prg} |");
     while (<RM>){ print WP "$_"; }
     close (RM);

     close (WP);

#making copies
if ( "${ARDOC_PROJECT_RELNUMB}" eq "" )
{
system("rm -f ${WWW_DIR}/ardoc_buildsummary${sortsuffix}.html");
}
else
{
system("rm -f ${WWW_DIR}/ardoc_buildsummary${sortsuffix}_${ARDOC_PROJECT_RELNUMB}.html"); 
}

system("cp -p ${webpage} ${WWW_DIR}/.");
} #foreach $sortsuffix (@sortind)

@prepx=();
@tprepy=();

system("cp -p ${webpage} ${WWW_DIR}/.");
system("cp -p ${inttestpage} ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/tick.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/cross_red.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/yl_ball.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/Back3.jpg ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/post-worldletter.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/pur_sq.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/question2_s.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/rad18x16.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/black_tick.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/Master.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/inform.gif ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/one_half.50x50.jpg ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/one_quarter.50x50.jpg ${WWW_DIR}/.");
system("cp -p ${ARDOC_HOME}/doc/images/three_quarters.50x50.jpg ${WWW_DIR}/.");

#copy previous tag list
$pfilegen1="${ARDOC_DBFILE_GEN}_res";
$pfilegen=basename($pfilegen1);
opendir(WWWS, ${ARDOC_WEBDIR});
my @wwwli = sort { compartim($a) <=> compartim($b) }
grep { /^${pfilegen}/ }
readdir (WWWS);
closedir(WWWS);

if ( $ARDOC_INC_BUILD eq "yes" )
{
    if ( ${ARDOC_PROJECT_RELNUMB_ORIG} ne "" ){
        $file_to_copy="${pfilegen}_${ARDOC_PROJECT_RELNUMB_ORIG}_prev";}
    else{
	$file_to_copy="${pfilegen}_res_prev";}
    $filefile="${ARDOC_WEBDIR}/${file_to_copy}";
    if ( -f $filefile ){
    system("cp -p ${ARDOC_WEBDIR}/${file_to_copy} ${WWW_WORK}/${pfilegen}_prev");
    }
}
else {   # if ( $ARDOC_INC_BUILD eq "yes" 
if ( $#wwwli > -1 ){
my @wwwlis = reverse @wwwli;
$file_to_copy=$wwwlis[0];
$file_to_copy=$wwwlis[1] if ( $#wwwlis > 0 ); 
$filefile="${ARDOC_WEBDIR}/${file_to_copy}";
if ( -f $filefile ){
system("cp -p ${ARDOC_WEBDIR}/${file_to_copy} ${WWW_WORK}/${pfilegen}_prev");
}
}
} # if ( $ARDOC_INC_BUILD eq "yes" )

#making index and other pages
 
###$prg = "${ARDOC_HOME}/ardoc_indexgen.pl ${WWW_WORK}/ardoc_projectpage.html";
###$pid = open(RM, "${prg} |");
###while (<RM>){ print STDOUT "$_"; }
###close (RM);

###$prg = "${ARDOC_HOME}/ardoc_configgen.pl ${WWW_WORK}/ardoc_configuration.html";
###$pid = open(RM, "${prg} |");
###while (<RM>){ print STDOUT "$_"; }
###close (RM);

###$prg = "${ARDOC_HOME}/ardoc_contentgen.pl ${WWW_WORK}/ardoc_content_${ARDOC_PROJECT_RELNUMB}.html";
###if ( "${ARDOC_PROJECT_RELNUMB}" eq "" )
###{
###    $prg = "${ARDOC_HOME}/ardoc_contentgen.pl ${WWW_WORK}/ardoc_content.html";
###}
###$pid = open(RM, "${prg} |");
###while (<RM>){ print STDOUT "$_"; }
###close (RM);

###system("cp -p ${WWW_WORK}/ardoc_projectpage.html ${WWW_DIR}/.");
##system("cp -p ${WWW_WORK}/ardoc_configuration.html ${WWW_DIR}/.");

if ( -f "${WWW_WORK}/ardoc_content.html" )
{
if ( "${ARDOC_PROJECT_RELNUMB}" eq "" )
{
system("cp -p ${WWW_WORK}/ardoc_content.html ${WWW_DIR}/.");
}
}

if ( -f "${WWW_WORK}/ardoc_content_${ARDOC_PROJECT_RELNUMB}.html" )
{
if ( "${ARDOC_PROJECT_RELNUMB}" ne "" )
{
system("cp -p ${WWW_WORK}/ardoc_content_${ARDOC_PROJECT_RELNUMB}.html ${WWW_DIR}/.");
}
}

chdir "${WWW_DIR}";
unlink "index.html";
#system("ln -s ardoc_projectpage.html index.html");
system("ln -s ardoc_buildsummary.html index.html");
#unlink "nightly_builds.html";
#system("ln -s ardoc_projectpage.html nightly_builds.html");
chdir "${prevdir}";











