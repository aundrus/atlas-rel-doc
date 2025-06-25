#!/usr/bin/env perl
#
# ARDOC - NIghtly COntrol System
# Author Alex Undrus <undrus@bnl.gov>
# 
# ----------------------------------------------------------
# ardoc_errorhandler.pl
# ----------------------------------------------------------
#
use Env;
use Cwd;
use File::Basename;
use File::stat;
#use Mail::Mailer;

sub compar{
    my $name = shift;
    my @test_1 = split('___' , $name);
    $val_c="";
    if ( $#test_1 > 0 ) {
        shift(@test_1);
        $xxxx=@test_1[0];
        @test_11 = split("__" , $xxxx); 
        $xxxx=@test_11[0];
        $test_11[0]=$xxxx . "00";
        $val_c=join("__",@test_11);   
    } else { # if ( $#test_1 > 0 )
 	my @test_2 = split("__" , $name);
        if ( $#test_2 > 0 ) {
	    $xxxx=shift(@test_2);
            @xxyy=split("_" , $xxxx);
            $xxnn=pop(@xxyy); 
            $test_2[0]=$test_2[0] . $xxnn;
	    $val_c=join("__",@test_2);
         } else {
	 $val_c=$test_2[0];
         }        
    } #elsif { # if ( $#test1 > 0 )
#    print "NNN $name\n"; 
#    print "VVV $val_c\n";
    return $val_c; 
} #end sub compar  

sub container_extractor{
    $testdirx=$_[0];
    @testd=split(/\//,$testdirx);
    for ($m=0; $m <= $#testd; $m++){
        $testj=join('/', @testd);
        $filfil="${ARDOC_RELHOME}/${prefix_relhome}/${testj}/cmt/version.cmt";
        last if ( -f $filfil );
        pop @testd;
        }
    $return_val=join('_', @testd);
    return $return_val;
}

sub ardoc_testhandler{
# if $_[0] = 1 -> qa tests, if $_[0] != 1 int and unit tests
$prefix_relhome="aogt8";
$par=$_[0];
$type="test";
my $ARDOC_TESTLOG = "$ARDOC_TESTLOG";
my $ARDOC_RELHOME = "$ARDOC_RELHOME";
my $ARDOC_INTTESTS_DIR = "$ARDOC_INTTESTS_DIR";
my $ARDOC_TEST_DBFILE_GEN = "$ARDOC_TEST_DBFILE_GEN";
my $ARDOC_INTTESTS_FILES = "$ARDOC_INTTESTS_FILES";
my $ATN_HOME = "$ATN_HOME";
my $ARDOC_WEBDIR = "$ARDOC_WEBDIR";
my $ARDOC_PROJECT_NAME = "$ARDOC_PROJECT_NAME";
my $ARDOC_NIGHTLY_NAME = "$ARDOC_NIGHTLY_NAME";
my $ARDOC_ARCH="$ARDOC_ARCH";
my $ARDOC_FULL_ERROR_ANALYSIS="$ARDOC_FULL_ERROR_ANALYSIS";

$ARDOC_TESTLOGDIR=dirname(${ARDOC_TESTLOG});
$ARDOC_TESTLOGDIR_TEMP="$ARDOC_TESTLOGDIR/temp";
$WTLogdir="ARDOC_TestLog_${release}";
$WTLogdir_full="${ARDOC_WEBDIR}/${WTLogdir}";
if ( ! -d $WTLogdir_full ){
    system("mkdir","-p","$WTLogdir_full");
}
$testprepage="ardoc_testprepage";
$dirdir="${ARDOC_RELHOME}/${ARDOC_INTTESTS_DIR}";

         opendir(DD, ${ARDOC_TESTLOGDIR});
         @allfiles = grep /^.+log$/, readdir DD;
         closedir DD;
         @list91 = grep !/^ardoc_.+$/, @allfiles;
         @list = grep !/^.+logloglog$/, @list91;
         @list91=();
##         @listfiles = sort { -M $a <=> -M $b } @list if ($par == 1);
         @listfiles = sort { compar($a) cmp compar($b) } @list; ## if ($par != 1);

         $filet_nn = "${ARDOC_WORK_AREA}/${testprepage}_number";

         my @test_db=();
         my $number_tests_db=0; 
         if ( "$ARDOC_TEST_DBFILE_GEN" ne "" ){
         if ( -f "$ARDOC_TEST_DBFILE_GEN" ){
         $fname="$ARDOC_TEST_DBFILE_GEN";
         open(UT, "$fname");
         chomp(@test_db=<UT>);
         close(UT);
         @test_db_nn = grep { /\w/ } @test_db;
         $number_tests_db=scalar(@test_db_nn);
         @test_db_nn = ();
         print "ardoc_errorhandler: number of tests in test_db $number_tests_db\n"; ## if ($par != 1);
         }
         }
         if ( -f $filet_nn ){ unlink "$filet_nn";}
         open(TF, ">$filet_nn");
         print TF "$number_tests_db\n";
         close(TF);

         $filet = "${ARDOC_WORK_AREA}/$testprepage";
         if ( -f $filet ){ unlink "$filet";}

         open(TF, ">$filet"); 
 
@body=();
$body_count=0;
@body_prev=();
@addr_total=();
@addr_total_prev=();
$testname_subject_prev="";
$dplusd_m="";
#print "LISTFILES $filet @listfiles\n";
@listfiles1=();
foreach $listfile (@listfiles){
    ($lin1 = $listfile) =~ s/ //g;
    next if (length($lin1) eq 0);
    next if $listfile =~ /^\.\.?$/;
    next if $listfile =~ /~$/;
    push(@listfiles1, $listfile); 
}
@listfiles=();

for ($mlf=0; $mlf <= $#listfiles1; $mlf++){
        $listfile=@listfiles1[$mlf];
	@listfields=split(/\./,$listfile);
	pop @listfields;
	$listfile_base=join('\.',@listfields);
	$listfileh="${listfile_base}.html";
#        print "MLF $mlf $#listfiles1 $listfile\n";
        $testname=(split(/\./,$listfile))[0];
        @fields = split(/_/, $testname);
        @first_fields=();
        @last_fields=();
        $testdir="";
        $m_last=0;

        for ($m=0; $m <= $#fields; $m++){
	push(@first_fields, $fields[$m]);
        $testdir1=join("\/", @first_fields);
        if ( $testdir1 eq "." || $testdir1 eq "\/" || $testdir1 eq "\/." ){
	$testdir1="";
        } 
        $direc="${ARDOC_RELHOME}/$prefix_relhome/$testdir1";
        if ( ! -d $direc ) {$m_last=$m; last;}
        $testdir="$testdir1";
        }

        for ($m_last; $m <= $#fields; $m++){
        push(@last_fields, $fields[$m]);
        }
        $testname_base=join("_", @last_fields);

#       searching for suite
        $testsuite="undefined";   
        @addr_t=();

#if ( $par != 1 ){ 
foreach (@test_db){
        next if ($_ =~ /^#/ );
        ( $lin1 = $_ ) =~ s/ //g;
        next if (length($lin1) eq 0);
        #   remove trailing leading stretches whitespaces
        $lll = join(' ', split(' ', $_));
        @fields = split(" ", $lll);
        $testname1 = $fields[1];
	$testname2=(split(/\./,$testname1))[0];
        $testdir1 = $fields[2];
        $testdir2=container_extractor($testdir1);
        $testname_compar="${testdir2}_${testname2}";

        $testsui = $fields[4];
        $testtime = $fields[5];
#print "AAA $testname1 $testname2 $testdir1 $testdir2 $testsui $testtime\n";
#print "BBB $testname_compar eq $testname \n";
		 if ( $testname_compar eq $testname ){
                  for ($m=7; $m <= $#fields; $m++){
                  push(@addr_t, $fields[$m]);
                  }
                  $testsuite="$testsui";
                  $testdir="$testdir2";
                  $testname_base="$testname2";
                  last;  
	     }
}
#} if par != 1
        $fecod="${ARDOC_TESTLOGDIR}/${testdir2}_${testname2}.exitcode";
        $exitcode="N/A";
        if ( -f $fecod ){
            open (FK, "$fecod");
            $exitcode = readline(FK);
            $exitcode =~ s/\n//gs;
            close(FK);
	}
        my @strng1=();
	$lower_NFEA=lc("$ARDOC_FULL_ERROR_ANALYSIS");
	#	if ( $exitcode eq "0" && $lower_NFEA ne "true" && $lower_NFEA ne "yes" && $testname !~ /unit-tests/ ){
	if ( $lower_NFEA ne "true" && $lower_NFEA ne "yes" && $testname !~ /unit-tests/ ){
	    #LIGHT error analysis
	    @strng1=`${ARDOC_HOME}/ardoc_errortester.pl -elst ${testname} ${release}`;
	    print " light test_tester: ${testname}_ERROR_MESSAGE ${release} : @strng1 ===${exitcode}==\n";
	} else {   
            @strng1=`${ARDOC_HOME}/ardoc_errortester.pl -est ${testname} ${release}`;
	    if ( $lower_NFEA eq "true" || $lower_NFEA eq "yes" ){
                print " full test_tester: ${testname}_ERROR_MESSAGE ${release} : @strng1 ===${exitcode}==\n";
	    } else {
		print " test_tester: ${testname}_ERROR_MESSAGE ${release} : @strng1 ===${exitcode}==\n";
	    }
        }
        $strng=@strng1[0];
        @wrn_pat=();
        @err_pat=();
        @scs_pat=();

        @fieldstr = split(" ", $strng);
        @patterns=();
             for ($m=3; $m <= $#fieldstr; $m++){
             push(@patterns, $fieldstr[$m]);
             }
        $tproblems=0;
        if ( $fieldstr[0] eq "M" && $strng ne "" ) {
        $tproblems=0.5;
        print "ardoc_testhandler.pl: test minor warnings in $testname !!!\n";
        print "                      pattern to blame: @patterns !!!\n"; 
        }
        if ( $fieldstr[0] eq "W" && $strng ne "" ) {
        $tproblems=1;
        print "ardoc_testhandler.pl: test warnings in $testname !!!\n";
        print "                      pattern to blame: @patterns !!!\n";
        }
        if ( $fieldstr[0] eq "G" && $strng ne "" ) {
	$tproblems=2;
        }
#        if ( $tproblems == 2 && $par != 1 ) {
        if ( $tproblems == 2 ) {
	print "ardoc_testhandler.pl: test problems in $testname !!!\n";
	print "                      pattern to blame: @patterns !!!\n";
#	print "BBBBBB $testname1 $testname2 $testdir1 $testdir2\n";

   $var="${ARDOC_TESTLOGDIR}/$listfile"; 
   $var_orig="${ARDOC_TESTLOGDIR}/$listfile";
   $varvar="${ARDOC_WEBPAGE}/ARDOC_TestLog_${release}/${listfileh}";
	@ftest = split("__", $testname);
        if ( $#ftest == 0 ){
            $testname_sh=$testname; }
        else{
            if ( $ftest[-1] eq "" || $ftest[-1] eq "a" || $ftest[-1] eq "k" || $ftest[-1] eq "x" || $ftest[-1] eq "m" ){ pop @ftest; }
            if ( $#ftest != 0 && $#ftest != 1 ){
                shift @ftest;
                if ( $#ftest > 1 && $ftest[0] eq ""){
                    shift @ftest;
                } 
            } 
            $testname_sh = join('#', @ftest);
        }

   $t2_ss=$testname2;
   @t2_spl=split('__', $testname2);
   if ( $#t2_spl > 0 ) {
   $t2_ss=$t2_spl[1]; 
   }
   $testname_subject=$t2_ss; 
   $dplusd=$testdir2 . '____' . $t2_ss;
   if ( $dplusd ne $dplusd_m ){
      @body=();
      @addr_total=();
      $body_count=0;
      foreach $address (@addr_t){
         if ( $address ne "" ){
	 if ( $address =~ /@/  ){
           push (@addr_total, $address); 
	   }
           }
      }
   }
   $body_count++;  
   @add_addi=();
#   print "ADDD0 @addr_total\n";
   foreach $address1 (@addr_t){
     ( $add1 = $address1 ) =~ s/ //g;
     $sig_eq=0;
     foreach $address (@addr_total) {
       ( $add = $address ) =~ s/ //g; 
#       print "ADDD1 $add1  $add\n"; 
       if ( $add eq $add1 ) { 
#	 print "ADDEE\n";
	 $sig_eq=1; last;
         }   
     }
   if ( $sig_eq == 0 ) {
     push ( @add_addi, $address1 );
#     print "ADDD2 $sig_eq $address1\n";
   }
   }   

   if ( $#add_addi >=0 ) {
   push(@addr_total, @add_addi); 
#   print "ADDD22 @add_addi\n";
   @add_addi=();
   }
   if ( $#addr_total < 0 && $#addr_t >= 0 ){
        foreach $address (@addr_t) {
	push ( @addr_total, $address );
#	print "ADDD3 $address\n";
        }
   } 
  
push(@body," ===========================================================\n");
push(@body," This message is generated by ARDOC build for \n");
push(@body," project $project , $nightly release $release ${ARDOC_ARCH}. \n");
push(@body," ARDOC system found possible problems with ${type} \n  ${testname_sh}\n");
push(@body," suspicious pattern:\"@patterns\" !!!\n");  
push(@body," ===========================================================\n");
push(@body," The ${type} logfile is available at: \n $var \n and(or) \n $varvar \n");
push(@body," ===========================================================\n");
push(@body," For further information please refer to $project ARDOC webpage \n");
push(@body," ${ARDOC_WEBPAGE}/index.html\n");
if ( ${type} eq "test" && ${var_orig} =~ /TriggerTest/ ){
    if ( -f $var_orig ){
        open (LOG,"<$var_orig");
        $nrec = 0;
        $nrec1 = 0;
        $signh=0;
        while (<LOG>){
            $nrec++;
            last if ( $nrec > 200 || $nrec1 > 100 );
            chomp;
            next if (length($_) eq 0);
            if ( $_ =~ /ATN/ && $_ =~ /Starting/ ) { $signh=1;}
            if ( $signh == 1 ) { $nrec1++;}
            if ( $nrec1 == 1 ){
push(@body," ===========================================================\n");
push(@body," FIRST 100 LINES OF TEST LOG\n");
push(@body," -----------------------------------------------------------\n");
            }
            if ( $signh == 1 ) {
push(@body,"$_\n");            
            }
        }
        close(LOG);
    }
}#if ( ${type} eq "test" )

} # if tproblems == 2
#-------------------------------
#print "DPLUSD $dplusd $dplusd_m\n";
if ( $dplusd ne $dplusd_m || $mlf == $#listfiles1 ){
$dplusd_m=$dplusd;
if ( $mlf == $#listfiles1 ){ 
    @body_prev=@body;
    @addr_total_prev=@addr_total;
    $body_count_prev=$body_count;
    $testname_subject_prev=$testname_subject;
}

if ($#body_prev >= 0 ){

    if ( ${body_count_prev} > 1 ) {
unshift (@body_prev," !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n");
unshift (@body_prev," ARDOC combined error meassages from ${body_count_prev} tests of ${testname_subject_prev} \n");
unshift (@body_prev," !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n");
    }

print "ardoc_errorhandler.pl: sending email about $body_count_prev pbs in $testname_subject_prev, size $#body_prev, file count $mlf\n";
#print "MMMMMM $mlf $#body_prev $body_count_prev \n @body_prev \n";
#print "AAAAAA @addr_total_prev BBBBB @cont_addr\n";

    foreach $address (@addr_total_prev){
        if ( $address ne "" ){
           if ( $address =~ /@/  ){
if ( $address =~ somebody ){
print "ardoc_errorhandler.pl: Problems with ${type} $testname_subject_prev !!! Mail is NOT sent to such $address code $nomail_t[0] \n";                            
}
else{
    @address_fin=();
    @address_ar=split(',',$address);
    foreach $add95 (@address_ar){
	( $add96 = $add95 ) =~ s/^\s+//;
        $add97 = lc($add95);
#        print "ADDADD $add95,$add96,$add97\n";
        if ( $add97 =~ /damazio/ || $add97 =~ /cpotter/ || $add97 =~ /cern\.fr/ || $add97 =~ /helenka/ ){
	    print "ardoc_errorhandler.pl: address $add96 blacklisted for ${type} $testname_subject_prev\n";
        } else {
            push(@address_fin, $add96); 
	}
    }
    $address_after_blacklist=join(',',@address_fin);
    ( $test_after_blacklist = $address_after_blacklist ) =~ s/\s//;
    if ( $test_after_blacklist ne "" ){
print "ardoc_errorhandler.pl: Problems with ${type} $testname_subject_prev !!! Mail is sent to $address_after_blacklist code $nomail_t[0] \n";
    } else {
print "ardoc_errorhandler.pl: Problems with ${type} $testname_subject_prev !!! Mail list is empty \n";
    }
if ( $nomail_t[0] eq 0 && $test_after_blacklist ne "" ){
    $from_address="atnight";
    $to_address="$address_after_blacklist";
    $subject="ARDOC: ${project}: ${type} problems in ${nightly} ${release} ${ARDOC_ARCH} with ${testname_subject_prev}";
#    $mailer = Mail::Mailer->new("sendmail");
#    $mailer->open({ From => "${from_address}",
#                      To => "${to_address}",
#                 Subject => "${subject}",
#          })
#    or die "Mailer can not open: $!\n";
#    print $mailer @body_prev;
#    $mailer->close();
}
} #if ( $address =~ somebody
} #if ( $address =~ /@/  )
} #if ( $address ne "" )
} #foreach $address
} # if $#body_prev
} #if ( $dplusd ne $dplusd_m ) 
#--------------------------------------
        $fec="${ARDOC_TESTLOGDIR}/${testdir2}_${testname2}.exitcode";
        $exitcod="N/A";
        if ( -f $fec ){
	    open (FK, "$fec");
            $exitcod = readline(FK);
            $exitcod =~ s/\n//gs;
            close(FK);
        }
        $tstmp="${ARDOC_TESTLOGDIR}/${testdir2}_${testname2}.timestamp";
        $time_beg="N/A";
        $time_end="N/A";
        if ( -f $tstmp ){
            open (FK, "$tstmp");
            $timelin1 = readline(FK);
            $timelin1 =~ s/\n//gs;
            ($timeline = $timelin1 ) =~ s/ //g;
	    @fields_time = split("#", $timeline);
            if ( $fields_time[0] ne "" ){
                $time_beg = $fields_time[0];
            }
            if ( $#fields_time > 0 ){
                if ( $fields_time[1] ne "" ){ 
            	    $time_end = $fields_time[1];
		}
	    }
            close(FK);
        } 
        print "===errorhandler: exit code,file,dir: ${exitcod} ${testdir2}_${testname2}.exitcode ${ARDOC_TESTLOGDIR}\n";
	print "===errorhandler: time begin,end,filestamp: ${time_beg} ${time_end} ${testdir2}_${testname2}.timestamp\n";
        print TF "$testname $testsuite $listfileh $tproblems $exitcod $testdir $testname_base $time_beg $time_end @addr_t \"\"\" $fieldstr[2] \"\"\" \"@patterns\" \n";
@body_prev=@body;
@addr_total_prev=@addr_total;
$body_count_prev=$body_count;
$testname_subject_prev=$testname_subject;
} # done
close(TF);

$WTLogdir="ARDOC_TestLog_${release}";
$WTLogdir_full="${ARDOC_WEBDIR}/${WTLogdir}";
    if ( ! -d $WTLogdir_full ){
    system("mkdir","-p","$WTLogdir_full");
    }

opendir(DDD, ${ARDOC_TESTLOGDIR});
@allcpfiles = readdir DDD;
closedir DDD;
  
@listf_9 = grep !/^.+\.loglog.+$/, @allcpfiles;
@listf = grep !/^.+\.html$/, @listf_9;
@allcpfiles=("");
foreach $lf (@listf){
        next if $lf =~ /^\.\.?$/;
        next if $lf =~ /~$/;
        $lf_full="${ARDOC_TESTLOGDIR}/${lf}";
        $lf_size=stat($lf_full)->size;
        if ( $lf_size <= 4000000 ){
        system("echo 'ARDOC NOTICE: THIS FILE IS ALSO AVAILABLE AT:' > ${WTLogdir_full}/${lf}");
        system("echo '${ARDOC_TESTLOGDIR}/${lf}' >> ${WTLogdir_full}/${lf}");
##        system("cat ${lf_full} >> ${WTLogdir_full}/${lf}");
#        system("cp -pf ${lf_full} ${WTLogdir_full}/.");
        }else{
        system("echo 'ARDOC NOTICE: THIS FILE IS TRUNCATED DUE TO LARGE SIZE' > ${WTLogdir_full}/${lf}");
        system("echo 'LARGER, POSSIBLY NOT TRUNCATED COPY IS ${ARDOC_TESTLOGDIR}/${lf}' >> ${WTLogdir_full}/${lf}");
##        system("cat ${lf_full} | head -c 4000000 >> ${WTLogdir_full}/${lf}");
        }
}
@listf=("");
} #end of sub

#print "------------------------------------------------------------\n";
#print "   Starting ARDOC error analysis\n";
#print "------------------------------------------------------------\n";
my $ARDOC_WORK_AREA="$ARDOC_WORK_AREA";
my $ARDOC_DBFILE = "$ARDOC_DBFILE";
my $ARDOC_DBFILE_GEN = "$ARDOC_DBFILE_GEN";
my $ARDOC_MAIL = "$ARDOC_MAIL";
my $ARDOC_MAIL_WARNINGS = "$ARDOC_MAIL_WARNINGS";
my $ARDOC_MAIL_MINOR_WARNINGS = "$ARDOC_MAIL_MINOR_WARNINGS";
my $ARDOC_MAIL_UNIT_TESTS = "$ARDOC_MAIL_UNIT_TESTS";
my $ARDOC_MAIL_INT_TESTS = "$ARDOC_MAIL_INT_TESTS";
my $ARDOC_MAIL_PROJECT_KEYS = "$ARDOC_MAIL_PROJECT_KEYS";
my $ARDOC_PROJECT_RELNAME = "$ARDOC_PROJECT_RELNAME";
my $ARDOC_PROJECT_NAME = "$ARDOC_PROJECT_NAME";
my $ARDOC_LOGDIR = "$ARDOC_LOGDIR";
my $ARDOC_TESTLOG = "$ARDOC_TESTLOG";
my $ARDOC_PROJECTBUILD_DIR = "$ARDOC_PROJECTBUILD_DIR";
my $ARDOC_WEBDIR = "$ARDOC_WEBDIR";
my $ARDOC_WEBPAGE = "$ARDOC_WEBPAGE";
my $ARDOC_NIGHTLY_NAME = "$ARDOC_NIGHTLY_NAME";
my $ARDOC_ARCH="$ARDOC_ARCH";
my $ARDOC_TESTLOGDIR = "";
$ARDOC_TESTLOGDIR = dirname(${ARDOC_TESTLOG});

$prevdir=cwd;

$nomail=1;
##if ( $ARDOC_MAIL eq "yes" && $part_t eq "no" ){ $nomail=0; }
@nomail_t=(1, 1, 1);

$fileorig="${ARDOC_DBFILE}";
$base_file=basename($ARDOC_DBFILE);
$filename_gen="${ARDOC_WORK_AREA}/${base_file}_gen";
$filename="$filename_gen";
$filename_res="${ARDOC_WORK_AREA}/${base_file}_gen_res";
if ( -f $filename_res ) { $filename="${filename_res}"; } 
$prepage="ardoc_prepage";
$prepage_problems="ardoc_prepage_problems";
$testprepage="ardoc_testprepage";
$release="${ARDOC_PROJECT_RELNAME}";
$project="${ARDOC_PROJECT_NAME}";
$nightly="${ARDOC_NIGHTLY_NAME}"; 
$ARDOC_LOGDIR=dirname($ARDOC_LOG);

### NO TEST RESULTS PROCESSING AT THIS MOMENT
ardoc_testhandler(2);
$ndir = "${ARDOC_RELHOME}/${ARDOC_PROJECTBUILD_DIR}";
chdir "$ndir";
 
$WLogdir="ARDOC_Log_${release}";
$WTLogdir="ARDOC_TestLog_${release}";
$ndir = "${ARDOC_WEBDIR}/${WLogdir}";
if ( ! -d $ndir ){ 
system("mkdir","-p","${ndir}");
}

$filet = "${ARDOC_WORK_AREA}/$testprepage";
$file="${ARDOC_WORK_AREA}/$prepage";

$part_t="no";
#This if block goes till the end
if ( $part_t eq "no" ) {
  
  opendir(DDD, ${ARDOC_LOGDIR});
  @allcpfiles = readdir DDD;
  closedir DDD;

  @listf1 = grep !/^.+\.loglog.+$/, @allcpfiles;
  @listf = grep !/^.+\.loglog$/, @listf1;
  @allcpfiles=("");
  foreach $lf (@listf){
    next if $lf =~ /^\.\.?$/;
    next if $lf =~ /~$/;
    system("cp -pf ${ARDOC_LOGDIR}/${lf} ${ARDOC_WEBDIR}/${WLogdir}/.");
  }
  @listf=("");
# remove ardoc_general.loglog and ardoc_build.loglog from web directory
# NO, KEEP ardoc_build.loglog
#  system("rm -f ${ARDOC_WEBDIR}/${WLogdir}/ardoc_build.loglog");
  system("rm -f ${ARDOC_WEBDIR}/${WLogdir}/ardoc_general.loglog");
  if ( -f $file ){ unlink "$file"; }

  open(DBF,"$filename_gen");
  chomp(my @dbc=<DBF>);
  close(DBF);
  %container_addr=();
  foreach (@dbc) 
  {
    next if ($_ =~ /^#/);
    ( $lin1 = $_ ) =~ s/ //g;
    next if (length($lin1) eq 0);
    $lll = join(' ', split(' ', $_));
    @fields = split(" ", $lll);
    $package = $fields[0];
    $tag = $fields[1];
    @addr=();
    for ($m=3; $m <= $#fields; $m++){
	push(@addr, $fields[$m]);
    }
    @fields = split("/", $package);
	     if ( $#fields == 0 ){
                 $container_addr{$package} = [ @addr ];
	     }
  }
#      for $fghi (keys %container_addr){
#      print "COOOO $fghi @{$container_addr{$fghi}}\n";
#  }

  @dbc=();
  open(DBF,"$filename");
  chomp(my @dbc=<DBF>);
  close(DBF);
  my @fieldstr=();
  my @patterns=();
  $scount=0;
  $totcount=0;

  open(FL,">$file");
  foreach (@dbc)
  {
#       Ignore comments
        next if ($_ =~ /^#/);
        ( $lin1 = $_ ) =~ s/ //g;
        next if (length($lin1) eq 0);
#       remove trailing leading stretches whitespaces
                 $lll = join(' ', split(' ', $_));
                 @fields = split(" ", $lll);
                 $package = $fields[0];
                 $tag = $fields[1];
         @addr=();
         for ($m=2; $m <= $#fields; $m++){
         push(@addr, $fields[$m]);
         }
	 ( $pkgn = $package ) =~ s/\//_/g;
         if ( $pkgn eq "" ){ $pkgn="$package"; }
	 $pkgbs=basename($package);
	 @fieldsp = split("/", $package);
	 @cont_addr=();
	 if ( $#fields > 0 ){
             $package_cont=$fieldsp[0];
             if (exists($container_addr{$package_cont})){
                 @cont_addr=@{$container_addr{$package_cont}};
                 $container_addr{$package} = [ @addr ];
	     }
	 }
         @strng1=`${ARDOC_HOME}/ardoc_errortester.pl -es ${pkgn} ${release} ${filename} ${package}`; 
#         print "ardoc_errorhandler.pl buildtest: @strng1 *** ${pkgbs} *** ${pkgn} VVV ${release} VVV ${filename} AAA @addr\n";  
#	  print "PIIII $package AA @addr AB @cont_addr\n";
	 $strng=@strng1[0];
	 @fieldstr = split(" ", $strng);
             @patterns=();
             for ($m=3; $m <= $#fieldstr; $m++){
             push(@patterns, $fieldstr[$m]);
             }
#         print "ardoc_errorhandler.pl buildtest: patt: @patterns \n";  
         $problems=0;
         if ( $fieldstr[0] eq "G" && $strng ne "" ) { 
         $problems=2;   
         print "ardoc_errorhandler.pl: error level build problems with $pkgn of $release !!!\n";
         print "ardoc_errorhandler.pl: offending pattern: @patterns\n";
         }
	 if ( $fieldstr[0] eq "W" && $strng ne "" ) {
	 $problems=1;
	 print "ardoc_errorhandler.pl: warning level build problems with $pkgn of $release !!!\n";
         print "ardoc_errorhandler.pl: offending pattern: @patterns\n";
	 }
         if ( $fieldstr[0] eq "M" && $strng ne "" ) {
	 $problems=0.5;
	 print "ardoc_errorhandler.pl: minor warning level build problems with $pkgn of $release !!!\n";
	 print "ardoc_errorhandler.pl: offending pattern: @patterns\n";
         }
  # Determine if there is a problem with unit and qa tests
  my @test_problems=(0, 0, 0);
  my @type=("", "qatest", "test"); 
  $i_init=2;

  for($i=$i_init; $i<=2; $i++){
  ####################################
  # i=1 : qa tests; i=2 : unit tests #
  ####################################
         open(TTT,"<$filet");
	 chomp(my @ttpp=<TTT>);
	 close(TTT);
	 $comp1 = lc($pkgn);
	 $test_problems[$i]=0;

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
                 $trecent_logfiles = $fields[2];
                 $tproblems = $fields[3];
                 @xxxx=();
                    for ($m=3; $m <= $#fields; $m++){
                    push(@xxxx, $fields[$m]);
		 }
                 $comp2 = lc($testname);
		 if ( $comp1 eq $comp2 ){
		     $test_problems[$i]=$tproblems;
                     break
                     }
  } #foreach (@ttpp)

        if ($test_problems[$i] eq 0.5){
        print "ardoc_errorhandler.pl: $type[$i] minor warnings with ${pkgn} !!!\n";}         
	if ($test_problems[$i] eq 1){
        print "ardoc_errorhandler.pl: $type[$i] warnings with ${pkgn} !!!\n";}
        if ($test_problems[$i] ge 2){
        print "ardoc_errorhandler.pl: $type[$i] problems with ${pkgn} !!!\n";}
  } #end of loop that process unit and qa tests

	 opendir(DD, ${ARDOC_LOGDIR});
 	 @allfiles = readdir DD;
         closedir DD;
         $stg="${pkgn}.loglog";
	 @listx = grep /^${stg}$/, @allfiles;
         @list = grep !/^\.\.?$/, @listx;
         $listfilesf = (sort { -M $a <=> -M $b } @list)[0];
#        print " ======= $listfilesf  =======\n";
         @listfields=split(/\./,$listfilesf);
         pop @listfields;
         $listfilesf_base=join('\.',@listfields);
         $listfilesh="${listfilesf_base}.html";

  if ( $listfilesf eq "" ){
  $lf = "${ARDOC_LOGDIR}/${pkgn}.loglog";
  open(FF, ">$lf"); 
  print FF " ARDOC determined that make did nothing for this package.\n";
  print FF " Error in package configuration or structure is possible.\n";
  close(FF); 
  $listfilesf="$ARDOC_LOGDIR/${pkgn}.loglog";
  $listfilesh="$ARDOC_LOGDIR/${pkgn}.html";
  system("cp -pf ${ARDOC_LOGDIR}/${pkgn}.loglog ${ARDOC_WEBDIR}/${WLogdir}/${pkgn}.html");
  system("cp -pf ${ARDOC_LOGDIR}/${pkgn}.loglog ${ARDOC_LOGDIR}/${pkgn}.html");
  $problems=2;
  $fieldstr[0]="G";
  ( $fieldstr[1] = $pkgn ) =~ s/_/\//g;
  $fieldstr[2]=""; 
  $fieldstr[3]="absent logfile";
  $patterns[0]=$fieldstr[3];
  print "ardoc_errorhandler: generating missing logfile @fieldstr\n";
  $strng="G $fieldstr[1] . $fieldstr[3]"; 
  }

  $listfiles=basename($listfilesh);
  $recent_logfile="$listfiles";
#  print " ======= $listfiles  =======\n";
#  print " --  $pkgn -- $recent_logfile -- $problems\n";
   $pkgcontainer=dirname($package);
#  print " --  $package --- $pkgcontainer --- $pkgn -- $recent_logfile -- $problems\n";
   if ( $pkgcontainer eq "." ){ $pkgcontainer="N/A"; }
   $pkgbase=basename($package);

   tr/A-Z/a-z/ for @addr;
   $lin1 = join(" ",@addr);
   ($line = $lin1 ) =~ s/ //g;
   
   $totcount++; 
   if ( $problems eq 2 || $problems eq 1 ) {$scount++;}

   if ( "$line" != "" && "$line" != "-" ){
   print FL "$pkgbase $pkgcontainer $recent_logfile $problems $test_problems[1] $test_problems[2] @addr \"\"\" $fieldstr[2] \"\"\" @patterns\n";
#   print " UUUUUUU $package $pkgcontainer $recent_logfile @addr \"\"\" $fieldstr[2] \"\"\" @patterns\n";
   }
   else{
   print FL "$pkgbase $pkgcontainer $recent_logfile $problems $test_problems[1] $test_problems[2] @addr \"\"\" $fieldstr[2] \"\"\" @patterns\n";
#   print " UUUUUUE $package $pkgcontainer $recent_logfile @addr \"\"\" $fieldstr[2] \"\"\" @patterns\n";
   }
  } # foreasch (@dbc
  close (FL);

  #print "RRRRR $scount $totcount\n";
  $percen=0;
  if ( $totcount != 0 ){ 
    $percen=($scount/($totcount+0.1-0.1))*100;
    $percen=int($percen);
    if ( $percen > 50 ){ 
      print "ardoc_errorhandler.pl: high percentage of packages with compilation problems : $percen : emails disabled\n";
      $nomail=2;
    } else {
      print "ardoc_errorhandler.pl: percentage of packages with compilation problems : $percen\n";
    }
  }  

  @dbc=();
  open(FL,"$file");
  chomp(my @dbc=<FL>);
  close(FL);

  foreach (@dbc)
  {
   next if ($_ =~ /^#/);
   ( $lin1 = $_ ) =~ s/ //g;
   next if (length($lin1) eq 0);
   $lll = join(' ', split(' ', $_));
   @fields9 = split(/ \"\"\" /, $lll);
   @fields = split(" ", $fields9[0]); 
   $patterns_b="";
   $drctr=""; 
   if( $#fields9 > 0 ){ $drctr=$fields9[1];}
   if( $#fields9 > 1 ){ $patterns_b=$fields9[2];}
   $pkgbase=$fields[0];
   $pkgcontainer=$fields[1]; 
   $package="$pkgcontainer/$pkgbase";
   if ( $pkgcontainer eq "N/A" ){ $package="$pkgbase";}
   ( $pkgn = $package ) =~ s/\//_/g;
   $recent_logfile=$fields[2];
   $problems=$fields[3];
   my @test_problems=(0,0,0);
   $test_problems[1]=$fields[4];
   $test_problems[2]=$fields[5];
   @addr=();
   for ($m=6; $m <= $#fields; $m++){
	push(@addr, $fields[$m]);
   }

   if ( ( $problems eq 2 || $problems eq 1 || $problems eq 0.5 ) && $patterns_b ne "" ){ 
   
   $alarm_level="problems";
   if ( $problems eq 1 ) { $alarm_level="warning signs"; } 
   if ( $problems eq 0.5 ) { $alarm_level="minor warning signs"; } 
#   $drctr_copy=$drctr;
#   if ( "$ARDOC_COPY_HOME" ne "" ){
#     $drctr_base=basename(${drctr});
#     $drctr_copy="${ARDOC_COPY_HOME}/${ARDOC_PROJECT_RELNAME_COPY}/ARDOC_area/${drctr_base}";
#   }
#   $var="${drctr_copy}/${pkgn}.loglog";
   $var="${drctr}/${pkgn}.loglog"; 
   $varvar="${ARDOC_WEBPAGE}/${WLogdir}/${pkgn}.html"; 
   @body=();
  push(@body," ===========================================================\n");
  push(@body," This message is generated by ARDOC build for \n");
  push(@body," project $project , $nightly release $release ${ARDOC_ARCH}. \n");
  push(@body," ARDOC system found possible $alarm_level for package \n $package\n");
  push(@body," suspicious pattern:\"$patterns_b\" !!!\n");
  push(@body," ===========================================================\n");
  push(@body," The build logfile is available at: \n $var \n and(or) \n $varvar \n");
  push(@body," ===========================================================\n");
  push(@body," For further information please refer to $project ARDOC webpage \n");
  push(@body," ${ARDOC_WEBPAGE}/index.html\n");
#  print "MMMMM @body \n";

    foreach $address (@addr){
    #$address =~ s/([@])/\\$1/g;
	if ( $address ne "" ){
           if ( $address =~ /@/  ){

  $nomail_1=$nomail;
#  $nomail_1=-1;
  if ( $ARDOC_MAIL_WARNINGS eq "no" && $alarm_level eq "warning signs" ){ $nomail_1=1; }
  if ( $ARDOC_MAIL_MINOR_WARNINGS ne "yes" && $alarm_level eq "minor warning signs" ){ $nomail_1=1; }

  print "ardoc_errorhandler.pl: Problems with $package !!! Mail is sent to $address code $nomail_1 (orig. $nomail ) \n";  
  if ( $nomail_1 eq 0 ){  
    $from_address="atnight";
    $to_address="$address";
    $subject="ARDOC: ${project}: build problems in ${nightly} ${release} ${ARDOC_ARCH} with ${package}";
#    $mailer = Mail::Mailer->new("sendmail");
#    $mailer->open({ From => "${from_address}",
#                      To => "${to_address}",
#                 Subject => "${subject}",
#          })
#    or die "Mailer can not open: $!\n";
#    print $mailer @body;
#    $mailer->close();
  }

  } #if ( $address =~ /@/  )
  } #if ( $address ne "" )
  } #foreach $address
  } #if problems

  for($i=2; $i<=2; $i++){
  ####################################
  # i=1 : qa tests; i=2 : unit tests #
  ####################################
  if ( $test_problems[$i] gt 0.5 ){

  $dirtest=dirname(${ARDOC_TESTLOG});
#  $dirtest_copy=$dirtest;
#    if ( "$ARDOC_COPY_HOME" ne "" ){
#    $dirtest_base=basename(${dirtest});
#    $dirtest_copy="${ARDOC_COPY_HOME}/${ARDOC_PROJECT_RELNAME_COPY}/ARDOC_area/${dirtest_base}";
#    }
#  $var="${dirtest_copy}/${pkgn}.loglog";
  $var="${dirtest}/${pkgn}.loglog"; 
  $varvar="${ARDOC_WEBPAGE}/${WTLogdir}/${pkgn}.html";
  @body=();
  $typet=$type[$i];
  push(@body," ===========================================================\n");
  push(@body," This message is generated by ARDOC build for \n");
  push(@body," project $project , $nightly release $release ${ARDOC_ARCH}. \n");
  push(@body," ARDOC system found possible problems with ${typet}s for package \n $package\n");
  push(@body," ===========================================================\n");
  push(@body," The ${typet} logfile is available at: \n $var \n and(or) \n $varvar \n");
  push(@body," ===========================================================\n");
  push(@body," For further information please refer to $project ARDOC webpage \n");
  push(@body," ${ARDOC_WEBPAGE}/index.html\n");

    foreach $address (@addr){
    #$address =~ s/([@])/\\$1/g;
        if ( $address ne "" ){
           if ( $address =~ /@/  ){

  print "ardoc_errorhandler.pl: Problems with ${typet}s of  $package !!! Mail is sent to $address code $nomail_t[$i]\n";
#  print "MMMMMM @body \n";

  if ( $nomail_t[$i] eq 0 ){
    $from_address="atnight";
    $to_address="$address";
    $subject="ARDOC: ${project}: ${typet} problems in ${nightly} ${release} ${ARDOC_ARCH} with ${package}";
#    $mailer = Mail::Mailer->new("sendmail");
#    $mailer->open({ From => "${from_address}",
#                      To => "${to_address}",
#                 Subject => "${subject}",
#          })
#    or die "Mailer can not open: $!\n";
#    print $mailer @body;
#    $mailer->close();
  }

  } #if ( $address =~ /@/  )
  } #if ( $address ne "" )
  } #foreach $address
  } #if test_problems
  } # end of loop over test types

  } # foreasch (@dbc : second loop

} # if $part_t eq "no"

chdir "${prevdir}";






