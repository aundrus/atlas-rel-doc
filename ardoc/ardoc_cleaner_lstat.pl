#!/usr/bin/env perl
use Env;
use File::Basename;
if ( "$#ARGV" <= 0 || "$#ARGV" > 2 ){
print "ardoc_cleaner.pl: two or three arguments required:\n";
print "-----path to area and maximum allowed age of files (days)\n";
print "-----and exception regexp\n";
exit 1;
} 

$area=$ARGV[0];
$days=$ARGV[1];
$reg_except="GFBBBBB";
if ( "$#ARGV" == 2 ) {$reg_except=$ARGV[2];}
$lmt=$days*10;

if ( ! -d $area ){
print "ardoc_cleaner.pl: area $area does not exist\n";
exit 1;
}

opendir(WWD, ${area});
@allfiles = grep { !/^\.\.?\z/ }
readdir (WWD);
closedir(WWD);

@allfiles=sort{(lstat("${area}/$a"))[9] <=> (lstat("${area}/$b"))[9]} @allfiles;

foreach $ff (@allfiles){
    $mkm="${area}/${ff}";
    if ( $mkm !~ /${reg_except}/ ){
        $mkmk=`${ARDOC_HOME}/ardoc_mtime_diff_lstat.pl $mkm`;
        if ($mkmk <= $lmt) {last;}
        if ($mkmk > $lmt){ 
        print "ardoc_cleaner: age > ${days} day(s):  $ff $mkmk $lmt\n";
        if ( -l $mkm ){
            $mkm_rl=readlink($mkm); 
	    if ( $mkm_rl =~ /\/eos\/squash/ ){
                print "ardoc_cleaner: SquashFS volume DELETED:  $mkm\n";
                $output_squash_rm=`eos squash rm ${mkm} 2>&1`;
		print "${output_squash_rm}\n";
            } else {
                print "ardoc_cleaner: link DELETED:  $mkm\n";
                system("rm -rf ${mkm}");
	    }
        } else { 
            print "ardoc_cleaner: DELETED:  $mkm\n";
            system("rm -rf ${mkm}");
        }
        }
    }
}
