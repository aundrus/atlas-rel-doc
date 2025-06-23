#!/usr/bin/env perl
use Env;
use File::Basename;
if ( "$#ARGV" < 0 || "$#ARGV" > 0 ){
print "ardoc_home_cleaner.pl: Error: one argument required:\n";
print "-----maximum allowed age of files/directories (days)\n";
exit 1;
} 

$days=$ARGV[0];
$lmt=$days*10;

my $ARDOC_HOME="$ARDOC_HOME";
my $ARDOC_WEBDIR="$ARDOC_WEBDIR";
my $ARDOC_JOB_LOG="$ARDOC_JOB_LOG";
if ( "$ARDOC_HOME" eq "" ){
    print "ardoc_home_cleaner.pl: Error: variable \$ARDOC_HOME is not defined \n";
    exit 1;
}
$ARDOC_HOME_DIR=dirname(${ARDOC_HOME});
if ( ! -d $ARDOC_HOME_DIR){
    print "ardoc_home_cleaner.pl: Error: area $ARDOC_HOME_DIR is not defined \n";
    exit 1;
}

print "ardoc_home_cleaner.pl: INFO: cleaning ardoc_local_gen_config files in $ARDOC_HOME_DIR \n";
opendir(WWD, ${ARDOC_HOME_DIR});
@allfiles = grep { !/^\.\.?\z/ }
readdir (WWD);
closedir(WWD);

@allfiles=sort{(stat("${area}/$a"))[9] <=> (stat("${area}/$b"))[9]} @allfiles;

foreach $ff (@allfiles){
    $mkm="${ARDOC_HOME_DIR}/${ff}";
    if ( $ff =~ /^ardoc_local_gen_config.*$/ ){
        $mkmk=`${ARDOC_HOME}/ardoc_mtime_diff.pl $mkm`;
        if ($mkmk <= $lmt) {last;}
        if ($mkmk > $lmt){ 
        print "ardoc_home_cleaner: age > ${days} day(s):  $ff $mkmk $lmt\n";
        print "ardoc_home_cleaner: DELETED:  $mkm\n";
        system("rm -rf ${mkm}");
        }
    }
}

if ( "$ARDOC_WEBDIR" ne "" && -d $ARDOC_WEBDIR){
    print "ardoc_home_cleaner.pl: INFO: cleaning web files areas in $ARDOC_WEBDIR \n";
    opendir(WWD, ${ARDOC_WEBDIR});
    @allfiles = grep { !/^\.\.?\z/ }
    readdir (WWD);
    closedir(WWD);

    @allfiles=sort{(stat("${area}/$a"))[9] <=> (stat("${area}/$b"))[9]} @allfiles;

    foreach $ff (@allfiles){
	$mkm="${ARDOC_WEBDIR}/${ff}";
	if ( $ff =~ /^ARDOC.*Log.*$/ ){
	    $mkmk=`${ARDOC_HOME}/ardoc_mtime_diff.pl $mkm`;
	    if ($mkmk <= $lmt) {last;}
	    if ($mkmk > $lmt){
		print "ardoc_home_cleaner: age > ${days} day(s):  $ff $mkmk $lmt\n";
		print "ardoc_home_cleaner: DELETED:  $mkm\n";
                system("rm -rf ${mkm}");
	    }
	}
    }
}

if ( "${ARDOC_JOB_LOG}" ne "" ){
    $ARDOC_JOB_LOGDIR=dirname(${ARDOC_JOB_LOG});
    if ( -d $ARDOC_JOB_LOGDIR){
        print "ardoc_home_cleaner.pl: INFO: cleaning job log area $ARDOC_JOB_LOGDIR\n";
	opendir(WWD, ${ARDOC_JOB_LOGDIR});
	@allfiles = grep { !/^\.\.?\z/ }
	readdir (WWD);
	closedir(WWD);

	@allfiles=sort{(stat("${area}/$a"))[9] <=> (stat("${area}/$b"))[9]} @allfiles;

	foreach $ff (@allfiles){
	    $mkm="${ARDOC_JOB_LOGDIR}/${ff}";
	    if ( $ff =~ /^log.*$/ ){
		$mkmk=`${ARDOC_HOME}/ardoc_mtime_diff.pl $mkm`;
		if ($mkmk <= $lmt) {last;}
		if ($mkmk > $lmt){
		    print "ardoc_home_cleaner: age > ${days} day(s):  $ff $mkmk $lmt\n";
		    print "ardoc_home_cleaner: DELETED:  $mkm\n";
                    system("rm -rf ${mkm}");
		}
	    }
	}
    }
}
