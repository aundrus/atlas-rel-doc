#!/usr/bin/env perl
#-----------------------------------------------------------------------------
# Author:      A. Undrus
#-----------------------------------------------------------------------------
#
use Env;
use File::Basename;

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

my $ARDOC_HOME="$ARDOC_HOME";
my $ARDOC_COPY_HOME="$ARDOC_COPY_HOME";
my $ARDOC_WORK_AREA="$ARDOC_WORK_AREA";
my $ARDOC_PROJECT_RELNAME_COPY = "$ARDOC_PROJECT_RELNAME_COPY";
my $ARDOC_LOGDIR = "$ARDOC_LOGDIR";
my $ARDOC_WEBDIR = "$ARDOC_WEBDIR";
my $ARDOC_WEBPAGE = "$ARDOC_WEBPAGE";
my $ARDOC_WEB_HOME = "$ARDOC_WEB_HOME";
$ARDOC_LOGDIR = dirname(${ARDOC_LOG});
$ARDOC_LOGDIRBASE = basename(${ARDOC_LOGDIR});
#
#-> check for correct number of arguments
#
    if ( "$#ARGV" < 0 || "$#ARGV" >= 2 ){
    print "ardoc_errortester:\n";
    print "One or two arguments required: name of logfile and --conf or --inst option\n";
    exit 2;
    }

$filename=$ARGV[0];
$option="copy";

while ($#ARGV>=0) {
    $_ = $ARGV[0];
    if ( $_ =~ /^-/ ){
        /^--conf$/ && do { $option="conf"; };
        /^--inst$/ && do { $option="inst"; };
        ( /^--checkout$/ || /^--co$/ ) && do { $option="checkout"; };
        shift;  
    } else {
	$filename=$_; shift;
    }
}
my @e_success = (" ", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning = ("package not found", "CMake Warning", "CMake Deprecation Warning", "> Warning:", "Warning:.*logfile.*not\savailable", "logfile not found", "CVBFGG");
my @e_warning_ignore = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning_ignore_1 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning_ignore_2 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning_ignore_3 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_warning_patterns_minor = ("CVBFGG", "Could.*NOT.*find", "Warning: the last line", "Warning: Unused class rule",'Warning:\s.*rule', "CVBFGG", "CVBFGG");
my @e_patterns = ("can not", "permission denied", "Disk quota exceeded", "CMake Error", "not remade because of errors", "connection problem", "cmake: command not found");
my @e_ignore = ("ERRORS: 0", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_ignore_2 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_ignore_3 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
my @e_patterns_correlators = (" ", " ", " ", " ", " ", " ", " ");
#USE the same patterns for option inst
#if ( $option eq "inst" ){
##    @e_warning = ("package not found", "CVBFGG", "Errors/Problems found", "> Warning:", "permission denied", "Disk quota exceeded", "CVBFGG");
##    @e_patterns = (": error:", "CMake Error", "No rule to make target", "raceback (most recent", "CVBFGG", "error: ld", "connection problem");
##    @e_ignore = ("collect2: error:", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "collect2: error:", "CVBFGG");
##    @e_ignore_2 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
##    @e_ignore_3 = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
#    @e_warning = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
#    @e_warning_patterns_minor = ("CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
#    @e_patterns = ("result FAILURE", "can not", "permission denied", "Disk quota exceeded", "CMake Error", "not remade because of errors", "cmake: command not found");
#    @e_ignore = ("CVBFGG", "ERRORS: 0", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG"); 
#}
if ( $option eq "checkout" ){
    @e_warning = ("package not found", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
    @e_patterns = ("can not", "permission denied", "Disk quota exceeded", "Timeout after", "ERROR:", "pb occured", "connection problem");
    @e_ignore = ("ERRORS: 0", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG");
}
my @e_count = (0,0,0,0,0,0,0);
my @w_count = (0,0,0,0,0,0,0);
my @w_minor_count = (0,0,0,0,0,0,0);
my @s_count = (1,0,0,0,0,0,0);
my @lineE = (0,0,0,0,0,0,0);
my @lineW = (0,0,0,0,0,0,0);
my @lineM = (0,0,0,0,0,0,0);
my @lineEValue = ("","","","","","","");
my @lineWValue = ("","","","","","","");
my @lineMValue = ("","","","","","","");
$lineT=0;
if ( -f $filename ){
open(FL, "<$filename");
while (<FL>){ 
      chomp;
      $line=$_;
      $lineT++;
      for ($m=0; $m <= $#e_patterns; $m++){
        if ( $e_patterns[$m] ne "" && $line =~ /\Q$e_patterns[$m]\E/ && $line !~ /\Q$e_ignore[$m]\E/ && $line !~ /\Q$e_ignore_2[$m]\E/ && $line !~ /\Q$e_ignore_3[$m]\E/){ 
	    if ( $e_patterns_correlators[$m] eq "" || $e_patterns_correlators[$m] eq " " ){
                $e_count[$m]++; 
                if ( $lineE[$m] == 0 ) { $lineE[$m]=$lineT; $lineEValue[$m]=$line; }
  	    }
            else {
              if ( $line =~ /\Q$e_patterns_correlators[$m]\E/ ){
		  $e_count[$m]++;
		  if ( $lineE[$m] == 0 ) { $lineE[$m]=$lineT; $lineEValue[$m]=$line; }
	      }
	    }
        }
      }

      for ($m=0; $m <= $#e_warning; $m++){
          if ( $e_warning[$m] =~ /\.\*/ ) {
              if ( $e_warning[$m] ne "" && $line =~ /$e_warning[$m]/ && $line !~ /\Q$e_warning_ignore[$m]\E/ && $line !~ /\Q$e_warning_ignore_1[$m]\E/ && $line !~ /\Q$e_warning_ignore_2[$m]\E/ && $line !~ /\Q$e_warning_ignore_3[$m]\E/ ){
		  $w_count[$m]++;
		  if ( $lineW[$m] == 0 ) { $lineW[$m]=$lineT; $lineWValue[$m]=$line; }
	      }
	  }
          else {
              if ( $e_warning[$m] ne "" && $line =~ /\Q$e_warning[$m]\E/ && $line !~ /\Q$e_warning_ignore[$m]\E/ && $line !~ /\Q$e_warning_ignore_1[$m]\E/ && $line !~ /\Q$e_warning_ignore_2[$m]\E/ && $line !~ /\Q$e_warning_ignore_3[$m]\E/ ){
                   $w_count[$m]++;
                   if ( $lineW[$m] == 0 ) { $lineW[$m]=$lineT; $lineWValue[$m]=$line; }
	      }
          }
      }

      for ($m=0; $m <= $#e_warning_patterns_minor; $m++){
          if ( $e_warning_patterns_minor[$m] =~ /\.\*/ ) {
              if ( $e_warning_patterns_minor[$m] ne "" && $line =~ /$e_warning_patterns_minor[$m]/ ){
    	          $w_minor_count[$m]++;
	          if ( $lineM[$m] == 0 ) { $lineM[$m]=$lineT; $lineMValue[$m]=$line;}
              }
	  }
          else {
              if ( $e_warning_patterns_minor[$m] ne "" && $line =~ /\Q$e_warning_patterns_minor[$m]\E/ ){
                  $w_minor_count[$m]++;
                  if ( $lineM[$m] == 0 ) { $lineM[$m]=$lineT; $lineMValue[$m]=$line;}
	      }
	  }
      }

      for ($m=0; $m <= $#e_success; $m++){
          if ( $line =~ /\Q$e_success[$m]\E/ && $s_count[$m] > -1 ) {$s_count[$m]--;}
      } 

} # while
close (FL);

#warn "EC: @e_count\n";
#warn "EW: @w_count\n";
#warn "ES: @s_count\n";

$eeee="";
$lineEE=0;
$lineWW=0;
$lineMM=0;
$lineEEValue=0;
$lineWWValue=0;
$lineMMValue=0;
for ($m=0; $m <= $#e_patterns; $m++){
    $count=$e_count[$m];
    next if ($count <= 0);
    if ( $e_patterns[$m] ne "CVBFGG" ){
	if ( $e_patterns_correlators[$m] eq "" || $e_patterns_correlators[$m] eq " " ){
          $eeee="$e_patterns[$m]"; $lineEE=$lineE[$m]; $lineEEValue=$lineEValue[$m]; last; 
	}
        else{
	    $eeee="$e_patterns[$m]"." AND "."$e_patterns_correlators[$m]"; $lineEE=$lineE[$m]; $lineEEValue=$lineEValue[$m]; last;
	}
    }
}

$ssss="";
for ($m=0; $m <= $#e_success; $m++){
    $count=$s_count[$m];
    next if ($count <= 0);
    $ssss="$e_success[$m]"."(ABSENSE OF)";
    last;
}

$wwww="";
for ($m=0; $m <= $#e_warning;  $m++){
    $count=$w_count[$m];  
    next if ($count <= 0);
    if ( $e_warning[$m] ne "CVBFGG" ){
    $wwww="$e_warning[$m]";
    $lineWW=$lineW[$m]; $lineWWValue=$lineWValue[$m];
    last;
    }
}

$wwww_minor="";
for ($m=0; $m <= $#e_warning_patterns_minor; $m++){
    $count=$w_minor_count[$m];
    next if ($count <= 0);
    if ( $e_warning_patterns_minor[$m] ne "CVBFGG" ){
        $wwww_minor="$e_warning_patterns_minor[$m]"; 
        $lineMM=$lineM[$m]; $lineMMValue=$lineMValue[$m];
        last;
    }
}

$mess="No problems found";
$linkline=0;
$linkvalue="";
$problems=0;
if ( $eeee ne "" ){
    $linkline=$lineEE; $linkvalue=$lineEEValue;
    $mess="Error pattern found: $eeee";
    $problems=2;
    print "G $eeee\n";
    }
elsif ( $ssss ne "" ) #if ( $eeee ne ""
{
    $linkline=0;
    $mess="Required success pattern not found: $ssss";
    $problems=2;
    print "G $mess";
}
elsif ( $wwww ne "" ) #if ( $eeee ne ""
{
    $linkline=$lineWW; $linkvalue=$lineWWValue;
    $mess="Serious warning pattern found: $wwww";
    $problems=1;
    print "W $wwww";
}
elsif ( $wwww_minor ne "" ) 
{
        $linkline=$lineMM; $linkvalue=$lineMMValue;
        $mess="Minor warning pattern found: $wwww_minor";
        $problems=0.5;
        print "M $wwww_minor";
} #else #if ( $wwww_minor ne "" ) 
###
} else { # if ( -f $filename )
$eeee="logfile not found: $filename";
$problems=10;
}

$filebase1=basename($filename);
$filedir=dirname($filename);
$filebase=$filebase1;
@filebase_a=split('\.',$filebase); 
if ( $#filebase_a > 0 ) {
pop @filebase_a;
$filebase=join('\.',@filebase_a);
$filehtml="$filedir/$filebase" . ".html";
}
$aid_message="";
$optn="$option";
if ( $optn eq "down" ){ $optn="kit installation";} 
if ( $optn eq "conf" ){ $optn="cmake build configuration";}
if ( $optn eq "inst" ){ $optn="externals build";}
if ( $optn eq "checkout" ){ $optn="code checkout";}
$aid_message_html = <<EAID;
<DIV id=hdr0>
<table bordercolor=\"#6600CC\" border=10 cellpadding=5 cellspacing=0 width=\"100%\">
<tr><td class=aid width=20% align=center valign=baseline>
<H1>ARDOC</H1>
</td>
<td class=ttl>
<EM><B><BIG>Converted $optn logfile</BIG></EM></B>
</td></tr>
<tr><td class=aid>
version  ${ARDOC_VERSION}
</td>
EAID

if ( $problems == 2 ){
$mess2="&nbsp;<BR>&nbsp;&nbsp;&nbsp;&nbsp;<A href=\"#prblm\">link to the problematic line</A><BR>";
if ( $linkline == 0 ){ $mess2=""; }
$aid_message_html1 = <<END11;
<td class=ttl><EM><B>${mess}</B></EM>
</td>
</tr>
</table>
</DIV>
<DIV id=hdr>
<B>
    ${mess2}
    &nbsp;&nbsp;&nbsp;&nbsp;<A href=\"#end\">link to the last line</A> <BR>
    &nbsp;<BR>
</B></DIV>
END11

} elsif ( $problems == 1 || $problems == 0.5 ) {
$mess2="&nbsp;<BR>&nbsp;&nbsp;&nbsp;&nbsp;<A href=\"#prblm\">link to the problematic line</A><BR>";
if ( $linkline == 0 ){ $mess2=""; }
$aid_message_html1 = <<END19;
<td class=ttl><EM><B>${mess}</B></EM>
</td>
</tr>
</table>
</DIV>
<DIV id=hdr>
<B>
    ${mess2}
&nbsp;&nbsp;&nbsp;&nbsp;<A href=\"#end\">link to the last line</A> <BR>
    &nbsp;<BR>
</B></DIV>
END19

} elsif ( $problems == 10 ) {
$mess="problem: \"$eeee\"";
$aid_message_html1 = <<END12;
<td class=ttl><EM><B>${mess}</B></EM>
</td>
</tr>
</table>
END12
} else {
$aid_message_html1 = <<END31;
<td class=ttl><EM><B>No problems found</EM></B>
</td>
</tr>
</table>
<DIV id=hdr>
<B>
&nbsp;<BR>
&nbsp;&nbsp;&nbsp;&nbsp;<A href=\"#end\">link to the last line</A> <BR>
&nbsp;<BR>
</B></DIV>
END31
}
###############################
# HTML LOG GENERATION
###############################
$aid_message_html=$aid_message_html . $aid_message_html1;
if ( $filehtml ne "" ){
  warn "ardoc_copy_errortester.pl: HTML: $filehtml\n";
  open(FG,">$filehtml");
  header_print( *FG, $problems, $option);
  print FG "$aid_message_html";
  print FG "<div id=hdr1>\n";
  print FG "original log file: <CODE> $filename </CODE><BR>\n";
  if ( $ARDOC_WEBPAGE ne "" ){
      $webloc="${ARDOC_WEBPAGE}/ARDOC_Log_${ARDOC_PROJECT_RELNAME_COPY}/$filebase1";
#      print FG "<BR>\n";
      print FG "<a href=\"${webloc}\"><b>text logfile (full size)</b></a>\n";  
  }
  print FG "</div>\n <P>\n";
  @allowed_1=();
  @allowed_2=();
    my $all_i=0;
    $total_ln=5000;
    $first_part=3000;
    $middle_part1=25;
    $middle_part2=25;
    $last_part=2000;
  $all_i++;
  $allowed_1[0][$all_i]=0;
  #print "TTTT $lineT  $total_ln\n";
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
  warn "ardoc_copy_errortester.pl: conversion info: @{$allowed_1[0]} -- @{$allowed_1[1]} \n";
  warn "ardoc_copy_errortester.pl: conversion info: @{$allowed_2[0]} -- @{$allowed_2[1]} \n";
  $ncount_line=0;
  $ncount_s[0]=0;
  open(FB,"<$filename");
  while (<FB>){
    $ncount_line++;
    $line_ok=0;
    for ( $ippo=0; $ippo <= $#{$allowed_1[0]}; $ippo++ ){
####    print "AAAA $ncount_line $ippo $allowed_1[0][$ippo] $allowed_2[0][$ippo]\n";
    if ( $ncount_line >= $allowed_1[0][$ippo] && $ncount_line <= $allowed_2[0][$ippo]){
    $line_ok=1;
    last;
    }
  }
  if (! $line_ok){$ncount_s[0]=0;}
  if ($line_ok){
    if ( $ncount_line != $linkline ){
    $ncount_s[0]++;
    if ( $ncount_s[0] == 1 && $ncount_line > 1 ) {
    print FG <<DOTT;
<DIV ID=hdr>................................................................<BR>
.....LINES TRUNCATED.....<BR>
................................................................
</DIV>
DOTT
   }
      print FG "${_} <BR>";
   }
   else{
      print FG "<div id=\"prblm\">${_}</div>";
      $ncount_s[0]++;
   }
   if ( $ncount_line == $lineT ){
      print FG "<div id=\"end\">END OF LOGFILE</div>";
   }
   } # if ($line_ok)
  }
  close(FB);

  print FG "
  </body>
  </html>
  ";

  close (FG);
} # if ( $filehtml ne "" ){

#copy generated htmllog to ${ARDOC_WEBDIR}
if ( $option eq "kit" || $option eq "down" || $option eq "rpm" || $option eq "pacball" ){  
$filehtml_base=basename($filehtml);
$copy_html="${ARDOC_WEBDIR}/ARDOC_Log_${ARDOC_PROJECT_RELNAME_COPY}/${filehtml_base}";
#warn "ardoc_copy_errortester: cp -Rp $filehtml $copy_html\n";
system("cp -Rp $filehtml $copy_html");
}
