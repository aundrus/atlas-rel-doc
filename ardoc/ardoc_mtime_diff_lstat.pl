#!/usr/bin/env perl
use Time::Local;

for (@ARGV) {
    @modtime = localtime((lstat($_))[9]);
    @curtime = localtime(time());
#    print "MMMM @modtime\n";
#    print "AMMM @modtime[0,1,2,3,4,5]\n"; 
    $timemod = timelocal(@modtime[0,1,2,3,4,5]);
    $timecur = timelocal(@curtime[0,1,2,3,4,5]);
    $timedif = $timecur - $timemod;
    $diffhour = $timedif/3600;
    $diftimprec_1 = int ($diffhour/24*10);  
#    print "DIFF1: $diffhour $diftimprec_1\n";
    $mtim=$modtime[7]+1;
    $mtimh=int ($modtime[2]/24*10);
    $ctim=$curtime[7]+1;
    $ctimh=int ($curtime[2]/24*10);
    $diftim=$ctim-$mtim;
    if($diftim < 0 ) {$diftim=$diftim + 366}
    $diftimprec=$diftim*10+$ctimh-$mtimh;
#    print "DIFF2: $diftim *10 + $ctimh - $mtimh $diftimprec\n"; 
    print "$diftimprec_1";
}
exit;













