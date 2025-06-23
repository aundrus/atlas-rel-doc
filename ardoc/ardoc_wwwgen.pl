#!/usr/bin/env perl
#
#
#
sub header{
    my $ARDOC_WEBDIR="${ARDOC_WEBDIR}";
    my $ARDOC_WEBPAGE="${ARDOC_WEBPAGE}";
    my @arr = split("_",$rel_name);
    my $lastel = $#arr;
    my $relnum = (splice(@arr,-1))[0];
    my $relbase = join("_",@arr);
#    my $relnum=$arr[$lastel];
#    my $relbase = $arr[0];   
    my $relnum_suffix = "_${relnum}";
    if ( $relnum eq "" ) { $relnum_suffix = ""; }
    if ( $relnum eq "RELEASE" ) { $relnum_suffix = ""; }
    if ( $lastel eq 0 ) { $relnum_suffix = ""; }
    my $cont_word="build";
    my $item_word="packages";
    if ($order eq 22) { $cont_word="test";}
    if ($order eq 22) { $item_word="tests";}

    my @wwwli=(); 
    opendir(WWWS, ${ARDOC_WEBDIR});
    @wwwli = sort
    grep { /^ardoc_${cont_word}summary_\d?\d?\d\.html$/ }
    readdir (WWWS);
    closedir(WWWS);

    my @wwwlis=();
    foreach (@wwwli)
    {
	my @arr1 = split("_",$_);
	my $relnum1=$arr1[$#arr1];
        my @arr2 = split('\.',$relnum1);
        pop(@arr2);
        my $relnum2=join('\.',@arr2);
#        my $relnum2=$arr2[0];
        my $nnnn="<a href=\"${ARDOC_WEBPAGE}/${_}\">${relbase}_${relnum2}</a>";
        push(@wwwlis, $nnnn) unless( $relnum2 == $relnum );
    }

print"
<html>

<style> table.header {
  background: #99CCFF;
  color: #CC0000;
} </style>

<style> body {
  color: black;
  background: cornsilk;
  font-family: Verdana, Arial, Helvetica, sans-serif;
  font-size: 10pt;
} </style>

<style>
a:link{color: navy}
a:hover{color: green}
a:visited{color: mediumblue}
a:active{color:chartreuse}
</style>

<style> #cellrose {
background-color: #FFCCCC;
} </style>

<style> #cellsalad {
background-color: #00FF33;
} </style>

<style> #cellsilk {
background-color: cornsilk;
} </style>

<head><title>

  ardoc webpage with ${cont_word} results
</title>

<SCRIPT SRC=\"status_test_pass${relnum_suffix}.js\" language=\"JavaScript\"></SCRIPT>
<SCRIPT SRC=\"status_test_fail${relnum_suffix}.js\" language=\"JavaScript\"></SCRIPT>
<SCRIPT SRC=\"status_unit_pass${relnum_suffix}.js\" language=\"JavaScript\"></SCRIPT>
<SCRIPT SRC=\"status_unit_fail${relnum_suffix}.js\" language=\"JavaScript\"></SCRIPT>
<SCRIPT SRC=\"test_completed${relnum_suffix}.js\" language=\"JavaScript\"></SCRIPT>
<SCRIPT SRC=\"test_total${relnum_suffix}.js\" language=\"JavaScript\"></SCRIPT>
</head>

<BODY class=body >
<FONT COLOR=\"#008080\"><FONT SIZE=-1></FONT></FONT>

<table class=header border=0 cellpadding=5 cellspacing=0 width=\"100%\">
";

if (${cont_word} eq "test"){
print "
<tr><td colspan=\"2\" bgcolor=\"#CCCFFF\" align=right>
<form>
<input type=button value=\"Close Window\" onClick=\"window.close();\" style=\"background: red; font-weight:bold\">
</form>
</td></tr>
";
}

print "
<tr><td colspan=\"2\" bgcolor=\"#CCCFFF\" align=center>
<br><EM><B><BIG>ARDOC (NIghtly COntrol System) ${cont_word} results
<br><br></EM></B></BIG></td>
<tr><td colspan=\"2\" align=center>
<br><BIG><B>Project: $ARDOC_PROJECT_NAME
<br>
";

if ( $ARDOC_BUILD_FROM_SCRATCH eq "yes" ){
print "Release: $rel_name &nbsp; -- &nbsp; Built from scratch on: ${ARDOC_HOSTNAME}\n";
}
else{
print "Release: $rel_name &nbsp; -- &nbsp; Built on: ${ARDOC_HOSTNAME}\n";
}

print "
<br>
</BIG><font size=\"-1\">\n";
    print "other releases available: @wwwlis <br>\n";
    if ( $ARDOC_TITLE_COMMENT ne "" ){
    print "$ARDOC_TITLE_COMMENT <br>\n";
    }

if ( $ARDOC_INC_BUILD eq "yes" ){
    print "Work area for incrementals: ${rel_loc} <br>\n";
}
else{
    print "Location: ${rel_loc} <br>\n";
}

$m_image="";
$tm_image="";
$filem="${ARDOC_WEBDIR}/status_email${relnum_suffix}";
$filetm="${ARDOC_WEBDIR}/status_test_email${relnum_suffix}";
if ( -f $filem ){
open (FK, "$filem");
my $line1 = readline(FK);
$line1 =~ s/\n//gs;
( $line = $line1 ) =~ s/ //gs;
if ( $line eq "1" ) { $m_image="E-MAILS SENT &nbsp; <IMG align=center SRC=\"post-worldletter.gif\" HEIGHT=17 WIDTH=17>,";}
close (FK);
}
if ( -f $filetm ){
    open (FK, "$filetm");
my $line1 = readline(FK);
$line1 =~ s/\n//gs;
( $line = $line1 ) =~ s/ //gs;
if ( $line eq "1" ) { $tm_image="(E-MAILS SENT &nbsp; <IMG align=center SRC=\"post-worldletter.gif\" HEIGHT=17 WIDTH=17>)";}
close (FK);
}


print"
Highlighted ${item_word} have problems, ${m_image}
click on names to see <a href=\"$dir_name\">logfiles</a></font></B><br>
</td></tr>

<tr><td colspan=\"2\" align=right><font size=\"-1\"> &nbsp; </font></td></tr>
<tr class=light>
<td bgcolor=\"#CCCFFF\" align=left><font size=\"-1\">
<a href=\"${ARDOC_WEBPAGE}/ardoc_content${relnum_suffix}.html\">list of tags</a>
</td>
<td bgcolor=\"#CCCFFF\" align=right colspan=1><font size=\"-1\">
<script language=\"JavaScript\">
    <!-- Hide script from old browsers
    document.write(\"Last modified \"+ document.lastModified)
    // end of script -->
    </script>
</font></td></tr></table><BR>

<table border=0 cellpadding=5 cellspacing=0 align=center width=\"90%\">
<tbody>
";

if (${cont_word} ne "test"){
print "
<tr bgcolor=\"99CCCC\"><TH colspan=8 align=center >
ATN Integration+Unit tests results
(click for <a href=\"ardoc_testsummary${relnum_suffix}.html\">details</a> or <a href=\"${ARDOC_COMMON_WEBPAGE}/ATNSummary.html\" target=\"cumulative test list\">cumulative results</a>)
</th>
</tr>";
##<form>
##<input type=button style=\"background: cornsilk; font-weight:bold\"
##value=\"Click for details\"
##onClick=\"myRef = window.open('ardoc_testsummary${relnum_suffix}.html','testwin',
##'left=20,top=20,width=900,height=700,resizable=1,scrollbars,toolbar,menubar');
##myRef.focus()\">
##</form>
}
else{
print "
<tr bgcolor=\"99CCCC\"><TH colspan=8 align=center >
ATN Integration+Unit tests results</th>
</tr>";
}

print"
<tr bgcolor=\"99CCCC\">
<th align=center >
number of tests:</th>
<th ID=cellsilk>
<SCRIPT>document.write(t_total${relnum_suffix}())</SCRIPT>
</th>
<th align=center >
completed:</th>
<th ID=cellsilk>
<SCRIPT>document.write(t_completed${relnum_suffix}())</SCRIPT>
</th>
<th align=center >
passed:</th>
<th ID=cellsalad> 
<SCRIPT>document.write(status_tp${relnum_suffix}())</SCRIPT>
+
<SCRIPT>document.write(status_up${relnum_suffix}())</SCRIPT>
</th>
<th align=center >
failed ${tm_image} :</th>
<th ID=cellrose>
<SCRIPT>document.write(status_tf${relnum_suffix}())</SCRIPT>
+
<SCRIPT>document.write(status_uf${relnum_suffix}())</SCRIPT>
</th>
</tr>";

my $ARDOC_COMMENT_TESTING_FILE="${ARDOC_WEBDIR}/ardoc_comment_testing";
if ( -f $ARDOC_COMMENT_TESTING_FILE )
{
    print"
    <tr bgcolor=\"99CCCC\">
    <th colspan=8 align=center>";
    open(TTT,"$ARDOC_COMMENT_TESTING_FILE");
    while (<TTT>) {    chomp;
		       print "$_ \n";
		   }
    close(TTT);
    print"
    </th>
    </tr>";
}

print"
</tbody>
</table>
<BR><BR>
";

print"
<table border=0 cellpadding=5 cellspacing=0 align=center width=\"90%\">
<tbody>
";
if (${cont_word} eq "test"){
if ( $ARDOC_WEB_HOME ne "" ){
print "
<tr><td><B>Package with Int. Test</B></td><td><B>Test File#Name</B></td><td><B>Test Suite</B></td><td><B>Result, E.Code</B></td><td><B>Work Dir.</B></td><td><B>Manager(s)</B></td></tr>
";
}
else{
print "
<tr><td><B>Package with Int. Test</B></td><td><B>Test File#Name</B></td><td><B>Test Suite</B></td><td><B>Result, E.Code</B></td><td><B>Manager(s)</B></td></tr>
";
}
}
exit;}
#
#
#
sub interim_test_header{
if ( $ARDOC_WEB_HOME ne "" ){
print "
<tr><td bgcolor=\"#99CCCC\">&nbsp;</td><td bgcolor=\"#99CCCC\">&nbsp;</td><td bgcolor=\"#99CCCC\">&nbsp;</td><td bgcolor=\"#99CCCC\">&nbsp;</td><td bgcolor=\"#99CCCC\">&nbsp;</td><td bgcolor=\"#99CCCC\">&nbsp;</td></tr>
<tr><td><B>Package with Unit Test</B></td><td><B>Test File#Name</B></td><td><B>Test Suite</B></td><td><B>Result, E.Code</B></td><td><B>Work Dir</B></td><td><B>Manager(s)</B></td></tr>
";
}
else{
print "
<tr><td bgcolor=\"#99CCCC\">&nbsp;</td><td bgcolor=\"#99CCCC\">&nbsp;</td><td bgcolor=\"#99CCCC\">&nbsp;</td><td bgcolor=\"#99CCCC\">&nbsp;</td><td bgcolor=\"#99CCCC\">&nbsp;</td></tr>
<tr><td><B>Package with Unit Test</B></td><td><B>Test File#Name</B></td><td><B>Test Suite</B></td><td><B>Result, E.Code</B></td><td><B>Manager(s)</B></td></tr>
";
}
exit;}
#
#
#
sub interim{
    my @arr9 = split("_",$rel_name);
    my $lastel = $#arr9;
    my $relnum=$arr9[$lastel];
    my $relnum_suffix = "_$relnum";
    if ( $relnum eq "" ) { $relnum_suffix = ""; }
    if ( $relnum eq "RELEASE" ) { $relnum_suffix = ""; }
    if ( $#arr9 eq 0 ) { $relnum_suffix = ""; }
print"
</table><BR>
";

print"
<table border=0 cellpadding=5 cellspacing=0 align=center width=\"90%\">
<tbody>
<tr bgcolor=\"99CCCC\"><align=center >
<th colspan=3>Build results for individual packages. Sorted by:</th>
</tr>";

if($order eq 1) { 
print"
<tr><align=center >
<th bgcolor=\"CCCCFF\"><A href=\"ardoc_buildsummary${relnum_suffix}.html\">packages names, failures in b/order first</A></th>
<th bgcolor=\"99CCCC\">build order</th>
<th bgcolor=\"CCCCFF\"><A href=\"ardoc_buildsummary2${relnum_suffix}.html\">containers names</A></th>
</tr>";
}
elsif($order eq 2) {
print"
<tr><align=center >
<th bgcolor=\"CCCCFF\"><A href=\"ardoc_buildsummary${relnum_suffix}.html\">packages names, failures in b/order first</A></th>
<th bgcolor=\"CCCCFF\"><A href=\"ardoc_buildsummary1${relnum_suffix}.html\">build order</A></th>
<th bgcolor=\"99CCCC\">containers names</th>
</tr>";
}
else{
print"
<tr><align=center >
<th bgcolor=\"99CCCC\">packages names, failures in b/order first</th>
<th bgcolor=\"CCCCFF\"><A href=\"ardoc_buildsummary1${relnum_suffix}.html\">build order</A></th>
<th bgcolor=\"CCCCFF\"><A href=\"ardoc_buildsummary2${relnum_suffix}.html\">containers names</A></th>
</tr>";
}

print"
</table>
<BR>
";

print"<table class=header border=10 cellpadding=5 cellspacing=0 align=center>";

my $TestTitle = "Test";
if ( $ARDOC_TITLE_TESTS ne "" )
{ $TestTitle = $ARDOC_TITLE_TESTS; } 

my $QATitle = "QA Test";
if ( $ARDOC_TITLE_QA ne "" )
{ $QATitle = $ARDOC_TITLE_QA; }



print"
</table>
<!--------------------------- Contents --------------------------->

<table cellspacing=10%>
<TR>
<TD><B>Package Name</B></TD> <TD><B>Container</B></TD> <TD><B>Build</B></TD> 
<TD><B>${QATitle}</B></TD> <TD><B>${TestTitle}</B></TD> <TD><B>Manager(s)</B></TD></TR>
";
exit;}
#
#
#
sub final{
print"


</table>
</body>
</html>
";
exit;}
#
#
#
use Env;
my $color = "";
my $clr1 = "";
my $color1 = "";
my $package_name = "";
my $a_names = "";
my $ARDOC_TITLE_COMMENT="$ARDOC_TITLE_COMMENT";
my $ARDOC_TITLE_TESTS="$ARDOC_TITLE_TESTS";
my $ARDOC_TITLE_QA="$ARDOC_TITLE_QA";
my $ARDOC_HOSTNAME="$ARDOC_HOSTNAME";
my $ARDOC_WEB_HOME="$ARDOC_WEB_HOME";
my $ARDOC_PROJECT_RELNAME="$ARDOC_PROJECT_RELNAME";
my $ARDOC_INC_BUILD="$ARDOC_INC_BUILD";
my $ARDOC_PROJECT_NAME="$ARDOC_PROJECT_NAME";
my $ARDOC_INTTESTS_DIR="$ARDOC_INTTESTS_DIR";
@output = ();

#-> parse arguments
    if ($#ARGV < 0) {exit 1;}
    while ($#ARGV>=0) {
	$_ = $ARGV[0];
	/^-[g]+$/ && do {
	    shift;
	    $package_name = $ARGV[0];
	    shift;
	    $container_name = $ARGV[0];
            shift;
            $dir_log = $ARGV[0];
	    shift;
	    $rec_log = $ARGV[0];
            shift;
            $prob = $ARGV[0];
            shift;
            $qdir_log = $ARGV[0];
            shift;
            $qrec_log = $ARGV[0];
            shift;
            $qprob = $ARGV[0];
            shift;
            $qecode = $ARGV[0];
            shift;
            $tdir_log = $ARGV[0];
            shift;
            $trec_log = $ARGV[0];
            shift;
            $tprob = $ARGV[0];
            shift;
            $tecode = $ARGV[0];
            for (my $i = 1; $i <= $#ARGV; $i++) 
            {
            $a_names=$a_names . $ARGV[$i] . " "
            }
	    $color="green";
	    goto end;
	};
        /^-[a]+$/ && do {
            shift;
            $test_dir = $ARGV[0];
            shift;
            $test_name_full = $ARGV[0];
            shift;
            $test_name = $ARGV[0];
            shift;
            $test_suite = $ARGV[0];
            shift;
            $dir_log = $ARGV[0];
            shift;
            $rec_log = $ARGV[0];
            shift;
            $prob = $ARGV[0];
            shift;
            $tecode = $ARGV[0];
            for (my $i = 1; $i <= $#ARGV; $i++)
            {
            $a_names=$a_names . $ARGV[$i] . " "
            }
            $color="green";
#            print "FFFF $test_name $dir_log\n";
            goto end2;
        };
	/^-[h]+$/ && do {
	    shift;
	    $order = $ARGV[0];
	    shift;
	    $proj_name = $ARGV[0];
	    shift;
	    $rel_name = $ARGV[0];
	    shift;
            $rel_loc = $ARGV[0];
            shift;
 	    $dir_name = $ARGV[0];
         &header;
        };
        /^-[u]+$/ && do {
            shift;
	    $order = $ARGV[0];
	    &interim_test_header;
        };
	/^-[i]+$/ && do {
	    shift;
	    $order = $ARGV[0];
	    shift;
	    $rel_name = $ARGV[0];
	    shift;
	    $dir_name = $ARGV[0];
         &interim;
        };
	/^-[f]+$/ && do {&final;};
	last;
end:
	shift;
    }

$red_bg="bgcolor=\"#F5623D\"";
$red_bg_1="bgcolor=\"#F0A675\"";
$red_bg_2="bgcolor=\"#FFCA59\"";
$rb_bg="bgcolor=\"#E87DA8\"";
$rb_bg_1="bgcolor=\"#FA9EB0\"";
$rb_bg_2="bgcolor=\"#FFE0E0\"";
$y_bg="bgcolor=\"#CCCCFF\"";
$yy_bg="bgcolor=\"#FFCCCC\"";
$v_bg="bgcolor=\"#BA55D3\"";
$v_bg_1="bgcolor=\"#CC9EFA\"";
$v_bg_2="bgcolor=\"#EOE1EB\"";
$hilight="";

if( $prob >= 2 ){
    $image="<IMG SRC=\"cross_red.gif\" HEIGHT=16 WIDTH=20>";
} 
elsif ( $prob == 1 ){
    $image="<IMG src=rad18x16.gif width=18 height=16>"; 
}
elsif ( $prob == 0.5 ){
    $image="<IMG src=yl_ball.gif width=20 height=20>";
}
else{
    $image="<IMG SRC=\"tick.gif\" HEIGHT=15 WIDTH=15>";
}
if ( $prob >= 2 ) { $hilight="$red_bg"; }
elsif  ( $prob == 1 ) { $hilight="$red_bg_1"; }
elsif  ( $prob == 0.5 ) { $hilight="$red_bg_2"; }
elsif  ( $tprob >= 2 ) { $hilight="$rb_bg"; }
elsif  ( $tprob == 1 ) { $hilight="$rb_bg_1"; }
elsif  ( $tprob == 0.5 ) { $hilight="$rb_bg_2"; }
elsif  ( $qprob >= 2 ) { $hilight="$v_bg"; }
elsif  ( $qprob == 1 ) { $hilight="$v_bg_1"; }
elsif  ( $qprob == 0.5 ) { $hilight="$v_bg_2"; }

push(@output,"<tr ${hilight}><td>"); 
push(@output,"<a href=\"$dir_log/$rec_log\">");
push(@output,"$package_name");
push(@output,"</a>");
push(@output,"<td>");
push(@output,"$container_name");
push(@output,"</td>");
push(@output,"</td>\n");
push(@output,"<td>");
push(@output,"${image}"); 
if($qrec_log eq "0" || $qrec_log eq "N/A")
   {
   push(@output,"</td><td>N/A</td>\n");   
   }
else
   {
   if($qprob eq "2")
      {
      push(@output,"</td><td><a href=\"$qdir_log/$qrec_log\">FAIL</a></td>\n");
      }
   if($qprob eq "1")
      {
      push(@output,"</td><td><a href=\"$qdir_log/$qrec_log\">WARN</a></td>\n");
      }
   if($qprob eq "0.5")
      {
      push(@output,"</td><td><a href=\"$qdir_log/$qrec_log\">NOTE</a></td>\n");
      }
   if($qprob ne "1" && $qprob ne "2" && $qprob ne "0.5")
      {
      push(@output,"</td><td><a href=\"$qdir_log/$qrec_log\">PASS</a></td>\n");
      }
    }

if($trec_log eq "0" || $trec_log eq "N/A")
   {
   push(@output,"</td><td>N/A</td>\n");
   }
else
   {
   if($tprob eq "2")
      {
      push(@output,"</td><td><a href=\"$tdir_log/$trec_log\">FAIL</a></td>\n");
      }
   if($tprob eq "1")
      {
      push(@output,"</td><td><a href=\"$tdir_log/$trec_log\">WARN</a></td>\n");
      }
   if($tprob eq "0.5")
      {
      push(@output,"</td><td><a href=\"$tdir_log/$trec_log\">NOTE</a></td>\n");
      }
   if($tprob ne "1" && $tprob ne "2" && $tprob ne "0.5")
      {
      push(@output,"</td><td><a href=\"$tdir_log/$trec_log\">PASS</a></td>\n");
      }
   }

if ( $a_names eq "" )
{push(@output,"</td><td>N/A</td>\n");}
else
{
( $aa_names = $a_names ) =~ s/@/&nbsp;at&nbsp;/g;
push(@output,"</td><td>$aa_names</td></tr>\n");
}
print @output;

exit;

end2:

$red_bg="bgcolor=\"#F5623D\"";
$red_bg_1="bgcolor=\"#F0A675\"";
$red_bg_2="bgcolor=\"#FFCA59\"";
$rb_bg="bgcolor=\"#E87DA8\"";
$rb_bg_1="bgcolor=\"#FA9EB0\"";
$rb_bg_2="bgcolor=\"#FFE0E0\"";
$y_bg="bgcolor=\"#CCCCFF\"";
$yy_bg="bgcolor=\"#FFCCCC\"";
$v_bg="bgcolor=\"#BA55D3\"";
$v_bg_1="bgcolor=\"#CC9EFA\"";
$v_bg_2="bgcolor=\"#EOE1EB\"";
$hilight="";
#print "SSS $dir_log/$rec_log $test_name \n";

if( $prob >= 2 ){
    $image="<IMG SRC=\"cross_red.gif\" HEIGHT=16 WIDTH=20>";
    $hilight="$rb_bg";
}
elsif ( $prob == 1 ){
    $image="<IMG src=rad18x16.gif width=18 height=16>";
    $hilight="$rb_bg_1";
}
elsif ( $prob == 0.5 ){
    $image="<IMG src=yl_ball.gif width=20 height=20>";
    $hilight="$rb_bg_2";
}
else{
    $image="<IMG SRC=\"tick.gif\" HEIGHT=15 WIDTH=15>";
}

{ push(@output,"<tr ${hilight}><td>"); }
push(@output,"$test_dir");
push(@output,"</td>\n");
push(@output,"<td>");
push(@output,"<a href=\"$dir_log/$rec_log\">");
push(@output,"$test_name_full");
push(@output,"</a>");
push(@output,"</td>\n");
push(@output,"<td>");
push(@output,"$test_suite");
push(@output,"</td><td>");
{ push(@output,"${image} ${tecode}"); }
push(@output,"</td>\n");
( $test_name_low = $test_name ) =~ tr/A-Z/a-z/;
( $test_suite_low = $test_suite ) =~ tr/A-Z/a-z/;
if ( $ATN_WORKDIR eq "new" ){
  $work_dir=$test_suite_low . "_work/" . $test_name_low . "_work";
} else {
    if ( $test_name_low =~ /^trig.*$/ || $test_suite_low eq "" ){
    $work_dir=$test_name_low . "_work";
    } else {
    $work_dir=$test_name_low . "_" . $test_suite_low . "_work";
    }
}

if ( $ARDOC_WEB_HOME ne "" ){
push(@output,"<td><a href=\"$ARDOC_WEB_HOME/$ARDOC_PROJECT_RELNAME/$ARDOC_INTTESTS_DIR/$work_dir\">link</a></td>\n");
}
if ( $a_names eq "" )
{push(@output,"<td>N/A</td>\n");}
else
{
( $aa_names = $a_names ) =~ s/\@/&nbsp;at&nbsp;/g;
push(@output,"<td>$aa_names</td>\n");
}
push(@output,"</tr>\n");
print @output;










