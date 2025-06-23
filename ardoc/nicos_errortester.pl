#!/usr/bin/env perl
#
#-----------------------------------------------------------------------------
#
# nicos_errortester.pl <package> <release>
#
# Shell script to test logfiles
#    code system. used to determine if rotation can be performed.
#
# Arguments:   <package>  Package name
#              <release>  Release name
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
use Cwd;
use File::Basename;
use URI::Escape;

sub header_print{
    local (*G) = @_[0];
    my $prblm=@_[1];
    my $test_nm=@_[2];
    my $comment="";
    if ( $prblm == 0.5 ) { $comment="M";}
    if ( $prblm == 1 ) { $comment="W";}
    if ( $prblm == 2 ) { $comment="E";}
print G "<html>
<!-- ${comment} -->
<style>
body {
  color: black;
  link: navy;
  vlink: maroon;
  alink: tomato;
  background: floralwhite;
  font-family: 'Lucida Console', 'Courier New', Courier, monospace;
  font-size: 10pt;
}
td.aid {
  background: #6600CC;
  color: orangered;
  text-align: center;
}
td.ttl {
  color: #6600CC;
  text-align: center;
}
a.small {
  color: navy;
  background: #FFCCFF;
  font-family: Verdana, Arial, Helvetica, sans-serif;
  font-size: 10pt;
}
#prblm {background-color: orange;}
#hdr0 {
  font-family: Verdana, Arial, Helvetica, sans-serif;
  font-size: 14pt;
}
#hdr {
background-color: #FFCCFF;
  font-family:'Times New Roman',Garamond, Georgia, serif;
  font-size: 14pt;
}
#hdr1 {
background-color: #CFECEC;
  font-family: Verdana, Arial, Helvetica, sans-serif;
  font-size: 10pt;
}
</style>

<head><title>
${test_nm} Logfile
</title>
</head>

<BODY class=body marginwidth=\"0\" marginheight=\"0\" topmargin=\"0\" leftmargin=\"0\">
";
}
#
$short=0;
$specformat=0;
$testtesting=0;
$qatesting=0;
# with light option the most error and warning patterns are invalidated for test log analysis
$light=0;

if ($#ARGV>=0) {
    $_ = $ARGV[0];
    /^-[qstel]+$/ && /s/ && do { $short=1; };
    /^-[qstel]+$/ && /e/ && do { $specformat=1; };
    /^-[qstel]+$/ && /t/ && do { $testtesting=1; };
    /^-[qstel]+$/ && /q/ && do { $qatesting=1; };
    /^-[qstel]+$/ && /l/ && do { $light=1; };
    /^-[qstel]+$/ && shift;
    }
#
#-> check for correct number of arguments
#
my $NICOS_LOG="$NICOS_LOG";
my $NICOS_TESTLOG="$NICOS_TESTLOG";
my $NICOS_HOME="$NICOS_HOME";
my $NICOS_PROJECT_NAME="$NICOS_PROJECT_NAME";

if ( $testtesting == 0 && $qatesting == 0 ){
    $type="package";
    $type_in_url="c";
    $type_in_html="build";
    $NICOS_TESTLOGDIR=dirname($NICOS_LOG);
    if ( "$#ARGV" ne 3 ){
    print "nicos_errortester:\n";
    print "Four arguments required: directory_package, release, tags file, package name\n";
    exit 2;
    }
}
else{
    $type_in_url="t";
    $type_in_html="test";
    $type="test";
    $type="qatest" if ($qatesting == 1);
    $NICOS_TESTLOGDIR=dirname(${NICOS_TESTLOG});
    $NICOS_TESTLOGDIR=dirname(${NICOS_QALOG}) if ($qatesting == 1);
    $NICOS_TESTLOGDIR_TEMP="$NICOS_TESTLOGDIR/temp";
    if ( "$#ARGV" ne 1 ){
    print "nicos_errortester:\n";
    print "Two arguments required: names of test, release @ARGV\n";
    exit 2;
}
}
$NICOS_TESTLOGDIRBASE = basename(${NICOS_TESTLOGDIR});

$filename=$ARGV[2];
$compname=$ARGV[0];
$release=$ARGV[1];
$pkgname_full=$ARGV[3];
$pkgname=$pkgname_full;
if ( $pkgname_full ne "" ){
$pkgname=basename($pkgname_full);
}

$cnt1=0;
while ($compname =~ /_${pkgname}/g) {$cnt1++; if ( $cnt1 > 25 ){last;}} 
if ( $cnt1 == 0 ){
    $contname = $compname;
} else {
    $cnt2=0;
    $_=$compname;
($contname = $compname ) =~ s{
(_)(${pkgname})
}
{ if (++$cnt2 == $cnt1 ){
""
} else {
$1 . $2
}
}gex;
}

my $TEST_SUCCESS_PATTERN="$NICOS_TEST_SUCCESS_PATTERN";
my $TEST_FAILURE_PATTERN="$NICOS_TEST_FAILURE_PATTERN";
my $TEST_WARNING_PATTERN="$NICOS_TEST_WARNING_PATTERN";
my $BUILD_FAILURE_PATTERN="$NICOS_BUILD_FAILURE_PATTERN";

if ($BUILD_FAILURE_PATTERN eq "") {
#    $BUILD_FAILURE_PATTERN="Error: path_not_found";
    $BUILD_FAILURE_PATTERN="CVBFGG";
} 
if ($qatesting == 1) {
    $TEST_SUCCESS_PATTERN="$NICOS_QA_SUCCESS_PATTERN";
    $TEST_FAILURE_PATTERN="$NICOS_QA_FAILURE_PATTERN";
    $TEST_WARNING_PATTERN="$NICOS_QA_WARNING_PATTERN";
}
my @e_patterns = (": error:", "CMake Error", "runtime error:", "No rule to make target", "${BUILD_FAILURE_PATTERN}", "raceback (most recent", "CVBFGG","error: ld","error: Failed to execute","no build logfile");
my @e_ignore = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "for ${NICOS_PROJECT_NAME}Release are");
my @e_ignore_2 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "for ${NICOS_PROJECT_NAME} are");
my @e_ignore_3 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "for ${NICOS_PROJECT_NAME}RunTime are");
my @e_ignore_4 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_ignore_5 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning_patterns = ("Errors/Problems found", "CMake Warning", "CMake Deprecation Warning", "Error in", "control reaches end of non-void", "suggest explicit braces", "> Warning:", "type qualifiers ignored on function return type", "[-Wsequence-point]", "mission denied", "nvcc warning :", "Warning: Fortran", 'library.*\sexposes\s+factory.*\sdeclared\s+in');
my @e_warning_patterns_correlators = ("", "", "", "", "", "", "", "${pkgname}","","","","","");
my @e_warning_patterns_ignore = ("Errors/Problems found : 0", "CVBFGG", "CVBFGG", "CVBFGG", "/external", "/external", "> Warning: template", "/external", "/external", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning_patterns_ignore_2 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG","CVBFGG","CVBFGG","CVBFGG","CVBFGG", "CVBFGG");
#my @e_warning_patterns_minor = ("overriding commands for target", "fake target due to", "ignoring commands for target", "CVBFGG", "too few arguments for format", "too many arguments for format", "unused variable");
my @e_warning_patterns_minor = (": warning: ", "Warning: the last line", "Warning: Unused class rule", 'Warning:\s.*rule',"#pragma message:", 'WARNING\s+.*GAUDI', "CVBFGG", "CVBFGG");
my @e_warning_patterns_minor_ignore = ("make[", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "ClassIDSvc", "CVBFGG", "CVBFGG");
my @e_warning_patterns_minor_ignore_2 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning_patterns_minor_ignore_3 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning_patterns_minor_ignore_4 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_success = ( "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning_success = ( "CVBFGG", "Package build succeeded", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @packages_to_bypass_success = ( "$NICOS_PROJECT_NAME", "${NICOS_PROJECT_NAME}Release", "${NICOS_PROJECT_NAME}RunTime" );
#
my $e_test_global_ignore="distcc";
my @e_test_failure=();
my @e_test_failure_ignore=();
my @e_test_failure_ignore_1=();
my @e_test_failure_ignore_2=();
my @e_test_failure_ignore_3=();
my @e_test_failure_ignore_4=();
my @e_test_failure_ignore_5=();
my @e_test_warnings=();
my @e_test_warnings_minor=();
my @e_test_warnings_minor_ignore=();
my @e_test_warnings_minor_ignore_1=();
my @e_test_warnings_minor_ignore_2=();
my @e_test_warnings_minor_ignore_3=();
my @e_test_warnings_minor_ignore_4=();
my @e_test_warnings_minor_ignore_5=();
my @e_test_warnings_minor_project_ignore=();
my @e_test_success=();
my @e_test_success_addtl=();
if ($qatesting == 1) {
@e_test_failure = ("*Timeout", "time quota spent", "*Failed", "ERROR_MESSAGE", "severity=FATAL", "Error: execution_error", "command not found", "tests FAILED", "tester: Error", "Errors while running CTest");
@e_test_failure_ignore = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "kvt: command not found", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_1 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_2 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_3 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_4 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_5 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings = ("${TEST_WARNING_PATTERN}", "raceback (most recent", "file not found", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor = ("severity=ERROR", "  ERROR", "No such file or directory", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore = ("CVBFGG", "ERROR (pool)", "INFO", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_1 = ("CVBFGG", "ERROR IN", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_2 = ("CVBFGG", "ServiceLocatorHelper", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_3 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_4 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_5 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_project_ignore = ("CVBFGG", "Athena", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_success = ( "CVBFGG", "${TEST_SUCCESS_PATTERN}", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_success_addtl = ();
} else { # if ($qatesting == 1)
@e_test_failure = ("test issue message: Timeout", "test status fail", "*Failed", "TEST FAILURE", "severity=FATAL", ": FAILURE ", "command not found", "ERROR_MESSAGE", " ERROR ", "exit code: 143", "time quota spent");
@e_test_failure_ignore = ("CVBFGG", "CVBFGG", "CVBFGG", "ctest status notrun", "CVBFGG", "check_log", "CVBFGG", "CVBFGG", "check_log", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_1 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "HelloWorld", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_2 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "Cannot interpolate outside histogram", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_3 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "INFO ", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_4 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "ERROR Propa", "CVBFGG", "CVBFGG");
@e_test_failure_ignore_5 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "Acts", "CVBFGG", "CVBFGG");
@e_test_warnings = ("${TEST_WARNING_PATTERN}", "raceback (most recent", "file not found", "Logfile error", "Non-zero return", "TEST WARNING", "*Timeout", "CVBFGG");
#@e_test_warnings_minor = ("severity=ERROR", "  ERROR", "No such file or directory", "ctest status notrun", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"); 
@e_test_warnings_minor = ("severity=ERROR", "  ERROR", "No such file or directory", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore = ("CVBFGG", "ERROR (pool)", "INFO", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_1 = ("CVBFGG", "ERROR IN", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_2 = ("CVBFGG", "ServiceLocatorHelper", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_3 = ("CVBFGG", "HelloWorld", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_4 = ("CVBFGG", "Cannot interpolate outside histogram", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_ignore_5 = ("CVBFGG", "Acts", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_warnings_minor_project_ignore = ("CVBFGG", "Athena", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_success = ( "Info: test completed", "${TEST_SUCCESS_PATTERN}", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
@e_test_success_addtl = (); 
if ( $light == 1 ){
    for ($m=0; $m <= $#e_test_failure; $m++){
        $e_test_failure[$m]="CVBFGG";
    }
    for ($m=0; $m <= $#e_test_warnings; $m++){
      	$e_test_warnings[$m]="CVBFGG";
    }
    for ($m=0; $m <= $#e_test_warnings_minor; $m++){
        $e_test_warnings_minor[$m]="CVBFGG";
    }
    $e_test_failure[0]="test issue message: Timeout";
    $e_test_failure[1]="test status fail";
    $e_test_failure[2]="TEST FAILURE";
    $e_test_failure_ignore[0]="CVBFGG";
    $e_test_failure_ignore[1]="CVBFGG";
    $e_test_failure_ignore[2]="ctest status notrun";
    $e_test_warnings_minor[0]="ctest status notrun"; $e_test_warnings_minor[1]="*Failed"; $e_test_warnings_minor[2]="TEST FAILURE";
#    $e_test_warnings_minor[0]="CVBFGG"; $e_test_warnings_minor[1]="*Failed"; $e_test_warnings_minor[2]="TEST FAILURE";
    $e_test_warnings_minor[3]="*Timeout"; $e_test_warnings_minor[4]="time quota spent";
    warn "===nicos_errortester.pl: limited error analysis for $compname\n";
} 
} # else if ($qatesting == 1)
my @e_count = (0,0,0,0,0,0,0,0,0,0,0);
my @w_count = (0,0,0,0,0,0,0,0,0,0,0,0,0);
my @w_minor_count = (0,0,0,0,0,0,0,0);
my @s_count = (0,0,0,0,0,0,0,0,0,0);
my @s_w_count = (0,1,0,0,0,0,0,0);
my @lineE = (0,0,0,0,0,0,0,0,0,0,0);
my @lineW = (0,0,0,0,0,0,0,0,0,0,0,0,0);
my @lineM = (0,0,0,0,0,0,0,0);
my @lineEValue = ("","","","","","","","","","","");
my @lineWValue = ("","","","","","","","","","","","","");
my @lineMValue = ("","","","","","","","");
if ( $testtesting == 1 || $qatesting == 1 ){ 
@s_count = (0,1,0,0,0,0,0,0,0,0); 
@s_w_count = (0,0,0,0,0,0,0,0);
$NICOS_TESTLOGDIR_TEMP="$NICOS_TESTLOGDIR/temp";
$file_er="${NICOS_TESTLOGDIR_TEMP}/${compname}_ERROR_MESSAGE";
$file_wa="${NICOS_TESTLOGDIR_TEMP}/${compname}_WARNING_MESSAGE";
$file_su="${NICOS_TESTLOGDIR_TEMP}/${compname}_SUCCESS_MESSAGE";
$dfgert=1;
#print "$file_er $file_wa $file_su\n";
     if (-f ${file_er} && $dfgert == 0){
           open(UT, "$file_er"); 
           while (<UT>) {
           chomp;
           ( $lin1 = $_ ) =~ s/ //g;
           next if (length($lin1) eq 0);
           ( $lin2 = $_ ) =~ s/\n//g;
#           print "EEEE =$lin2=\n"; 
           push(@e_test_failure,$lin2);  
           push(@e_test_failure_ignore,"CVBFGG");
           push(@e_test_failure_ignore_1,"CVBFGG");
           push(@e_test_failure_ignore_2,"CVBFGG");
           push(@e_test_failure_ignore_3,"CVBFGG");
           push(@e_test_failure_ignore_4,"CVBFGG");
           push(@e_test_failure_ignore_5,"CVBFGG");
           $a=0;
           push(@e_count,$a);
	   push(@lineE,$a);
           $a_strng="";
           push(@lineEValue,$a_strng);
           }
     close(UT);   
     }
     if (-f ${file_wa} && $dfgert == 0){
           open(UT, "$file_wa");
           while (<UT>) {
           chomp;
           ( $lin1 = $_ ) =~ s/ //g;
           next if (length($lin1) eq 0);
           ( $lin2 = $_ ) =~ s/\n//g;
           push(@e_test_warnings,$lin2);
           $a=0;
           push(@w_count,$a);
	   push(@lineW,$a);
           $a_strng="";
           push(@lineWValue,$a_strng);
           }
     close(UT);
     }
     if (-f ${file_su} && $dfgert == 0){
           open(UT, "$file_su");
           while (<UT>) {
           ( $lin1 = $_ ) =~ s/ //g;
           next if (length($lin1) eq 0);
           ( $lin2 = $_ ) =~ s/\n//g;
           push(@e_test_success,$lin2);
           push(@e_test_success_addtl,$lin2);
#           print "SSSS ===${lin2}=====@e_test_success_addtl\n";
           $a=1;
           push(@s_count,$a);
           } 
     close(UT);
     }
}

#print " e_test_failure @e_test_failure : @e_count \n";
#print " e_test_warnings @e_test_warnings : @w_count : $TEST_WARNING_PATTERN\n";
#print " e_test_success @e_test_success : @s_count \n";

if ( $specformat eq 0 ){
    print "====================================================================\n";
    print "=== CHECK logfiles related to $compname in $release\n";
    print "====================================================================\n";
    print " \n";
}

if ( $testtesting == 0 && $qatesting == 0 ){ 
open(DBF,"$filename");
chomp(my @dbc=<DBF>);
close(DBF);
#warn "PKGNAME_F ${pkgname_full}\n";
@list = grep /^${pkgname_full}[^a-zA-Z0-9_]/, @dbc; 
#warn "@list\n";
$lll = join(' ', split(' ', $list[0]));
$tag = (split(" ", $lll))[1];
#warn "TAG $tag\n";
}

#
#
opendir(DD, ${NICOS_TESTLOGDIR});
@allfiles = readdir DD;
closedir DD;
$stg="${compname}.loglog";
@list = grep /^${stg}$/, @allfiles;
$listfiles = (sort { -M $a <=> -M $b } @list)[0];
#print " --- $compname --- $NICOS_TESTLOGDIR -- $listfiles\n";

   $lineT=0;
   $file="$NICOS_TESTLOGDIR/$listfiles"; 
   $filebase1=basename($file);
   $filedir=dirname($file); 
   $filebase=$filebase1;
   @filebase_a=split('\.',$filebase);
   if ( $#filebase_a > 0 ) {
       pop @filebase_a;
       $filebase=join('\.',@filebase_a);
       $filehtml="$filedir/$filebase" . ".html";
   }
   $textfile_http="${NICOS_WEBPAGE}/NICOS_Log_${NICOS_PROJECT_RELNAME_COPY}/${filebase1}";
   if ( ${testtesting} != 0 ){
   $textfile_http="${NICOS_WEBPAGE}/NICOS_TestLog_${NICOS_PROJECT_RELNAME_COPY}/${filebase1}";
   } elsif ( ${qatesting} != 0 ){
   $textfile_http="${NICOS_WEBPAGE}/NICOS_QALog_${NICOS_PROJECT_RELNAME_COPY}/${filebase1}";
   }
   $optn="$contname $pkgname build";
   if ( ${testtesting} != 0 || ${qatesting} != 0 ){
   @f_contname=split("__",$contname);
   $contname1=$f_contname[0];
   $inddd=$#f_contname; 
   $tname="";
   if ( $inddd > 0 ){
       $tname=$f_contname[$inddd];
   }
   @f_tname=split("_",$tname);
   $ft1=$#f_tname;
   if ( $ft1 > 0 ){
       if ( $f_tname[$ft1] =~ /^\w\s*$/ ){
           pop(@f_tname);
           $tname=join("_",@f_tname);
       } 
   }
   @f_contname1=split("_",$contname1);
   $fcnt1=$#f_contname1;
   $tnumber="";
   if ( $fcnt1 > 0 ){
       $fcnt9=$f_contname1[$fcnt1];
       if ( $fcnt9 =~ /^\d\d$/ ){
           $tnumber=pop(@f_contname1);
           $tnumber="#".$tnumber;
           $contname1=join("_",@f_contname1); 
	   }
   }  
   $fcnt1=$#f_contname1;
   $fcnt9=$f_contname1[$fcnt1];
   if ( lc($fcnt9) eq lc($tname) ){ $tname="";} 
   $optn="$contname1 $tnumber $tname test";
   }
$aid_message_html = <<EAID;
<DIV id=hdr0>
<table bordercolor=\"#6600CC\" border=10 cellpadding=5 cellspacing=0 width=\"100%\">
<tr><td class=aid width=20% align=center valign=baseline>
<H1>NICOS</H1>
</td>
<td class=ttl>
<EM><B><BIG>$optn logfile</BIG></EM></B>
</td></tr>
<tr><td class=aid>
    version  ${NICOS_VERSION}
</td>
EAID

   if ( -f $file ){
   open(FL, "<$file");
   while (<FL>){ 
      chomp;
      $line=$_;
      $lineT++;
      if ( ${testtesting} == 0 && ${qatesting} == 0 ){
      for ($m=0; $m <= $#e_patterns; $m++){
        if ( $e_patterns[$m] ne "" && $line =~ /\Q$e_patterns[$m]\E/ && $line !~ /\Q$e_ignore[$m]\E/ && $line !~ /\Q$e_ignore_2[$m]\E/ && $line !~ /\Q$e_ignore_3[$m]\E/ && $line !~ /\Q$e_ignore_4[$m]\E/ && $line !~ /\Q$e_ignore_5[$m]\E/){ 
        $e_count[$m]++;
        if ( $lineE[$m] == 0 ) { $lineE[$m]=$lineT; $lineEValue[$m]=$line; }
        }
      }
      for ($m=0; $m <= $#e_warning_patterns; $m++){
          if ( $e_warning_patterns[$m] =~ /\.\*/ ) {
              if ( $e_warning_patterns[$m] ne "" && $line =~ /$e_warning_patterns[$m]/ && $line !~ /\Q$e_warning_patterns_ignore[$m]\E/ && $line !~ /\Q$e_warning_patterns_ignore_2[$m]\E/){
                  if ( $e_warning_patterns_correlators[$m] eq "" ){
                      $w_count[$m]++;
                      if ( $lineW[$m] == 0 ) { $lineW[$m]=$lineT; $lineWValue[$m]=$line; }
                  }
                  else{
                      if ( $line =~ /\Q$e_warning_patterns_correlators[$m]\E/ ){
                          $w_count[$m]++;
                          if ( $lineW[$m] == 0 ) { $lineW[$m]=$lineT; $lineWValue[$m]=$line; }
                      }
                  }
              }
          }
          else {
              if ( $e_warning_patterns[$m] ne "" && $line =~ /\Q$e_warning_patterns[$m]\E/ && $line !~ /\Q$e_warning_patterns_ignore[$m]\E/ && $line !~ /\Q$e_warning_patterns_ignore_2[$m]\E/){
                  if ( $e_warning_patterns_correlators[$m] eq "" ){
                      $w_count[$m]++;
                      if ( $lineW[$m] == 0 ) { $lineW[$m]=$lineT; $lineWValue[$m]=$line; }
                  }
                  else{
                      if ( $line =~ /\Q$e_warning_patterns_correlators[$m]\E/ ){
                          $w_count[$m]++;
                          if ( $lineW[$m] == 0 ) { $lineW[$m]=$lineT; $lineWValue[$m]=$line; }
                      }
                  }
              }
          }
      }
      for ($m=0; $m <= $#e_warning_patterns_minor; $m++){
          if ( $e_warning_patterns_minor[$m] =~ /\.\*/ ) {
              if ( $e_warning_patterns_minor[$m] ne "" && $line =~ /$e_warning_patterns_minor[$m]/ && $line !~ /\Q$e_warning_patterns_minor_ignore[$m]\E/ && $line !~ /\Q$e_warning_patterns_minor_ignore_2[$m]\E/ && $line !~ /\Q$e_warning_patterns_minor_ignore_3[$m]\E/ && $line !~ /\Q$e_warning_patterns_minor_ignore_4[$m]\E/ ){
	      $w_minor_count[$m]++;
	      if ( $lineM[$m] == 0 ) { $lineM[$m]=$lineT; $lineMValue[$m]=$line; }
              }
          }
          else {
              if ( $e_warning_patterns_minor[$m] ne "" && $line =~ /\Q$e_warning_patterns_minor[$m]\E/ && $line !~ /\Q$e_warning_patterns_minor_ignore[$m]\E/ && $line !~ /\Q$e_warning_patterns_minor_ignore_2[$m]\E/ && $line !~ /\Q$e_warning_patterns_minor_ignore_3[$m]\E/ && $line !~ /\Q$e_warning_patterns_minor_ignore_4[$m]\E/ ){
              $w_minor_count[$m]++;
              if ( $lineM[$m] == 0 ) { $lineM[$m]=$lineT; $lineMValue[$m]=$line; }
              }
          }
      }
      $bypass_success=0;
      for ($ppp=0; $ppp <= $#packages_to_bypass_success; $ppp++){
         if ( $packages_to_bypass_success[$ppp] eq $pkgname ) {$bypass_success++;} 
      }
#      warn "PPPPPPPPPPP $pkgname $bypass_success\n";
      for ($m=0; $m <= $#e_success; $m++){
        if ( ( $line =~ /\Q$e_success[$m]\E/ || $bypass_success != 0 ) && $s_count[$m] > -1 ) {$s_count[$m]--;}
      }     
      for ($m=0; $m <= $#e_warning_success; $m++){
        if ( ( $line =~ /\Q$e_warning_success[$m]\E/ || $bypass_success != 0 ) && $s_w_count[$m] > -1 ) {$s_w_count[$m]--;}
      } 
      }
      else{     
        for ($m=0; $m <= $#e_test_failure; $m++){
	    if ( $e_test_failure[$m] ne "" && $line =~ /\Q$e_test_failure[$m]\E/ && $line !~ /\Q$e_test_global_ignore\E/ && $line !~ /\Q$e_test_failure_ignore[$m]\E/ && $line !~ /\Q$e_test_failure_ignore_1[$m]\E/ && $line !~ /\Q$e_test_failure_ignore_2[$m]\E/ && $line !~ /\Q$e_test_failure_ignore_3[$m]\E/ && $line !~ /\Q$e_test_failure_ignore_4[$m]\E/ && $line !~ /\Q$e_test_failure_ignore_5[$m]\E/){
	      $ignr=0;
	      ( $lin1 = $_ ) =~ s/ //g;
              for ($ms=0; $ms <= $#e_test_success_addtl; $ms++){
                  ( $esa1 = $e_test_success_addtl[$ms] ) =~ s/ //g; 
		  if ( $esa1 ne "" && $e_test_success_addtl[$ms] ne " " && $line =~ /\Q$e_test_success_addtl[$ms]\E/ ){
#                      warn "ESAA $e_test_success_addtl[$ms]\n";
		      $ignr=1;
                  }
              }
            if ( $ignr == 0 ) {
                $e_count[$m]++;
		if ( $lineE[$m] == 0 ) { $lineE[$m]=$lineT; $lineEValue[$m]=$line; }
            }
	  }
#        print "X $line\n";
#        print "YY $e_count[$m] XXX $e_test_failure[$m]\n";
      } # for
   } # if ( ${testtesting} eq 0

    if ( ${testtesting} != 0 || ${qatesting} != 0 ){

    for ($m=0; $m <= $#e_test_warnings; $m++){
        if ( $e_test_warnings[$m] =~ /\.\*/ ) {
            if ( $e_test_warnings[$m] ne "" && $line =~ /$e_test_warnings[$m]/ && $line !~ /\Q$e_test_global_ignore\E/){
	    $w_count[$m]++;
            if ( $lineW[$m] == 0 ) { $lineW[$m]=$lineT; $lineWValue[$m]=$line; }
            }
        }
        else {
            if ( $e_test_warnings[$m] ne "" && $line =~ /\Q$e_test_warnings[$m]\E/ && $line !~ /\Q$e_test_global_ignore\E/){
            $w_count[$m]++;
            if ( $lineW[$m] == 0 ) { $lineW[$m]=$lineT; $lineWValue[$m]=$line; }
            }
        }
    } # for

    for ($m=0; $m <= $#e_test_warnings_minor; $m++){
        if ( $e_test_warnings_minor[$m] ne "" && $line =~ /\Q$e_test_warnings_minor[$m]\E/){
        if ( $NICOS_PROJECT_NAME ne $e_test_warnings_minor_project_ignore[$m] && $line !~ /\Q$e_test_global_ignore\E/ && $line !~ /\Q$e_test_warnings_minor_ignore[$m]\E/ && $line !~ /\Q$e_test_warnings_minor_ignore_1[$m]\E/ && $line !~ /\Q$e_test_warnings_minor_ignore_2[$m]\E/ && $line !~ /\Q$e_test_warnings_minor_ignore_3[$m]\E/ && $line !~ /\Q$e_test_warnings_minor_ignore_4[$m]\E/ && $line !~ /\Q$e_test_warnings_minor_ignore_5[$m]\E/ ){
        $w_minor_count[$m]++;
        if ( $lineM[$m] == 0 ) { $lineM[$m]=$lineT; $lineMValue[$m]=$line; }
        }
        }
    } # for

    for ($m=0; $m <= $#e_test_success; $m++){
#        print "X $line\n";
        if ( $line =~ /\Q$e_test_success[$m]\E/ && $s_count[$m] > -1 ) {$s_count[$m]--;}
#        print "YS $line VV $m $s_count[$m] XXX $e_test_success[$m]\n";
    } # for
    } # if ( ${testtesting} 

   } # while
   close (FL);
      $eeee="";
      $lineEE=0;
      $lineWW=0;
      $lineMM=0;
      $lineEEValue=0;
      $lineWWValue=0;
      $lineMMValue=0;
      if ( ${testtesting} == 0 && ${qatesting} == 0 ){
      for ($m=0; $m <= $#e_patterns; $m++){
      $count=$e_count[$m];
      next if ($count <= 0); 
      if ( $e_patterns[$m] ne "CVBFGG" ){
      $eeee="$e_patterns[$m]"; $lineEE=$lineE[$m]; $lineEEValue=$lineEValue[$m]; last;
      }
      }
      }
      else
      {
      for ($m=0; $m <= $#e_test_failure; $m++){
      $count=$e_count[$m];
      next if ($count <= 0);
      if ( $e_test_failure[$m] ne "CVBFGG" ){
	$eeee="$e_test_failure[$m]"; $lineEE=$lineE[$m]; $lineEEValue=$lineEValue[$m]; last;
        }
      }
      }   

      $ssss="";
      $n_ele=$#e_success;
      if ( ${testtesting} != 0 || ${qatesting} != 0 ){ $n_ele=$#e_test_success;} 
      for ($m=0; $m <= $n_ele; $m++){
      $count=$s_count[$m];
      next if ($count <= 0);
      if ( ${testtesting} != 0 || ${qatesting} != 0 ){
        $ssss="$e_test_success[$m]"."(ABSENSE OF)"; 
        last;
        }
      else
        {
        $ssss="$e_success[$m]"."(ABSENSE OF)"; 
        last;
        } 
      }

      $ssww="";
      $n_ele=$#e_warning_success;
      if ( ${testtesting} != 0 || ${qatesting} != 0 ){ $n_ele=$#e_warning_test_success;}
      for ($m=0; $m <= $n_ele; $m++){
      $count=$s_w_count[$m];
      next if ($count <= 0);
      if ( ${testtesting} != 0 || ${qatesting} != 0 ){
#        $ssww="$e_warning_test_success[$m]"."(ABSENSE OF)";
        last;
        }
      else
        {
	$ssww="$e_warning_success[$m]"."(ABSENSE OF)";
	last;
        }
      }

      $wwww="";
      if ( ${testtesting} == 0 && ${qatesting} == 0 ){
      for ($m=0; $m <= $#e_warning_patterns; $m++){
      $count=$w_count[$m];
      next if ($count <= 0);
          if ( $e_warning_patterns[$m] ne "CVBFGG" ){
	  $wwww="$e_warning_patterns[$m]";
          $lineWW=$lineW[$m]; $lineWWValue=$lineWValue[$m]; 
          if ( $e_warning_patterns_correlators[$m] ne "" ){
	      $wwww="$wwww"." AND "."$e_warning_patterns_correlators[$m]";
	      $lineWW=$lineW[$m]; $lineWWValue=$lineWValue[$m];
          }  
          last;
          }
      }
      }
      else{      
      for ($m=0; $m <= $#e_test_warnings; $m++){
      $count=$w_count[$m];
      next if ($count <= 0);
             if ( $e_test_warnings[$m] ne "CVBFGG" ){
	     $wwww="$e_test_warnings[$m]"; $lineWW=$lineW[$m]; $lineWWValue=$lineWValue[$m]; last;
             }
      }
      }

      if ( ${testtesting} == 0 && ${qatesting} == 0 ){
      for ($m=0; $m <= $#e_warning_patterns_minor; $m++){
	  $count=$w_minor_count[$m];
	  next if ($count <= 0);
          if ( $e_warning_patterns_minor[$m] ne "CVBFGG" ){
	      $wwww_minor="$e_warning_patterns_minor[$m]"; $lineMM=$lineM[$m]; $lineMMValue=$lineMValue[$m];
	      last;
          }
      }
      }
      else{
      for ($m=0; $m <= $#e_test_warnings_minor; $m++){
	  $count=$w_minor_count[$m];
	  next if ($count <= 0);
	  if ( $e_test_warnings_minor[$m] ne "CVBFGG" ){
	      $wwww_minor="$e_test_warnings_minor[$m]"; $lineMM=$lineM[$m]; $lineMMValue=$lineMValue[$m]; last;
	  }
      }
      }
                $mess="No problems found";
                if ( $light == 1 ) {
                    $mess="Test succeeded, based on the exit code (error highlighting off)";
		}
                $linkline=0;
                $linkvalue="";
                $problems=0;
                if ( $eeee ne "" ){ 
                $linkline=$lineEE; $linkvalue=$lineEEValue;
                $mess="Error pattern found: $eeee";
                $problems=2; 
                if ( $specformat eq 0 ){
                    print "====================================================================\n";
                    print " $type $compname has problem. See \n";
                    print " $file \n";
                    print " for pattern(s)  ------ $eeee -----\n";
                    print "====================================================================\n";
		    } 
	        else{
#                    $varbase = basename($var);
                    print "G $compname $NICOS_TESTLOGDIR $eeee";
                }
                if ( $short eq 0 ){
                    exit 2;
                }
                } 
                elsif ( $ssss ne "" ) #if ( $eeee ne ""
                {
		    $linkline=0;
                    ($ssss1 = $ssss) =~ s/\Q(ABSENSE OF)\E//;
		    $mess="Required success pattern not found: $ssss1";
         	    $problems=2;
                    if ( $specformat eq 0 ){
                    print "===================================================\
================\n";
                    print " $type $compname has problem. See \n";
                    print " $file \n";
                    print " for pattern(s)  ------ $ssss -----\n";
                    print "====================================================================\n";
	            }
		    else{
#			$varbase = basename($var);
			print "G $compname $NICOS_TESTLOGDIR $ssss";
		    }
		    if ( $short eq 0 ){
			exit 2;
		    }

		}
                elsif ( $wwww ne "" ) #if ( $eeee ne "" 
	        {
		    $linkline=$lineWW; $linkvalue=$lineWWValue;
		    $mess="Serious warning pattern found: $wwww";
		    $problems=1;
                    if ( $specformat eq 0 ){
			print "====================================================================\n";
			print " $type $compname has warning. See \n";
			print " $file \n";
			print " for pattern(s)  ------ $wwww -----\n";
			print "====================================================================\n";
                    }
		    else{
#			$varbase = basename($var);
			print "W $compname $NICOS_TESTLOGDIR $wwww";
		    }
		    if ( $short eq 0 ){
			exit 2;
		    }
                } #eslif ( $wwww ne "" )
                elsif ( $ssww ne "" ) #if ( $eeee ne ""
                {
                    $linkline=0;
                    ($ssww1 = $ssww) =~ s/\Q(ABSENSE OF)\E//;
                    $mess="Essential pattern not found: $ssww1 , this triggers serious warning";
                    $problems=2;
                    if ( $specformat eq 0 ){
                    print "===================================================\                                    
================\n";
                    print " $type $compname has warning. See \n";
                    print " $file \n";
                    print " for pattern(s)  ------ $ssww -----\n";
                    print "====================================================================\n";
                    }
                    else{
                        print "W $compname $NICOS_TESTLOGDIR $ssww";
                    }
                    if ( $short eq 0 ){
                        exit 2;
                    }
                } #eslif ( $ssww ne "" )
                else #if ( $wwww ne "" )
                {
                if ( $wwww_minor ne "" )
                {
                    $linkline=$lineMM; $linkvalue=$lineMMValue;
		    $mess="Minor warning pattern found: $wwww_minor";
                    $problems=0.5;
                    if ( $specformat eq 0 ){
                        print "====================================================================\n";
                        print " $type $compname has minor warning. See \n";
                        print " $file \n";
                        print " for pattern(s)  ------ $wwww_minor-----\n";
                        print "====================================================================\n";
                    }
                    else{
#                       $varbase = basename($var);
                        print "M $compname $NICOS_TESTLOGDIR $wwww_minor";
                    }
                    if ( $short eq 0 ){
                        exit 2;
                    }
                } #if ( $wwww_minor ne "" )
                } #else #if ( $wwww ne "" )
###############################
# HTML LOG GENERATION
###############################
$mess2="";
if ( $linkline != 0 ){
    $mess2="&nbsp;<BR>&nbsp;&nbsp;&nbsp;&nbsp;problematic line: </B><BR> &nbsp;&nbsp;&nbsp; <A class=small href=\"#prblm\">${linkvalue}</A><BR><B>";
}
$aid_message_html1 = <<END11;
<td class=ttl><EM><B>${mess}</B></EM>
</td>
</tr>
</table>
</DIV>
<DIV id=hdr>
<B>
    ${mess2}
    &nbsp;&nbsp;&nbsp;&nbsp;<A href=\"#end\">Link to the last line</A> <BR>
    &nbsp;<BR>
</B></DIV>
END11

$aid_message_html=$aid_message_html . $aid_message_html1;
if ( $filehtml ne "" ){
#    warn "nicos_errortester.pl: HTML: $filehtml\n";
    open(FG,">$filehtml");
    header_print( *FG, $problems, $option);
    print FG "$aid_message_html";
    print FG "<div id=hdr1>\n";
    if ( $testtesting == 0 && $qatesting == 0 ){
#    print FG "<a href=\"https://svnweb.cern.ch/trac/atlasoff/browser/${pkgname_full}/tags/${tag}\"><b>SVN browser link</b></a><BR>\n";
    print FG "<b><i>Placeholder for a link to GitLab</i></b><BR>\n"; 
#    warn "BROWSER LINK: <a href=\"https://svnweb.cern.ch/trac/atlasoff/browser/${pkgname_full}/tags/${tag}\"><b>SVN browser link</b></a>\n";
    }
    print FG "<b>Original log file:</b><CODE> $file </CODE><BR>\n";
#    print FG "copied to: <CODE> ${NICOS_COPY_HOME}/${NICOS_PROJECT_RELNAME_COPY}/NICOS_area/${NICOS_TESTLOGDIRBASE}/$filebase1 </CODE>\n";
    if ( $NICOS_WEB_HOME ne "" ){
	$webloc="${NICOS_WEB_HOME}/${NICOS_PROJECT_RELNAME_COPY}/NICOS_area/${NICOS_TESTLOGDIRBASE}/$filebase1";
#	print FG "<BR>\n";
#	print FG "<a href=\"${webloc}\"><b>Web access to the log file</b></a>\n";
    }
    if ( $NICOS_WEBPAGE ne "" ){
        $websum_d="http://atlas-nightlies-browser.cern.ch/~platinum/nightlies/info?tp=${type_in_url}&nightly=${NICOS_NIGHTLY_NAME}&rel=${NICOS_PROJECT_RELNAME_COPY}&ar=${NICOS_ARCH}&proj=${NICOS_PROJECT_NAME}";
        $websum="${NICOS_WEBPAGE}/nicos_${type_in_html}summary_${NICOS_PROJECT_RELNUMB_COPY}.html";
#	print FG "<BR>\n";
#        print FG "<a href=\"${websum_d}\"><b>Release ${type_in_html} summary</b></a>\n";
#        print FG "<BR>\n";
#        print FG "<a href=\"${websum}\"><b>Release ${type_in_html} summary (old static version)</b></a>\n";
    }
    print FG "</div>\n <P><PRE>\n";
    @allowed_1=();
    @allowed_2=();
    my $all_i=0;
    $total_ln=5000;
    $first_part=3000;
    $middle_part1=25;
    $middle_part2=25;
    $last_part=2000;
    if ( $testtesting != 0 ){
      if ( "${MR_TRAINING_DOMAIN}" ne "" ){
        print FG "Note: this MR training job probes domain ${MR_TRAINING_DOMAIN}, git branch ${MR_CURRENT_GIT_BRANCH}\n";
      }
      if ( $file =~ /^.*unit-tests.*$/ ){ 
        print FG "Note: there is limit of 75000 lines for this logfile. Excess lines (if any) are truncated.\n";  
        $total_ln=75000;
        $first_part=40000;
        $middle_part1=250;
        $middle_part2=250;
        $last_part=35000; 
      }
      else {
        print FG "Note: there is limit of 20000 lines for this logfile. Excess lines (if any) are truncated.\n";
        $total_ln=20000;
        $first_part=12000;
        $middle_part1=100;
        $middle_part2=100;
        $last_part=8000;        
      }
    }

    $all_i++;
    $allowed_1[0][$all_i]=0;
#    warn "TTTT $lineT, $lineMM, $lineWW, $lineEE,  $total_ln\n";
#    warn "LLLL $linkline $linkvalue\n";
    if ( $lineT <= $total_ln ){
	$allowed_2[0][$all_i]=$total_ln;
    }
    else {
	$allowed_2[0][$all_i]=$first_part;
	$brd=$lineT - $last_part + 1;
	$all_i++;
	$allowed_1[0][$all_i]=$brd;
	$allowed_2[0][$all_i]=$lineT;
	$brd_e1=$linkline-$middle_part1;
	$brd_e2=$linkline+$middle_part2;
	$all_i++;
	$allowed_1[0][$all_i]=$brd_e1;
	$allowed_2[0][$all_i]=$brd_e2;
    }
#    warn "nicos_errortester.pl: conversion info: @{$allowed_1[0]} -- @{$allowed_1[1]} \n";
#    warn "nicos_errortester.pl: conversion info: @{$allowed_2[0]} -- @{$allowed_2[1]} \n";
    $ncount_line=0;
    $first_line="ExecTest.stdout:";
    $first_line_ok=1;
    @first_arr=(); 
    $last_line="qmtest.target:";
    $last_line_sea=$lineT-5;
    $first_line_sea=3;
    if ( $first_line_sea >= ($lineT-1) ) {$first_line_sea=$lineT-1};
    $line_ok_2=1;
    $ncount_s[0]=0;
    open(FB,"<$file");
    while (<FB>){
	$ncount_line++;
#        warn "F $first_line_sea OK $first_line_ok CNT $ncount_line\n";
	$line_ok_1=1;
        $line_ok=0;
        if ( $_ =~ /^.*qmtest\.end_time.*$/ ||  $_=~ /^.*qmtest\.start_time.*$/ ) { $_=$_ . " (GMT time)"; } 
        if ( $ncount_line < $first_line_sea && $first_line_ok == 1 ){
	    $line_ok_1=0;
            ( $line_nosp = $_ ) =~ s/ //g;
            chomp($line_nosp);
            if ( $line_nosp eq $first_line ) { $first_line_ok=0;}
            push(@first_arr, $_);  
        }  
        if ( $ncount_line == $first_line_sea && $first_line_ok == 1 ){
	    $first_line_ok=0;
            %replacements = ( '<' => '&lt;', '>' => '&gt;', '&' => '&amp;',);
	    $replacement_string = join '', keys %replacements;
            foreach $f_line (@first_arr){
#                $encode_line = uri_escape($f_line);
                 $encode_line = $f_line;
                 if ( $f_line !~ /^.*CI_TEST.*href.*$/ && $f_line !~ /^.*test.*tailoring.*href.*$/ ) { 
                   ( $encode_line = $f_line) =~ s/([\Q$replacement_string\E])/$replacements{$1}/g;
#                  if ( $f_line =~ /</ ){ warn "RRR $encode_line"; }
                 }
		print FG "${encode_line}";
	    }
	}
        if ( $ncount_line > $last_line_sea ){
            ( $line_nosp = $_ ) =~ s/ //g;
            chomp($line_nosp);
            if ( $line_nosp eq $last_line ) { $line_ok_2=0;}
        }
  	for ( $ippo=0; $ippo <= $#{$allowed_1[0]}; $ippo++ ){
#    print "AAAA $ncount_line $ippo $allowed_1[0][$ippo] $allowed_2[0][$ippo]\n";
	    if ( $ncount_line >= $allowed_1[0][$ippo] && $ncount_line <= $allowed_2[0][$ippo]){
		$line_ok=1;
		last;
	    }
	}
	if (! $line_ok){$ncount_s[0]=0;}
	%replacements = ( '<' => '&lt;', '>' => '&gt;', '&' => '&amp;',);
	$replacement_string = join '', keys %replacements;
	if ($line_ok){
	    if ( $ncount_line != $linkline ){
		$ncount_s[0]++;
		if ( $ncount_s[0] == 1 && $ncount_line > 1 ) {
		    print FG <<DOTT;
<DIV ID=hdr>................................................................<BR>
.....LINES TRUNCATED <BR>
.....first $first_part lines, bottom $last_part lines <BR>
.....as well as lines around error messsage are displayed <BR>
................................................................
</DIV>
DOTT
                }
                if ($line_ok_1 && $line_ok_2) {
                $escp=$_;
                if ( $escp !~ /^.*CI_TEST.*href.*$/ && $escp !~ /^.*test.*tailoring.*href.*$/ ) {
                  $escp =~ s/([\Q$replacement_string\E])/$replacements{$1}/g; 
                }
                print FG "${escp}";
#                if ( $_ =~ /</ ){ warn "RRR $escp"; }
                }
            }
            else{
                $escp=$_;
                if ( $escp !~ /^.*CI_TEST.*href.*$/ && $escp !~ /^.*test.*tailoring.*href.*$/ ) {
                  $escp =~ s/([\Q$replacement_string\E])/$replacements{$1}/g; 
                }
                print FG "<div id=\"prblm\">${escp}</div>";
#                if ( $_ =~ /</ ){ warn "RRR $escp"; }
                $ncount_s[0]++;
            }
            if ( $ncount_line == $lineT ){
                print FG "  </PRE>\n";
                print FG "  <div id=\"end\">END OF LOGFILE</div>";
            }
        } # if ($line_ok)
} #while
close(FB);

  print FG "
  </body>
  </html>
  ";
close (FG);
} # if ( $filehtml ne "" ){

#copy generated htmllog to ${NICOS_WEBDIR}
$filehtml_base=basename($filehtml);
$copy_html="${NICOS_WEBDIR}/NICOS_Log_${NICOS_PROJECT_RELNAME_COPY}/${filehtml_base}";
if ( ${testtesting} != 0 ){
    $copy_html="${NICOS_WEBDIR}/NICOS_TestLog_${NICOS_PROJECT_RELNAME_COPY}/${filehtml_base}";
}
elsif ( ${qatesting} != 0 ){
    $copy_html="${NICOS_WEBDIR}/NICOS_QALog_${NICOS_PROJECT_RELNAME_COPY}/${filehtml_base}";
}
#warn "nicos_errortester: cp -Rp $filehtml $copy_html\n";
    system("cp -Rp $filehtml $copy_html");

if ( $short eq 0 ){
    print "(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)\n";
    print "         Logfiles of $type $compname looks OK\n";
    print "(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)(..)\n";
}
} # if file
else
{
    if ( $short eq 0 ){
    print "nicos_errortester.pl found problem/warning, logfile(s) : $file\n"
    }
}

